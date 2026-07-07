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
  across all modules. PROPOSED 2026-07-06 (Claude default, veto before first
  canonical figure ships):
  - **blue concrete** = A operand / primary data
  - **purple concrete** = B operand / secondary data
  - **pink concrete** = control (strobes, selects, enables)
  - **red concrete** (dark) = output / result
  Rationale: matches the operand colors readers meet in the module-legend
  treatment (registers dusty-blue feed A; RAM rose is adjacent to purple), and
  control-pink stays visually distinct from signal-red dust.
- **Ground:** sand / smooth sandstone reads like blueprint paper in renders.
- Legacy builds in other blocks don't need rebuilding: add a `swap` to the
  shot, e.g. `--swap white_wool=white_concrete` (render-time retexture only).

## Composition legend treatment (decided 2026-07-06)

For shots that compose large components into one build (the capstone machine,
decoder/encoder assemblies), the module regions carry the color and everything
else goes quiet. Opt-in per shot — never a default:

```json
"height_tint": 0,          // uniform paper structure (height bands OFF —
                           // they fight the legend for the color channel)
"tint": "<annotation blocks mapped to region hues>"
```

Region hues are the course gate-fill pastels one step deeper (structure stays
paper `f5f1ea`, outlines ink `30231e`):

| Module region | Hex | Family |
| :-- | :-- | :-- |
| Registers | `a8c4d6` | dusty-blue (OR) |
| RAM / ROM | `e4b0ab` | rose (NOT) |
| ALU | `f2d489` | amber (XOR) |
| Control | `aecf9c` | sage (AND) |
| Clock | `ddd5a0` | olive |
| Display / I/O | `f0bd94` | peach |
| Bus | `30231e` | ink |
| unmapped annotation blocks | `f5f1ea` | paper |

Tint keys are block-name substrings (longest wins); redstone components are
never overridden. Add `"clip"` to cut a single bit-slice for a top-down
"schematic view" of a stacked build. The canonical-* shots in `shots.json`
show the lane-tint variant of the same mechanism.

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
3b. `MIEX_OFFLINE_MODE=1` is set in `~/apps/MiEx/miex.env` — MiEx's startup
   GitHub check hangs indefinitely when rate-limited (symptom: CLI export
   times out at 600s with log.txt stuck on "Searching for built-in files in
   GitHub repositories"). Keep it set; batch exports launch MiEx dozens of
   times and will trip the rate limit.
4. Choosing looks: `python3 scripts/sweep.py <shot> --sweep style|angle`
   renders a labeled contact sheet; pick by ID, record the choice in
   `shots.json`.
