#!/usr/bin/env python3
"""Turn a raw headshot into something an ASCII ramp can actually read.

  1. rembg strips the background so only the subject survives
  2. the alpha mask is cropped to the subject's bounding box
  3. CLAHE boosts local contrast, which is what stops faces turning into mush
  4. the result is composited onto pure white and padded to the panel aspect

Usage:  python scripts/prep_photo.py source-photo.jpg
Output: assets/portrait.png
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "portrait.png"
TARGET_ASPECT = 346 / 422      # must match make_ascii_svg.py's drawing box
MARGIN = 0.06                  # breathing room around the subject


def cutout(path):
    from rembg import remove
    img = Image.open(path).convert("RGBA")
    return remove(img)


def crop_to_subject(rgba):
    alpha = np.array(rgba)[:, :, 3]
    ys, xs = np.where(alpha > 12)
    if len(xs) == 0:
        return rgba
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    pad_x = int((x1 - x0) * MARGIN)
    pad_y = int((y1 - y0) * MARGIN)
    w, h = rgba.size
    box = (max(0, x0 - pad_x), max(0, y0 - pad_y),
           min(w, x1 + pad_x), min(h, y1 + pad_y))
    return rgba.crop(box)


def pad_to_aspect(rgba):
    w, h = rgba.size
    if w / h > TARGET_ASPECT:          # too wide -> add height
        new_h = int(round(w / TARGET_ASPECT))
        canvas = Image.new("RGBA", (w, new_h), (0, 0, 0, 0))
        canvas.paste(rgba, (0, (new_h - h) // 2))
    else:                              # too tall -> add width
        new_w = int(round(h * TARGET_ASPECT))
        canvas = Image.new("RGBA", (new_w, h), (0, 0, 0, 0))
        canvas.paste(rgba, ((new_w - w) // 2, 0))
    return canvas


def boost_contrast(rgba):
    white = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    flat = Image.alpha_composite(white, rgba).convert("L")
    arr = np.array(flat)
    clahe = cv2.createCLAHE(clipLimit=2.6, tileGridSize=(8, 8))
    arr = clahe.apply(arr)
    # Keep the removed background pure white so the ramp maps it to a space.
    mask = np.array(rgba)[:, :, 3] < 12
    arr[mask] = 255
    return Image.fromarray(arr)


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: python scripts/prep_photo.py <photo>")
    src = Path(sys.argv[1])
    if not src.exists():
        raise SystemExit(f"no such file: {src}")

    rgba = pad_to_aspect(crop_to_subject(cutout(src)))
    out = boost_contrast(rgba)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.save(OUT)
    print(f"wrote {OUT} ({out.size[0]}x{out.size[1]})")


if __name__ == "__main__":
    main()
