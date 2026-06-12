# Redstone University — Render Style Guide

The single reference for how course images look and how they're produced.
Pipeline: `python3 scripts/shots.py <shot>` (see `renders/shots.json`).

## Views

Every circuit gets up to two renders:

| View | Purpose | Camera | Lighting | Tonemap | Bloom |
| :-- | :-- | :-- | :-- | :-- | :-- |
| `iso` | build-step / diagram images in lessons | orthographic, 35.26° elevation, azimuth per shot, margin 1.3 | bright with defined soft shadow (shadows are load-bearing for multi-level dust legibility) | Standard | off |
| `beauty` | module hero shots, part openers | perspective, 28° elevation | warm sun, soft shadows | AgX Punchy | on |

## The locked look (decided 2026-06-12)

- **Outlines: silhouettes+borders only** (`--outline sil`, the default). Crease
  outlines are inconsistent on MiEx's merged geometry — per-block separation is
  the texture grid's job (`--grid on`, default). Outline width auto-scales with
  zoom so large builds don't read heavy.
- **Dust: generated vector wires** (`--dust vector`, the default). MiEx dust
  geometry is used only as data (positions + power); wires are rebuilt from the
  connection graph. Dark red = idle, brighter red = live signal (real power
  levels from the save). `--dust power` for the 0-15 ramp.
- **Component states**: lit torches/lamps/repeaters/comparators glow; off/unlit
  variants never do.
- **Toon modes** (`--toon unlit|cel`) exist but are not the course default.

## Redstone dust

Rendered **schematic, not realistic** (`--dust solid`, the default): clean
constant-width strokes with rounded junction dots, shadeless so lighting can
never wash them out.

- unpowered = matte dark red
- powered = vivid red with a slight glow
- `--dust power` = color ramp by signal strength 0–15 (use for the signal-decay
  lesson in Module 0)
- stroke width (4/16 block) and dot size (6/16) are set in the texture
  generator; regenerate via the snippet in git history if taste changes

## Build materials (course standard)

- **Platforms / structure:** white concrete (flat, matte — dust traces read
  like ink on it). Light gray concrete where white glares.
- **Wiring lanes:** colored concrete, one color per signal role, consistent
  across all modules:
  - TODO(fielding): lock the lane palette — current lab uses pink, blue,
    purple, dark red; assign semantics (A bus / B bus / control / output)
- **Ground:** sand / smooth sandstone reads like blueprint paper in renders.
- Legacy builds in other blocks don't need rebuilding: add a `swap` to the
  shot, e.g. `--swap white_wool=white_concrete` (render-time retexture only).

## Emissive blocks

Torches, lit lamps, glowstone etc. emit real light and bloom in `beauty`.
Lamps/dust only glow if they were POWERED when the world was saved — set the
circuit to the state the lesson needs, then exit the world, then export.

## Operational rules

1. Bedrock writes saves to disk **only on world exit** — leave the world
   before exporting or you export stale data.
2. Close the MiEx GUI while `shots.py` runs (one process may hold the world's
   LevelDB lock).
3. `~/apps/MiEx/MiEx.jar` is locally patched (region bounds via CLI);
   stock jar backed up as `MiEx.jar.orig`. Re-apply the patch after any MiEx
   update (see tix ru-7778b0 for details).
4. Choosing looks: `python3 scripts/sweep.py <shot> --sweep style|angle`
   renders a labeled contact sheet; pick by ID, record the choice in
   `shots.json`.
