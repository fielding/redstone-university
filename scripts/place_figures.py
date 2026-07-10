#!/usr/bin/env python3
"""
Declarative figure placement: sync pipeline outputs into the course tree.

Each entry in renders/diagrams.json / renders/shots.json may carry a "place"
key mapping its rendered output(s) to the committed image path(s) under src/.
Running this after a rebuild makes renderer fixes retroactively apply to every
placed figure — placement stops being a hand-copy.

    diagrams.json entry:  "place": "src/<module>/images/<name>_circuitverse"
                          (copies .png and .svg; extension-less destination)
    shots.json entry:     "place": {"iso": "src/<module>/images/x.png",
                                    "top": "src/<module>/images/y.png"}

Usage:
    python3 scripts/place_figures.py            # copy everything that exists
    python3 scripts/place_figures.py --check    # report, change nothing
                                                # (exit 1 if anything is stale)

A source that hasn't been rendered locally is reported and skipped — Minecraft
shots only rebuild on the machine that has the worlds and MiEx.
"""
import argparse
import filecmp
import json
import os
import shutil
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(rel):
    with open(os.path.join(REPO, rel)) as f:
        return json.load(f)


def pairs():
    """Yield (source_abs, dest_abs) for every placed figure."""
    diagrams = load("renders/diagrams.json")
    # generator outputs (--gate-intros, --seg-labeled, ...): source and dest
    # filenames are explicit and identical in basename, png+svg
    for name, dest in diagrams.get("_generated", {}).items():
        for ext in (".png", ".svg"):
            yield (os.path.join(REPO, "renders/cv-out", name + ext),
                   os.path.join(REPO, dest + ext))
    for key, entry in diagrams.items():
        if key in ("_defaults", "_generated") or not isinstance(entry, dict):
            continue
        place = entry.get("place")
        if not place:
            continue
        name = entry.get("name", key)
        dests = place if isinstance(place, list) else [place]
        for dest in dests:
            for ext in (".png", ".svg"):
                yield (os.path.join(REPO, "renders/cv-out", name + ext),
                       os.path.join(REPO, dest + "_circuitverse" + ext))

    shots = load("renders/shots.json")
    for key, entry in shots.items():
        if key == "_defaults" or not isinstance(entry, dict):
            continue
        place = entry.get("place")
        if not place:
            continue
        for view, dest in place.items():
            yield (os.path.join(REPO, "renders/out", f"{key}_{view}.png"),
                   os.path.join(REPO, dest))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="report without copying; exit 1 if stale")
    a = ap.parse_args()

    copied, stale, missing, ok = [], [], [], []
    for src, dest in pairs():
        rel_s = os.path.relpath(src, REPO)
        rel_d = os.path.relpath(dest, REPO)
        if not os.path.exists(src):
            missing.append(rel_s)
            continue
        same = os.path.exists(dest) and filecmp.cmp(src, dest, shallow=False)
        if same:
            ok.append(rel_d)
        elif a.check:
            stale.append(rel_d)
        else:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(src, dest)
            copied.append(rel_d)

    if copied:
        print(f"placed {len(copied)}:")
        for d in copied:
            print(f"  {d}")
    if stale:
        print(f"STALE {len(stale)} (source differs from placed copy):")
        for d in stale:
            print(f"  {d}")
    if missing:
        print(f"skipped {len(missing)} (no local render):")
        for s in missing:
            print(f"  {s}")
    print(f"up to date: {len(ok)}")
    if a.check and stale:
        sys.exit(1)


if __name__ == "__main__":
    main()
