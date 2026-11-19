"""Read-only access to Google Calendar and Notion, plus the single write the agent is allowed:
saving a finding to the Proposals database. Uses only the Python standard library."""

import json
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

import config


def _http(method, url, headers=None, body=None, form=None):
    data = None
    headers = dict(headers or {})
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    elif form is not None:
        data = urllib.parse.urlencode(form).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode() or "{}")


class GoogleCalendar:
    """Read-only. The refresh token is created with the calendar.readonly scope, so Google itself
    refuses any write even if this code were changed."""

    def __init__(self, client_id, client_secret, refresh_token):
        self.client_id, self.client_secret, self.refresh_token = client_id, client_secret, refresh_token
        self._token = None

    def _access_token(self):
        if not self._token:
            out = _http("POST", "https://oauth2.googleapis.com/token", form={
                "client_id": self.client_id, "client_secret": self.client_secret,
                "refresh_token": self.refresh_token, "grant_type": "refresh_token"})
            self._token = out["access_token"]
        return self._token

    def list_events(self, start, end):
        """start/end: timezone-aware datetimes. Returns events from the allowed calendars only."""
        events = []
        for cal_id, cal_name in config.CALENDARS.items():
            q = urllib.parse.urlencode({"timeMin": start.isoformat(), "timeMax": end.isoformat(),
                                        "singleEvents": "true", "orderBy": "startTime",
                                        "maxResults": 250, "timeZone": config.TIMEZONE})
            url = f"https://www.googleapis.com/calendar/v3/calendars/{urllib.parse.quote(cal_id)}/events?{q}"
            data = _http("GET", url, headers={"Authorization": f"Bearer {self._access_token()}"})
            for e in data.get("items", []):
                if e.get("status") == "cancelled":
                    continue
                s, en = e.get("start", {}), e.get("end", {})
                events.append({
                    "calendar": cal_name, "calendar_id": cal_id, "event_id": e.get("id"),
                    "title": e.get("summary", "(no title)"),
                    "all_day": "date" in s,
                    "start": s.get("dateTime") or s.get("date"),
                    "end": en.get("dateTime") or en.get("date"),
                    "free": e.get("transparency") == "transparent",
                })
        events.sort(key=lambda x: x["start"] or "")
        return events


class Notion:
    VERSION = "2022-06-28"

    def __init__(self, token):
        self.headers = {"Authorization": f"Bearer {token}", "Notion-Version": self.VERSION}

    def _query(self, db_id, body):
        rows, cursor = [], None
        while True:
            b = dict(body)
            if cursor:
                b["start_cursor"] = cursor
            out = _http("POST", f"https://api.notion.com/v1/databases/{db_id}/query", self.headers, b)
            rows += out.get("results", [])
            if not out.get("has_more"):
                return rows
            cursor = out.get("next_cursor")

    @staticmethod
    def _text(prop):
        if not prop:
            return ""
        parts = prop.get("title") or prop.get("rich_text") or []
        return "".join(p.get("plain_text", "") for p in parts)

    @staticmethod
    def _date(prop):
        d = (prop or {}).get("date")
        return d.get("start") if d else None

    @staticmethod
    def _select(prop):
        s = (prop or {}).get("select") or (prop or {}).get("status")
        return s.get("name") if s else None

    def open_items(self):
        """To-dos, projects and ideas that are not done."""
        rows = self._query(config.TASKS_DB_ID, {"filter": {"property": "Status", "status": {"does_not_equal": "Done"}}})
        items = []
        for r in rows:
            p = r["properties"]
            items.append({
                "title": self._text(p.get("Task")), "type": self._select(p.get("Type")),
                "due": self._date(p.get("Due")), "show_from": self._date(p.get("Show from")),
                "progress": (p.get("Progress %") or {}).get("number"),
            })
        return items

    def pending_proposals(self):
        rows = self._query(config.PROPOSALS_DB_ID, {"filter": {"property": "Status", "select": {"equals": "Pending"}}})
        return [{"title": self._text(r["properties"].get("Title")),
                 "check": self._text(r["properties"].get("Check")),
                 "kind": self._select(r["properties"].get("Kind"))} for r in rows]

    def save_proposal(self, f):
        rt = lambda s: {"rich_text": [{"text": {"content": s[:1900]}}]} if s else {"rich_text": []}
        props = {
            "Title": {"title": [{"text": {"content": f["title"]}}]},
            "Kind": {"select": {"name": f["kind"]}},
            "Status": {"select": {"name": "Pending"}},
            "Source": {"select": {"name": "Nightly check"}},
            "Detail": rt(f["detail"]),
            "Check": rt(f["check_id"]),
            "Action": rt(json.dumps(f["action"]) if f.get("action") else ""),
        }
        if f.get("for_date"):
            props["For date"] = {"date": {"start": f["for_date"]}}
        return _http("POST", "https://api.notion.com/v1/pages", self.headers,
                     {"parent": {"database_id": config.PROPOSALS_DB_ID}, "properties": props})
