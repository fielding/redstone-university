#!/usr/bin/env python3
"""
One-command screenshot pipeline: Bedrock world -> MiEx (headless) -> Blender -> PNGs.

Usage:
    python3 scripts/shots.py <shot-name> [...]   # export + render named shots
    python3 scripts/shots.py --all               # everything in renders/shots.json
    python3 scripts/shots.py <shot> --render-only    # skip MiEx, reuse last USD
    python3 scripts/shots.py <shot> --export-only    # just produce the USD
    python3 scripts/shots.py <shot> --packs A,B,C    # override resource packs
    python3 scripts/shots.py <shot> --azimuth 135    # override camera azimuth

Shots are defined in renders/shots.json:
    {
      "7segment": {
        "world": "/path/to/world/folder",
        "bounds": [minX, minY, minZ, maxX, maxY, maxZ],
        "views": ["iso", "beauty"],          // optional, default both
        "azimuth": 45,                        // optional
        "out": "src/Part-I--Foundations/04_Decoders-and-Displays/images"  // optional
      }
    }

Reminder: Bedrock saves to disk only on world exit. Leave the world in-game
before running this, or you will export stale data.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS_FILE = os.path.join(REPO, "renders", "shots.json")
USD_CACHE = os.path.join(REPO, "renders", "usd")
DEFAULT_OUT = os.path.join(REPO, "renders", "out")
MIEX_JAR = os.path.expanduser("~/apps/MiEx/MiEx.jar")
MIEX_DIR = os.path.dirname(MIEX_JAR)
RENDER_SCRIPT = os.path.join(REPO, "scripts", "render_usd.py")

DEFAULT_PACKS = ["UsdPreviewSurface", "BlenderCycles", "base_resource_pack"]


def load_shots():
    """
    Returns (shots, defaults). Every shot inherits the optional settings in
    the special "_defaults" entry (views, azimuth, swap, margin, ...) unless
    it overrides them itself.
    """
    if not os.path.exists(SHOTS_FILE):
        sys.exit(f"No shots file at {SHOTS_FILE} — create it first (see scripts/shots.py docstring).")
    with open(SHOTS_FILE) as f:
        data = json.load(f)
    defaults = data.pop("_defaults", {})
    return {name: {**defaults, **shot} for name, shot in data.items()}, defaults


def check_no_gui():
    """MiEx GUI and CLI can't open the same world: LevelDB allows one lock holder."""
    r = subprocess.run(["pgrep", "-f", "MiEx.jar"], capture_output=True)
    if r.returncode == 0:
        sys.exit("MiEx GUI is running — close it first (it holds the world's database lock).")


