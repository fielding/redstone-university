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
    if not os.path.exists(SHOTS_FILE):
        sys.exit(f"No shots file at {SHOTS_FILE} — create it first (see scripts/shots.py docstring).")
    with open(SHOTS_FILE) as f:
        return json.load(f)


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


def render(name, shot, usd_path, out_dir, azimuth, views):
    args = ["blender", "-b", "-P", RENDER_SCRIPT, "--", usd_path,
            "--out", out_dir, "--name", name,
            "--views", ",".join(views)]
    if azimuth is not None:
        args += ["--azimuth", str(azimuth)]
    if shot.get("swap"):
        args += ["--swap", shot["swap"]]
    for opt in ("margin", "elevation", "outline", "dust", "toon"):
        if opt in shot:
            args += [f"--{opt}", str(shot[opt])]
    print(f"[{name}] rendering {', '.join(views)} -> {out_dir}")
    result = subprocess.run(args, capture_output=True, text=True, timeout=1800)
    wrote = [l for l in result.stdout.splitlines() if l.startswith("wrote ")]
    for line in wrote:
        print(f"[{name}] {line}")
    if not wrote:
        print(result.stdout[-2000:])
        sys.exit(f"[{name}] render produced no output")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("names", nargs="*")
    p.add_argument("--all", action="store_true")
    p.add_argument("--export-only", action="store_true")
    p.add_argument("--render-only", action="store_true")
    p.add_argument("--packs", help="comma-separated resource pack override")
    p.add_argument("--azimuth", type=float)
    p.add_argument("--views")
    p.add_argument("--out")
    a = p.parse_args()

    shots = load_shots()
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
