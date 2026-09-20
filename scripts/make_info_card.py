#!/usr/bin/env python3
"""Hand-authored neofetch-style info card, rendered as an animated SVG.

Every row fades and slides in on a short stagger, so the card reads top to
bottom like output scrolling out of a real terminal.
"""
from pathlib import Path

from theme import (ACCENT, AMBER, BLUE, BORDER, DOT_AMBER, DOT_GREEN, DOT_RED,
                   MAGENTA, MONO, MUTED, RED, TEXT, window_chrome)

OUT = Path(__file__).resolve().parents[1] / "info-card.svg"

W, H = 490, 520
X_LABEL, X_VALUE = 18, 104
LINE = 21.0
START_Y = 78
STEP = 0.075          # stagger between rows

# (label, [(text, colour), ...]) - a row with an empty label is a continuation.
ROWS = [
    ("role",    [("Software Development Engineer", ACCENT)]),
    ("based",   [("Navi Mumbai, India", MUTED)]),
    ("uptime",  [("3+ years shipping production frontends", TEXT)]),
    ("focus",   [("architecture", TEXT), (" · ", MUTED),
                 ("design systems", TEXT), (" · ", MUTED), ("performance", TEXT)]),
    (None,      []),
    ("core",    [("React", BLUE), (" · ", MUTED), ("TypeScript", BLUE), (" · ", MUTED),
                 ("Redux", BLUE), (" · ", MUTED), ("TanStack Query", BLUE)]),
    ("",        [("Node.js", BLUE), (" · ", MUTED), ("Express", BLUE), (" · ", MUTED),
                 ("Tailwind", BLUE), (" · ", MUTED), ("Chart.js", BLUE)]),
    ("perf",    [("code splitting", TEXT), (" · ", MUTED), ("web workers", TEXT),
                 (" · ", MUTED), ("virtual lists", TEXT)]),
    ("quality", [("Jest", TEXT), (" · ", MUTED), ("RTL", TEXT), (" · ", MUTED),
                 ("WCAG 2.1 AA", TEXT), (" · ", MUTED), ("design systems", TEXT)]),
    (None,      []),
    # The numbers used to live here too, which meant the impact panel and this
    # card were repeating each other a scroll apart. Impact owns the figures
    # now; this card names the work and keeps the identity.
    ("ai",      [("authored custom Claude skills for our", TEXT)]),
    ("",        [("design system, FTUX and PR review", TEXT)]),
    ("shipped", [("Stripe Terminal tap-to-pay checkout", TEXT)]),
    ("",        [("waitlist · form builder · RBAC", TEXT)]),
    ("",        [("embedded Superset dashboards", TEXT)]),
    (None,      []),
    ("labs",    [("Blockchain certificates", MAGENTA), (" (Solidity · IPFS)", MUTED)]),
    ("",        [("StudyNotion", MAGENTA), (" MERN EdTech platform", MUTED)]),
    (None,      []),
    ("status",  [("open to opportunities", ACCENT)]),
    ("contact", [("diveshjadhav72@gmail.com", BLUE)]),
]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    parts, y, i = [], START_Y, 0
    for label, spans in ROWS:
        if label is None:                      # blank spacer line
            y += LINE * 0.45
            continue
        delay = round(0.35 + i * STEP, 3)
        i += 1
        if label:
            parts.append(
                f'<text class="row" x="{X_LABEL}" y="{y:.1f}" fill="{ACCENT}" '
                f'style="animation-delay:{delay}s">{label}</text>'
            )
        tspans = "".join(f'<tspan fill="{c}">{esc(t)}</tspan>' for t, c in spans)
        parts.append(
            f'<text class="row" x="{X_VALUE}" y="{y:.1f}" '
            f'style="animation-delay:{delay}s">{tspans}</text>'
        )
        y += LINE

    dots = "".join(
        f'<rect class="row" x="{X_LABEL + n * 17}" y="{H - 34}" width="13" height="9" rx="2" '
        f'fill="{c}" style="animation-delay:{0.35 + i * STEP + 0.05 * n:.3f}s"/>'
        for n, c in enumerate([DOT_RED, DOT_AMBER, DOT_GREEN, BLUE, MAGENTA, ACCENT, TEXT])
    )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"
     font-family="{MONO}" role="img" aria-label="About Divesh Jadhav">
  <style>
    text {{ font-family: {MONO}; font-size: 13px; fill: {TEXT}; }}
    .row {{ opacity: 0; animation: slide .45s cubic-bezier(.2,.7,.3,1) both 1; }}
    .head {{ font-size: 16px; font-weight: 700; }}
    .cursor {{ animation: blink 1.1s steps(1) infinite; }}
    @keyframes slide {{
      from {{ opacity: 0; transform: translateX(-10px); }}
      to   {{ opacity: 1; transform: translateX(0); }}
    }}
    @keyframes blink {{ 0%, 49% {{ opacity: 1 }} 50%, 100% {{ opacity: 0 }} }}
    @media (prefers-reduced-motion: reduce) {{
      .row, .cursor {{ animation: none !important; opacity: 1 !important; transform: none !important; }}
    }}
  </style>
{window_chrome(W, H, "whoami — zsh")}
  <text class="row head" x="{X_LABEL}" y="50" style="animation-delay:.1s">
    <tspan fill="{ACCENT}">divesh</tspan><tspan fill="{MUTED}">@</tspan><tspan fill="{BLUE}">github</tspan>
  </text>
  <line class="row" x1="{X_LABEL}" y1="58" x2="{W - X_LABEL}" y2="58" stroke="{BORDER}"
        style="animation-delay:.22s"/>
{chr(10).join(parts)}
{dots}
  <text class="row" x="{X_LABEL}" y="{H - 12}" fill="{MUTED}" style="animation-delay:{0.35 + i * STEP + 0.4:.3f}s">
    <tspan fill="{ACCENT}">$</tspan> <tspan class="cursor">▍</tspan>
  </text>
</svg>
'''
    OUT.write_text(svg)
    print(f"wrote {OUT} ({len(svg)} bytes, {i} rows)")


if __name__ == "__main__":
    main()
