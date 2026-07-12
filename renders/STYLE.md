# Redstone University — Render Style Guide

The single reference for how course images look and how they're produced.
Pipeline: `python3 scripts/shots.py <shot>` (see `renders/shots.json`).

## Views

Every circuit gets up to two renders:

| View | Purpose | Camera | Lighting | Tonemap | Bloom |
| :-- | :-- | :-- | :-- | :-- | :-- |
| `iso` | build-step / diagram images in lessons | orthographic, 35.26° elevation, azimuth per shot, margin 1.3 | bright with defined soft shadow (shadows are load-bearing for multi-level dust legibility) | Standard | off |
| `beauty` | module hero shots, part openers | perspective, 28° elevation | warm sun, soft shadows | AgX Punchy | on |

### Large flat builds (decided 2026-07-09)

A wide single-layer build (the legible 4-bit RCA, ~100×36 blocks) gets **no
iso** — at that aspect the angled view collapses into a sliver of detail
floating in empty frame. Treatment:

- **Top view only, high resolution.** Give the shot a `"res"` matched to the
  build's aspect — the render log's `ortho fit: content WxH` line has the
  exact numbers; canvas aspect = W:H keeps the margins even (the 4-bit RCA is
  `3600x1306`).
- **Pair the overview with the module close-up.** The hi-res top shows the
  repetition and the carry chain; the small-tier iso of the repeated module
  (the 1-bit full adder) carries the gate-level detail. Overview + detail,
  never one image trying to do both.
- The ortho camera contain-fits since 2026-07-09 — a mismatched res
  letterboxes instead of cropping, so this can't silently cut a build off.

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
- **Wiring lanes (LARGE SCHEMATICS ONLY):** individual components render
  **plain** — white platform, plain dust/components — same as every Part I
  figure. Colored-concrete signal lanes are a *sectioning aid reserved for
  large, busy schematics* (the full ALU datapath, the assembled machine),
  where color helps trace which lane is which; they are **not** applied to
  small single-component builds (a gate, an adder slice, a MUX, a register).
  When lanes are used, the roles are:
  - **blue** = A operand / primary data · **purple** = B operand / secondary
    data · **pink** = control (strobes, selects, enables) · **red** = output /
    result.
  (Decided 2026-07-07, correcting an earlier over-application of lanes to
  small canonical samples.)
- **Ground:** sand / smooth sandstone reads like blueprint paper in renders.
- **Ground/platform rule (decided 2026-07-08, crop rebuilt 2026-07-09):**
  every figure floats on the build's own bottom blocks — the true ground never
  appears. Pick the mode by how the build sits:
  - **`remove` (default)** — build is on its own base blocks with a separate
    floor below (the Part I pattern). Deletes the floor layer, keeps the pads.
  - **`crop`** — build is laid out directly on the ground (most hand-built
    figures). Deletes the true ground entirely and **generates a clean base
    block under every cell the circuit occupies** — the ground is treated
    as if it were just the block the build sits on, reproducing the
    hand-lift-and-export look of the Part I figures without touching the
    world; ground with nothing on it vanishes. Circuit geometry (dust, wires,
    components) is never stripped. (Buried ground has no side faces in a MiEx
    export, which is why the blocks are synthesized rather than kept.)
    The generated layer renders in the **warm cream band, matching the Part I
    bottoms — not white** (decided 2026-07-09: white stays reserved for the
    page and for ghosted structure in legend shots).
  - **`keep`** — not used for course figures.
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