def export_usd(name, shot, packs):
    """Drive MiEx in CLI mode to export the shot's region to a USD."""
    check_no_gui()
    os.makedirs(USD_CACHE, exist_ok=True)
    usd_path = os.path.join(USD_CACHE, f"{name}.usd")
    b = shot["bounds"]
    if len(b) != 6:
        sys.exit(f"{name}: bounds must be [minX, minY, minZ, maxX, maxY, maxZ]")
    # Requires the locally patched MiEx.jar (see MiEx.jar.orig for the stock
    # release): upstream exp-23 has two bugs that make applyExportSettings
    # ignore region bounds entirely — it passes the wrong JSON object to
    # ExportBounds.fromJson, and its reflection never matches primitive
    # int/float/boolean fields.
    region = {
        "Region 1": {
            "minX": b[0], "minY": b[1], "minZ": b[2],
            "maxX": b[3], "maxY": b[4], "maxZ": b[5],
            "offsetX": (b[0] + b[3]) // 2,
            "offsetY": b[1],
            "offsetZ": (b[2] + b[5]) // 2,
        }
    }
    commands = [
        {"command": "loadWorld", "world": shot["world"], "loadWorldResourcePacks": False},
        {"command": "loadDimension", "dimension": shot.get("dimension", "overworld")},
        {"command": "setActiveResourcePacks", "resourcePacks": packs},
        {"command": "applyExportSettings", "settings": {
            "exportRegions": region,
            "chunkSize": shot.get("chunkSize", 16),
            # merged geometry reads as one body in renders; keep blocks
            # individual so images work as build instructions ("optimise":
            # true per-shot for very large builds if export size hurts)
            "runOptimiser": shot.get("optimise", False),
        }},
        {"command": "export", "path": usd_path},
        {"command": "quit"},
    ]
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(commands, f)
        cmd_file = f.name

    print(f"[{name}] exporting via MiEx CLI -> {usd_path}")
    result = subprocess.run(
        ["java", "-jar", MIEX_JAR, "-cli", "-commandFile", cmd_file],
        cwd=MIEX_DIR, capture_output=True, text=True, timeout=600,
    )
    os.unlink(cmd_file)
    errors = [l for l in (result.stdout + result.stderr).splitlines()
              if "[COMMAND] {\"error" in l or "Exception" in l]
    for line in errors[:5]:
        print(f"[{name}]   MiEx: {line}")
    if not os.path.exists(usd_path):
        sys.exit(f"[{name}] export failed — no USD produced. Run with the GUI open to debug,"
                 f" or check {MIEX_DIR}/log.txt")
    chunks_dir = usd_path[:-4] + "_chunks"
    chunk_bytes = sum(os.path.getsize(os.path.join(chunks_dir, c))
                      for c in os.listdir(chunks_dir)) if os.path.isdir(chunks_dir) else 0
    if chunk_bytes < 1000:
        sys.exit(f"[{name}] export is EMPTY ({chunk_bytes} bytes of chunks). Causes: world not"
                 f" saved (exit the world in-game first), wrong bounds, or wrong world.")
    print(f"[{name}] export ok ({chunk_bytes // 1024} KB of chunk data)")
    return usd_path


