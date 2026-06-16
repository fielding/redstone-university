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
`--seg-labeled` (7-segment naming reference).

If text uses the wrong font, the Young Serif / Fira Code TTFs aren't installed
for cairosvg (`~/Library/Fonts` + `fc-cache -f`).

## Minecraft render — procedure

```bash
# 0. CLOSE the MiEx GUI first (LevelDB lock).
# 1. Get bounds: open MiEx, frame+export the region, read bounds from
#    ~/apps/MiEx/log.txt  (minX minY minZ maxX maxY maxZ per export block).
#    The GUI export renders black (MaterialX) — we only want its bounds.
# 2. Add the shot to renders/shots.json with those bounds (see schema).
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

Commands: `--all` (everything), `<names>` (subset), `--render-only` (reuse cached
USD), `--export-only`, `--adopt <name>` (make an entry from the last export).

A multi-stage figure (e.g. 7-segment construction) is several renders stitched
with Pillow — crop each to `getbbox()` and paste on a transparent canvas.

## When you're done

- Confirm the figure renders in the running dev site (or `node
  web/scripts/sync-content.mjs` then rebuild).
- If you added genuinely new pipeline capability, update
  `docs/image-pipelines/` and this skill.

## Known limits (don't fight these silently — surface them)

- The CV simulator does not trace through `SubCircuit` black boxes, so a display
  fed by a subcircuit renders unlit (fine for structural diagrams).
- MiEx can't export signs (block entities) — no render is possible.
- Fixed-size gate glyphs: a >2-input gate's outer pins poke past the body. The
  fix (scale glyph height to fan-in) is a known, unimplemented improvement.