With `ground: crop`, the synthesized base pads inherit the block family they
replaced (a build's own base course shadows the world ground), so a region
whose base is built from a tinted family carries its color at ground level
too — block a region's base in a dedicated family and the whole region reads
as one mass instead of markers floating on cream.

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

## 7-segment displays (decided 2026-07-09)

Display walls render **white**: neutralize the bezel/frame blocks per shot with
`"tint": "black_concrete=f5f1ea,pink=f5f1ea,orange=f5f1ea,terracotta=f5f1ea,magenta=f5f1ea"`
so lamps carry all the contrast, and set "height_tint": 0 on plain display faces (the top band otherwise rose-tints the top row). Applies to every 7-segment figure going
forward. Multi-panel display figures are shot per-panel (own centered camera,
no cross-frame parallax) and stitched with scripts/compose_7segment.py;
all panels share ONE azimuth and use "projection": "ortho" — the tele lens foreshortens walls differently by depth, pure ortho keeps every panel plane-parallel. Rebuild: shots.py 7seg-wall 7seg-lit 7seg-closeup, then compose_7segment.py, place manually over 04/images/7-segment-display_minecraft.png.

## M4 complete-digital-display — composition legend (2026-07-11)

Same wool language as the M5 integration build, so the hues transfer 1:1
and mean the same thing across figures:

- `gray_wool` -> e4b0ab rose — the 10-to-7 encoder ROM (memory family)
- `blue_wool` -> aecf9c sage — the 4-to-10 decoder
- `cyan_wool` -> a8c4d6 dusty-blue — display driver stage
- `black_concrete` -> f5f1ea paper — the 7-segment panel reads white
- `white_wool` / `smooth_stone` / `cobblestone` -> f5f1ea paper — wiring + structure

Flat fills (`height_tint: 0`), Fielding-approved. Optional REGION HEIGHT
SHADING (`height_tint` > 0 with a tint map) steps each region palest at its
base to full hue at its top (`_hue_band` in render_usd.py) — first tried on
05_integration-bug at 0.85; keep/drop verdict per figure is Fielding's.

## Region height shading — the tone band (final, 2026-07-11)

Legend-tinted families step through tones of their own hue by build layer,
normalized to EACH FAMILY's own height (a 3-layer region uses 3 tones, not
the palest sliver of the whole build's ramp). Direction: LIGHTER WITH
HEIGHT — full hue at the region's base (grounded, matches its pads), paling
upward; circuits read best against the paler upper tones. Band shape:
whitened (+40% white) at top ... full hue mid ... 0.88x darkened at base,
via _hue_band() in render_usd.py. Enable with height_tint > 0 on a tinted
shot (0.85 standard); 0 keeps flat legend fills.

Adopted on: 05_integration-bug (M5) and 04_complete-digital-display (M4,
"toned" per Fielding). Component legibility partners: lamps rim at 1.33x
linework + lit lamps emit 1.6x; torches rim 2.5x in top views. Crop pads
are evidence-based: only where the world had support; familyless pads are
dropped, levers/lamps over air float.

## In-image legend chips (2026-07-11, Fielding request)

Composed figures that carry region tints get a small legend stamped into the
PNG: one chip block per region + label in Young Serif ink 30231e. Chips are
REAL Blender renders (scripts/legend_chip.py) — same iso camera, flat
emission fill, and Freestyle ink as the figures — a single block floating
on transparency, cached per hue in renders/out/chips/. Bottom-left corner,
auto-dodging to another corner if the build reaches in. Implementation:
`ensure_chips()` + `stamp_legend()` in scripts/shots.py, driven by a
per-shot `"legend": {"Adder": "f2d489", ...}` object (order = display
order). Labels use region names, not block names. Adopted on
05_integration-bug (Adder/Decoder/ROM/Display driver) and 05_4-bit-rca
(Full adder / Repeated slice); roll onto other composed shots (M4 complete
display, hex display, payoff) as they come up for render.

## Module figures: neutral alone, colored in composition (2026-07-11)

A module rendered ALONE (the 1-bit full adder) uses the small-build scheme:
neutral structure, height bands only, no section colors (Fielding). Color
arrives when the figure carries COMPOSITION semantics: the 4-bit RCA aerial
tints slice 0 yellow (wool families, f2d489 = "the module you built")
against gray repeats (concrete families, c7c0b6), and the integration/legend
shots tint by region. Corollary: schematic mode ghosts any family not in a
tint map, so a colored build with NO tint map flattens to cream — that is
the "everything is cream" failure. Related renderer honesty rules: the
resting-plane detection is median-based over circuit vertices (min() let a
single sunken dust decal keep the real course AND generate pads under it —
the doubled-base failure); a plan view can carry its own canvas via
`top_res` (tall builds want portrait; page width is the only hard limit).
