#!/usr/bin/env python3
"""Compose the M4 7-segment figure from its four per-panel shots.

Each panel is shot separately (own centered camera — no cross-frame
parallax), alpha-trimmed, height-matched (closeup at half height), and
stitched onto a transparent canvas. Re-render the 7seg-* shots, then run
this; output lands in renders/out/7-segment-display_composed.png.
"""
from PIL import Image
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, 'renders/out')

def trim(im):
    return im.crop(im.getchannel('A').getbbox())

names = ['7seg-8', '7seg-wall', '7seg-lit', '7seg-closeup']
MIRROR = {'7seg-lit', '7seg-closeup'}   # shot from az315; mirroring restores
panels = []                              # the az135 stagger, faces stay front
for n in names:
    p = trim(Image.open(os.path.join(OUT, f'{n}_iso.png')).convert('RGBA'))
    if n in MIRROR:
        p = p.transpose(Image.FLIP_LEFT_RIGHT)
    panels.append(p)
H = max(p.height for p in panels[:3])
scaled = []
for i, p in enumerate(panels):
    h = H if i < 3 else int(H * 0.5)
    scaled.append(p.resize((round(p.width * h / p.height), h), Image.LANCZOS))
GAP = 90
W = sum(p.width for p in scaled) + GAP * (len(scaled) - 1)
out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
x = 0
for p in scaled:
    out.paste(p, (x, H - p.height), p)
    x += p.width + GAP
dest = os.path.join(OUT, '7-segment-display_composed.png')
out.save(dest)
print('wrote', dest, out.size)
