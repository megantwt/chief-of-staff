# Optional: nightly check

A small agent that runs on GitHub every evening, before the evening brief. Claude looks over the next few weeks of your Google Calendar and your Notion list for **patterns the daily view misses**, and writes findings to the Notion *Proposals* database. It never sends its own message: findings appear in the evening brief under "Needs you", in Home (Approve / Got it), and as charts in the Sunday evening brief.

## What it looks for

1. **Stalled projects + free time:** a project untouched for 7+ days, paired with tomorrow's longest free stretch ("Seminar paper hasn't moved in 9 days. Tomorrow 14:00 to 17:00 is free."). Free stretches are computed in code (`free_stretches` in `agent.py`), and "untouched" comes from Notion's last-edited time. It never says how long to work.
2. **Bump drift:** anything bumped 3+ times. Home counts bumps in the *Times bumped* property (add it to your Tasks database as a Number).
3. **Exams or interviews in the next 30 days** with no "Plan for …" to-do.
4. **Crowded weeks:** 3 or more deadlines in one week within the next 4 weeks.
5. **Projects due within 14 days:** your own progress figure next to the deadline.

Clashes and overdue to-dos are deliberately not here: Quick add warns about clashes the moment you add an event, and the briefs already show overdue items.

## How it stays safe

Claude does the thinking. The code limits what any run can do, whatever the model says.

| Rule | Enforced by |
|---|---|
| Can't change the calendar at all | Google token only has the `calendar.readonly` permission |
| Can't edit or delete Notion items | Notion integration only has *Read* and *Insert* permissions; the only write is a new Proposal row |
| Calendar changes need your tap | Approvals are stored as a suggested change; the Home app makes it only on Approve |
| Never delete, only create or move | `guardrails.py` refuses any other action |
| Only your own calendars | allow-list from the `COS_CALENDARS` secret (shared and holiday calendars left out) |
| No hours or time blocks | `guardrails.py` refuses findings that suggest them |
| No repeats, no flooding | at most 8 findings a night; duplicates (same `check_id`) refused |
| Calendar and Notion text can't give orders | stated in the prompt, and nothing it reads can unlock a tool |
| Trial mode | set the `DRY_RUN` variable to `true`: it shows findings in the run log and saves nothing |

## Files

- `agent.py`: the prompt, the tools and the Claude tool loop
- `sources.py`: read Google Calendar and Notion, and save a proposal (standard library only)
- `guardrails.py`: the rules above
- `config.py`: model and limits; calendar and database IDs come from secrets, so none are in the code
- `.github/workflows/nightly.yml`: runs tests, then the check, every day at 23:15 UTC (6:15 PM Boston in winter)
- `get_google_token.py`: one-time helper to get the read-only Google token
- `tests/`: offline tests with a scripted fake Claude (`python -m unittest discover -s tests`)

## Setup (about 20 minutes, once)

### 0. Your own copy of this repo
1. **Fork** this repo on GitHub (top right).
2. In your fork, open the **Actions** tab and click **I understand my workflows, go ahead and enable them**. GitHub keeps scheduled workflows off in new forks until you do this.
3. If you set up the Chief of Staff with the Claude skill, say **"Prepare my nightly check settings"** in Claude. It gives you the values for step 4 (your calendar list and database IDs), ready to paste.

### 1. Notion (2 minutes)
1. Go to <https://www.notion.so/profile/integrations>, then **New integration**. Name it "Chief of Staff nightly check" and choose your workspace.
2. Under **Capabilities**, keep **Read content** and **Insert content**, and **untick Update content**.
3. Copy the **Internal integration secret**. This is `NOTION_TOKEN`.
4. Open each database, **Chief of Staff – Tasks** and **Chief of Staff – Proposals**, then **•••** › **Connections** › add the integration.
5. Check the databases have the properties the agent reads and writes (the skill's setup creates them all):
   - Tasks: Task, Type, Status, Due, Show from, Progress %, **Times bumped** (number).
   - Proposals: Title, Kind, Status, Detail, Action, For date, **Check** (text), **Source** (select with a *Nightly check* option), Created.

### 2. Google Calendar, read-only (10 minutes)
1. Go to <https://console.cloud.google.com>, then **New project** ("chief-of-staff").
2. **APIs & Services** › **Library** › enable **Google Calendar API**.
3. **OAuth consent screen**: choose External, fill in the app name and your email, and add yourself as a test user. Then set the publishing status to **In production**. While it's in *Testing*, Google expires the token every 7 days.
4. **Credentials** › **Create credentials** › **OAuth client ID** › **Desktop app**. Copy the client ID and secret: these are `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`.
5. On your laptop, run `python get_google_token.py <client id> <client secret>` and sign in with your personal Gmail. Google will warn that the app isn't verified: click **Advanced** › **Go to chief-of-staff**. This is expected for your own app. Allow "See your calendars". The script prints `GOOGLE_REFRESH_TOKEN`.

### 3. Claude API
Create a key at <https://console.anthropic.com>. This is `ANTHROPIC_API_KEY`. One run a night costs a few cents.

### 4. GitHub
1. Go to repo **Settings** › **Secrets and variables** › **Actions** › **New repository secret**, and add the five secrets: `ANTHROPIC_API_KEY`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN`, `NOTION_TOKEN`. Then add three more with your own IDs, so they never appear in the code: `COS_CALENDARS` (a JSON object of calendar ID → name, e.g. `{"you@gmail.com": "classes", "abc123@group.calendar.google.com": "deadlines"}`), `COS_TASKS_DB_ID` and `COS_PROPOSALS_DB_ID` (the 32-character IDs in your Notion database links). Optionally add `COS_OWNER` (your first name, so the agent knows who it works for) and `COS_TIMEZONE` (e.g. `America/New_York`).
   - **Calendar IDs:** in Google Calendar, open a calendar's **Settings and sharing** › **Integrate calendar** › **Calendar ID**. Your main calendar's ID is your Gmail address. Leave out holiday calendars and calendars other people own.
   - **Database IDs:** open the database in Notion, **Share** › **Copy link**. The ID is the 32 characters after the last `/` and before any `?`.
2. On the **Variables** tab, add `DRY_RUN` = `true` for the first week.
3. Go to **Actions** › **Nightly check** › **Run workflow** to test now. Manual runs default to a dry run. Read the log.
4. Once you're happy with it, delete the `DRY_RUN` variable (or set it to `false`). From then on, scheduled runs save their findings.
