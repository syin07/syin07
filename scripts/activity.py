"""Draw the last year of GitHub contributions as a waveform (assets/activity.svg).

Run by .github/workflows/activity.yml once a day. Standard library only.
    python scripts/activity.py           # real data, needs GITHUB_TOKEN
    python scripts/activity.py --demo    # fake data, for previewing the design
"""
import json
import math
import os
import random
import sys
import urllib.request

USER = os.environ.get("GITHUB_REPOSITORY_OWNER", "syin07")
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "activity.svg")

ACCENT = "#1D4ED8"
MUTED = "#64748B"
W, H, PAD = 1200, 150, 60
MID, MAX_BAR, BAR_W = 62, 46, 11

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionCount } }
      }
    }
  }
}
"""


def fetch_weeks():
    """Return (weekly totals, yearly total) from the GitHub GraphQL API."""
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
    weeks = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in cal["weeks"]]
    return weeks, cal["totalContributions"]


def demo_weeks():
    rng = random.Random(7)
    weeks = [max(0, int(rng.gauss(4 + 14 * i / 52, 6))) for i in range(53)]
    return weeks, sum(weeks)


def render(weeks, total):
    peak = max(weeks) or 1
    pitch = (W - 2 * PAD - BAR_W) / (len(weeks) - 1)
    bars = []
    for i, count in enumerate(weeks):
        x = PAD + i * pitch
        if count == 0:
            # an empty week is a small dot on the centre line
            bars.append(
                f'<circle cx="{x + BAR_W / 2:.1f}" cy="{MID}" r="2.5" fill="{MUTED}" fill-opacity="0.35"/>'
            )
            continue
        strength = math.sqrt(count / peak)  # sqrt so quiet weeks stay visible
        half = max(4, strength * MAX_BAR)
        bars.append(
            f'<rect x="{x:.1f}" y="{MID - half:.1f}" width="{BAR_W}" height="{2 * half:.1f}" '
            f'rx="{BAR_W / 2}" fill="{ACCENT}" fill-opacity="{0.35 + 0.65 * strength:.2f}"/>'
        )
    font = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{total} contributions in the last year">
  {chr(10).join('  ' + b for b in bars).strip()}
  <text x="{PAD}" y="{H - 12}" font-family="{font}" font-size="15" fill="{MUTED}">{total:,} contributions in the last year</text>
  <text x="{W - PAD}" y="{H - 12}" text-anchor="end" font-family="{font}" font-size="15" fill="{MUTED}">one bar per week</text>
</svg>
"""


if __name__ == "__main__":
    weeks, total = demo_weeks() if "--demo" in sys.argv else fetch_weeks()
    with open(OUT, "w") as f:
        f.write(render(weeks, total))
    print(f"wrote {os.path.normpath(OUT)}: {len(weeks)} weeks, {total} contributions")
