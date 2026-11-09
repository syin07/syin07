"""Next-token sampling banner. Usage: python3 scripts/banner.py assets/banner.svg [freeze_seconds]"""
import sys

W, H = 1200, 300
CX = W / 2                            # everything is centred on this line
BG = "#FFFFFF"                        # GitHub's light page colour, so the banner has no visible edge
INK, MUTED, TRACK = "#1F2328", "#6B7280", "#E5E7EB"   # GitHub's own text colour, neutral greys
ACCENT, ACCENT_TEXT = "#F59E0B", "#B45309"            # amber for shapes; a darker amber where it has to be read as text
sans = "-apple-system,BlinkMacSystemFont,'SF Pro Display','Helvetica Neue',Helvetica,Arial,sans-serif"
emoji = "'Apple Color Emoji','Segoe UI Emoji','Noto Color Emoji',sans-serif"
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
LAND, SLIDE = 1.05, 0.28              # when a token lands within its step, and how long the line takes to re-centre
FS, CH = 27, 27 * 0.6                 # sentence font size and monospace advance
SY = 204                              # sentence baseline
COL_W, COL_GAP, CY = 176, 44, 254     # candidate columns: width, gap, label baseline
HELLO, HELLO_W = "Hi, I'm Sandy", 420 # headline and its approximate width (412 in SF Pro, 439 in Arial)
WAVE_FS, WAVE_GAP = 60, 16            # the hand is a separate element so it can wave
freeze = float(sys.argv[2]) if len(sys.argv) > 2 else None


def pct(t):
    return f"{max(0.0, min(100.0, 100 * t / T)):.2f}%"


chars = sum(len(tok) for tok, _ in STEPS) + len(STEPS) - 1
SX = CX - chars * CH / 2              # where the finished sentence starts
cols_x = CX - (3 * COL_W + 2 * COL_GAP) / 2

css, sentence, panels = [], [], []
shifts = []                           # (time, offset): how far right the line sits to stay centred while it is short
x = SX
for k, (tok, cands) in enumerate(STEPS):
    t0 = k * STEP
    last = k == len(STEPS) - 1
    land = t0 + LAND
    shifts.append((t0, (SX + chars * CH - x) / 2))
    # the token landing in the sentence
    css.append(f"@keyframes tok{k} {{ 0%, {pct(land)} {{ opacity: 0; }} {pct(land + 0.18)}, {pct(HOLD_END)} {{ opacity: 1; }} {pct(HOLD_END + 0.5)}, 100% {{ opacity: 0; }} }}")
    sentence.append(f'<text class="a" style="animation-name:tok{k}" x="{x:.1f}" y="{SY}" font-family="{mono}" font-size="{FS}" font-weight="600" fill="{INK}">{tok}</text>')
    # cursor waiting where the token will land
    css.append(f"@keyframes cur{k} {{ 0%, {pct(t0)} {{ opacity: 0; }} {pct(t0 + 0.05)}, {pct(land)} {{ opacity: 1; }} {pct(land + 0.1)}, 100% {{ opacity: 0; }} }}")
    sentence.append(f'<rect class="a" style="animation-name:cur{k}" opacity="0" x="{x:.1f}" y="{SY - 23}" width="3" height="28" rx="1.5" fill="{ACCENT}"/>')
    # candidates: three columns, each a word and its probability over a bar
    out = HOLD_END if last else t0 + STEP - 0.12
    css.append(f"@keyframes pan{k} {{ 0%, {pct(t0)} {{ opacity: 0; }} {pct(t0 + 0.12)}, {pct(out)} {{ opacity: 1; }} {pct(out + (0.5 if last else 0.1))}, 100% {{ opacity: 0; }} }}")
    css.append(f"@keyframes bar{k} {{ 0%, {pct(t0 + 0.08)} {{ transform: scaleX(0); }} {pct(t0 + 0.55)}, 100% {{ transform: scaleX(1); }} }}")
    cols = []
    for c, (word, p) in enumerate(cands):
        cx = cols_x + c * (COL_W + COL_GAP)
        hit = word == tok
        col = ACCENT if hit else MUTED
        num = ACCENT_TEXT if hit else MUTED
        cols.append(
            f'<text x="{cx:.0f}" y="{CY}" font-family="{mono}" font-size="17" font-weight="{600 if hit else 400}" fill="{INK if hit else MUTED}">{word}</text>'
            f'<text x="{cx + COL_W:.0f}" y="{CY}" text-anchor="end" font-family="{mono}" font-size="15" fill="{num}">{p:.2f}</text>'
            f'<rect x="{cx:.0f}" y="{CY + 11}" width="{COL_W}" height="6" rx="3" fill="{TRACK}"/>'
            f'<rect class="a bar" style="animation-name:bar{k}" x="{cx:.0f}" y="{CY + 11}" width="{max(6, p * COL_W):.0f}" height="6" rx="3" fill="{col}" fill-opacity="{1 if hit else 0.45}"/>'
        )
    panels.append(f'<g class="a" style="animation-name:pan{k}" opacity="{1 if last else 0}">' + "".join(cols) + "</g>")
    x += (len(tok) + 1) * CH