def stamp_legend(png_path, legend):
    """
    Stamp a small swatch+label legend onto a rendered figure. Config: a
    per-shot "legend" object mapping label -> region hex, in display order
    (the flat legend hue — the anchor of the region's tone band). Placement
    prefers the bottom-left corner and walks the other corners if the build
    reaches into it.
    """
    from PIL import Image, ImageDraw, ImageFont

    ink = (48, 35, 30, 255)  # STYLE.md outline ink 30231e
    img = Image.open(png_path).convert("RGBA")
    w, h = img.size
    sw = max(30, round(w * 0.023))
    gap, pad = round(sw * 0.45), round(sw * 0.55)
    margin = sw
    font = ImageFont.truetype(
        os.path.expanduser("~/Library/Fonts/YoungSerif-Regular.ttf"),
        round(sw * 0.80))
    draw = ImageDraw.Draw(img)

    items, x = [], 0
    for label, hexcol in legend.items():
        rgb = tuple(int(hexcol[i:i + 2], 16) for i in (0, 2, 4))
        items.append((x, label, rgb))
        x += sw + gap + draw.textlength(label, font=font) + pad * 2
    row_w, row_h = x - pad * 2, sw

    def corner_free(rx, ry):
        box = img.crop((int(rx), int(ry),
                        int(min(w, rx + row_w)), int(min(h, ry + row_h))))
        return box.getchannel("A").getbbox() is None

    corners = [(margin, h - margin - row_h), (margin, margin),
               (w - margin - row_w, margin),
               (w - margin - row_w, h - margin - row_h)]
    ox, oy = next((c for c in corners if corner_free(*c)), corners[0])

    for off, label, rgb in items:
        sx = ox + off
        draw.rounded_rectangle([sx, oy, sx + sw, oy + sw], radius=sw * 0.22,
                               fill=(*rgb, 255), outline=ink,
                               width=max(2, sw // 14))
        draw.text((sx + sw + gap, oy + sw / 2), label,
                  font=font, fill=ink, anchor="lm")
    img.save(png_path)


def render(name, shot, usd_path, out_dir, azimuth, views):
    args = ["blender", "-b", "-P", RENDER_SCRIPT, "--", usd_path,
            "--out", out_dir, "--name", name,
            "--views", ",".join(views)]
    if azimuth is not None:
        args += ["--azimuth", str(azimuth)]
    if shot.get("swap"):
        args += ["--swap", shot["swap"]]
    if shot.get("transparent"):
        args += ["--transparent"]
    for opt in ("margin", "elevation", "outline", "dust", "toon",
                "projection", "technical", "height-tint", "top-azimuth", "ground", "hide",
                "tint", "clip", "res", "torch-marks"):
        key = opt.replace("-", "_")
        if key in shot:
            args += [f"--{opt}", str(shot[key])]
    print(f"[{name}] rendering {', '.join(views)} -> {out_dir}")
    result = subprocess.run(args, capture_output=True, text=True, timeout=1800)
    wrote = [l for l in result.stdout.splitlines() if l.startswith("wrote ")]
    for line in wrote:
        print(f"[{name}] {line}")
    if not wrote:
        print(result.stdout[-2000:])
        sys.exit(f"[{name}] render produced no output")
    if shot.get("legend"):
        for line in wrote:
            stamp_legend(line[len("wrote "):].strip(), shot["legend"])
        print(f"[{name}] legend stamped on {len(wrote)} file(s)")


def adopt(name):
    """
    Create/update a shots.json entry from the most recent MiEx export
    (GUI or CLI) by parsing the export settings MiEx wrote to its log.
    Workflow: frame the shot in the MiEx GUI, export once anywhere, then
    `shots.py --adopt my-shot`.
    """
    log_path = os.path.join(MIEX_DIR, "log.txt")
    block, last = [], None
    with open(log_path) as f:
        for line in f:
            if line.startswith("Exporting world to"):
                block = []
            block.append(line)
            if line.startswith("Exported:"):
                last = block[:]
    if not last:
        sys.exit("No export found in MiEx log — export once (GUI is fine) first.")

    def grab(key):
        for line in last:
            s = line.strip()
            if s.startswith(key + ":"):
                return s.split(":", 1)[1].strip()
        return None

    world = grab("world")
    bounds = [int(grab(k)) for k in ("minX", "minY", "minZ", "maxX", "maxY", "maxZ")]
    shots = {}
    if os.path.exists(SHOTS_FILE):
        with open(SHOTS_FILE) as f:
            shots = json.load(f)
    entry = shots.get(name, {})
    entry.update({"world": world, "bounds": bounds})
    shots[name] = entry
    os.makedirs(os.path.dirname(SHOTS_FILE), exist_ok=True)
    with open(SHOTS_FILE, "w") as f:
        json.dump(shots, f, indent=2)
        f.write("\n")
    print(f"adopted '{name}': bounds={bounds}")
    print(f"  world: {world}")
    print("  inherits _defaults (azimuth, swap, views, ...) — override per-shot in renders/shots.json")
    print("  tip: tighten minY/maxY in renders/shots.json if the Y range is the full world")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("names", nargs="*")
    p.add_argument("--adopt", metavar="NAME",
                   help="create a shots.json entry from the most recent MiEx export")
    p.add_argument("--all", action="store_true")
    p.add_argument("--export-only", action="store_true")
    p.add_argument("--render-only", action="store_true")
    p.add_argument("--packs", help="comma-separated resource pack override")
    p.add_argument("--azimuth", type=float)
    p.add_argument("--views")
    p.add_argument("--out")
    a = p.parse_args()

    if a.adopt:
        adopt(a.adopt)
        return

    shots, _ = load_shots()
    names = list(shots.keys()) if a.all else a.names
    if not names:
        sys.exit("Name a shot or use --all. Available: " + ", ".join(shots.keys()))

    for name in names:
        if name not in shots:
            sys.exit(f"Unknown shot '{name}'. Available: " + ", ".join(shots.keys()))
        shot = shots[name]
        packs = a.packs.split(",") if a.packs else shot.get("packs", DEFAULT_PACKS)

        usd_path = os.path.join(USD_CACHE, f"{name}.usd")
        if not a.render_only:
            usd_path = export_usd(name, shot, packs)
        elif not os.path.exists(usd_path):
            sys.exit(f"[{name}] no cached USD at {usd_path}; run without --render-only first")

        if not a.export_only:
            out_dir = a.out or shot.get("out", DEFAULT_OUT)
            azimuth = a.azimuth if a.azimuth is not None else shot.get("azimuth")
            views = a.views.split(",") if a.views else shot.get("views", ["iso", "beauty"])
            render(name, shot, usd_path, out_dir, azimuth, views)


if __name__ == "__main__":
    main()
