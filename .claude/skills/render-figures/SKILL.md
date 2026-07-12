---
name: render-figures
description: Generate, regenerate, and place course figures via the two image pipelines (CircuitVerse diagrams from the .cv graph, Minecraft renders from the world). Invoke when adding/updating any figure in the book, or when a new entry is added to renders/diagrams.json or renders/shots.json.
---

# Render figures

Drive the course's two image pipelines. Full reference lives in
`docs/image-pipelines/` — read it when you need detail; this skill is the
operating procedure.

## First: which pipeline?

- A **logic diagram** (gates, decoders, displays, abstractions) → **CircuitVerse
  pipeline** (`scripts/cv_render.py`, `renders/diagrams.json`). Output
  `*_circuitverse.png`.
- A **photo of the Redstone build** (blocks, dust, lamps) → **Minecraft
  pipeline** (`scripts/shots.py`, `renders/shots.json`). Output `*_minecraft.png`.

## The invariant (never skip)

A figure is "in the book" only after **all** of:
1. its config entry exists (`diagrams.json` / `shots.json`),
2. the script has been run and the output eyeballed,
3. the PNG is copied into `src/Part-*/<module>/images/<name>_(circuitverse|minecraft).png`,
4. `draft.md` references it.

`src/` is the source of truth; the site build syncs `src/` → Astro content.
**Never hand-edit a generated PNG** — change config/script and re-run.
`renders/cv-out/`, `renders/out/`, `renders/usd/` are git-ignored scratch.

## CircuitVerse diagram — procedure

```bash
CV="$HOME/Downloads/Redstone University.cv"
python3 scripts/pull_cv.py                          # refresh from circuitverse.org first
python3 scripts/cv_render.py "$CV" --list           # confirm the scope name exists
# add/extend the entry in renders/diagrams.json, then:
python3 scripts/cv_render.py "$CV" --batch renders/diagrams.json
```

Then **view** `renders/cv-out/<name>.png`, copy into the module's images folder
under the name `draft.md` uses, and reference it.

Entry knobs (see circuitverse-diagrams.md for the schema):
- `inputs: [..]` — force input states so a composite shows its defining case
  (XOR `[1,0]`, NOR `[0,0]`, NAND `[1,1]`); the sim re-solves the lit state.
- `only: ["Input"]` — render just those element types (bare I/O).
- `compose: ["A","B"], sep: "equiv"` — lay scopes side by side joined by `≡`.

Special generators (write to `--out` dir): `--heroes` (7 gate symbols),
`--gate-intros` (7 hero+example), `--layout-demo` (subcircuit before/after),
`--seg-labeled` (7-segment naming reference), `--seg-strip "A=abcefg,…"`
(row of lit 7-seg panels with labels — the hex-letters strip).

After touching the router/wire code, assert the no-false-junction invariant
(wires of different nets only meet as perpendicular crossings):

```bash
CV_DEBUG_SEGS=/tmp/segs.jsonl python3 scripts/cv_render.py "$CV" --batch renders/diagrams.json
python3 scripts/check_cv_junctions.py /tmp/segs.jsonl
```

If text uses the wrong font, the Young Serif / Fira Code TTFs aren't installed
for cairosvg (`~/Library/Fonts` + `fc-cache -f`).

## Minecraft render — procedure

```bash
# 0. CLOSE the MiEx GUI first (LevelDB lock).
# 1. Get bounds: open MiEx, frame+export the region, read bounds from
#    ~/apps/MiEx/log.txt  (minX minY minZ maxX maxY maxZ per export block).
#    The GUI export renders black (MaterialX) — we only want its bounds.
# 2. Add the shot to renders/shots.json with those bounds (see schema).
#    Bounds rule (all mins inclusive, maxes exclusive): minY = the BUILD'S
#    OWN BASE COURSE — the blocks the components sit ON. Cut only PLOT
#    GROUND below it. Getting this wrong by one is the classic failure:
#    minY at the component level amputates the base course (wool/structure
#    vanishes, dust runs float — 2026-07-11); minY into the plot ground
#    shows a doubled base. Distinguish course vs ground with a bot block
#    census per y-level when unsure (build blocks match the footprint;
#    ground spans the whole plot). maxY = one ABOVE the tallest block
#    (display panels clip otherwise). Trim x/z tight to the build: slack
#    pulls in neighbor-plot geometry as stray cream arms. A FAWE selection
#    maps as min corner verbatim, max corner +1 on each axis; bump minY +1
#    only if the selection includes plot ground.
#    Fielding marks corners in-world with a single OAK FENCE post — hidden
#    from renders via _defaults "hide": "oak_fence" (glass is NOT hidden;
#    future builds use it). Before exporting after in-world edits, flush
#    chunks: bot connect -> /save-all flush (see minecraft-agents tools).
# 3. Render (CLI re-export with correct materials + Blender):
python3 scripts/shots.py <shot-name>
# 4. View renders/out/<shot>_iso.png, copy into src/.../images/, reference it.
```