# cursor resting after the finished sentence
end = (len(STEPS) - 1) * STEP + LAND
css.append(f"@keyframes curEnd {{ 0%, {pct(end)} {{ opacity: 0; }} {pct(end + 0.1)}, {pct(HOLD_END)} {{ opacity: 1; }} {pct(HOLD_END + 0.5)}, 100% {{ opacity: 0; }} }}")
sentence.append(f'<rect class="a" style="animation-name:curEnd" x="{x - CH + 5:.1f}" y="{SY - 23}" width="3" height="28" rx="1.5" fill="{ACCENT}"/>')

# the line slides left as each token lands, so the text so far is always centred
stops = [f"0% {{ transform: translateX({shifts[0][1]:.1f}px); }}"]
for k in range(len(STEPS)):
    land = k * STEP + LAND
    nxt = shifts[k + 1][1] if k + 1 < len(shifts) else 0.0
    stops.append(f"{pct(land)} {{ transform: translateX({shifts[k][1]:.1f}px); }}")
    stops.append(f"{pct(land + SLIDE)} {{ transform: translateX({nxt:.1f}px); }}")
stops.append(f"{pct(HOLD_END + 0.5)} {{ transform: translateX(0px); }}")
stops.append(f"{pct(HOLD_END + 0.6)}, 100% {{ transform: translateX({shifts[0][1]:.1f}px); }}")  # reset while invisible
css.append("@keyframes line { " + " ".join(stops) + " }")

# the hand waves a few times at the top of each loop, then rests
hello_x = CX - (HELLO_W + WAVE_GAP + WAVE_FS) / 2 + HELLO_W   # right edge of the greeting
swings = [(0.3, 0), (0.5, 16), (0.7, -8), (0.9, 16), (1.1, -6), (1.3, 12), (1.6, 0)]
css.append("@keyframes wave { " + " ".join(f"{pct(t)} {{ transform: rotate({d}deg); }}" for t, d in [(0, 0)] + swings) + " 100% { transform: rotate(0deg); } }")

timing = f"animation-duration: {T}s; animation-iteration-count: infinite; animation-timing-function: ease-out;"
if freeze is not None:  # testing only: pause the loop at a given second
    timing += f" animation-play-state: paused; animation-delay: -{freeze}s;"

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Hi, I'm Sandy. Computer science at UC San Diego. I like to know how models think.">
  <defs>
    <style>
      .a {{ {timing} }}
      .bar {{ transform-box: fill-box; transform-origin: left center; }}
      .wave {{ transform-box: fill-box; transform-origin: 70% 75%; animation-timing-function: ease-in-out; }}
      {chr(10).join("      " + c for c in css).strip()}
      @media (prefers-reduced-motion: reduce) {{ .a {{ animation: none; }} }}
    </style>
  </defs>
  <rect width="{W}" height="{H}" rx="16" fill="{BG}"/>

  <text x="{hello_x:.0f}" y="96" text-anchor="end" font-family="{sans}" font-size="72" font-weight="700" letter-spacing="-2" word-spacing="8" fill="{INK}">{HELLO}</text>
  <text class="a wave" style="animation-name:wave" x="{hello_x + WAVE_GAP:.0f}" y="93" font-family="{emoji}" font-size="{WAVE_FS}">\U0001F44B</text>
  <text x="{CX:.0f}" y="136" text-anchor="middle" font-family="{mono}" font-size="19" fill="{MUTED}">CS @ UC San Diego</text>

  <g class="a" style="animation-name:line">
    {chr(10).join("    " + s for s in sentence).strip()}
  </g>

  {chr(10).join("  " + p for p in panels).strip()}
</svg>
'''
open(sys.argv[1], "w", encoding="utf-8").write(svg)
