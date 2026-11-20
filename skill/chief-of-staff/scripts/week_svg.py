"""Draw the Sunday "week ahead" picture for the evening brief as one SVG.

Input JSON:
{
  "days": [{"label": "Mon 23", "events": [{"start": "09:00", "end": "10:30"}],
            "marks": [{"kind": "deadline" | "exam", "title": "Paper outline due"}]}],   # 7 days, Monday first
  "projects": [{"title": "Seminar paper", "pct": 35, "due": "Dec 14"}],               # due may be ""
  "patterns": [{"kind": "stalled" | "bumped", "text": "Seminar paper hasn't moved in 9 days"}]
}
Usage: python3 week_svg.py week.json > week.svg
"""
import html
import json
import sys

d = json.load(open(sys.argv[1]))
esc = lambda s: html.escape(str(s), quote=True)
cut = lambda s, n: s if len(s) <= n else s[: n - 1] + "…"
m = lambda s: int(s[:2]) * 60 + int(s[3:5])
D0, D1 = 8 * 60, 22 * 60
BX0, BX1 = 64, 300                      # day bar area
bx = lambda t: BX0 + (min(max(t, D0), D1) - D0) / (D1 - D0) * (BX1 - BX0)

out, y = [], 0


def label(text, yy):
    out.append(f'<text class="th" x="4" y="{yy}" dominant-baseline="central">{esc(text)}</text>')


# ---- next week by day ------------------------------------------------------
days = d.get("days", [])
if days:
    y += 14
    label("Next week", y)
    y += 22
    for t in (8, 12, 16, 20):
        out.append(f'<text class="ts" x="{bx(t * 60):.0f}" y="{y}" text-anchor="middle" dominant-baseline="central">{t}:00</text>')
    y += 14
    for day in days:
        evs = sorted((m(e["start"]), m(e["end"])) for e in day.get("events", []) if e.get("start") and e.get("end"))
        busy = []
        for a, b in evs:
            a, b = max(a, D0), min(b, D1)
            if b <= a:
                continue
            if busy and a <= busy[-1][1]:
                busy[-1][1] = max(busy[-1][1], b)
            else:
                busy.append([a, b])
        free = (D1 - D0) - sum(b - a for a, b in busy)
        out.append(f'<text class="ts" x="4" y="{y + 9}" dominant-baseline="central">{esc(day.get("label", ""))}</text>')
        out.append(f'<rect x="{BX0}" y="{y}" width="{BX1 - BX0}" height="18" rx="4" fill="none" stroke="var(--b)" stroke-width="0.8" stroke-dasharray="3 2"/>')
        for a, b in busy:
            out.append(f'<g class="c-teal"><rect x="{bx(a):.1f}" y="{y}" width="{max(bx(b) - bx(a), 2):.1f}" height="18" rx="2" stroke-width="0.5"/></g>')
        fh, fm = divmod(free, 60)
        free_txt = (f"{fh}h" if fh else "") + (f" {fm}m" if fm else "") or "0m"
        out.append(f'<text class="ts" x="{BX1 + 8}" y="{y + 9}" dominant-baseline="central">{free_txt.strip()} free</text>')
        y += 24
        for mk in day.get("marks", [])[:3]:
            word = "Exam: " if mk.get("kind") == "exam" else ("" if "due" in mk.get("title", "").lower() else "Due: ")
            out.append(f'<g class="c-amber"><rect x="{BX0}" y="{y - 2}" width="{BX1 - BX0}" height="18" rx="4" stroke-width="0.5"/>'
                       f'<text class="ts" x="{BX0 + 8}" y="{y + 7}" dominant-baseline="central">{word}{esc(cut(mk.get("title", ""), 34))}</text></g>')
            y += 22
        y += 4
    out.append(f'<g class="c-teal"><rect x="{BX0}" y="{y}" width="12" height="10" rx="2" stroke-width="0.5"/></g>'
               f'<text class="ts" x="{BX0 + 18}" y="{y + 5}" dominant-baseline="central">Booked</text>'
               f'<rect x="{BX0 + 80}" y="{y}" width="12" height="10" rx="2" fill="none" stroke="var(--b)" stroke-width="0.8" stroke-dasharray="3 2"/>'
               f'<text class="ts" x="{BX0 + 98}" y="{y + 5}" dominant-baseline="central">Free (8:00 to 22:00)</text>')
    y += 22

# ---- project progress -------------------------------------------------------
projects = d.get("projects", [])
if projects:
    y += 16
    label("Projects", y)
    y += 20
    for p in projects:
        pct = max(0, min(100, int(p.get("pct") or 0)))
        out.append(f'<text class="ts" x="4" y="{y}" dominant-baseline="central">{esc(cut(p.get("title", ""), 44))}</text>')
        y += 12
        w = 236
        out.append(f'<g class="c-gray"><rect x="4" y="{y}" width="{w}" height="10" rx="4" stroke-width="0.5"/></g>')
        if pct:
            out.append(f'<g class="c-teal"><rect x="4" y="{y}" width="{max(w * pct / 100, 4):.1f}" height="10" rx="4" stroke-width="0.5"/></g>')
        due = f' · due {p["due"]}' if p.get("due") else ""
        out.append(f'<text class="ts" x="{4 + w + 8}" y="{y + 5}" dominant-baseline="central">{pct}%{esc(due)}</text>')
        y += 26

# ---- patterns the nightly check found --------------------------------------
patterns = d.get("patterns", [])
if patterns:
    y += 12
    label("Patterns noticed", y)
    y += 20
    for pt in patterns[:6]:
        stalled = pt.get("kind") == "stalled"
        out.append(f'<g class="{"c-coral" if stalled else "c-purple"}"><rect x="4" y="{y - 9}" width="64" height="18" rx="4" stroke-width="0.5"/>'
                   f'<text class="ts" x="36" y="{y}" text-anchor="middle" dominant-baseline="central">{"Stalled" if stalled else "Bumped"}</text></g>')
        out.append(f'<text class="ts" x="76" y="{y}" dominant-baseline="central">{esc(cut(pt.get("text", ""), 46))}</text>')
        y += 24

H = y + 16
print(f'<svg width="100%" viewBox="0 0 380 {H}" role="img"><title>Your week ahead</title>'
      f'<desc>Next week day by day with booked and free time and deadlines, project progress, and patterns noticed.</desc>'
      + "".join(out) + "</svg>")
