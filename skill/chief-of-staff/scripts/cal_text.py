import json, sys
d = json.load(open(sys.argv[1]))
ev = sorted(d["events"], key=lambda e: e["start"])
m = lambda s: int(s[:2]) * 60 + int(s[3:5])
f = lambda x: f"{x // 60}:{x % 60:02d}"
dur = lambda n: (f"{n // 60}h" if n >= 60 else "") + (f" {n % 60}m" if n % 60 else "")
D0 = min([480] + [m(e["start"]) // 30 * 30 for e in ev]); D1 = max([1320] + [-(-m(e["end"]) // 30) * 30 for e in ev])
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
rows = {}
for t in range(D0, D1, 30):
    on = [e for e in ev if m(e["start"]) < t + 30 and t < m(e["end"])]
    starting = [e for e in on if t <= m(e["start"]) < t + 30]
    label = " / ".join(f"{e['title'][:24]} {f(m(e['start']))}–{f(m(e['end']))}" for e in starting)
    if label and len(on) > 1: label += "  (clash)"
    rows[t] = ["▓▓" if len(on) > 1 else "██" if on else "░░", label]
for a, b in gaps:
    t = -(-a // 30) * 30 if rows.get(a // 30 * 30, ["", ""])[0] != "░░" else a // 30 * 30
    if t in rows and not rows[t][1]:
        rows[t][1] = f"free {f(a)}–{f(b)} ({dur(b - a).strip()})"
print("\n".join(f"{f(t):>5} {rows[t][0]}  {rows[t][1]}".rstrip() for t in range(D0, D1, 30)) + f"\n{f(D1):>5}")
