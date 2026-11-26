#!/usr/bin/env python3
"""
live3d_qa.py — does each live 3D figure show the same circuit as its book PNG?

A live figure replaces a placed *_minecraft.png on the site, so it must agree
with the image (and the caption written against it). The renderer reproduces
the Blender look closely; what drifts is the DATA: a book PNG rendered from an
older export can show other lever positions, other powered wires, or another
block layout than the build in today's USD cache.

For every published figure this compares the live render (viewer/snap.mjs
--placed) with the book PNG on two signals:

  wires   the dust/torch state, cell by cell on a coarse grid: in how many
          cells that carry redstone in both images does one show it powered
          and the other unpowered
  layout  overlap (IoU) of the two silhouettes, each in its own box
  jump    how far the build's box moves between the PNG and the live frame
          (the canvas replaces the image in place)

and writes renders/live3d-qa.json. Figures over the thresholds are proposed
for renders/live3d-hold.json, which `usd_to_scene.py --publish` honors: held
figures stay static images on the site until the book PNG or the build is
brought back in line.

    node viewer/snap.mjs --placed --out-dir renders/out-three/placed
    python3 scripts/live3d_qa.py [--renders renders/out-three/placed] [--write-hold]
"""
import json
import os
import sys

from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS = os.path.join(REPO, "renders", "shots.json")
REPORT = os.path.join(REPO, "renders", "live3d-qa.json")
HOLD = os.path.join(REPO, "renders", "live3d-hold.json")

GRID = (96, 72)          # wire cells: ~1/3 block on the largest figures, so a missing column registers
MASK = (192, 144)        # silhouette resolution
WIRE_MISMATCH_MAX = 0.12  # fraction of shared wire cells that disagree
LAYOUT_IOU_MIN = 0.92
JUMP_MAX = 0.05           # build box shift at the PNG -> live swap, as a fraction of the frame
WIRE_PRESENCE_MAX = 0.10  # fraction of redstone cells with no counterpart nearby


def classify(path):
    """Per-pixel classes on the figure: powered redstone (bright red),
    unpowered redstone (deep red), and the silhouette."""
    im = Image.open(path).convert("RGBA")
    # compare the figure area only: both PNGs are rendered at the shot res,
    # but a legend can grow the canvas downward
    w, h = im.size
    lit = Image.new("L", (w, h))
    dark = Image.new("L", (w, h))
    px = im.load()
    lp, dp = lit.load(), dark.load()
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            r, g, b, a = px[x, y]
            if a < 200:
                continue
            if r >= 200 and g <= 110 and b <= 100 and r - g >= 120:
                lp[x, y] = 255
            elif 60 <= r <= 150 and g <= 55 and b <= 55 and r >= 2 * g + 15:
                dp[x, y] = 255
    sil = im.getchannel("A").point(lambda v: 255 if v > 128 else 0)
    return im.size, lit, dark, sil


def _main_run(profile, gap):
    """Longest-mass run of non-empty entries, splitting on >= gap empties."""
    runs, start, empty = [], None, 0
    for i, v in enumerate(profile + [0] * (gap + 1)):
        if v:
            if start is None:
                start = i
            empty = 0
            end = i
        elif start is not None:
            empty += 1
            if empty >= gap:
                runs.append((start, end))
                start, empty = None, 0
    return max(runs, key=lambda r: sum(profile[r[0]:r[1] + 1])) if runs else (0, len(profile) - 1)


