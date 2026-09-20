#!/usr/bin/env python3
"""Render the portrait as ASCII art inside an animated SVG.

Each row of characters sits in its own horizontal clip whose width animates
from 0 to full, so the portrait types itself in line by line like a terminal
drawing it. Rows start on a stagger; the whole reveal finishes in under three
seconds and then freezes.

Source precedence:
  1. assets/portrait.txt  - a pre-rendered character grid (what ships here)
  2. assets/portrait.png  - a prepped photo from scripts/prep_photo.py
  3. a built-in DJ monogram placeholder, so the README is never broken
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from theme import ACCENT, BLUE, MAGENTA, MONO, MUTED, window_chrome

ROOT = Path(__file__).resolve().parents[1]
SRC_TXT = ROOT / "assets" / "portrait.txt"
SRC_IMG = ROOT / "assets" / "portrait.png"
OUT = ROOT / "divesh-ascii.svg"

W, H = 370, 520
PAD_X, TOP = 12, 42                 # drawing box sits below the 30px title bar
BOX_W, BOX_H = W - 2 * PAD_X, H - TOP - 16
COLS = 64
MONO_ASPECT = 0.55                  # advance width / line height for a mono glyph
CELL_W = BOX_W / COLS

# Bright -> dark. A space for paper-white, '@' for the deepest shadow.
RAMP = " .`:-=+*cs#%@"

ROW_DUR = 0.34                      # how long one row takes to wipe in
ROW_STEP = 0.042                    # stagger between consecutive rows

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


def fallback_rows(rows):
    """Chunky DJ monogram - at this resolution fine detail turns to mush."""
    s = 10
    w, h = COLS * s, rows * s
    img = Image.new("L", (w, h), 255)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([s * 2, s * 2, w - s * 2, h - s * 2],
                        radius=s * 4, outline=0, width=int(s * 1.4))
    d.text((w / 2, h * 0.40), "DJ", fill=0, anchor="mm", font=_font(int(h * 0.42)))
    d.text((w / 2, h * 0.65), "< / >", fill=60, anchor="mm", font=_font(int(h * 0.13)))
    d.text((w / 2, h * 0.80), "run scripts/prep_photo.py", fill=130, anchor="mm",
           font=_font(int(h * 0.05)))
    return to_rows(img.filter(ImageFilter.GaussianBlur(s * 0.25)), rows)


def to_rows(img, rows):
    """Downsample to the character grid, then quantise onto the density ramp.

    Two things matter at 64x43. Unsharp-masking before the resize keeps the
    eyes, nostrils and jawline from averaging away, and equalising the ink
    histogram afterwards stops every mid-tone landing on the same glyph -
    which is what makes a naive ramp render look like a grey blob.
    """
    img = img.convert("L")
    img = Image.blend(img, img.filter(ImageFilter.UnsharpMask(2, 150, 3)), 0.85)
    img = img.resize((COLS, rows), Image.LANCZOS)

    ink = (255.0 - np.asarray(img, dtype=np.float32)) / 255.0   # 0 paper, 1 ink
    subject = ink > 0.02
    if subject.any():
        vals = ink[subject]
        # Rank-transform the subject's tones across the ramp's full span.
        order = vals.argsort().argsort().astype(np.float32)
        spread = np.empty_like(ink)
        spread[subject] = 0.06 + 0.94 * (order / max(1, len(vals) - 1))
        spread[~subject] = 0.0
        ink = spread

    top = len(RAMP) - 1
    return [
        "".join(RAMP[int(ink[y, x] * top + 0.5)] for x in range(COLS)).rstrip()
        for y in range(rows)
    ]


def load_rows():
    if SRC_TXT.exists():
        rows = SRC_TXT.read_text().split("\n")
        while rows and not rows[-1].strip():
            rows.pop()
        return rows, "portrait"
    if SRC_IMG.exists():
        img = Image.open(SRC_IMG)
        rows = int(round(COLS * MONO_ASPECT / (img.width / img.height)))
        return to_rows(img, max(20, min(rows, 60))), "portrait"
    return fallback_rows(50), "placeholder"


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def main():
    rows, source = load_rows()
    cell_h = BOX_H / len(rows)

    clips, texts = [], []
    for i, line in enumerate(rows):
        if not line.strip():
            continue
        y = TOP + i * cell_h
        begin = round(0.25 + i * ROW_STEP, 3)
        clips.append(
            f'<clipPath id="w{i}"><rect x="{PAD_X}" y="{y:.2f}" width="0" height="{cell_h:.2f}">'
            f'<animate attributeName="width" values="0;{BOX_W}" begin="{begin}s" '
            f'dur="{ROW_DUR}s" fill="freeze" calcMode="spline" keySplines="0.2 0.7 0.3 1" '
            f'keyTimes="0;1"/></rect></clipPath>'
        )
        texts.append(
            f'<text clip-path="url(#w{i})" x="{PAD_X}" y="{y + cell_h * 0.78:.2f}" '
            f'textLength="{len(line) * CELL_W:.2f}" lengthAdjust="spacing" '
            f'xml:space="preserve">{esc(line)}</text>'
        )

    total = round(0.25 + len(rows) * ROW_STEP + ROW_DUR, 2)
    caret_y = min(TOP + len(rows) * cell_h + 14, H - 10)

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
    .caret {{ fill: {ACCENT}; font-size: 13px; animation: blink 1.1s steps(1) infinite; }}
    .cmd {{ font-size: 13px; fill: {MUTED}; }}
    @keyframes blink {{ 0%, 49% {{ opacity: 1 }} 50%, 100% {{ opacity: 0 }} }}
    @media (prefers-reduced-motion: reduce) {{ .caret {{ animation: none }} }}
  </style>
{window_chrome(W, H, "portrait.sh — ascii")}
  <text class="cmd" x="{PAD_X}" y="38"><tspan fill="{ACCENT}">$</tspan> ./render --{source} --cols {COLS}</text>
{chr(10).join(texts)}
  <text class="caret" x="{PAD_X}" y="{caret_y:.2f}">▍</text>
</svg>
'''
    OUT.write_text(svg)
    print(f"wrote {OUT} ({len(svg)} bytes) - {COLS}x{len(rows)} from {source}, "
          f"animation {total}s")


if __name__ == "__main__":
    main()
