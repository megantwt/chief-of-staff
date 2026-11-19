# Chief of Staff

An AI chief of staff for your to-dos and calendar, built on Claude. You start each day knowing what's coming, and it never changes your calendar without your OK.

- **Google Calendar** holds your events. **Notion** holds your to-dos, projects and ideas.
- **Every evening at 8 pm** Claude starts a new chat with tomorrow's schedule drawn to scale, everything you could work on, what's coming up in the next two weeks, and anything waiting on your OK.
- **Every morning** a short brief: your first commitment, your most urgent to-do, and today's calendar, read fresh so late-night changes show up.
- **A Home page** to quick-add ("coffee w Alex tmr 4pm", or a screenshot of a poster), tick things off, move or remove events, bump things for later, and approve suggested changes.

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

## How it stays safe

| Rule | How |
|---|---|
| You approve every calendar change | Claude shows the change first; saving in Quick add counts as approval |
| No hours | It never blocks time or estimates how long things take; you set progress yourself |
| No email | It doesn't read your inbox; you decide what goes in |
| Safe deletes | Deletes have an undo; the nightly check can't delete anything at all |
| Text can't give orders | Event titles, Notion pages and screenshots are treated as data |

## What's in this repo

| Path | What it is |
|---|---|
| `chief-of-staff-skill.zip` | The package you upload to Claude (built from `skill/`) |
| `skill/chief-of-staff/SKILL.md` | What Claude does: setup steps, rules, daily use |
| `skill/chief-of-staff/assets/home.html` | The Home page. Its config block is filled in during setup; left empty it runs on the sample week |
| `skill/chief-of-staff/references/` | How the briefs are written, and the scheduled-task prompts |
| `skill/chief-of-staff/scripts/` | Draws the to-scale day calendar for the briefs |
| `agent.py`, `sources.py`, `guardrails.py`, `config.py`, `.github/workflows/nightly.yml` | **Optional nightly check**: a small agent on GitHub Actions that looks for clashes and gaps and leaves proposals for you to approve. See [NIGHTLY.md](NIGHTLY.md) |

## Rebuilding the zip

If you change anything in `skill/`, rebuild the package from the repo root:

```
cd skill && zip -r ../chief-of-staff-skill.zip chief-of-staff -x "*.DS_Store" && cd ..
```