def build_only(sil):
    """Crop a silhouette to the build: drop the legend row (separated from the
    build by empty space) and the empty margins."""
    w, h = sil.size
    small = sil.resize((w // 4, h // 4), Image.BOX)
    sw, sh = small.size
    px = small.load()
    rows = [sum(1 for x in range(sw) if px[x, y] > 64) for y in range(sh)]
    y0, y1 = _main_run(rows, max(3, sh // 60))
    cols = [sum(1 for y in range(y0, y1 + 1) if px[x, y] > 64) for x in range(sw)]
    x0, x1 = _main_run(cols, max(3, sw // 30))
    return sil.crop((x0 * 4, y0 * 4, (x1 + 1) * 4, (y1 + 1) * 4))


def _box(sil):
    """Bounding box of the build in a silhouette (legend row excluded)."""
    w, h = sil.size
    small = sil.resize((w // 4, h // 4), Image.BOX)
    sw, sh = small.size
    px = small.load()
    rows = [sum(1 for x in range(sw) if px[x, y] > 64) for y in range(sh)]
    y0, y1 = _main_run(rows, max(3, sh // 60))
    cols = [sum(1 for y in range(y0, y1 + 1) if px[x, y] > 64) for x in range(sw)]
    x0, x1 = _main_run(cols, max(3, sw // 30))
    return (x0 * 4, y0 * 4, (x1 + 1) * 4, (y1 + 1) * 4)


def compare(book_png, live_png):
    bs, bl, bd, bsil = classify(book_png)
    ls, ll, ld, lsil = classify(live_png)
    # align by each build's own box: older book renders frame differently,
    # which is cosmetic; what must agree is what is drawn where on the build
    bb, lb = _box(bsil), _box(lsil)

    def state(lit, dark, box):
        L = list(lit.crop(box).resize(GRID, Image.BOX).get_flattened_data())
        D = list(dark.crop(box).resize(GRID, Image.BOX).get_flattened_data())
        return [None if l + d < 6 else (l > d) for l, d in zip(L, D)]

    sb, sl = state(bl, bd, bb), state(ll, ld, lb)
    shared = [(a, b) for a, b in zip(sb, sl) if a is not None and b is not None]
    wire_mismatch = (sum(1 for a, b in shared if a != b) / len(shared)) if shared else 0.0
    # redstone present in one image's cell but absent from the same cell (and
    # its neighbours, to absorb a cell of slop) in the other
    W, H = GRID

    def near(states, i):
        x, y = i % W, i // W
        return any(states[yy * W + xx] is not None
                   for yy in range(max(0, y - 1), min(H, y + 2))
                   for xx in range(max(0, x - 1), min(W, x + 2)))
    either = [i for i in range(W * H) if sb[i] is not None or sl[i] is not None]
    lonely = [i for i in either if (sb[i] is not None and not near(sl, i)) or (sl[i] is not None and not near(sb, i))]
    wire_presence = len(lonely) / len(either) if either else 0.0

    mb = [v > 127 for v in bsil.crop(bb).resize(MASK, Image.BOX).get_flattened_data()]
    ml = [v > 127 for v in lsil.crop(lb).resize(MASK, Image.BOX).get_flattened_data()]
    inter = sum(1 for a, b in zip(mb, ml) if a and b)
    union = sum(1 for a, b in zip(mb, ml) if a or b)
    iou = inter / union if union else 1.0
    # where the build sits in the frame: the live canvas replaces the PNG in
    # place, so a different framing reads as the figure jumping
    jump = max(abs(bb[i] - lb[i]) / (min(bs[0], ls[0]) if i % 2 == 0 else min(bs[1], ls[1])) for i in range(4))
    return {"wire_mismatch": round(wire_mismatch, 3), "wire_presence": round(wire_presence, 3),
            "jump": round(jump, 3),
            "wire_cells": len(shared), "layout_iou": round(iou, 3)}


def main():
    args = sys.argv[1:]
    renders = os.path.join(REPO, "renders", "out-three", "placed")
    if "--renders" in args:
        renders = args[args.index("--renders") + 1]
    shots = json.load(open(SHOTS))
    # judge every placed figure the site could use, independent of the
    # current hold list (otherwise held figures would never be re-checked)
    candidates = []
    for shot in sorted(k for k in shots if not k.startswith("_")):
        for view, dest in sorted((shots[shot].get("place") or {}).items()):
            book = os.path.join(REPO, dest)
            name = os.path.splitext(os.path.basename(dest))[0]
            module_dir = os.path.join(REPO, *dest.split("/")[:3])
            prose = "".join(open(os.path.join(module_dir, f)).read()
                            for f in ("draft.md", "introduction.md") if os.path.exists(os.path.join(module_dir, f)))
            if os.path.exists(book) and f"images/{name}.png" in prose:
                candidates.append((shot, view, book))
    results, hold = {}, {}
    for shot, view, book in candidates:
        if True:
            live = os.path.join(renders, f"{shot}_{view}.png")
            if not os.path.exists(live):
                sys.exit(f"missing live render {live} (run viewer/snap.mjs --placed --out-dir {renders})")
            r = compare(book, live)
            key = f"{shot}/{view}"
            reasons = []
            if r["wire_mismatch"] > WIRE_MISMATCH_MAX:
                reasons.append(f"redstone state differs in {r['wire_mismatch']:.0%} of shared wire cells")
            if r["wire_presence"] > WIRE_PRESENCE_MAX:
                reasons.append(f"redstone missing or extra in {r['wire_presence']:.0%} of wire cells")
            if r["jump"] > JUMP_MAX:
                reasons.append(f"build shifts {r['jump']:.0%} of the frame when the figure goes live")
            if r["layout_iou"] < LAYOUT_IOU_MIN:
                reasons.append(f"layout overlap {r['layout_iou']:.2f}")
            r["verdict"] = "hold" if reasons else "match"
            results[key] = r
            if reasons:
                hold[key] = "; ".join(reasons)
            print(f"{r['verdict']:5s}  state {r['wire_mismatch']:4.2f}  presence {r['wire_presence']:4.2f} ({r['wire_cells']:4d} cells)  "
                  f"layout {r['layout_iou']:.2f}  jump {r['jump']:.2f}  {key}")
    with open(REPORT, "w") as f:
        json.dump(results, f, indent=1, sort_keys=True)
        f.write("\n")
    print(f"\n{len(results) - len(hold)} match, {len(hold)} proposed for hold -> {os.path.relpath(REPORT, REPO)}")
    if "--write-hold" in args:
        with open(HOLD, "w") as f:
            json.dump(hold, f, indent=1, sort_keys=True)
            f.write("\n")
        print(f"wrote {os.path.relpath(HOLD, REPO)}")


if __name__ == "__main__":
    main()
