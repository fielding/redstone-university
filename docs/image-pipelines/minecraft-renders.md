# Minecraft render pipeline

Renders the **actual Redstone builds** from the Bedrock world into clean
isometric / aerial figures, in the same palette as the diagrams.

- **Orchestrator:** `scripts/shots.py` (MiEx CLI export → Blender render)
- **Renderer:** `scripts/render_usd.py` (Blender headless, USD → png)
- **Config:** `renders/shots.json`
- **Output:** `renders/out/<shot>_<view>.png` → placed as
  `src/.../images/<name>_minecraft.png`
- **World:** the mcpelauncher Bedrock world referenced by each shot's `world`.

## Pipeline at a glance

```
world (LevelDB)
   │  MiEx CLI export (bounds → USD, UsdPreviewSurface materials)
   ▼
renders/usd/<shot>.usd   (cached; git-ignored)
   │  Blender headless (render_usd.py): trim, ground-strip, palette, camera
   ▼
renders/out/<shot>_<view>.png   (git-ignored)
   │  manual: crop/compose + copy
   ▼
src/.../images/<name>_minecraft.png   (committed; referenced by draft.md)
```

## Quickstart

```bash
python3 scripts/shots.py --all                 # export + render every shot
python3 scripts/shots.py 04_2-to-4-decoder-1   # one shot (export + render)
python3 scripts/shots.py <name> --render-only  # reuse cached USD, just re-render
python3 scripts/shots.py <name> --export-only  # just re-export the USD
```

⚠️ **Close the MiEx GUI before running** — the GUI and the CLI cannot both hold
the world's LevelDB lock. `shots.py` errors clearly if the GUI is open.

## Adding a new shot

The only hard part is getting the **bounds** (the block AABB to frame). Workflow:

1. Build the thing in the world.
2. Open MiEx (`java -jar ~/apps/MiEx/MiEx.jar`), frame the region, and **export**
   it. The GUI export itself renders black (it uses MaterialX) — we don't use the
   file, we just want the bounds it logs.
3. Read the bounds from `~/apps/MiEx/log.txt` — each "Exporting world to …" block
   logs `minX minY minZ maxX maxY maxZ`. (`shots.py --adopt <name>` does this for
   the **last** export only; for several, read the log directly.)
4. Add a shot to `renders/shots.json` (schema below) with those `bounds`.
5. `python3 scripts/shots.py <name>` — re-exports via CLI (correct materials) and
   renders.
6. Eyeball `renders/out/<name>_iso.png`, then copy into `src/.../images/` and
   reference in `draft.md`.

> Tip: components in a tidy row at constant Z and even spacing can be sliced into
> per-item shots by giving each its own narrow X `bounds` (this is how the
> prelude toolkit icons were made — one shot per block column).

## `renders/shots.json` schema

Top-level `_defaults` is merged into every shot; any key can be overridden
per-shot.

```jsonc
{
  "_defaults": {
    "views": ["iso", "top"],
    "azimuth": 135,
    "swap": "white_wool=white_concrete",
    "technical": "schematic",
    "transparent": true,
    "height_tint": 0.9,
    "projection": "tele",
    "ground": "remove"
  },
  "<shot-name>": {
    "world":  "/…/minecraftWorlds/<id>",   // required
    "bounds": [minX, minY, minZ, maxX, maxY, maxZ],   // required
    "views":  ["iso"],          // override: which cameras to render
    "ground": "remove2",        // keep | remove | remove2 | crop
    "hide":   "white_wool,cobblestone",   // comma list: drop meshes by name substring
    "azimuth": 150,             // iso camera rotation
    "projection": "tele",       // tele (near-iso telephoto) | ortho
    "swap": "white_wool=white_concrete"   // material swaps
  }
}
```

### Views

- `iso` — the near-isometric telephoto hero shot (default for everything).
- `top` — straight-down aerial. Paired with `iso` for decoders/larger builds.
- `beauty` — perspective glamour shot (used rarely).

### `ground` modes (`render_usd.py --ground`)

The build usually sits on a flat base platform; these control it. `base_z` is
computed **after** stray-bedrock trimming so it's the build, not the world floor.

- `keep` — leave everything.
- `remove` — delete the lowest block layer (the platform); the build keeps its
  own base block.
- `remove2` — delete the lowest **two** layers (platform **and** the base block).
- `crop` — keep the platform only under the build's footprint (synthesized
  "pad" blocks stand in as a clean floor). Lever cells never seed pads — the
  block under/behind a lever is render noise; levers read as floating inputs.

### `torch-marks` — top-view torch legibility (default: `stroke`)

From above, a torch head is a 2-px dot that vanishes against dust strokes.
In schematic top views every redstone torch (including repeater/comparator
indicators) gets a heavy ink rim — its own Freestyle lineset at
`TORCH_STROKE_MULT` (2.5×) the base linework weight, so "rimmed dot = torch,
plain dot = dust" reads instantly. Iso views are never marked. Disable
per-shot with `"torch_marks": "off"`.

### `hide` — drop blocks by mesh name

Comma-separated substrings matched against object names; matching meshes are
removed. Used for the toolkit component icons: hide the structural blocks
(`white_wool,white_concrete,cobblestone,smooth_stone,lime_concrete`) so only the
component (lever/torch/repeater/comparator/lamp) remains. Note: a side-mounted
component (lever, wall torch) sits in the **same** layer as its block, so
`remove2` would delete it too — use `hide` for those.

### `tint` — recolor block families to legend colors

