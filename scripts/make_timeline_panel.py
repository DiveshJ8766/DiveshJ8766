#!/usr/bin/env python3
"""Career timeline as a Gantt inside the terminal chrome.

Colour is sequential, not categorical, and that is a deliberate correction.
Three distinct hues from this palette fail a CVD check — blue and purple sit
ΔE 2.7 apart under deuteranopia and 13.2 under normal vision, below the hard
floor. But roles in a timeline are not competing identities needing to be told
apart by colour: they are one thing over time, ordered, each directly labelled.
So one hue, brighter with recency, which reads correctly for everyone and
carries meaning colour-by-identity would not.

Widths are proportional to real month counts, which is the only honest way to
draw a timeline; a bar per role at equal width would flatten two years and six
months into the same mark.
"""
from pathlib import Path

from theme import ACCENT, BORDER, MONO, MUTED, TEXT, window_chrome

OUT = Path(__file__).resolve().parents[1] / "timeline-card.svg"

W = 860
PAD = 24
SPAN = W - 2 * PAD
TOP = 96
ROW_H = 56
BAR_H = 16

# (title, domain, start (y, m), end (y, m) inclusive, present?, hue)
# Oldest first, so it reads left-to-right and top-to-bottom like a calendar.
ROLES = [
    ("Application Engineer", "capital markets trading platform",
     (2023, 7), (2025, 8), False, "#006d32"),
    ("Application Engineer", "KYC registry platform",
     (2025, 9), (2026, 3), False, "#26a641"),
    ("Software Development Engineer", "services booking & payments platform",
     (2026, 4), (2026, 9), True, "#39d353"),
]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

START = ROLES[0][2]
END = ROLES[-1][3]
TOTAL = (END[0] - START[0]) * 12 + (END[1] - START[1]) + 1


def idx(ym):
    return (ym[0] - START[0]) * 12 + (ym[1] - START[1])


def x_of(months):
    return PAD + SPAN * months / TOTAL


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    axis_y = TOP + len(ROLES) * ROW_H + 6
    height = axis_y + 40

    parts = []
    for i, (title, domain, s, e, present, hue) in enumerate(ROLES):
        y = TOP + i * ROW_H
        x0, x1 = x_of(idx(s)), x_of(idx(e) + 1)
        months = idx(e) - idx(s) + 1
        delay = round(0.32 + i * 0.14, 3)
        dur = f"{months // 12}y {months % 12}m" if months >= 12 else f"{months} mo"
        span = (f"{MONTHS[s[1] - 1]} {s[0]} — "
                f"{'present' if present else f'{MONTHS[e[1] - 1]} {e[0]}'} · {dur}")

        # Labels sit in a fixed left gutter, never anchored to the bar. Anchored
        # to x0 they ran off the right edge for the later roles, and clamping
        # them back just detached a label from the bar it belonged to. The bar
        # carries the time position; the text reads as a list.
        label = f"{title} · {domain}"
        if len(label) * 7.5 > SPAN:
            raise SystemExit(f"label too long for the panel: {label!r}")

        parts.append(
            f'  <g class="row" style="animation-delay:{delay}s">\n'
            f'    <text class="ttl" x="{PAD}" y="{y - 7:.1f}">{esc(title)}'
            f'<tspan class="dom"> · {esc(domain)}</tspan></text>\n'
            f'    <rect class="track" x="{PAD}" y="{y:.1f}" width="{SPAN}" '
            f'height="{BAR_H}" rx="{BAR_H / 2}" fill="#161b22"/>\n'
            f'    <rect class="{"bar live" if present else "bar"}" x="{x0:.1f}" y="{y:.1f}" '
            f'width="{x1 - x0:.1f}" height="{BAR_H}" rx="{BAR_H / 2}" fill="{hue}"/>\n'
            f'    <text class="spn" x="{PAD}" y="{y + BAR_H + 15:.1f}">{esc(span)}</text>\n'
            f'  </g>'
        )

    ticks = []
    for yr in range(START[0] + 1, END[0] + 1):
        x = x_of(idx((yr, 1)))
        ticks.append(
            f'  <line class="row" x1="{x:.1f}" y1="{TOP - 24:.1f}" x2="{x:.1f}" '
            f'y2="{axis_y:.1f}" stroke="{BORDER}" style="animation-delay:.3s"/>\n'
            f'  <text class="yr row" x="{x + 6:.1f}" y="{axis_y + 18:.1f}" '
            f'style="animation-delay:.3s">{yr}</text>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height:.0f}" viewBox="0 0 {W} {height:.0f}"
     font-family="{MONO}" role="img" aria-label="Career timeline: application engineer on a capital markets platform from July 2023, then a KYC registry platform, then software development engineer from April 2026">
  <style>
    text {{ font-family: {MONO}; }}
    .row {{ opacity: 0; animation: rise .5s cubic-bezier(.2,.7,.3,1) both 1; }}
    .cmd {{ font-size: 15px; fill: {TEXT}; }}
    .ttl {{ font-size: 12.5px; font-weight: 600; fill: {TEXT}; }}
    .dom {{ font-weight: 400; fill: {MUTED}; }}
    .spn {{ font-size: 10.5px; fill: {MUTED}; }}
    .track {{ opacity: .55; }}
    .yr  {{ font-size: 10.5px; fill: {MUTED}; }}
    .live {{ animation: rise .5s cubic-bezier(.2,.7,.3,1) both 1,
                        pulse 2.8s ease-in-out infinite 1s; }}
    .cursor {{ animation: blink 1.1s steps(1) infinite; }}
    @keyframes rise {{
      from {{ opacity: 0; transform: translateY(8px); }}
      to   {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes pulse {{ 0%, 100% {{ filter: none }} 50% {{ filter: brightness(1.3) }} }}
    @keyframes blink {{ 0%, 49% {{ opacity: 1 }} 50%, 100% {{ opacity: 0 }} }}
    @media (prefers-reduced-motion: reduce) {{
      .row, .live, .cursor {{ animation: none !important; opacity: 1 !important;
                              transform: none !important; }}
    }}
  </style>
{window_chrome(W, height, "timeline.sh")}
  <text class="cmd row" x="{PAD}" y="58" style="animation-delay:.1s"><tspan fill="{ACCENT}">$</tspan> git log --date=short --reverse<tspan class="cursor" fill="{ACCENT}"> _</tspan></text>
  <text class="cmd row" x="{W - PAD}" y="58" text-anchor="end" fill="{MUTED}"
        style="animation-delay:.2s">{TOTAL // 12}y {TOTAL % 12}m · {len(ROLES)} roles</text>
  <line class="row" x1="{PAD}" y1="70" x2="{W - PAD}" y2="70" stroke="{BORDER}"
        style="animation-delay:.26s"/>
{chr(10).join(ticks)}
  <line class="row" x1="{PAD}" y1="{axis_y:.1f}" x2="{W - PAD}" y2="{axis_y:.1f}"
        stroke="{BORDER}" style="animation-delay:.3s"/>
{chr(10).join(parts)}
</svg>
'''
    OUT.write_text(svg)
    print(f"wrote {OUT} — {TOTAL} months across {len(ROLES)} roles, height {height:.0f}px")


if __name__ == "__main__":
    main()