Key per-shot knobs (inherit `_defaults`):
- `views`: `["iso"]` for gates, `["iso","top"]` for decoders/larger builds.
- `ground`: `keep | remove | remove2 | crop` — `remove` drops the platform but
  keeps the build's base block; `remove2` also drops the base block.
- `hide: "white_wool,cobblestone,…"` — drop structural meshes by name, keeping
  the component (use for icons; needed for side-mounted parts like levers that
  `remove2` would eat).
- `tint: "blue_concrete=a8c4d6,…"` — recolor block families to flat legend
  colors (substring match, longest key wins; survives the `technical` restyle;
  never touches redstone components). For composed multi-module builds use the
  **composition legend treatment**: `tint` + `height_tint: 0`, region hues and
  rationale in `renders/STYLE.md`; the canonical-* shots show the lane-tint
  variant (`clip` additionally cuts a bit-slice schematic view).
- `torch_marks`: `stroke` (default) rims every top-view torch dot with heavy
  ink (2.5× linework) so torches read against dust; `off` disables. Iso views
  are never marked. Related: crop pads are never synthesized under levers —
  levers render as floating inputs.
- `legend: {"Adder": "f2d489", …}` — stamp an in-image swatch+label legend
  (Young Serif, ink outline) onto every view of the shot, bottom-left corner
  (auto-dodges to another corner if the build reaches into it). Use on
  composed/tinted figures; labels+hues must match the region semantics in
  `renders/STYLE.md`. Post-pass in shots.py — re-render to re-stamp.
- **A build renders all-cream when its block families are missing from the
  shot's `tint` map** (schematic mode ghosts unmapped structure by design).
  Module builds in the adder language need
  `yellow_concrete=f2d489,orange_concrete=f2d489,smooth_stone=f5f1ea,cobblestone=f5f1ea`.

Commands: `--all` (everything), `<names>` (subset), `--render-only` (reuse cached
USD), `--export-only`, `--adopt <name>` (make an entry from the last export).

A multi-stage figure (e.g. 7-segment construction) is several renders stitched
with Pillow — crop each to `getbbox()` and paste on a transparent canvas.

## When you're done

- The dev site (localhost:4321) serves the **src/ drafts**: `sync-content.mjs`
  wipes and re-copies `src/` → `web/src/content/` when the server starts.
  After placing a figure, **restart the dev server** (`PREVIEW_ALL_PARTS=true
  npm run dev` in `web/`) — a running server keeps serving its cached
  processed copy of a replaced image even after a manual sync.
- `course/` and `assets/images/` are **built outputs**, not places to put
  files: `scripts/publish.py` (run by CI on every push to main) flattens each
  module to `course/<Part>/<Module>.md` and copies images to
  `assets/images/<module-prefix>_<name>.png`. After pushing, pull the bot's
  "Rebuild course materials" commit rather than editing those trees.
- If you added genuinely new pipeline capability, update
  `docs/image-pipelines/` and this skill.

## Known limits (don't fight these silently — surface them)

- The CV simulator does not trace through `SubCircuit` black boxes, so a display
  fed by a subcircuit renders unlit (fine for structural diagrams).
- MiEx can't export signs (block entities) — no render is possible.
- Fixed-size gate glyphs: a >2-input gate's outer pins poke past the body. The
  fix (scale glyph height to fan-in) is a known, unimplemented improvement.
