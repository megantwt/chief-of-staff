"""Settings for the nightly check.

Personal values (calendar IDs, Notion database IDs) are NOT stored in this file. They come from
GitHub Actions secrets, so the repo can be public. Without them, the placeholders below are used
(that's what the offline tests run against).
"""

import json
import os

TIMEZONE = (os.environ.get("COS_TIMEZONE") or "America/New_York")

# First name used in the agent's instructions. Set the COS_OWNER secret, or leave it as "the user".
OWNER = (os.environ.get("COS_OWNER") or "the user")

# Calendars the agent may READ, as {"calendar id": "name"}. Anything not listed is ignored.
# Set the COS_CALENDARS secret to a JSON object like the placeholder below.
_PLACEHOLDER_CALENDARS = {
    "you@example.com": "classes",
    "deadlines-calendar-id@group.calendar.google.com": "deadlines",
    "exams-calendar-id@group.calendar.google.com": "exam/interviews",
    "social-calendar-id@group.calendar.google.com": "social",
}
CALENDARS = json.loads(os.environ["COS_CALENDARS"]) if os.environ.get("COS_CALENDARS") else _PLACEHOLDER_CALENDARS

# Notion databases (IDs only; access is granted by sharing them with the integration).
TASKS_DB_ID = ((os.environ.get("COS_TASKS_DB_ID") or "").strip() or "your-tasks-database-id")
PROPOSALS_DB_ID = ((os.environ.get("COS_PROPOSALS_DB_ID") or "").strip() or "your-proposals-database-id")

# Claude model and limits.
MODEL = "claude-sonnet-5-5"
MAX_TURNS = 12            # tool-use rounds per run
MAX_FINDINGS = 8          # most proposals/heads-ups saved per night
LOOKAHEAD_DAYS = 30       # how far ahead the agent may read the calendar
