"""Offline tests: no network, no keys. A scripted fake Claude drives the real tool loop."""

import os
import sys
import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import config  # noqa: E402
from agent import Run, enrich, free_stretches  # noqa: E402
from guardrails import Rejected, validate_finding  # noqa: E402

LAW = "you@example.com"
NOW = datetime(2026, 11, 18, 18, 15, tzinfo=ZoneInfo("America/New_York"))


class FakeCalendar:
    def __init__(self):
        self.calls = []

    def list_events(self, start, end):
        self.calls.append((start, end))
        return [
            {"calendar": "law classes", "calendar_id": LAW, "event_id": "e1", "title": "BKC Lunch Talk",
             "all_day": False, "start": "2026-11-19T12:20:00-05:00", "end": "2026-11-19T13:30:00-05:00", "free": False},
            {"calendar": "social", "calendar_id": "social-calendar-id@group.calendar.google.com", "event_id": "e2",
             "title": "Coffee with Ana", "all_day": False, "start": "2026-11-19T13:00:00-05:00",
             "end": "2026-11-19T13:30:00-05:00", "free": False},
        ]


class FakeNotion:
    def __init__(self, pending=None):
        self.saved = []
        self._pending = pending or []

    def open_items(self):
        return [
            {"title": "Reply to TA", "type": "To-do", "due": "2026-11-17", "show_from": None, "progress": None,
             "times_bumped": None, "last_edited": "2026-11-17T15:00:00.000Z"},
            {"title": "Seminar paper", "type": "Project", "due": "2026-12-14", "show_from": None, "progress": 35,
             "times_bumped": 0, "last_edited": "2026-11-08T15:00:00.000Z"},
            {"title": "Learn SQL", "type": "Project", "due": None, "show_from": "2026-11-25", "progress": 0,
             "times_bumped": 3, "last_edited": "2026-11-16T15:00:00.000Z"},
        ]

    def pending_proposals(self):
        return list(self._pending)

    def save_proposal(self, f):
        self.saved.append(f)


class ScriptedModel:
    """Plays back a fixed list of assistant turns."""

    def __init__(self, turns):
        self.turns, self.seen = list(turns), []

    def create(self, system, messages, tools):
        self.seen.append(messages[-1])
        return {"content": self.turns.pop(0)}


def call(i, name, args):
    return {"type": "tool_use", "id": f"t{i}", "name": name, "input": args}


CLASH = {"kind": "Approval", "title": "Coffee clashes with the lunch talk", "check_id": "clash:2026-11-19:e2",
         "detail": "Move coffee with Ana to 13:30 to 14:00, right after the talk.", "for_date": "2026-11-19",
         "action": {"op": "update", "calendarId": "social-calendar-id@group.calendar.google.com",
                    "eventId": "e2", "startTime": "2026-11-19T13:30:00", "endTime": "2026-11-19T14:00:00"}}


class GuardrailTests(unittest.TestCase):
    def test_good_approval_passes(self):
        f = validate_finding(CLASH, set(), 0)
        self.assertEqual(f["action"]["op"], "update")

    def test_delete_refused(self):
        bad = dict(CLASH, action=dict(CLASH["action"], op="delete"))
        with self.assertRaises(Rejected):
            validate_finding(bad, set(), 0)

    def test_unknown_calendar_refused(self):
        bad = dict(CLASH, action=dict(CLASH["action"], calendarId="not-allowed@example.com"))
        with self.assertRaises(Rejected):
            validate_finding(bad, set(), 0)

    def test_hours_refused(self):
        bad = {"kind": "Heads-up", "title": "Block 3 hours for the problem set", "detail": "", "check_id": "x"}
        with self.assertRaises(Rejected):
            validate_finding(bad, set(), 0)

    def test_duplicate_refused(self):
        with self.assertRaises(Rejected):
            validate_finding(CLASH, {"clash:2026-11-19:e2"}, 0)

    def test_limit(self):
        with self.assertRaises(Rejected):
            validate_finding(CLASH, set(), config.MAX_FINDINGS)

    def test_headsup_drops_action(self):
        f = validate_finding({"kind": "Heads-up", "title": "Overdue: Reply to TA", "detail": "Due Nov 17.",
                              "check_id": "overdue:2026-11-18", "action": {"op": "delete"}}, set(), 0)
        self.assertIsNone(f["action"])


STALLED = {"kind": "Heads-up", "title": "Seminar paper hasn't moved in 10 days",
           "detail": "Tomorrow 13:30 to 22:00 is free.", "check_id": "stalled:Seminar paper:2026-W47",
           "for_date": "2026-11-19"}


