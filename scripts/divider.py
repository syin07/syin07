"""Section divider: a dotted line with a pulse of amber bars travelling along it, like a signal passing through.

Usage: python3 scripts/divider.py assets/divider.svg [freeze_seconds]
"""
import sys

W, H = 1200, 36
MID = H / 2
GREY, ACCENT = "#9CA3AF", "#F59E0B"
PAD, PITCH = 32, 16                    # side margin and distance between ticks
TW, TH = 4, 4                          # a resting tick is a 4x4 dot
T, TRAVEL = 7.0, 5.2                   # loop length, and how long the pulse takes to cross
RISE, PEAK = 0.34, 5.5                 # seconds a tick takes to rise (and to fall), and how many times taller it gets
freeze = float(sys.argv[2]) if len(sys.argv) > 2 else None

n = int((W - 2 * PAD) / PITCH) + 1
ticks = []
for i in range(n):
    x = PAD + i * PITCH
    edge = min(i, n - 1 - i) / (n - 1)                 # 0 at the ends, 0.5 in the middle
    fade = min(1.0, 0.12 + edge * 5)                   # the line fades out towards both ends
    delay = TRAVEL * i / (n - 1) - (freeze or 0)
    ticks.append(
        f'<rect class="t" style="animation-delay:{delay:.2f}s" x="{x - TW / 2:.1f}" y="{MID - TH / 2}" '
        f'width="{TW}" height="{TH}" rx="{TW / 2}" fill="{GREY}" opacity="{fade:.2f}"/>'
    )

up, down = 100 * RISE / T, 100 * 2 * RISE / T
paused = " animation-play-state: paused;" if freeze is not None else ""   # testing only
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="">
  <style>
    .t {{ transform-box: fill-box; transform-origin: center; animation: pulse {T}s ease-in-out infinite;{paused} }}
    @keyframes pulse {{ 0% {{ transform: scaleY(1); fill: {GREY}; }} {up:.2f}% {{ transform: scaleY({PEAK}); fill: {ACCENT}; }} {down:.2f}%, 100% {{ transform: scaleY(1); fill: {GREY}; }} }}
    @media (prefers-reduced-motion: reduce) {{ .t {{ animation: none; }} }}
  </style>
  {chr(10).join("  " + t for t in ticks).strip()}
</svg>
'''
open(sys.argv[1], "w", encoding="utf-8").write(svg)
