import json, sys, html
d = json.load(open(sys.argv[1]))
ev = sorted(d.get("events", []), key=lambda e: e["start"])
allday = d.get("allday", [])
m = lambda s: int(s[:2]) * 60 + int(s[3:5])
f = lambda x: f"{x // 60}:{x % 60:02d}"
dur = lambda n: ((f"{n // 60}h" if n >= 60 else "") + (f" {n % 60}m" if n % 60 else "")).strip()
esc = lambda s: html.escape(s, quote=True)
D0 = min([480] + [m(e["start"]) // 60 * 60 for e in ev]); D1 = max([1320] + [-(-m(e["end"]) // 60) * 60 for e in ev])
HP, X0, X1 = 36, 50, 372
top = 44 if allday else 14
y = lambda t: top + (t - D0) / 60 * HP
H = int(y(D1)) + 24
out = [f'<svg width="100%" viewBox="0 0 380 {H}" role="img"><title>{esc(d.get("title", "Day calendar"))}</title><desc>Events and free time drawn to scale, one hour per row.</desc>']
if allday:
    txt = "All day: " + ", ".join(allday)
    out.append(f'<g class="c-blue"><rect x="{X0}" y="8" width="{X1 - X0}" height="26" rx="4" stroke-width="0.5"/><text class="ts" x="{X0 + 10}" y="21" dominant-baseline="central">{esc(txt[:48])}</text></g>')
for t in range(D0, D1 + 1, 60):
    out.append(f'<line x1="{X0}" x2="{X1}" y1="{y(t):.0f}" y2="{y(t):.0f}" stroke="var(--b)" stroke-width="0.5"/><text class="ts" x="4" y="{y(t):.0f}" dominant-baseline="central">{f(t)}</text>')
busy = []
for e in ev:
    a, b = m(e["start"]), m(e["end"])
    if busy and a <= busy[-1][1]: busy[-1][1] = max(busy[-1][1], b)
    else: busy.append([a, b])
gaps, c = [], max(D0, 480)
for a, b in busy:
    if a - c >= 30: gaps.append((c, a))
    c = max(c, b)
if min(D1, 1320) - c >= 30: gaps.append((c, min(D1, 1320)))
for a, b in gaps:
    h = y(b) - y(a) - 2
    out.append(f'<g class="c-green"><rect x="{X0 + 2}" y="{y(a) + 1:.0f}" width="{X1 - X0 - 4}" height="{h:.0f}" rx="4" stroke-width="0.5" stroke-dasharray="4 3"/>')
    if h >= 20: out.append(f'<text class="ts" x="{X0 + 12}" y="{y(a) + 13:.0f}" dominant-baseline="central">Free {f(a)}–{f(b)} · {dur(b - a)}</text>')
    out.append('</g>')
for i, e in enumerate(ev):
    a, b = m(e["start"]), m(e["end"])
    clash = any(j != i and m(o["start"]) < b and a < m(o["end"]) for j, o in enumerate(ev))
    col = min(1, sum(1 for o in ev[:i] if m(o["start"]) < b and a < m(o["end"]))) if clash else 0
    w = (X1 - X0 - 4) / 2 - 2 if clash else X1 - X0 - 4
    x = X0 + 2 + col * ((X1 - X0 - 4) / 2 + 2)
    h = max(y(b) - y(a) - 2, 16)
    maxc = 20 if clash else 40
    title = e["title"] if len(e["title"]) <= maxc else e["title"][:maxc - 1] + "…"
    out.append(f'<g class="{"c-amber" if clash else "c-teal"}"><rect x="{x:.0f}" y="{y(a) + 1:.0f}" width="{w:.0f}" height="{h:.0f}" rx="4" stroke-width="0.5"/>')
    if h >= 34:
        out.append(f'<text class="th" x="{x + 10:.0f}" y="{y(a) + 13:.0f}" dominant-baseline="central">{esc(title)}</text><text class="ts" x="{x + 10:.0f}" y="{y(a) + 29:.0f}" dominant-baseline="central">{f(a)}–{f(b)}{" · clash" if clash else ""}</text>')
    else:
        out.append(f'<text class="ts" x="{x + 10:.0f}" y="{y(a) + 1 + h / 2:.0f}" dominant-baseline="central">{esc(title)} · {f(a)}–{f(b)}</text>')
    out.append('</g>')
out.append('</svg>')
print("".join(out))
