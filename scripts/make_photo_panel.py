#!/usr/bin/env python3
"""Render the real headshot inside the terminal window chrome.

Why this exists alongside make_ascii_svg.py: a 64-column grid with a
13-step density ramp carries roughly 2,700 glyphs of information. That is
enough to read as "a person with dark curly hair and a beard" but not enough
for a likeness of one specific person - the panel is 370px wide, legible
ASCII needs ~6px per glyph, so the column count is capped long before
accuracy arrives. When the brief is "it should match my face", the honest
answer is the photograph.

The terminal framing, the title bar and the line-by-line reveal all survive;
only the pixels underneath change. The image is embedded as a data URI
because GitHub renders README SVGs through <img>, which blocks external
references but allows data URIs.

Usage:  python scripts/make_photo_panel.py <photo> [--on-dark]
Output: divesh-photo.svg
"""
import base64
import io
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prep_photo import cutout, crop_head                      # noqa: E402
from theme import ACCENT, MONO, MUTED, PANEL, window_chrome    # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "divesh-photo.svg"

W, H = 370, 520
PAD_X, TOP = 12, 50
BOX_W, BOX_H = W - 2 * PAD_X, H - TOP - 16
RADIUS = 6
SUPERSAMPLE = 2                     # so it stays crisp on a HiDPI display


def build_image(src, on_dark):
    rgba = crop_head(cutout(src, allow_rembg=False))
    if on_dark:
        panel = Image.new("RGBA", rgba.size, tuple(
            int(PANEL[i:i + 2], 16) for i in (1, 3, 5)) + (255,))
        rgba = Image.alpha_composite(panel, rgba)
    flat = rgba.convert("RGB").resize(
        (BOX_W * SUPERSAMPLE, BOX_H * SUPERSAMPLE), Image.LANCZOS)
    buf = io.BytesIO()
    flat.save(buf, "JPEG", quality=88, optimize=True, progressive=True)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        raise SystemExit("usage: python scripts/make_photo_panel.py <photo> [--on-dark]")
    src = Path(args[0])
    if not src.exists():
        raise SystemExit(f"no such file: {src}")

    b64 = build_image(src, "--on-dark" in sys.argv[1:])

    # Reveal as a top-to-bottom wipe, so it still reads as the terminal
    # painting the panel rather than an image that was simply pasted in.
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"
     font-family="{MONO}" role="img" aria-label="Photograph of Divesh Jadhav">
  <defs>
    <clipPath id="round">
      <rect x="{PAD_X}" y="{TOP}" width="{BOX_W}" height="{BOX_H}" rx="{RADIUS}"/>
    </clipPath>
    <clipPath id="wipe">
      <rect x="{PAD_X}" y="{TOP}" width="{BOX_W}" height="0">
        <animate attributeName="height" values="0;{BOX_H}" begin="0.25s" dur="0.9s"
                 fill="freeze" calcMode="spline" keySplines="0.2 0.7 0.3 1" keyTimes="0;1"/>
      </rect>
    </clipPath>
  </defs>
  <style>
    .cmd {{ font-size: 13px; fill: {MUTED}; }}
    .caret {{ fill: {ACCENT}; font-size: 13px; animation: blink 1.1s steps(1) infinite; }}
    @keyframes blink {{ 0%, 49% {{ opacity: 1 }} 50%, 100% {{ opacity: 0 }} }}
    @media (prefers-reduced-motion: reduce) {{ .caret {{ animation: none }} }}
  </style>
{window_chrome(W, H, "portrait.sh — photo")}
  <text class="cmd" x="{PAD_X}" y="38"><tspan fill="{ACCENT}">$</tspan> ./render --portrait --raw</text>
  <g clip-path="url(#wipe)">
    <image clip-path="url(#round)" x="{PAD_X}" y="{TOP}" width="{BOX_W}" height="{BOX_H}"
           preserveAspectRatio="xMidYMid slice"
           xlink:href="data:image/jpeg;base64,{b64}"
           xmlns:xlink="http://www.w3.org/1999/xlink"/>
  </g>
  <rect x="{PAD_X}" y="{TOP}" width="{BOX_W}" height="{BOX_H}" rx="{RADIUS}"
        fill="none" stroke="#30363d"/>
</svg>
'''
    OUT.write_text(svg)
    print(f"wrote {OUT} ({len(svg) // 1024} KB)")


if __name__ == "__main__":
    main()
