#!/usr/bin/env python3
"""Project cards as a terminal panel, replacing the markdown table.

The table was the one block on the page still wearing GitHub's own chrome,
which made it read as an afterthought next to three hand-built panels. Three
cards in one window, same palette, same stagger.

SVG has no text wrapping, so every description is wrapped here against a
measured character budget and the script fails if a card overflows its box
rather than letting a line run past the border. That check is the whole
reason this is generated instead of hand-written.
"""
from pathlib import Path

from theme import (ACCENT, BLUE, BORDER, MAGENTA, MONO, MUTED, PANEL, TEXT,
                   window_chrome)

OUT = Path(__file__).resolve().parents[1] / "projects-card.svg"

W, H = 860, 306
PAD = 24
GAP = 22
COLS = 3
CARD_W = (W - 2 * PAD - GAP * (COLS - 1)) / COLS
CARD_X_PAD = 14
CARD_Y = 84
CARD_H = 196

TITLE_PX, DESC_PX, CHIP_PX = 13.5, 11.5, 10
MONO_RATIO = 0.6                       # advance width / font size for this stack
TITLE_LINES, DESC_LINES = 2, 5
DESC_LEAD = 15.5

INNER = CARD_W - 2 * CARD_X_PAD
TITLE_CH = int(INNER / (TITLE_PX * MONO_RATIO))
DESC_CH = int(INNER / (DESC_PX * MONO_RATIO))

PROJECTS = [
    ("01", "Blockchain Certificates", BLUE,
     "Tamper-proof issuance and verification. Solidity contracts on an "
     "Ethereum testnet, MetaMask auth, 100+ records.",
     ["React", "Solidity", "IPFS", "Ethereum"]),
    ("02", "StudyNotion EdTech", MAGENTA,
     "Full-stack MERN learning platform. JWT auth, instructor dashboards, "
     "Razorpay payments.",
     ["MongoDB", "Express", "React", "Node"]),
    ("03", "This profile", ACCENT,
     "Every panel is an SVG my own Python scripts generate, re-rendered "
     "daily by a GitHub Action.",
     ["Python", "SVG", "Actions"]),
]


def wrap(text, width, max_lines, where):
    lines, line = [], ""
    for word in text.split():
        cand = f"{line} {word}".strip()
        if len(cand) <= width:
            line = cand
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    if len(lines) > max_lines:
        raise SystemExit(
            f"{where}: needs {len(lines)} lines at {width} chars but only "
            f"{max_lines} fit — shorten the copy or widen the card")
    return lines


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    parts = []
    for i, (idx, title, hue, desc, chips) in enumerate(PROJECTS):
        x = PAD + i * (CARD_W + GAP)
        tx = x + CARD_X_PAD
        delay = round(0.35 + i * 0.13, 3)

        t_lines = wrap(title, TITLE_CH, TITLE_LINES, f"title {idx}")
        d_lines = wrap(desc, DESC_CH, DESC_LINES, f"description {idx}")

        body = [
            f'  <g class="row" style="animation-delay:{delay}s">',
            f'    <rect x="{x:.1f}" y="{CARD_Y}" width="{CARD_W:.1f}" height="{CARD_H}" '
            f'rx="8" fill="{PANEL}" stroke="{BORDER}"/>',
            f'    <rect x="{x:.1f}" y="{CARD_Y}" width="3" height="{CARD_H}" '
            f'rx="1.5" fill="{hue}"/>',
            f'    <text class="idx" x="{tx:.1f}" y="{CARD_Y + 24}">{idx}</text>',
        ]
        y = CARD_Y + 46
        for ln in t_lines:
            body.append(f'    <text class="ttl" x="{tx:.1f}" y="{y:.1f}" '
                        f'fill="{hue}">{esc(ln)}</text>')
            y += 18
        y = CARD_Y + 46 + TITLE_LINES * 18 + 8
        for ln in d_lines:
            body.append(f'    <text class="dsc" x="{tx:.1f}" y="{y:.1f}">{esc(ln)}</text>')
            y += DESC_LEAD

        cx = tx
        chip_y = CARD_Y + CARD_H - 18
        for chip in chips:
            cw = len(chip) * CHIP_PX * MONO_RATIO + 12
            if cx + cw > x + CARD_W - CARD_X_PAD:      # wrap onto the row above
                cx = tx
                chip_y -= 18
            body.append(
                f'    <rect x="{cx:.1f}" y="{chip_y - 11}" width="{cw:.1f}" height="15" '
                f'rx="4" fill="#161b22" stroke="{BORDER}"/>')
            body.append(
                f'    <text class="chp" x="{cx + cw / 2:.1f}" y="{chip_y}" '
                f'text-anchor="middle">{esc(chip)}</text>')
            cx += cw + 6
        body.append("  </g>")
        parts.append("\n".join(body))

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"
     font-family="{MONO}" role="img" aria-label="Projects: blockchain certificate verification, StudyNotion EdTech platform, this profile">
  <style>
    text {{ font-family: {MONO}; }}
    .row {{ opacity: 0; animation: rise .5s cubic-bezier(.2,.7,.3,1) both 1; }}
    .cmd {{ font-size: 15px; fill: {TEXT}; }}
    .idx {{ font-size: 10px; fill: {MUTED}; letter-spacing: .12em; }}
    .ttl {{ font-size: {TITLE_PX}px; font-weight: 600; }}
    .dsc {{ font-size: {DESC_PX}px; fill: {MUTED}; }}
    .chp {{ font-size: {CHIP_PX}px; fill: {TEXT}; }}
    .cursor {{ animation: blink 1.1s steps(1) infinite; }}
    @keyframes rise {{
      from {{ opacity: 0; transform: translateY(10px); }}
      to   {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes blink {{ 0%, 49% {{ opacity: 1 }} 50%, 100% {{ opacity: 0 }} }}
    @media (prefers-reduced-motion: reduce) {{
      .row, .cursor {{ animation: none !important; opacity: 1 !important;
                       transform: none !important; }}
    }}
  </style>
{window_chrome(W, H, "projects.sh")}
  <text class="cmd row" x="{PAD}" y="58" style="animation-delay:.1s"><tspan fill="{ACCENT}">$</tspan> ls -la projects/<tspan class="cursor" fill="{ACCENT}"> _</tspan></text>
  <text class="cmd row" x="{W - PAD}" y="58" text-anchor="end" fill="{MUTED}"
        style="animation-delay:.2s">{len(PROJECTS)} items</text>
  <line class="row" x1="{PAD}" y1="70" x2="{W - PAD}" y2="70" stroke="{BORDER}"
        style="animation-delay:.28s"/>
{chr(10).join(parts)}
</svg>
'''
    OUT.write_text(svg)
    print(f"wrote {OUT} ({len(svg)} bytes) — {len(PROJECTS)} cards, "
          f"title {TITLE_CH}ch, desc {DESC_CH}ch")


if __name__ == "__main__":
    main()
