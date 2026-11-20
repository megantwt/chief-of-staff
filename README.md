# Chief of Staff

An AI chief of staff that runs my calendar and my to-do list as one system, so I start each day knowing what's coming and what I realistically have room for. It never changes my calendar without my OK.

Built with Claude for DPI-681 (Question 2) by Megan. **[Try the app →](https://claude.ai/artifact/MhbJwnfFpbeNcHif4ehrSe)**

## The problem

**1. My calendar and my to-do list compete for the same hours, but they don't know about each other.**
A calendar says where I need to be; a to-do list says what I need to get done. Both draw on the same day, so the more there is on my list, the less I should book into my calendar. But they live in separate apps. I'd accept a coffee chat, a talk and a study group, and only at 10 pm notice that the problem set is due tomorrow and there's no gap left. Neither app ever says "you have two free hours and four things due."

**2. One to-do list treats everything as the same kind of task.**
An exam in three weeks, a seminar paper due next month, "reply to the TA" and "start a podcast someday" sit in one list with the same checkbox. The list grows, everything looks equally urgent, and it becomes overwhelming. Worse, the things that need preparing weeks ahead (exams, interviews) get buried under small tasks until it's too late to prepare well. They aren't the same kind of thing, so they shouldn't be handled the same way.

**3. I want to know what tomorrow looks like before it starts.**
I plan better and feel calmer when I've seen the shape of the next day the night before (what's booked, where the free time is, what I could work on) and get a quick reminder in the morning before the first thing.

## How it solves them

### 1. One view of time and tasks
- **The day drawn to scale, next to the list.** Home and both briefs show the day hour by hour, with free stretches marked in green, right beside everything I could work on. I can see at a glance whether the list fits the day.
- **Clash warnings when I add something.** Quick add checks the calendar before I save ("This overlaps BKC Lunch Talk 12:20–13:30").
- **Free time matched to stalled work.** The nightly check agent notices a project I haven't touched in a week and points to my next free stretch ("Seminar paper hasn't moved in 9 days. Tomorrow 14:00 to 17:00 is free.").
- **The week at a glance.** Every Sunday the brief shows next week day by day: booked versus free time, with deadlines and exams marked on their day.
- **Deliberately no hour estimates.** It shows the space and lets me decide what fits. It never blocks time for me or guesses how long something will take.

### 2. Different kinds of tasks, handled differently
| Kind | How it's handled |
|---|---|
| **Exams and interviews** | Go on the calendar (on an exams calendar), and a "Plan for …" to-do is created automatically, hidden until two weeks before. The nightly check flags any exam that still has no plan. |
| **Projects** | Their own list, with a deadline and a progress slider that I move myself. Projects can wait under "Starting later". Flagged when they stall, or when the deadline is within 14 days. |
| **Short to-dos** | A plain list sorted by due date, overdue in red. Tick off with undo. |
| **Ideas** | A separate "someday" list, kept out of the daily briefs so it doesn't add noise. |
| **Anything** | Can be **bumped** until a date: it disappears and comes back on its own. Things bumped three or more times get flagged, so nothing quietly rots. |

Quick add sorts new items for me: Claude reads "stats midterm 15 dec, bump me on 5 dec" or a screenshot of a poster and fills in the type, date and calendar, which I check before saving. Any item can switch between to-do and project.

### 3. Briefs that prepare me for the day
- **Evening brief (8 pm):** a new Claude chat with a notification. Tomorrow drawn to scale, every to-do and project I could work on, what's coming in the next two weeks, anything waiting for my OK, and a short quote I can rate.
- **Morning brief:** arrives 30 minutes before my first event (between 6:00 and 7:30): first commitment, most urgent to-do, and the day drawn fresh, so changes I made last night show up.
- **Sunday, "Your week ahead":** next week by day, project progress, and patterns the agent noticed.

## Design choices
- **I approve every calendar change.** Saving in Quick add counts as approval; the agent can only suggest.
- **No hours.** Progress and time estimates are mine to make, not the bot's.
- **No email access.** I decide what goes in. Less access, less to go wrong.
- **An agent, but a cautious one.** The nightly check decides what's worth raising, but its limits are enforced in code: a read-only calendar token, insert-only Notion access, and guardrails that refuse deletions or time blocks whatever the model says.

## How it's built
- **Google Calendar** holds events; **Notion** holds to-dos, projects, ideas and the agent's proposals.
- **Home** is a Claude artifact that reads and writes both through Claude's connectors.
- **Three Claude scheduled tasks:** the evening brief, the morning brief, and a silent 5:41 am task that moves the morning brief to fit the first event.
- **The nightly check** is a Python agent on GitHub Actions using the Claude API, with tests (`tests/`).
- **The skill** packages all of it, so anyone can install it on their own accounts.

## Try it (no setup)

