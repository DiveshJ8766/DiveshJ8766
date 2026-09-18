#!/usr/bin/env python3
"""Render assets/portrait.png as ASCII art inside an animated SVG.

Each row of characters sits in its own horizontal clip, and the clip's width
animates from 0 to full — so the portrait types itself in line by line,
exactly like a terminal drawing it. Rows start on a stagger; the whole thing
is done in under three seconds and then freezes.

If no prepped portrait exists yet, a built-in geometric placeholder (a React
atom over a DJ monogram) is used instead, so the README is never broken.
"""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from theme import ACCENT, BLUE, MAGENTA, MONO, MUTED, window_chrome

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets" / "portrait.png"
OUT = ROOT / "divesh-ascii.svg"

W, H = 370, 480
PAD_X, TOP = 12, 42            # drawing box: below the 30px title bar
BOX_W, BOX_H = W - 2 * PAD_X, H - TOP - 16      # 346 x 422
COLS = 76
MONO_ASPECT = 0.55             # advance width / line height for a mono glyph

CELL_W = BOX_W / COLS
CELL_H = CELL_W / MONO_ASPECT
ROWS = int(BOX_H // CELL_H)

# Bright -> dark. A space for paper-white, '@' for the deepest shadow.
RAMP = " .`:-=+*cs#%@"

ROW_DUR = 0.34                 # how long one row takes to wipe in
ROW_STEP = 0.042               # stagger between consecutive rows


FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "C:/Windows/Fonts/arialbd.ttf",
]


def _font(px):
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, px)
            except OSError:
                pass
    return ImageFont.load_default(size=px)


def fallback_image():
    """Legible stand-in until a prepped portrait exists: a big DJ monogram.

    Deliberately chunky - at 76x50 characters, fine detail turns to mush, so
    the placeholder is bold type inside a frame rather than clever art.
    """
    s = 10
    w, h = COLS * s, ROWS * s
    img = Image.new("L", (w, h), 255)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([s * 2, s * 2, w - s * 2, h - s * 2],
                        radius=s * 4, outline=0, width=int(s * 1.4))
    d.text((w / 2, h * 0.40), "DJ", fill=0, anchor="mm", font=_font(int(h * 0.42)))
    d.text((w / 2, h * 0.65), "< / >", fill=60, anchor="mm", font=_font(int(h * 0.13)))
    d.text((w / 2, h * 0.80), "run scripts/prep_photo.py", fill=130, anchor="mm",
           font=_font(int(h * 0.05)))
    return img.filter(ImageFilter.GaussianBlur(s * 0.25))


def to_rows(img):
    img = img.convert("L").resize((COLS, ROWS), Image.LANCZOS)
    px = img.load()
    out = []
    for y in range(ROWS):
        line = []
        for x in range(COLS):
            idx = int((255 - px[x, y]) / 255 * (len(RAMP) - 1) + 0.5)
            line.append(RAMP[idx])
        out.append("".join(line).rstrip())
    return out


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def main():
    img = Image.open(SRC) if SRC.exists() else fallback_image()
    source = "portrait" if SRC.exists() else "placeholder"
    rows = to_rows(img)

    clips, texts = [], []
    for i, line in enumerate(rows):
        if not line:
            continue
        y = TOP + i * CELL_H
        begin = round(0.25 + i * ROW_STEP, 3)
        clips.append(
            f'<clipPath id="w{i}"><rect x="{PAD_X}" y="{y:.2f}" width="0" height="{CELL_H:.2f}">'
            f'<animate attributeName="width" from="0" to="{BOX_W}" begin="{begin}s" '
            f'dur="{ROW_DUR}s" fill="freeze" calcMode="spline" keySplines="0.2 0.7 0.3 1" '
            f'keyTimes="0;1" values="0;{BOX_W}"/></rect></clipPath>'
        )
        texts.append(
            f'<text clip-path="url(#w{i})" x="{PAD_X}" y="{y + CELL_H * 0.78:.2f}" '
            f'textLength="{len(line) * CELL_W:.2f}" lengthAdjust="spacing" '
            f'xml:space="preserve">{esc(line)}</text>'
        )

    total = round(0.25 + len(rows) * ROW_STEP + ROW_DUR, 2)
    caret_y = TOP + len(rows) * CELL_H

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"
     font-family="{MONO}" role="img" aria-label="ASCII portrait of Divesh Jadhav">
  <defs>
    <linearGradient id="ink" x1="0" y1="0" x2="0.35" y2="1">
      <stop offset="0%" stop-color="{ACCENT}"/>
      <stop offset="55%" stop-color="{BLUE}"/>
      <stop offset="100%" stop-color="{MAGENTA}"/>
    </linearGradient>
{chr(10).join(clips)}
  </defs>
  <style>
    text {{ font-family: {MONO}; font-size: {CELL_W / 0.6:.2f}px; fill: url(#ink); }}
    .caret {{ fill: {ACCENT}; font-size: 11px; animation: blink 1.1s steps(1) infinite; }}
    .cmd {{ font-size: 11px; fill: {MUTED}; }}
    @keyframes blink {{ 0%, 49% {{ opacity: 1 }} 50%, 100% {{ opacity: 0 }} }}
    @media (prefers-reduced-motion: reduce) {{ .caret {{ animation: none }} }}
  </style>
{window_chrome(W, H, "portrait.sh — ascii")}
  <text class="cmd" x="{PAD_X}" y="38"><tspan fill="{ACCENT}">$</tspan> ./render --{source} --cols {COLS}</text>
{chr(10).join(texts)}
  <text class="caret" x="{PAD_X}" y="{min(caret_y + 14, H - 10):.2f}">▍</text>
</svg>
'''
    OUT.write_text(svg)
    print(f"wrote {OUT} ({len(svg)} bytes) - {COLS}x{ROWS} from {source}, "
          f"animation {total}s")


if __name__ == "__main__":
    main()
