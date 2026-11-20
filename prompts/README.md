# The prompts that run

These are the exact instructions behind Megan's chief of staff, with private values (calendar IDs, Notion database and view IDs, the Home page link, task IDs) replaced by `<placeholders>`.

| File | What it is | Where it runs |
|---|---|---|
| [`evening-brief.md`](evening-brief.md) | The 8 pm brief about tomorrow, plus the Sunday "Your week ahead" section | Claude scheduled task, daily at 7:47 pm |
| [`morning-brief.md`](morning-brief.md) | The short morning brief about today | Claude scheduled task, at the time set below |
| [`set-morning-brief-time.md`](set-morning-brief-time.md) | Moves the morning brief to 30 minutes before the first event (between 6:00 and 7:30) | Claude scheduled task, daily at 5:41 am, no notifications |
| `SYSTEM` in [`../agent.py`](../agent.py) | The nightly check agent's system prompt | GitHub Actions, daily before the evening brief |
| [`../skill/chief-of-staff/SKILL.md`](../skill/chief-of-staff/SKILL.md) | What Claude does in chat and during setup | Any Claude chat, once the skill is installed |

**Scripts.** The live brief prompts include the full text of the drawing scripts so each scheduled run works on its own. Here they are replaced by a pointer to the files in [`../skill/chief-of-staff/scripts/`](../skill/chief-of-staff/scripts/): `cal_svg.py` (Script A), `cal_text.py` (Script B) and `week_svg.py` (Script C).

**Your own copy.** If you install the skill, Claude writes these prompts for you during setup, filled in with your own calendars and lists. The generic templates are in [`../skill/chief-of-staff/references/scheduled-prompts.md`](../skill/chief-of-staff/references/scheduled-prompts.md).