👉 **[Open the app](https://claude.ai/artifact/MhbJwnfFpbeNcHif4ehrSe)** (sign in to Claude if it asks) and choose **Not now: try it on a sample week**. It's the real app running on a made-up student's week, with a guided tour. Nothing touches your accounts.

## Install it on your own accounts (about 5 minutes)

You need a Claude plan with skills and scheduled tasks, plus free Notion and Google accounts.

1. **Download** [`chief-of-staff-skill.zip`](chief-of-staff-skill.zip) from this repo. Don't unzip it.
2. **Upload it to Claude:** go to **Customize → Skills**, click **+**, then **Create skill → Upload a skill**, and choose the zip. Code execution needs to be on in your settings.
3. **Connect** the **Notion** and **Google Calendar** connectors in Claude.
4. **In a new chat, say: "Set up my chief of staff."**

Claude then:
- creates two Notion databases (Tasks, Proposals), or reuses them if you already have them;
- lists your calendars and asks which to ignore and what kind each one is (classes, deadlines, exams, social…);
- builds your own copy of the Home page, linked to your accounts. It asks for permission the first time it uses them;
- schedules your evening and morning briefs, plus a silent early-morning task that moves the morning brief to fit your first event.

After that, just talk to it: "add dinner with Jamie Friday 7pm", "bump the reading until Monday", "brief me for tomorrow", or send a photo of a flyer.

### Optional: add the nightly check agent (about 20 minutes)

For people comfortable with GitHub. Everything above works without it.

1. **Fork this repo** (top right on GitHub). Then open your fork's **Actions** tab and click **I understand my workflows, go ahead and enable them**: GitHub turns scheduled workflows off in new forks.
2. In Claude, say **"Prepare my nightly check settings."** Claude gives you your calendar list and Notion database IDs, ready to paste.
3. Follow [NIGHTLY.md](NIGHTLY.md): a read-only Notion integration, a read-only Google token, a Claude API key, and the GitHub secrets. Start with `DRY_RUN` = `true`.

Its findings show up in your evening brief under "Needs you", in Home, and in the Sunday charts.

## Safety rules at a glance

| Rule | How |
|---|---|
| You approve every calendar change | Claude shows the change first; saving in Quick add counts as approval |
| No hours | It never blocks time or estimates how long things take; you set progress yourself |
| No email | It doesn't read your inbox; you decide what goes in |
| Safe deletes | Deletes have an undo; the nightly check can't delete anything at all |
| Clashes flagged | Quick add warns before you save an event that overlaps something |
| Text can't give orders | Event titles, Notion pages and screenshots are treated as data |

## What's in this repo

| Path | What it is |
|---|---|
| `chief-of-staff-skill.zip` | The package you upload to Claude (built from `skill/`) |
| `skill/chief-of-staff/SKILL.md` | What Claude does: setup steps, rules, daily use |
| `skill/chief-of-staff/assets/home.html` | The Home page. Its config block is filled in during setup; left empty it runs on the sample week |
| `skill/chief-of-staff/references/` | How the briefs are written, and the scheduled-task prompt templates Claude fills in for you |
| `prompts/` | The exact prompts behind Megan's own setup (evening brief, morning brief, morning-time setter), with private IDs replaced. See [prompts/README.md](prompts/README.md) |
| `skill/chief-of-staff/scripts/` | Draws the to-scale day calendar for the briefs (`cal_svg.py`, `cal_text.py`) and the Sunday week-ahead picture (`week_svg.py`) |
| `agent.py`, `sources.py`, `guardrails.py`, `config.py`, `.github/workflows/nightly.yml` | **Optional nightly check**: a small agent on GitHub Actions that spots stalled projects, repeat bumps, exams without a plan and crowded weeks, and leaves suggestions for you to approve. Tests in `tests/`. See [NIGHTLY.md](NIGHTLY.md) |

## Where the prompts live

Everything that tells Claude what to do is in this repo:
- **The skill** (`skill/chief-of-staff/SKILL.md`): what Claude does in chat and how it sets everything up.
- **The scheduled-task prompts:** templates in `skill/chief-of-staff/references/scheduled-prompts.md`, and the live versions from Megan's setup in `prompts/`. The live copies that actually run are stored in Claude's scheduled tasks; the ones here are copies with private IDs removed.
- **The nightly check's system prompt:** `SYSTEM` in `agent.py`.

## Rebuilding the zip

If you change anything in `skill/`, rebuild the package from the repo root:

```
cd skill && zip -r ../chief-of-staff-skill.zip chief-of-staff -x "*.DS_Store" && cd ..
```

## Privacy

This tool is built for personal use. Each person who sets it up runs their own copy with their own keys, and no data is sent to the author.

**What the nightly check reads**
- **Google Calendar:** events from the calendars you list in `COS_CALENDARS`, for the next 30 days. Access is read-only: it cannot create, change or delete events.
- **Notion:** your Chief of Staff Tasks and Proposals databases. It can read them and add new rows to Proposals, but cannot edit or delete existing pages.

**What it does with that data**
- Sends it to the Claude API (Anthropic) to look for patterns, such as stalled projects, repeatedly bumped items and crowded weeks.
- Saves its suggestions as new rows in your Proposals database. Nothing changes on your calendar or task list unless you approve it.
- Does not read email and does not keep copies of your data anywhere else. GitHub Actions run logs show only counts and errors, not event or task details.

**Keys:** all keys are stored as encrypted GitHub Actions secrets in your own repo and never appear in the code. To revoke access at any time, remove the app at myaccount.google.com/permissions, delete the Notion connection, or delete the GitHub secrets.

**Contact:** open an issue on this repo.