class HelperTests(unittest.TestCase):
    def test_free_stretches_longest_first_and_ignores_free_events(self):
        events = FakeCalendar().list_events(None, None) + [
            {"all_day": False, "free": True, "start": "2026-11-19T09:00:00-05:00", "end": "2026-11-19T11:00:00-05:00"},
            {"all_day": True, "free": False, "start": "2026-11-19", "end": "2026-11-20"}]
        free = free_stretches(events, "2026-11-19")
        self.assertEqual(free[0], {"start": "13:30", "end": "22:00"})
        self.assertIn({"start": "08:00", "end": "12:20"}, free)
        self.assertEqual(len(free), 2)

    def test_free_stretches_skips_short_gaps(self):
        events = [{"start": "2026-11-19T08:00:00-05:00", "end": "2026-11-19T12:00:00-05:00"},
                  {"start": "2026-11-19T12:30:00-05:00", "end": "2026-11-19T22:00:00-05:00"}]
        self.assertEqual(free_stretches(events, "2026-11-19"), [])

    def test_enrich_adds_days_since_edit_and_bumps(self):
        items = enrich(FakeNotion().open_items(), NOW)
        paper = next(i for i in items if i["title"] == "Seminar paper")
        self.assertEqual(paper["days_since_edit"], 10)
        self.assertNotIn("last_edited", paper)
        self.assertEqual(items[0]["times_bumped"], 0)
        self.assertEqual(items[2]["times_bumped"], 3)


class LoopTests(unittest.TestCase):
    def test_pattern_run_uses_free_time_and_saves_heads_up(self):
        model = ScriptedModel([
            [call(1, "list_open_items", {}), call(2, "list_pending_proposals", {}),
             call(3, "free_time", {"date": "2026-11-19"})],
            [call(4, "save_finding", STALLED),
             call(5, "save_finding", {"kind": "Heads-up", "title": "Block 2 hours for the paper",
                                      "detail": "", "check_id": "stalled:x"})],
            [{"type": "text", "text": "Saved 1 stalled-project note."}],
        ])
        notion = FakeNotion()
        run = Run(model, FakeCalendar(), notion, NOW)
        self.assertEqual(run.go(), "Saved 1 stalled-project note.")
        self.assertEqual([f["check_id"] for f in notion.saved], ["stalled:Seminar paper:2026-W47"])
        self.assertIn("no hours", run.rejected[0]["reason"])
        tool_results = model.seen[1]["content"]
        free = next(r for r in tool_results if r["tool_use_id"] == "t3")["content"]
        self.assertIn("13:30", free)
        items = next(r for r in tool_results if r["tool_use_id"] == "t1")["content"]
        self.assertIn("days_since_edit", items)

    def test_free_time_beyond_window_is_empty(self):
        cal = FakeCalendar()
        model = ScriptedModel([[call(1, "free_time", {"date": "2027-06-01"})], [{"type": "text", "text": "done"}]])
        Run(model, cal, FakeNotion(), NOW).go()
        self.assertEqual(cal.calls, [])

    def test_full_run_saves_through_guardrails(self):
        model = ScriptedModel([
            [call(1, "list_calendar_events", {"start_date": "2026-11-19", "end_date": "2026-11-19"}),
             call(2, "list_open_items", {}), call(3, "list_pending_proposals", {})],
            [call(4, "save_finding", CLASH),
             call(5, "save_finding", dict(CLASH, action=dict(CLASH["action"], op="delete"), check_id="bad"))],
            [{"type": "text", "text": "Saved 1 clash fix."}],
        ])
        notion = FakeNotion()
        run = Run(model, FakeCalendar(), notion, NOW)
        summary = run.go()
        self.assertEqual(summary, "Saved 1 clash fix.")
        self.assertEqual(len(notion.saved), 1)
        self.assertEqual(len(run.rejected), 1)
        self.assertIn("never delete", run.rejected[0]["reason"])

    def test_dry_run_saves_nothing(self):
        model = ScriptedModel([[call(1, "save_finding", CLASH)], [{"type": "text", "text": "done"}]])
        notion = FakeNotion()
        run = Run(model, FakeCalendar(), notion, NOW, dry_run=True)
        run.go()
        self.assertEqual(notion.saved, [])
        self.assertEqual(len(run.saved), 1)

    def test_existing_pending_not_repeated(self):
        model = ScriptedModel([[call(1, "save_finding", CLASH)], [{"type": "text", "text": "done"}]])
        notion = FakeNotion(pending=[{"title": "x", "check": "clash:2026-11-19:e2", "kind": "Approval"}])
        run = Run(model, FakeCalendar(), notion, NOW)
        run.go()
        self.assertEqual(notion.saved, [])

    def test_calendar_window_capped(self):
        cal = FakeCalendar()
        model = ScriptedModel([[call(1, "list_calendar_events", {"start_date": "2026-11-19", "end_date": "2027-06-01"})],
                               [{"type": "text", "text": "done"}]])
        Run(model, cal, FakeNotion(), NOW).go()
        start, end = cal.calls[0]
        self.assertLessEqual((end - start).days, config.LOOKAHEAD_DAYS + 1)

    def test_tool_error_reported_not_crashing(self):
        class Broken(FakeNotion):
            def open_items(self):
                raise RuntimeError("Notion is down")
        model = ScriptedModel([[call(1, "list_open_items", {})], [{"type": "text", "text": "Could not read Notion."}]])
        out = Run(model, FakeCalendar(), Broken(), NOW).go()
        self.assertEqual(out, "Could not read Notion.")
        self.assertIn("Notion is down", model.seen[-1]["content"][0]["content"])


if __name__ == "__main__":
    unittest.main()
