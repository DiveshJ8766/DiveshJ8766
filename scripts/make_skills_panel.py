#!/usr/bin/env python3
"""Full technical skill inventory as a chip grid inside the terminal chrome.

Six groups, every chip from the CV. SVG cannot wrap text or lay out inline
boxes, so chips are measured and flowed here against the column width, rows
are counted, and the panel height is derived from the result — nothing is
hard-coded, so adding a skill cannot push a chip off the edge.

Colour does no encoding work: every chip is the same surface and text token.
Grouping and position carry the meaning, so hues would only add noise.
"""
from pathlib import Path

from theme import ACCENT, BORDER, MONO, MUTED, TEXT, window_chrome

OUT = Path(__file__).resolve().parents[1] / "skills-card.svg"

W = 860
PAD = 24
LABEL_W = 132
CHIP_X = PAD + LABEL_W
CHIP_AREA = W - CHIP_X - PAD
CHIP_PX, CHIP_H, CHIP_GAP = 11, 21, 6
ROW_LEAD = CHIP_H + 7
GROUP_GAP = 13
TOP = 86
MONO_RATIO = 0.6

GROUPS = [
    ("languages", ["JavaScript (ES6+)", "TypeScript", "C++", "HTML5", "CSS3"]),
    ("frameworks", ["React.js", "Redux", "TanStack Query", "React Hook Form",
                    "Node.js", "Express.js", "Tailwind CSS", "Bootstrap",
                    "Chart.js", "Puppeteer"]),
    ("frontend", ["Frontend Architecture", "Design Systems", "Reusable Components",
                  "RBAC", "REST APIs"]),
    ("performance", ["Lazy Loading", "Code Splitting", "Caching", "Web Workers",
                     "Service Workers", "Virtualized Lists"]),
    ("testing", ["Jest", "React Testing Library", "WCAG 2.1 AA"]),
    ("tooling", ["Git", "GitHub", "Cursor", "Lovable", "Postman", "Stripe Terminal",
                 "Apache Superset", "Cloudinary", "IPFS", "MetaMask"]),
]


def chip_w(text):
    return len(text) * CHIP_PX * MONO_RATIO + 16


def flow(chips):
    """Greedy-flow chips into rows that fit CHIP_AREA."""
    rows, row, used = [], [], 0.0
    for c in chips:
        w = chip_w(c)
        if row and used + CHIP_GAP + w > CHIP_AREA:
            rows.append(row)
            row, used = [c], w
        else:
            used += (CHIP_GAP if row else 0) + w
            row.append(c)
    if row:
        rows.append(row)
    return rows


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    laid = [(label, flow(chips)) for label, chips in GROUPS]
    height = TOP + sum(len(r) * ROW_LEAD + GROUP_GAP for _, r in laid) - GROUP_GAP + 20

    parts, y, n = [], TOP, 0
    for label, rows in laid:
        delay = round(0.3 + n * 0.09, 3)
        n += 1
        parts.append(f'  <text class="grp" x="{PAD}" y="{y + 15:.1f}" '
                     f'style="animation-delay:{delay}s">{label}</text>')
        for row in rows:
            x = CHIP_X
            for chip in row:
                w = chip_w(chip)
                parts.append(
                    f'  <g class="row" style="animation-delay:{delay}s">'
                    f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{CHIP_H}" '
                    f'rx="5" fill="#161b22" stroke="{BORDER}"/>'
                    f'<text class="chp" x="{x + w / 2:.1f}" y="{y + 14.5:.1f}" '
                    f'text-anchor="middle">{esc(chip)}</text></g>')
                x += w + CHIP_GAP
            y += ROW_LEAD
        y += GROUP_GAP

    total = sum(len(c) for _, c in GROUPS)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height:.0f}" viewBox="0 0 {W} {height:.0f}"
     font-family="{MONO}" role="img" aria-label="Technical skills across languages, frameworks, frontend engineering, performance, testing and tooling">
  <style>
    text {{ font-family: {MONO}; }}
    .row, .grp {{ opacity: 0; animation: rise .45s cubic-bezier(.2,.7,.3,1) both 1; }}
    .cmd {{ font-size: 15px; fill: {TEXT}; }}
    .grp {{ font-size: 11.5px; fill: {ACCENT}; }}
    .chp {{ font-size: {CHIP_PX}px; fill: {TEXT}; }}
    .cursor {{ animation: blink 1.1s steps(1) infinite; }}
    @keyframes rise {{
      from {{ opacity: 0; transform: translateY(6px); }}
      to   {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes blink {{ 0%, 49% {{ opacity: 1 }} 50%, 100% {{ opacity: 0 }} }}
    @media (prefers-reduced-motion: reduce) {{
      .row, .grp, .cursor {{ animation: none !important; opacity: 1 !important;
                             transform: none !important; }}
    }}
  </style>
{window_chrome(W, height, "skills.sh")}
  <text class="cmd row" x="{PAD}" y="58" style="animation-delay:.1s"><tspan fill="{ACCENT}">$</tspan> cat skills.json | jq -r keys[]<tspan class="cursor" fill="{ACCENT}"> _</tspan></text>
  <text class="cmd row" x="{W - PAD}" y="58" text-anchor="end" fill="{MUTED}"
        style="animation-delay:.2s">{total} entries</text>
  <line class="row" x1="{PAD}" y1="70" x2="{W - PAD}" y2="70" stroke="{BORDER}"
        style="animation-delay:.26s"/>
{chr(10).join(parts)}
</svg>
'''
    OUT.write_text(svg)
    print(f"wrote {OUT} — {total} chips, {sum(len(r) for _, r in laid)} rows, "
          f"height {height:.0f}px")


if __name__ == "__main__":
    main()