Comma-separated `block=RRGGBB` pairs matched as substrings against material
names; longest matching key wins (`light_blue_wool` beats `blue_wool`).
Matching blocks render as a flat fill in the given color — in `technical`
modes it replaces the structure fill, so tinted regions survive the schematic
restyle. Redstone components are never overridden (circuit state stays
readable). This is the module-legend mechanism: color a build's annotation
wool by major component, e.g.

```json
"tint": "blue_concrete=a8c4d6,pink_concrete=e0b6c4,red_concrete=c47a72"
```

Gotcha: in `technical` modes, structure families **not** in the tint map are
ghosted to the neutral fill by design — a colored build with no tint map
renders uniformly cream. Standalone module shots whose build speaks the color
language need their families mapped (see `renders/STYLE.md`).

### `legend` — in-image swatch+label chips

A per-shot `"legend"` object stamps a legend row onto every rendered view
(post-pass in `shots.py`, not Blender): rounded swatch per region + Young
Serif label in ink `30231e`, bottom-left corner, auto-dodging to another
corner if the build occupies it. Keys are display labels, values the flat
region hue (the tone band's anchor); order is display order.

```json
"legend": {"Adder": "f2d489", "Decoder": "aecf9c", "ROM": "e4b0ab"}
```

Re-render to re-stamp — the stamp bakes into `renders/out/<shot>_<view>.png`.

## `shots.py` CLI

| Flag | Effect |
|---|---|
| `<names…>` | render just these shots (default: all) |
| `--all` | export + render every shot |
| `--export-only` | only run the MiEx CLI export (refresh the cached USD) |
| `--render-only` | only run Blender on the cached USD in `renders/usd/` |
| `--adopt <name>` | create a shots.json entry from the most recent MiEx export's logged bounds |
| `--packs <list>` | resource pack override (default forces UsdPreviewSurface) |
| `--azimuth <deg>` / `--views <list>` / `--out <dir>` | one-off overrides |

`shots.py` forwards these per-shot keys to `render_usd.py`: `margin`,
`elevation`, `outline`, `dust`, `toon`, `projection`, `technical`,
`height-tint`, `top-azimuth`, `ground`, `hide`, `tint` (plus `swap`,
`transparent`, `azimuth`, `views`).

## `render_usd.py` (the renderer)

Headless Blender. Key options (most are set via `shots.json`, but useful when
debugging a single USD directly):

```
blender -b -P scripts/render_usd.py -- <usd> --out <dir> --name <n> \
        --views iso --transparent --projection tele --ground remove \
        --technical schematic --height-tint 0.9 --swap white_wool=white_concrete
```

`--views --res --samples --azimuth --no-trim --cluster-gap --lighting
--transform --glare --elevation --margin --projection --top-azimuth --ground
--max-layer --explode --outline --grid --toon --technical --transparent
--height-tint --dust --swap --hide --top-margin --clip --ground-no-outline`

### Cutaways & block filtering (opt-in; off by default)

These default to no-op, so existing course shots render identically — pass them
explicitly when you want them:
- **`--clip <axis:lo:hi[,axis:lo:hi]>`** — keep only a fractional slab of the
  build's bbox and re-tighten the frame. e.g. `--clip z:0.55:1.0` (top 45%) or a
  cross-section `--clip y:0.0:0.5`. Axes are Blender world x/y/z (z = vertical).
- **`--hide =<block>`** — exact block-id match (vs the default substring match),
  including MiEx face variants (`deepslate_top` etc.). So `--hide =stone,=deepslate`
  strips raw cave stone without deleting built `stone_bricks`/`deepslate_bricks`.
  Mix with substring tokens: `--hide =stone,_ore,sculk,water`.
- **`--outline sil`** — true silhouette only (no per-block border/seam); `off`
  drops it entirely (right for large/zoomed-out beauty shots — the per-block
  outline becomes a grid). Schematic mode honors an explicit `--outline`.
- **`--ground-no-outline`** — drop the kept/cropped ground layer from the outline
  pass so a zoomed-out floor doesn't drown in per-block lines.

Caveat: filtering can't reveal a tunnel *carved* through stone — removing the
stone removes the tunnel walls. Use a cross-section `--clip` (keep the rock) for
carved passages.

Notable behavior:
- **Stray-geometry trim** runs first (drops bedrock/floor far below the build) so
  the height-tint and framing measure the build, not the world floor at z≈-880.
- **`technical: schematic`** = warm-parchment ground, sepia ink linework, warm
  per-layer height tint (`height_tint` strength), the look the diagrams share.
- **`projection: tele`** = near-isometric telephoto (fixes the depth-ambiguity
  illusion plain ortho gives Redstone).

## Composing multi-shot figures

Some figures are several renders stitched together (e.g. the 7-segment display's
4 construction stages). Crop each render to its alpha bbox and lay them out with
Pillow:

```python
from PIL import Image
imgs = [Image.open(p).convert("RGBA") for p in stages]
imgs = [im.crop(im.getbbox()) for im in imgs]   # trim transparent margins
# then paste side by side on a transparent canvas, vertically centered
```

(See the `7-segment-display_minecraft.png` build in git history for the full
script.)

## Gotchas

- **MiEx GUI exports render BLACK** (MaterialX). Always re-export via `shots.py`
  (CLI forces `UsdPreviewSurface`). The GUI export is only for harvesting bounds.
- **GUI vs CLI lock** — close the GUI before any CLI export.
- **`renders/usd/` and `renders/out/` are git-ignored** (regenerable). Only the
  copies placed in `src/.../images/` are committed.
- A full pass over the locked-in set is `python3 scripts/shots.py --all`
  (~14 min for ~34 shots → ~63 PNGs).
