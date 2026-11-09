"""Draw the last year of GitHub contributions as a day-by-week grid (assets/activity.svg).

Run by .github/workflows/activity.yml once a day. Standard library only.
    python scripts/activity.py                     # real data, needs GITHUB_TOKEN
    python scripts/activity.py --demo out.svg      # fake data, for previewing the design
    python scripts/activity.py --demo out.svg 3.0  # the same, with the animation frozen at 3 seconds
"""
import datetime as dt
import json
import math
import os
import random
import sys
import urllib.request

USER = os.environ.get("GITHUB_REPOSITORY_OWNER", "syin07")
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "activity.svg")

MUTED, EMPTY = "#6B7280", "#F1F2F4"
SHADES = ["#FDE8B8", "#F9C860", "#F59E0B", "#C2710A"]  # one hue, light to dark: few contributions to many
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
W = 1200
PITCH, CELL = 20, 16          # distance between squares, and their size
X0, Y0 = 96, 44               # top-left corner of the grid
T, TRAVEL = 7.0, 5.2          # the ripple: loop length, and how long it takes to cross the grid

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date weekday contributionCount } }
      }
    }
  }
}
"""


def fetch_weeks():
    """Return (weeks, yearly total). Each week is a list of (date, weekday, count), Sunday first."""
    body = json.dumps({"query": QUERY, "variables": {"login": USER}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={
            "Authorization": "bearer " + os.environ["GITHUB_TOKEN"],
            "Content-Type": "application/json",
            "User-Agent": USER,
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    if "errors" in payload:
        raise SystemExit(f"GitHub API error: {payload['errors']}")
    cal = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = [
        [(d["date"], d["weekday"], d["contributionCount"]) for d in w["contributionDays"]]
        for w in cal["weeks"]
    ]
    return weeks, cal["totalContributions"]


def demo_weeks():
    """A made-up year that gets busier over time, ending today."""
    rng = random.Random(11)
    today = dt.date.today()
    start = today - dt.timedelta(days=364 + (today.weekday() + 1) % 7)  # back to a Sunday
    weeks, day = [], start
    while day <= today:
        if not weeks or day.weekday() == 6:
            weeks.append([])
        busy = 0.6 + 2.4 * len(weeks) / 53
        if day.weekday() >= 5:
            busy *= 0.5
        count = 0 if rng.random() < 0.38 else int(rng.expovariate(1 / (busy * 2.2)))
        if rng.random() < 0.02:
            count += rng.randint(12, 26)
        weeks[-1].append((day.isoformat(), (day.weekday() + 1) % 7, count))
        day += dt.timedelta(days=1)
    return weeks, sum(c for w in weeks for _, _, c in w)


def text(x, y, s, anchor="start", size=13):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{FONT}" font-size="{size}" fill="{MUTED}">{s}</text>'


def render(weeks, total, freeze=None):
    peak = max((c for w in weeks for _, _, c in w), default=0) or 1
    pitch = min(PITCH, (W - X0 - 44) // len(weeks))  # GitHub sometimes returns 54 weeks
    cell = pitch - 4
    out, last_label = [], -9
    for i, week in enumerate(weeks):
        x = X0 + i * pitch
        first = dt.date.fromisoformat(week[0][0])
        if first.day <= 7 and i - last_label >= 3 and i <= len(weeks) - 2:
            last_label = i
            out.append(text(x, Y0 - 12, first.strftime("%b")))  # the week a month starts in
        squares = []
        for _, weekday, count in week:
            # sqrt so a single huge day doesn't wash out every ordinary one
            shade = EMPTY if count == 0 else SHADES[min(3, int(4 * math.sqrt(count / peak) - 1e-9))]
            squares.append(f'<rect x="{x}" y="{Y0 + weekday * pitch}" width="{cell}" height="{cell}" rx="4" fill="{shade}"/>')
        delay = TRAVEL * i / (len(weeks) - 1) - (freeze or 0)
        out.append(f'<g class="w" style="animation-delay:{delay:.2f}s">' + "".join(squares) + "</g>")
    for weekday, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        out.append(text(X0 - 14, Y0 + weekday * pitch + cell - 3, name, "end"))

    base = Y0 + 7 * pitch + 26
    right = X0 + len(weeks) * pitch - 4
    out.append(text(X0, base, f"{total:,} contributions in the last year", size=15))
    out.append(text(right, base, "more", "end"))
    for k, shade in enumerate(reversed([EMPTY] + SHADES)):
        out.append(f'<rect x="{right - 64 - k * 20}" y="{base - 13}" width="16" height="16" rx="4" fill="{shade}"/>')
    out.append(text(right - 64 - 4 * 20 - 10, base, "less", "end"))

    paused = " animation-play-state: paused;" if freeze is not None else ""  # testing only
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {base + 18}" width="{W}" height="{base + 18}" role="img" aria-label="{total} contributions in the last year, one square per day">
  <style>
    .w {{ animation: ripple {T}s ease-in-out infinite;{paused} }}
    @keyframes ripple {{ 0%, 12%, 100% {{ opacity: 1; }} 6% {{ opacity: 0.45; }} }}
    @media (prefers-reduced-motion: reduce) {{ .w {{ animation: none; }} }}
  </style>
  {chr(10).join('  ' + o for o in out).strip()}
</svg>
"""


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--demo"]
    path = next((a for a in args if a.endswith(".svg")), OUT)
    freeze = next((float(a) for a in args if not a.endswith(".svg")), None)
    weeks, total = demo_weeks() if "--demo" in sys.argv else fetch_weeks()
    with open(path, "w", encoding="utf-8") as f:
        f.write(render(weeks, total, freeze))
    print(f"wrote {os.path.normpath(path)}: {len(weeks)} weeks, {total} contributions")
