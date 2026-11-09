"""Link buttons that sit under the banner. Usage: python3 scripts/buttons.py  (writes assets/btn-<name>.svg)

GitHub strips CSS from READMEs, so each button is a small image wrapped in a link.
They copy the geometry of shields.io's "for-the-badge" style (28px tall, square corners, bold
uppercase Verdana, 14px logo) so they line up with shields.io tech badges used elsewhere in the README.
"""
import os

OUT = os.path.join(os.path.dirname(__file__), "..", "assets")
INK, ACCENT, WHITE = "#1F2328", "#F59E0B", "#FFFFFF"
font = "Verdana,Geneva,DejaVu Sans,sans-serif"

H, FS, SPACING = 28, 10, 1.25          # badge height, font size, letter spacing
LOGO_X, LOGO, TEXT_X, PAD_R = 9, 14, 32, 12

# advance widths of Verdana Bold at 100px, so the badge can be sized without measuring text
VERDANA_BOLD = {
    "A": 78, "B": 76, "C": 72, "D": 83, "E": 68, "F": 65, "G": 81, "H": 84, "I": 55, "J": 56, "K": 77, "L": 64, "M": 95,
    "N": 85, "O": 85, "P": 73, "Q": 85, "R": 78, "S": 71, "T": 68, "U": 81, "V": 76, "W": 113, "X": 76, "Y": 74, "Z": 69,
    "+": 87, "#": 87, ".": 36, "-": 48, "/": 69, "&": 86, " ": 33, **{d: 71 for d in "0123456789"},
}

# 16x16 line icons, scaled down to the 14px logo box
ICONS = {
    "website": '<circle cx="8" cy="8" r="6.5"/><ellipse cx="8" cy="8" rx="2.8" ry="6.5"/><path d="M1.5 8h13"/>',
    "resume": '<path d="M4.2 1.5h5.1l3 3v9.3a.7.7 0 0 1-.7.7H4.2a.7.7 0 0 1-.7-.7V2.2a.7.7 0 0 1 .7-.7z"/><path d="M9.2 1.7v3h3"/><path d="M5.9 8.6h4.2M5.9 11.2h4.2"/>',
    "linkedin": '<rect x="1.5" y="1.5" width="13" height="13" rx="3"/><path d="M5 7.4v3.9M8 11.3V7.4M8 9.1c0-1 .7-1.7 1.6-1.7s1.5.7 1.5 1.7v2.2"/><circle cx="5" cy="4.9" r=".6" fill="currentColor" stroke-width="1"/>',
    "email": '<rect x="1.5" y="3" width="13" height="10" rx="2"/><path d="M2.2 4.6L8 9l5.8-4.4"/>',
}

# (file name, label, background, text colour, icon colour) -- one amber button, the rest dark
BUTTONS = [
    ("website", "Website", ACCENT, INK, INK),
    ("resume", "Resume", INK, WHITE, ACCENT),
    ("linkedin", "LinkedIn", INK, WHITE, ACCENT),
    ("email", "Email", INK, WHITE, ACCENT),
]


def render(name, label, bg, fg, icon_col):
    caps = label.upper()
    text_w = sum(VERDANA_BOLD.get(c, 75) for c in caps) / 10 + SPACING * len(caps)
    w = TEXT_X + text_w + PAD_R
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:g} {H}" width="{w:g}" height="{H}" role="img" aria-label="{label}">
  <rect width="{w:g}" height="{H}" fill="{bg}" shape-rendering="crispEdges"/>
  <g transform="translate({LOGO_X} {(H - LOGO) / 2:g}) scale({LOGO / 16})" fill="none" stroke="{icon_col}" color="{icon_col}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</g>
  <text x="{TEXT_X}" y="17.5" textLength="{text_w:g}" font-family="{font}" font-size="{FS}" font-weight="bold" fill="{fg}" text-rendering="geometricPrecision">{caps}</text>
</svg>
'''


if __name__ == "__main__":
    for name, label, bg, fg, icon_col in BUTTONS:
        path = os.path.join(OUT, f"btn-{name}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(render(name, label, bg, fg, icon_col))
        print("wrote", os.path.normpath(path))
