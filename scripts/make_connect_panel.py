#!/usr/bin/env python3
"""connect.sh - the contact panel, as terminal output.

Paired with the badge row in the README rather than replacing it: links
inside an <img>-loaded SVG are inert, so this panel does the looking and the
badges underneath do the clicking. The live dot is the only animation that
carries meaning here - it marks the status row as current.
"""
from pathlib import Path

from theme import (ACCENT, AMBER, BLUE, BORDER, MAGENTA, MONO, MUTED, TEXT,
                   window_chrome)

OUT = Path(__file__).resolve().parents[1] / "connect-card.svg"

W = 860
PAD = 24
X_LABEL, X_VALUE = PAD, PAD + 120
TOP = 96
LINE = 25.0

ROWS = [
    ("status",   [("open to opportunities", ACCENT)], True),
    ("looking",  [("frontend / full-stack — performance, design systems,", TEXT)], False),
    ("",         [("and shipping quickly", TEXT)], False),
    (None,       [], False),
    ("email",    [("diveshjadhav72@gmail.com", BLUE)], False),
    ("linkedin", [("in/diveshjadhav8766", BLUE)], False),
    ("portfolio",[("projects-nine-woad.vercel.app", BLUE)], False),
    (None,       [], False),
    ("based",    [("Navi Mumbai, India", TEXT)], False),
    ("timezone", [("IST (UTC+5:30)", MUTED)], False),
    ("open to",  [("full-time", AMBER), (" · ", MUTED), ("contract", AMBER),
                  (" · ", MUTED), ("interesting problems", AMBER)], False),
]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    parts, y, i = [], TOP, 0
    for label, spans, live in ROWS:
        if label is None:
            y += LINE * 0.5
            continue
        delay = round(0.32 + i * 0.07, 3)
        i += 1
        if label:
            parts.append(f'  <text class="lbl row" x="{X_LABEL}" y="{y:.1f}" '
                         f'style="animation-delay:{delay}s">{label}</text>')
        if live:
            parts.append(f'  <circle class="dot row" cx="{X_VALUE + 5}" cy="{y - 4:.1f}" r="4" '
                         f'fill="{ACCENT}" style="animation-delay:{delay}s"/>')
            off = 18
        else:
            off = 0
        tspans = "".join(f'<tspan fill="{c}">{esc(t)}</tspan>' for t, c in spans)
        parts.append(f'  <text class="val row" x="{X_VALUE + off}" y="{y:.1f}" '
                     f'style="animation-delay:{delay}s">{tspans}</text>')
        y += LINE

    height = y + 22
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height:.0f}" viewBox="0 0 {W} {height:.0f}"
     font-family="{MONO}" role="img" aria-label="Contact details: open to opportunities, diveshjadhav72 at gmail dot com, LinkedIn in/diveshjadhav8766, portfolio, based in Navi Mumbai India">
  <style>
    text {{ font-family: {MONO}; }}
    .row {{ opacity: 0; animation: rise .45s cubic-bezier(.2,.7,.3,1) both 1; }}
    .cmd {{ font-size: 15px; fill: {TEXT}; }}
    .lbl {{ font-size: 12.5px; fill: {MUTED}; }}
    .val {{ font-size: 12.5px; fill: {TEXT}; }}
    .dot {{ animation: rise .45s cubic-bezier(.2,.7,.3,1) both 1,
                       beat 2.2s ease-in-out infinite .8s; }}
    .cursor {{ animation: blink 1.1s steps(1) infinite; }}
    @keyframes rise {{
      from {{ opacity: 0; transform: translateX(-8px); }}
      to   {{ opacity: 1; transform: translateX(0); }}
    }}
    @keyframes beat {{ 0%, 100% {{ opacity: 1 }} 50% {{ opacity: .35 }} }}
    @keyframes blink {{ 0%, 49% {{ opacity: 1 }} 50%, 100% {{ opacity: 0 }} }}
    @media (prefers-reduced-motion: reduce) {{
      .row, .dot, .cursor {{ animation: none !important; opacity: 1 !important;
                             transform: none !important; }}
    }}
  </style>
{window_chrome(W, height, "connect.sh")}
  <text class="cmd row" x="{PAD}" y="58" style="animation-delay:.1s"><tspan fill="{ACCENT}">$</tspan> ./connect.sh --status<tspan class="cursor" fill="{ACCENT}"> _</tspan></text>
  <text class="cmd row" x="{W - PAD}" y="58" text-anchor="end" fill="{MUTED}"
        style="animation-delay:.2s">replies from IST hours</text>
  <line class="row" x1="{PAD}" y1="70" x2="{W - PAD}" y2="70" stroke="{BORDER}"
        style="animation-delay:.26s"/>
{chr(10).join(parts)}
</svg>
'''
    OUT.write_text(svg)
    print(f"wrote {OUT} — {i} rows, height {height:.0f}px")


if __name__ == "__main__":
    main()
