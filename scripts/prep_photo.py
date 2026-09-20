#!/usr/bin/env python3
"""Turn a raw headshot into something an ASCII ramp can actually read.

The hard part is the mask. A ramp only has ~13 density steps, so any
background that survives gets quantised into noise that reads as texture on
the subject's shoulders. Two strategies, in order:

  1. rembg, if it happens to be installed (best on busy backgrounds)
  2. flat-backdrop chroma key in LAB space - samples the border, keeps the
     largest connected foreground blob, fills holes. This is what studio
     headshots on a solid colour actually need, and it needs no 200MB model.

Then CLAHE for local contrast (the thing that stops faces turning to mush),
a percentile stretch across foreground pixels only, and a pad to the panel
aspect so the ASCII grid isn't letterboxed.

Usage:  python scripts/prep_photo.py source-photo.jpg [--no-rembg]
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
MARGIN = 0.05                  # breathing room around the subject
BORDER_FRAC = 0.045            # how much of each edge counts as "backdrop"


def cutout_rembg(path):
    from rembg import remove
    return remove(Image.open(path).convert("RGBA"))


def cutout_chroma(path):
    """Key out a flat backdrop: LAB distance from the dominant border colour."""
    bgr = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if bgr is None:
        raise SystemExit(f"could not decode {path}")
    h, w = bgr.shape[:2]
    lab = cv2.cvtColor(cv2.GaussianBlur(bgr, (5, 5), 0), cv2.COLOR_BGR2LAB)

    b = max(2, int(round(min(h, w) * BORDER_FRAC)))
    ring = np.concatenate([
        lab[:b].reshape(-1, 3), lab[-b:].reshape(-1, 3),
        lab[:, :b].reshape(-1, 3), lab[:, -b:].reshape(-1, 3),
    ])
    # Median over the ring, then re-median over pixels close to it, so a bit of
    # subject bleeding into a corner doesn't drag the key colour off.
    key = np.median(ring, axis=0)
    d = np.linalg.norm(ring.astype(np.float32) - key, axis=1)
    key = np.median(ring[d < max(12.0, np.percentile(d, 70))], axis=0)

    # Chroma (a,b) separates a coloured backdrop from skin far better than L,
    # which is why a plain grey-level threshold always eats the hair.
    dist = np.linalg.norm(lab[:, :, 1:].astype(np.float32) - key[1:], axis=2)
    dl = np.abs(lab[:, :, 0].astype(np.float32) - key[0])
    thr = max(9.0, float(np.percentile(dist, 35)) + 7.0)
    fg = ((dist > thr) | (dl > 55)).astype(np.uint8)

    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, k, iterations=1)
    fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, k, iterations=3)

    n, lbl, stats, _ = cv2.connectedComponentsWithStats(fg, 8)
    if n > 1:                                  # keep the biggest blob only
        fg = (lbl == 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])).astype(np.uint8)

    holes = cv2.bitwise_not(fg * 255)          # fill anything enclosed by it
    ff = holes.copy()
    cv2.floodFill(ff, np.zeros((h + 2, w + 2), np.uint8), (0, 0), 0)
    fg = np.maximum(fg * 255, ff)

    alpha = cv2.GaussianBlur(fg, (0, 0), 1.2)
    rgba = np.dstack([cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB), alpha])
    return Image.fromarray(rgba, "RGBA")


def cutout(path, allow_rembg=True):
    if allow_rembg:
        try:
            print("mask: rembg")
            return cutout_rembg(path)
        except Exception as e:
            print(f"mask: rembg unavailable ({e.__class__.__name__}), keying backdrop")
    else:
        print("mask: chroma key (rembg skipped)")
    return cutout_chroma(path)


def crop_to_subject(rgba):
    alpha = np.array(rgba)[:, :, 3]
    ys, xs = np.where(alpha > 12)
    if len(xs) == 0:
        return rgba
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    pad_x, pad_y = int((x1 - x0) * MARGIN), int((y1 - y0) * MARGIN)
    w, h = rgba.size
    return rgba.crop((max(0, x0 - pad_x), max(0, y0 - pad_y),
                      min(w, x1 + pad_x), min(h, y1 + pad_y)))


def pad_to_aspect(rgba):
    w, h = rgba.size
    if w / h > TARGET_ASPECT:                  # too wide -> add height below
        new_h = int(round(w / TARGET_ASPECT))
        canvas = Image.new("RGBA", (w, new_h), (0, 0, 0, 0))
        canvas.paste(rgba, (0, 0))             # top-align: keeps the face high
    else:                                      # too tall -> add width evenly
        new_w = int(round(h * TARGET_ASPECT))
        canvas = Image.new("RGBA", (new_w, h), (0, 0, 0, 0))
        canvas.paste(rgba, ((new_w - w) // 2, 0))
    return canvas


def boost_contrast(rgba):
    white = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    flat = Image.alpha_composite(white, rgba).convert("L")
    arr = np.array(flat)
    mask = np.array(rgba)[:, :, 3] >= 12       # subject pixels

    arr = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8)).apply(arr)

    # Stretch across the subject only. Done over the whole frame the white
    # background pins the top of the range and the face stays flat.
    if mask.any():
        lo, hi = np.percentile(arr[mask], (2, 98))
        if hi > lo:
            f = arr.astype(np.float32)
            f = np.clip((f - lo) * 255.0 / (hi - lo), 0, 255)
            arr = f.astype(np.uint8)

    arr[~mask] = 255                           # ramp maps pure white to a space
    return Image.fromarray(arr)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        raise SystemExit("usage: python scripts/prep_photo.py <photo> [--no-rembg]")
    src = Path(args[0])
    if not src.exists():
        raise SystemExit(f"no such file: {src}")

    rgba = cutout(src, allow_rembg="--no-rembg" not in sys.argv[1:])
    out = boost_contrast(pad_to_aspect(crop_to_subject(rgba)))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.save(OUT)
    print(f"wrote {OUT} ({out.size[0]}x{out.size[1]})")


if __name__ == "__main__":
    main()
