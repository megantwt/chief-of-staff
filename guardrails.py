"""Rules enforced in code, whatever the model says. The model can only *suggest*; these decide."""

import re
from datetime import date

import config

KINDS = {"Approval", "Heads-up"}
OPS = {"create", "update"}
ISO_DT = re.compile(r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}(:\d{2})?)?$")
HOURS_WORDS = re.compile(r"\b(\d+(\.\d+)?\s*(h|hrs?|hours?)\b|block (out )?time|work session|study session)", re.I)


class Rejected(Exception):
    pass


def validate_finding(f, pending_checks, saved_this_run):
    """Return a cleaned finding or raise Rejected with a reason the model can read."""
    if saved_this_run >= config.MAX_FINDINGS:
        raise Rejected(f"limit reached: at most {config.MAX_FINDINGS} findings per night")
    kind = f.get("kind")
    if kind not in KINDS:
        raise Rejected("kind must be 'Approval' or 'Heads-up'")
    title = (f.get("title") or "").strip()
    detail = (f.get("detail") or "").strip()
    check_id = (f.get("check_id") or "").strip()
    if not title or len(title) > 120:
        raise Rejected("title is required and must be at most 120 characters")
    if len(detail) > 500:
        raise Rejected("detail must be at most 500 characters")
    if not check_id:
        raise Rejected("check_id is required")
    if check_id in pending_checks:
        raise Rejected("duplicate: a pending item with this check_id already exists")
    if HOURS_WORDS.search(title + " " + detail):
        raise Rejected("no hours: do not suggest time blocks or durations for tasks")
    for_date = f.get("for_date")
    if for_date:
        try:
            date.fromisoformat(for_date[:10])
        except ValueError:
            raise Rejected("for_date must be YYYY-MM-DD")
        for_date = for_date[:10]
    action = f.get("action")
    if kind == "Heads-up":
        action = None
    else:
        action = validate_action(action)
    return {"kind": kind, "title": title, "detail": detail, "check_id": check_id,
            "for_date": for_date, "action": action}


def validate_action(a):
    """An Approval carries the exact calendar change the Home app will make IF the user taps Approve.
    The agent itself has no way to change the calendar."""
    if not isinstance(a, dict):
        raise Rejected("an Approval needs an action object")
    if a.get("op") not in OPS:
        raise Rejected("action.op must be 'create' or 'update' (never delete)")
    if a.get("calendarId") not in config.CALENDARS:
        raise Rejected("action.calendarId must be one of the allowed calendars")
    if a["op"] == "update" and not a.get("eventId"):
        raise Rejected("an update needs eventId")
    if a["op"] == "create" and not a.get("summary"):
        raise Rejected("a create needs summary")
    for k in ("startTime", "endTime"):
        if a.get(k) and not ISO_DT.match(str(a[k])):
            raise Rejected(f"action.{k} must be local ISO time like 2026-11-20T13:15:00, no offset")
    if a["op"] == "create" and not (a.get("startTime") and a.get("endTime")):
        raise Rejected("a create needs startTime and endTime")
    keep = ("op", "calendarId", "eventId", "summary", "startTime", "endTime", "allDay")
    return {k: a[k] for k in keep if k in a}
