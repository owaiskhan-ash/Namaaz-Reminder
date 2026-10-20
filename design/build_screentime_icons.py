#!/usr/bin/env python3
"""
Screen Time Reminder — web icon assets.

The Android launcher icon for Screen Time Reminder is a vector: a white clock
on an ink tile (`online.justsimpleapps.screentime`, background #0B0B0C). This
script redraws exactly that geometry for the website, so the icon in the app
collection is the same mark the phone shows.

  * docs/assets/screentime/icon-64.png    favicon / footer mark
  * docs/assets/screentime/icon-128.png   nav + app card
  * docs/assets/screentime/icon-256.png   retina app card
  * docs/assets/screentime/icon-512.png   social card

Everything is drawn at 4x and downsampled, so the curves stay smooth.

Run:  python3 design/build_screentime_icons.py
"""

from __future__ import annotations

import os

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets", "screentime")

# Matches app/src/main/res/values/ic_launcher_background.xml (#0B0B0C).
INK = (11, 11, 12, 255)
PAPER = (255, 255, 255, 255)

SIZES = (64, 128, 256, 512)
SUPERSAMPLE = 4

# The launcher vector lives on a 108 x 108 canvas; keep those coordinates.
CANVAS = 108.0
TILE_RADIUS = 24.0          # ~22% of the canvas, the Pixel/Samsung tile shape
RING_RADIUS = 25.0
RING_WIDTH = 3.2
HAND_WIDTH = 3.2


def draw_icon(size: int) -> Image.Image:
    work = size * SUPERSAMPLE
    s = work / CANVAS

    def pt(x: float, y: float) -> tuple[float, float]:
        return (x * s, y * s)

    im = Image.new("RGBA", (work, work), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # Ink tile.
    d.rounded_rectangle([0, 0, work - 1, work - 1], radius=TILE_RADIUS * s, fill=INK)

    ring_w = max(1, round(RING_WIDTH * s))
    hand_w = max(1, round(HAND_WIDTH * s))

    # Dial.
    cx, cy = 54.0, 54.0
    d.ellipse(
        [pt(cx - RING_RADIUS, cy - RING_RADIUS), pt(cx + RING_RADIUS, cy + RING_RADIUS)],
        outline=PAPER,
        width=ring_w,
    )

    # Hands: 12 o'clock and roughly 4 o'clock.
    d.line([pt(cx, cy), pt(cx, 40.0)], fill=PAPER, width=hand_w)
    d.line([pt(cx, cy), pt(64.5, 60.5)], fill=PAPER, width=hand_w)

    # Round the hand ends (PIL lines have square caps).
    for x, y in ((cx, 40.0), (64.5, 60.5)):
        r = HAND_WIDTH * s / 2
        d.ellipse([pt(x - r / s, y - r / s), pt(x + r / s, y + r / s)], fill=PAPER)

    # Pin.
    pin = 2.6
    d.ellipse([pt(cx - pin, 52.8 - pin), pt(cx + pin, 52.8 + pin)], fill=PAPER)

    return im.resize((size, size), Image.LANCZOS)


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    for size in SIZES:
        path = os.path.join(OUT, f"icon-{size}.png")
        draw_icon(size).save(path, optimize=True)
        print(f"wrote {os.path.relpath(path, ROOT)}")


if __name__ == "__main__":
    main()
