# Chief of Staff

An AI chief of staff for your to-dos and calendar, built on Claude. You start each day knowing what's coming, and it never changes your calendar without your OK.

- **Google Calendar** holds your events. **Notion** holds your to-dos, projects and ideas.
- **Every evening at 8 pm** Claude starts a new chat with tomorrow's schedule drawn to scale, everything you could work on, what's coming up in the next two weeks, and anything waiting on your OK. **On Sundays** it adds *Your week ahead*: next week day by day (booked vs free time, deadlines and exams), your project progress, and patterns worth noticing.
- **Every morning** a short brief: your first commitment, your most urgent to-do, and today's calendar, read fresh so late-night changes show up.
- **A Home page** to quick-add ("coffee w Alex tmr 4pm", or a screenshot of a poster), with a warning if the new event clashes with something; tick things off, move or remove events, bump things for later, and approve suggested changes.
- **An optional nightly check agent** (Python on GitHub Actions) that looks for patterns the daily view misses: projects that have stalled (paired with your next free stretch), things you keep bumping, exams with no plan, crowded weeks. It only ever suggests; you approve.

Built for DPI-681 (Question 2) by Megan.

## Try it (no setup)

Open the shared app and choose **Not now: try it on a sample week**. It's the real app running on a made-up student's week, with a guided tour. Nothing touches your accounts.

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
- schedules your evening and morning briefs.

After that, just talk to it: "add dinner with Jamie Friday 7pm", "bump the reading until Monday", "brief me for tomorrow", or send a photo of a flyer.

### Optional: add the nightly check agent (about 20 minutes)

For people comfortable with GitHub. Everything above works without it.

1. **Fork this repo** (top right on GitHub). Then open your fork's **Actions** tab and click **I understand my workflows, go ahead and enable them**: GitHub turns scheduled workflows off in new forks.
2. In Claude, say **"Prepare my nightly check settings."** Claude gives you your calendar list and Notion database IDs, ready to paste.
3. Follow [NIGHTLY.md](NIGHTLY.md): a read-only Notion integration, a read-only Google token, a Claude API key, and the GitHub secrets. Start with `DRY_RUN` = `true`.

Its findings show up in your evening brief under "Needs you", in Home, and in the Sunday charts.

## How it stays safe

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
| `skill/chief-of-staff/references/` | How the briefs are written, and the scheduled-task prompts |
| `skill/chief-of-staff/scripts/` | Draws the to-scale day calendar for the briefs (`cal_svg.py`, `cal_text.py`) and the Sunday week-ahead picture (`week_svg.py`) |
| `agent.py`, `sources.py`, `guardrails.py`, `config.py`, `.github/workflows/nightly.yml` | **Optional nightly check**: a small agent on GitHub Actions that spots stalled projects, repeat bumps, exams without a plan and crowded weeks, and leaves suggestions for you to approve. Tests in `tests/`. See [NIGHTLY.md](NIGHTLY.md) |

## Rebuilding the zip

If you change anything in `skill/`, rebuild the package from the repo root:

```
cd skill && zip -r ../chief-of-staff-skill.zip chief-of-staff -x "*.DS_Store" && cd ..
```
