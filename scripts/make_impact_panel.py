#!/usr/bin/env python3
"""Hand-authored impact panel: a KPI row of stat tiles, rendered as an SVG.

Why tiles and not a chart. These are a handful of headline numbers whose only
job is to be read, so the form is a KPI row - a grouped bar chart here would
be actively misleading, because putting "+35% bookings" and "-70% page load"
on one axis invents a comparison that does not exist. They share no baseline,
no unit and not even a direction. Four tiles, four distinct dimensions, no
shared scale, no meters.

Colour does one job: every value is the same amber the info card already uses
for metrics, so the number reads as "a figure" rather than as a category. All
the ink is a text token against the panel surface - amber 9.50:1, text
11.97:1, muted 6.01:1, all clearing WCAG AA.
"""
from pathlib import Path

from theme import ACCENT, AMBER, BORDER, MONO, MUTED, TEXT, window_chrome

OUT = Path(__file__).resolve().parents[1] / "impact-card.svg"

W, H = 860, 248
PAD = 24
INNER = W - 2 * PAD
GAP = 20
TILES = 4
TILE_W = (INNER - GAP * (TILES - 1)) / TILES
TILE_Y = 92
STEP = 0.11                     # stagger between tiles

# (category, value, label) - one per dimension, so nothing overlaps.
STATS = [
    ("performance", "−70%", "initial page load"),
    ("business",    "+35%", "bookings from waitlist"),
    ("velocity",     "40%", "faster feature dev"),
    ("quality",     "+40%", "unit test coverage"),
]

# Everything else, kept deliberately secondary so the four above stay the point.
ALSO = [
    "−60% API calls", "−30% bundle size", "−80% UI freezes",
    "−80% manual form setup", "WCAG 2.1 AA",
]

# ~7.2px per glyph at 12px in this mono stack. The supporting line is the only
# thing here long enough to run off the panel, so it is measured rather than
# eyeballed - the first render overflowed and silently clipped a metric.
CHAR_W = 7.2
ALSO_BUDGET = INNER


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    tiles = []
    for i, (cat, value, label) in enumerate(STATS):
        x = PAD + i * (TILE_W + GAP)
        d = round(0.35 + i * STEP, 3)
        tiles.append(
            f'  <g class="row" style="animation-delay:{d}s">\n'
            f'    <text class="cat" x="{x:.1f}" y="{TILE_Y}">{esc(cat)}</text>\n'
            f'    <text class="val" x="{x:.1f}" y="{TILE_Y + 46}">{esc(value)}</text>\n'
            f'    <text class="lbl" x="{x:.1f}" y="{TILE_Y + 72}">{esc(label)}</text>\n'
            f'  </g>'
        )
        if i:                    # hairline separator, layout not data
            rx = x - GAP / 2
            tiles.append(
                f'  <line class="row" x1="{rx:.1f}" y1="{TILE_Y - 18}" '
                f'x2="{rx:.1f}" y2="{TILE_Y + 78}" stroke="{BORDER}" '
                f'style="animation-delay:{d}s"/>'
            )

    also_delay = round(0.35 + TILES * STEP + 0.1, 3)
    also = " · ".join(ALSO)
    width = (len(also) + len("also ")) * CHAR_W
    if width > ALSO_BUDGET:
        raise SystemExit(
            f"supporting line needs {width:.0f}px but only {ALSO_BUDGET:.0f}px "
            f"is available - drop an entry from ALSO")

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"
     font-family="{MONO}" role="img"
     aria-label="Impact metrics: 70% faster initial page load, 35% more bookings, 40% faster feature development, 40% more unit test coverage">
  <style>
    text {{ font-family: {MONO}; }}
    .row {{ opacity: 0; animation: rise .5s cubic-bezier(.2,.7,.3,1) both 1; }}
    .cmd {{ font-size: 15px; fill: {TEXT}; }}
    .cat {{ font-size: 11px; fill: {MUTED}; letter-spacing: .08em; }}
    .val {{ font-size: 38px; font-weight: 600; fill: {AMBER}; }}
    .lbl {{ font-size: 12.5px; fill: {TEXT}; }}
    .also {{ font-size: 12px; fill: {MUTED}; }}
    .cursor {{ animation: blink 1.1s steps(1) infinite; }}
    @keyframes rise {{
      from {{ opacity: 0; transform: translateY(8px); }}
      to   {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes blink {{ 0%, 49% {{ opacity: 1 }} 50%, 100% {{ opacity: 0 }} }}
    @media (prefers-reduced-motion: reduce) {{
      .row, .cursor {{ animation: none !important; opacity: 1 !important;
                       transform: none !important; }}
    }}
  </style>
{window_chrome(W, H, "impact.sh")}
  <text class="cmd row" x="{PAD}" y="58" style="animation-delay:.1s"><tspan fill="{ACCENT}">$</tspan> ./impact --all-roles</text>
  <text class="cmd row" x="{W - PAD}" y="58" text-anchor="end" fill="{MUTED}"
        style="animation-delay:.2s">3+ years · 3 roles</text>
  <line class="row" x1="{PAD}" y1="70" x2="{W - PAD}" y2="70" stroke="{BORDER}"
        style="animation-delay:.28s"/>
{chr(10).join(tiles)}
  <line class="row" x1="{PAD}" y1="{TILE_Y + 100}" x2="{W - PAD}" y2="{TILE_Y + 100}"
        stroke="{BORDER}" style="animation-delay:{also_delay}s"/>
  <text class="also row" x="{PAD}" y="{TILE_Y + 124}" style="animation-delay:{also_delay}s">
    <tspan fill="{MUTED}">also </tspan>{esc(also)}<tspan class="cursor" fill="{ACCENT}"> _</tspan>
  </text>
</svg>
'''
    OUT.write_text(svg)
    print(f"wrote {OUT} ({len(svg)} bytes, {TILES} tiles)")


if __name__ == "__main__":
    main()
