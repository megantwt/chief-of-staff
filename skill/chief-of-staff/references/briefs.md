# Briefs

Both briefs only **read**. They never change the calendar or Notion, apart from the evening brief marking Heads-ups as Seen. Each brief is sent **exactly once**.

## Reading the data (both briefs)

1. **Calendar.** For every calendar in `config.calendars`, call `list_events` with that `calendarId`, the day's range as local times without an offset (`YYYY-MM-DDT00:00:00` to the next day's `T00:00:00`), `orderBy: "startTime"`. Skip cancelled events and events marked free (transparent). All-day events have `start.date` instead of `start.dateTime`.
2. **Notion tasks.** Call `notion-query-data-sources` with `{"data":{"mode":"view","view_url": config.tasksView,"page_size":100}}`, and follow `next_cursor` while `has_more`. Each row has the keys `"Task"`, `"Type"`, `"Status"`, `"date:Due:start"`, `"date:Show from:start"`, `"Progress %"` and `"url"`. Keep rows whose Status isn't Done. Hide rows whose Show from is after the brief's day.
3. **Check your count.** Before writing, count the to-dos and projects you kept. If the query failed or returned nothing while the view clearly has rows, say "I couldn't read your Notion list tonight" in that section. Never claim the list is empty when you couldn't read it.

## Drawing the day

Write the day to `/tmp/cal.json`:
```json
{"title": "Tomorrow's schedule", "allday": ["Paper due"], "events": [{"title": "Seminar", "start": "13:30", "end": "15:00"}]}
```
Times are 24-hour local. Run `python3 cal_svg.py /tmp/cal.json` (the script is in the task prompt; save it to a file first). Show the SVG it prints **inline in the message** with the visualizer's show_widget tool if you have one. Otherwise run `cal_text.py` the same way and put its output in a code block. Never send the calendar as a separate image file.

## Evening brief (8 pm, about tomorrow)

Send it as two messages.

**Message 1**
- **Good evening, <owner>.** One line on the shape of tomorrow: how many events, the first one and its time, the longest free stretch, and any clashes.
- **Schedule**, then the inline drawing of tomorrow.

**Message 2**
- **To work on tomorrow:** every visible to-do, sorted by due date, each with its due label (overdue, due tomorrow, a date). Then every visible project with the user's own Progress %. Even an empty day has projects to work on.
- **On the horizon:** exams, interviews and deadlines in the next 14 days, from calendars of kind exam or deadlines, plus to-dos due in that window.
- **Needs you:** Pending rows of the Proposals view (`config.proposalsView`). For Approvals, give the title and say they can approve in Home. For Heads-ups, give the title and detail, then set their Status to Seen.
- **For tonight:** one short, well-known quote with its author, and ask for a 👍 or 👎. If they answer, keep the kind of quote they like.
- A link to their Home page, if it exists.

Your final response is one line, which becomes the notification. For example: "Tomorrow: 5 events, first Statistics at 9:00. 1 thing needs your OK."

## Morning brief (about today)

Read the calendars **fresh** so it reflects anything the user changed last night. Don't list what changed.

**Message 1**
- **Good morning, <owner>.**
- First thing: the first event and its time, or "nothing booked" if there isn't one.
- Most urgent: the to-do with the earliest due date, if any.
- **Today**, then the inline drawing of today.

**Message 2:** the Home link.

Your final response is one line: "First thing: <event> at <time>."
