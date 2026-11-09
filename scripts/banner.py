"""Next-token sampling banner. Usage: python3 scripts/banner.py assets/banner.svg [freeze_seconds]"""
import sys

W, H = 1200, 300
NAVY, ACCENT, MUTED, TRACK = "#0B1F44", "#1D4ED8", "#64748B", "#E3E9F5"
sans = "-apple-system,BlinkMacSystemFont,'SF Pro Display','Helvetica Neue',Helvetica,Arial,sans-serif"
mono = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

# (chosen token, [(candidate, probability), ...]) -- chosen is not always the top one: it's sampling
STEPS = [
    ("I", [("I", 0.62), ("We", 0.21), ("The", 0.09)]),
    ("like", [("like", 0.48), ("want", 0.31), ("need", 0.12)]),
    ("to", [("to", 0.91), ("how", 0.04), ("it", 0.02)]),
    ("know", [("know", 0.44), ("see", 0.27), ("learn", 0.19)]),
    ("how", [("how", 0.57), ("why", 0.24), ("what", 0.11)]),
    ("models", [("things", 0.41), ("models", 0.37), ("minds", 0.13)]),
    ("think", [("think", 0.46), ("work", 0.35), ("learn", 0.12)]),
]
T, STEP, HOLD_END = 16.0, 1.5, 14.6   # loop length, seconds per token, when everything fades
FS, CH = 27, 27 * 0.6                 # sentence font size and monospace advance
SX, SY = 74, 238                      # sentence origin
PX, PY, PW, PH = 812, 58, 328, 184    # candidates card
freeze = float(sys.argv[2]) if len(sys.argv) > 2 else None


def pct(t):
    return f"{max(0.0, min(100.0, 100 * t / T)):.2f}%"


css, body = [], []
x = SX
for k, (tok, cands) in enumerate(STEPS):
    t0 = k * STEP
    last = k == len(STEPS) - 1
    land = t0 + 1.05
    # the token landing in the sentence
    css.append(f"@keyframes tok{k} {{ 0%, {pct(land)} {{ opacity: 0; }} {pct(land + 0.18)}, {pct(HOLD_END)} {{ opacity: 1; }} {pct(HOLD_END + 0.5)}, 100% {{ opacity: 0; }} }}")
    body.append(f'<text class="a" style="animation-name:tok{k}" x="{x:.1f}" y="{SY}" font-family="{mono}" font-size="{FS}" font-weight="600" fill="{NAVY}">{tok}</text>')
    # cursor waiting where the token will land
    css.append(f"@keyframes cur{k} {{ 0%, {pct(t0)} {{ opacity: 0; }} {pct(t0 + 0.05)}, {pct(land)} {{ opacity: 1; }} {pct(land + 0.1)}, 100% {{ opacity: 0; }} }}")
    body.append(f'<rect class="a" style="animation-name:cur{k}" opacity="0" x="{x:.1f}" y="{SY - 23}" width="3" height="28" rx="1.5" fill="{ACCENT}"/>')
    # candidates panel
    out = HOLD_END if last else t0 + STEP - 0.12
    css.append(f"@keyframes pan{k} {{ 0%, {pct(t0)} {{ opacity: 0; }} {pct(t0 + 0.12)}, {pct(out)} {{ opacity: 1; }} {pct(out + (0.5 if last else 0.1))}, 100% {{ opacity: 0; }} }}")
    css.append(f"@keyframes bar{k} {{ 0%, {pct(t0 + 0.08)} {{ transform: scaleX(0); }} {pct(t0 + 0.55)}, 100% {{ transform: scaleX(1); }} }}")
    rows = []
    for r, (word, p) in enumerate(cands):
        y = PY + 78 + r * 36
        hit = word == tok
        col = ACCENT if hit else MUTED
        rows.append(
            f'<text x="{PX + 26}" y="{y}" font-family="{mono}" font-size="19" font-weight="{600 if hit else 400}" fill="{NAVY if hit else MUTED}">{word}</text>'
            f'<rect x="{PX + 118}" y="{y - 13}" width="130" height="12" rx="6" fill="{TRACK}"/>'
            f'<rect class="a bar" style="animation-name:bar{k}" x="{PX + 118}" y="{y - 13}" width="{max(8, p * 130):.0f}" height="12" rx="6" fill="{col}" fill-opacity="{1 if hit else 0.45}"/>'
            f'<text x="{PX + PW - 24}" y="{y}" text-anchor="end" font-family="{mono}" font-size="16" fill="{col}">{p:.2f}</text>'
        )
    body.append(f'<g class="a" style="animation-name:pan{k}" opacity="{1 if last else 0}">' + "".join(rows) + "</g>")
    x += (len(tok) + 1) * CH

# cursor resting after the finished sentence
end = (len(STEPS) - 1) * STEP + 1.05
css.append(f"@keyframes curEnd {{ 0%, {pct(end)} {{ opacity: 0; }} {pct(end + 0.1)}, {pct(HOLD_END)} {{ opacity: 1; }} {pct(HOLD_END + 0.5)}, 100% {{ opacity: 0; }} }}")
body.append(f'<rect class="a" style="animation-name:curEnd" x="{x - CH + 5:.1f}" y="{SY - 23}" width="3" height="28" rx="1.5" fill="{ACCENT}"/>')

timing = f"animation-duration: {T}s; animation-iteration-count: infinite; animation-timing-function: ease-out;"
if freeze is not None:  # testing only: pause the loop at a given second
    timing += f" animation-play-state: paused; animation-delay: -{freeze}s;"

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Sandy Yin, computer science at UC San Diego. I like to know how models think.">
  <defs>
    <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1.2" fill="{NAVY}" fill-opacity="0.07"/>
    </pattern>
    <style>
      .a {{ {timing} }}
      .bar {{ transform-box: fill-box; transform-origin: left center; }}
      {chr(10).join("      " + c for c in css).strip()}
      @media (prefers-reduced-motion: reduce) {{ .a {{ animation: none; }} }}
    </style>
  </defs>
  <rect width="{W}" height="{H}" rx="24" fill="#F6F8FC"/>
  <rect width="{W}" height="{H}" rx="24" fill="url(#dots)"/>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="24" fill="none" stroke="{NAVY}" stroke-opacity="0.08"/>

  <text x="72" y="122" font-family="{sans}" font-size="74" font-weight="700" letter-spacing="-2.5" fill="{NAVY}">Sandy Yin</text>
  <rect x="74" y="146" width="64" height="6" rx="3" fill="{ACCENT}"/>
  <text x="74" y="186" font-family="{mono}" font-size="19" fill="{MUTED}">CS @ UC San Diego</text>

  <rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="18" fill="#FFFFFF" stroke="{NAVY}" stroke-opacity="0.10"/>
  <text x="{PX + 26}" y="{PY + 38}" font-family="{mono}" font-size="14" letter-spacing="1.5" fill="{MUTED}">NEXT TOKEN</text>

  {chr(10).join("  " + b for b in body).strip()}
</svg>
'''
open(sys.argv[1], "w").write(svg)
