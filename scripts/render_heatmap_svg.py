#!/usr/bin/env python3
"""Render data/contributions.json as an animated SVG heatmap.

The grid reveals itself diagonally: every cell's delay is a function of
(column + row), so the wave sweeps from the top-left corner down and to the
right. Cells at the top two levels keep a slow shimmer afterwards so the
panel still feels alive once the reveal has finished.
"""
import datetime
import json
from pathlib import Path

from theme import ACCENT, BORDER, HEAT, MONO, MUTED, TEXT, window_chrome

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "contributions.json"
OUT = ROOT / "contrib-heatmap.svg"

W, H = 860, 270
GRID_X, GRID_Y = 50, 92
CELL, GAP = 12, 3
PITCH = CELL + GAP
STEP = 0.011           # seconds of delay per diagonal step
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def streaks(days):
    """(current, longest) run of consecutive days with at least one contribution."""
    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] > 0 else 0
        longest = max(longest, run)
    current = 0
    for d in reversed(days):
        if d["count"] == 0:
            break
        current += 1
    return current, longest


def main():
    data = json.loads(DATA.read_text())
    days = data["days"]

    first = datetime.date.fromisoformat(days[0]["date"])
    # Anchor column 0 on the Sunday of the first week (GitHub weeks start Sunday).
    origin = first - datetime.timedelta(days=(first.weekday() + 1) % 7)

    cells, month_ticks, seen = [], [], set()
    max_delay = 0.0
    for d in days:
        date = datetime.date.fromisoformat(d["date"])
        col = (date - origin).days // 7
        row = (date.weekday() + 1) % 7
        x = GRID_X + col * PITCH
        y = GRID_Y + row * PITCH
        delay = round((col + row) * STEP, 3)
        max_delay = max(max_delay, delay)
        lvl = min(d["level"], len(HEAT) - 1)
        if d["count"] >= 8:
            lvl = 5
        cls = "c hot" if lvl >= 4 else "c"
        label = "no contributions" if d["count"] == 0 else (
            f"{d['count']} contribution{'s' if d['count'] != 1 else ''}")
        cells.append(
            f'<rect class="{cls}" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
            f'fill="{HEAT[lvl]}" style="animation-delay:{delay}s">'
            f"<title>{d['date']} - {label}</title></rect>"
        )
        key = (date.year, date.month)
        if key not in seen and date.day <= 7:
            seen.add(key)
            month_ticks.append((x, MONTHS[date.month - 1], delay))

    cur, longest = streaks(days)
    best = max(days, key=lambda d: d["count"])
    active = sum(1 for d in days if d["count"] > 0)

    months_svg = "".join(
        f'<text class="fade" x="{x}" y="80" style="animation-delay:{d:.3f}s">{m}</text>'
        for x, m, d in month_ticks
    )
    day_svg = "".join(
        f'<text class="fade dim" x="42" y="{GRID_Y + r * PITCH + 10}" text-anchor="end" '
        f'style="animation-delay:{r * STEP + 0.1:.3f}s">{lbl}</text>'
        for r, lbl in ((1, "Mon"), (3, "Wed"), (5, "Fri"))
    )
    legend_x = W - 230
    legend = "".join(
        f'<rect class="c" x="{legend_x + 34 + i * PITCH}" y="{H - 30}" width="{CELL}" height="{CELL}" '
        f'rx="2.5" fill="{HEAT[i]}" style="animation-delay:{max_delay + 0.05 + i * 0.05:.3f}s"/>'
        for i in range(5)
    )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"
     font-family="{MONO}" role="img" aria-label="Contribution graph for {data['user']}">
  <style>
    text {{ font-family: {MONO}; }}
    .c {{ opacity: 0; transform-box: fill-box; transform-origin: center;
          animation: pop .45s ease-out both 1; }}
    .fade {{ opacity: 0; font-size: 12px; fill: {MUTED};
             animation: fade .5s ease-out both 1; }}
    .dim {{ font-size: 11px; }}
    .hot {{ animation: pop .45s ease-out both 1, glow 3.4s ease-in-out infinite; }}
    .cursor {{ animation: blink 1.1s steps(1) infinite; }}
    @keyframes pop {{
      from {{ opacity: 0; transform: translateY(-4px) scale(.4); }}
      to   {{ opacity: 1; transform: translateY(0) scale(1); }}
    }}
    @keyframes fade {{ from {{ opacity: 0 }} to {{ opacity: 1 }} }}
    @keyframes glow {{ 0%, 100% {{ filter: none }} 50% {{ filter: brightness(1.45) }} }}
    @keyframes blink {{ 0%, 49% {{ opacity: 1 }} 50%, 100% {{ opacity: 0 }} }}
    @media (prefers-reduced-motion: reduce) {{
      .c, .fade, .hot, .cursor {{ animation: none !important; opacity: 1 !important;
                                  transform: none !important; }}
    }}
  </style>
{window_chrome(W, H, f"{data['user']} — contributions.sh")}
  <text class="fade" x="16" y="56" font-size="15" fill="{ACCENT}" style="animation-delay:.05s">$</text>
  <text class="fade" x="30" y="56" font-size="15" fill="{TEXT}" style="animation-delay:.05s">git log --since=1.year --oneline | wc -l</text>
  <text class="fade" x="{W - 16}" y="56" font-size="15" fill="{ACCENT}" text-anchor="end"
        style="animation-delay:.6s">{data['total']} contributions</text>
{months_svg}
{day_svg}
{''.join(cells)}
  <text class="fade dim" x="16" y="{H - 20}" style="animation-delay:{max_delay + 0.1:.3f}s" fill="{MUTED}">
    <tspan fill="{ACCENT}">{active}</tspan> active days · longest streak <tspan fill="{ACCENT}">{longest}</tspan> · current <tspan fill="{ACCENT}">{cur}</tspan> · busiest <tspan fill="{ACCENT}">{best['count']}</tspan> on {best['date']}<tspan class="cursor" fill="{ACCENT}"> _</tspan>
  </text>
  <text class="fade dim" x="{legend_x}" y="{H - 20}" style="animation-delay:{max_delay + 0.05:.3f}s">Less</text>
{legend}
  <text class="fade dim" x="{legend_x + 34 + 5 * PITCH + 6}" y="{H - 20}"
        style="animation-delay:{max_delay + 0.3:.3f}s">More</text>
</svg>
'''
    OUT.write_text(svg)
    print(f"wrote {OUT} ({len(svg)} bytes, {len(cells)} cells)")


if __name__ == "__main__":
    main()
