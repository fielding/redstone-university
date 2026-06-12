#!/usr/bin/env python3
"""
Render a matrix of look variants for one shot and composite a labeled contact
sheet, so the course style can be chosen by eye instead of guessed.

Usage:
    python3 scripts/sweep.py <shot-name> [--sweep style|angle] [--view beauty|iso]

Uses the cached USD in renders/usd/<shot>.usd (run scripts/shots.py <shot>
--export-only first if it doesn't exist). Draft quality: 640px, 32 samples.
Output: renders/out/<shot>_sweep_<kind>.png
"""

import argparse
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USD_CACHE = os.path.join(REPO, "renders", "usd")
OUT = os.path.join(REPO, "renders", "out")
RENDER_SCRIPT = os.path.join(REPO, "scripts", "render_usd.py")

# (variant id, human label, extra render_usd.py args)
STYLE_VARIANTS = [
    ("A1", "flat light / standard",          ["--lighting", "flat", "--transform", "standard", "--glare", "off"]),
    ("A2", "flat light / standard + glow",   ["--lighting", "flat", "--transform", "standard", "--glare", "on"]),
    ("A3", "flat light / punchy",            ["--lighting", "flat", "--transform", "punchy", "--glare", "off"]),
    ("B1", "sun / punchy + glow (current)",  ["--lighting", "sun", "--transform", "punchy", "--glare", "on"]),
    ("B2", "sun / standard + glow",          ["--lighting", "sun", "--transform", "standard", "--glare", "on"]),
    ("B3", "sun / agx + glow",               ["--lighting", "sun", "--transform", "agx", "--glare", "on"]),
    ("B4", "sun / filmic + glow",            ["--lighting", "sun", "--transform", "filmic", "--glare", "on"]),
    ("B5", "sun / punchy, no glow",          ["--lighting", "sun", "--transform", "punchy", "--glare", "off"]),
]

ANGLE_VARIANTS = [
    (f"Z{int(az):03d}", f"azimuth {int(az)}", ["--azimuth", str(az)])
    for az in (0, 45, 90, 135, 180, 225, 270, 315)
] + [
    ("E20", "elevation 20 (low)", ["--elevation", "20"]),
    ("E35", "elevation 35 (iso)", ["--elevation", "35.264"]),
    ("E55", "elevation 55 (high)", ["--elevation", "55"]),
    ("E75", "elevation 75 (top-down)", ["--elevation", "75"]),
]


def render_variant(usd, vid, extra, view, workdir):
    args = ["blender", "-b", "-P", RENDER_SCRIPT, "--", usd,
            "--out", workdir, "--name", vid, "--views", view,
            "--res", "640x480", "--samples", "32"] + extra
    r = subprocess.run(args, capture_output=True, text=True, timeout=600)
    path = os.path.join(workdir, f"{vid}_{view}.png")
    if not os.path.exists(path):
        print(r.stdout[-1500:])
        sys.exit(f"variant {vid} failed to render")
    return path


def contact_sheet(tiles, out_path, cols=4):
    pad, caption_h = 8, 26
    w, h = Image.open(tiles[0][2]).size
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (w + pad) + pad, rows * (h + caption_h + pad) + pad), (24, 24, 28))
    draw = ImageDraw.Draw(sheet)
    for i, (vid, label, path) in enumerate(tiles):
        cx = pad + (i % cols) * (w + pad)
        cy = pad + (i // cols) * (h + caption_h + pad)
        img = Image.open(path).convert("RGBA")
        bg = Image.new("RGBA", img.size, (40, 40, 46, 255))
        bg.alpha_composite(img)
        sheet.paste(bg.convert("RGB"), (cx, cy))
        draw.text((cx + 4, cy + h + 5), f"{vid}  {label}", fill=(235, 235, 235))
    sheet.save(out_path)
    return out_path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("name")
    p.add_argument("--sweep", choices=["style", "angle"], default="style")
    p.add_argument("--view", default="beauty")
    a = p.parse_args()

    usd = os.path.join(USD_CACHE, f"{a.name}.usd")
    if not os.path.exists(usd):
        sys.exit(f"No cached USD at {usd} — run: python3 scripts/shots.py {a.name} --export-only")

    variants = STYLE_VARIANTS if a.sweep == "style" else ANGLE_VARIANTS
    workdir = os.path.join(OUT, f"_sweep_{a.name}_{a.sweep}")
    os.makedirs(workdir, exist_ok=True)

    tiles = []
    for vid, label, extra in variants:
        print(f"rendering {vid}: {label}")
        tiles.append((vid, label, render_variant(usd, vid, extra, a.view, workdir)))

    out_path = os.path.join(OUT, f"{a.name}_sweep_{a.sweep}.png")
    contact_sheet(tiles, out_path)
    print(f"contact sheet: {out_path}")


if __name__ == "__main__":
    main()
