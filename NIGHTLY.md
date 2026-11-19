# Optional: nightly check

A small agent that runs on GitHub every evening, before Megan's 8 PM brief. Claude looks over the next few weeks of her Google Calendar and her Notion list, and writes **findings** to the Notion *Proposals* database. The 8 PM brief (a Claude scheduled task) and the Home app pick them up from there.

## What it checks

1. **Clashes tomorrow:** suggests moving one event to the nearest free slot. This is an *Approval*, so it only happens if Megan taps Approve in Home.
2. **Exams or interviews in the next 30 days** with no "Plan for …" to-do.
3. **Overdue to-dos.**
4. **Bumped items coming back tomorrow.**
5. **Crowded weeks:** 3 or more deadlines in one week within the next 4 weeks.
6. **Projects due within 14 days:** shows her own progress figure next to the deadline.

## How it stays safe

Claude does the thinking. The code limits what any run can do, whatever the model says.

| Rule | Enforced by |
|---|---|
| Can't change the calendar at all | Google token only has the `calendar.readonly` permission |
| Can't edit or delete Notion items | Notion integration only has *Read* and *Insert* permissions; the only write is a new Proposal row |
| Calendar changes need Megan's tap | Approvals are stored as a suggested change; the Home app makes it only on Approve |
| Never delete, only create or move | `guardrails.py` refuses any other action |
| Only her own calendars | allow-list from the `COS_CALENDARS` secret (shared and holiday calendars left out) |
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

### 1. Notion (2 minutes)
1. Go to <https://www.notion.so/profile/integrations>, then **New integration**. Name it "Chief of Staff nightly check" and choose your workspace.
2. Under **Capabilities**, keep **Read content** and **Insert content**, and **untick Update content**.
3. Copy the **Internal integration secret**. This is `NOTION_TOKEN`.
4. Open each database, **Chief of Staff – Tasks (test)** and **Chief of Staff – Proposals**, then **•••** › **Connections** › add the integration.

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
2. On the **Variables** tab, add `DRY_RUN` = `true` for the first week.
3. Go to **Actions** › **Nightly check** › **Run workflow** to test now. Manual runs default to a dry run. Read the log.
4. Once you're happy with it, delete the `DRY_RUN` variable (or set it to `false`). From then on, scheduled runs save their findings.
