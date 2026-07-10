# CircuitVerse diagram pipeline

Draws clean, schematic logic diagrams **directly from the CircuitVerse project
graph** — no exporting SVG from CircuitVerse and no Figma. Geometry is computed,
so wires are perfectly aligned and everything is recolorable to the design
system.

- **Script:** `scripts/cv_render.py`
- **Source graph:** `~/Downloads/Redstone University.cv` (the CircuitVerse
  project data; one file holds *all* circuits as named scopes). Refresh it
  straight from circuitverse.org with `python3 scripts/pull_cv.py` — the
  project id lives in `renders/diagrams.json` `_defaults.cv_project`, the
  previous file is kept as `.bak`, and a manual "Export as file" download
  works too (identical JSON).
- **Config:** `renders/diagrams.json`
- **Output:** `renders/cv-out/<name>.svg` + `.png` → placed as
  `src/.../images/<placed-name>_circuitverse.png`

## Quickstart

```bash
CV="$HOME/Downloads/Redstone University.cv"

python3 scripts/pull_cv.py                                # refresh $CV from circuitverse.org
python3 scripts/cv_render.py "$CV" --list                 # list every circuit/scope
python3 scripts/cv_render.py "$CV" --batch renders/diagrams.json   # render the whole set
python3 scripts/cv_render.py "$CV" "XOR Gate" -o /tmp/x.svg --gate-colors --png  # one circuit
```

## Adding a new diagram

1. Make sure the circuit exists in the `.cv` (re-export from CircuitVerse if you
   added one). `--list` shows the exact scope names.
2. Add an entry to `renders/diagrams.json` (see schema below).
3. `python3 scripts/cv_render.py "$CV" --batch renders/diagrams.json`
4. Eyeball `renders/cv-out/<name>.png`.
5. Copy it to the module's images folder under the name `draft.md` references:
   `cp renders/cv-out/<name>.png src/Part-I--Foundations/<module>/images/<name>_circuitverse.png`
6. Reference it in `draft.md` (`![alt](./images/<name>_circuitverse.png)`) if not
   already, then `node web/scripts/sync-content.mjs` (or just rebuild) to see it.

## `renders/diagrams.json` schema

```jsonc
{
  "_defaults": { "out": "renders/cv-out", "gate_colors": true, "scale": 2 },
  "<key>": {
    "circuit": "<exact scope name in the .cv>",   // required unless compose
    "name":    "<output filename stem>",           // -> cv-out/<name>.png
    "inputs":  [1, 0],        // optional: force Input boxes (left->right by x)
    "only":    ["Input"],     // optional: render ONLY these element types (skips wires/dots)
    "compose": ["A", "B"],    // optional: lay several scopes side by side
    "sep":     "equiv",       // optional: separator glyph for compose ("equiv" = ≡)
    "scale":   2,             // optional: overrides _defaults
    "gate_colors": true       // optional: overrides _defaults
  }
}
```

Field notes:

- **`inputs`** — a list of `0/1` applied to the circuit's Input boxes in
  left→right (x) order. The simulator re-solves the whole net from these, so the
  lit/unlit state of internal wires and the output follows. Use this to make a
  composite gate show the **same defining case** as its abstract symbol
  (e.g. XOR `[1,0]`, NOR `[0,0]`, NAND `[1,1]`).
- **`only`** — restricts rendering to the listed `objectType`s and skips wires +
  connection dots. `["Input"]` gives the bare labeled input boxes (used for the
  Module 1 "4-bit input interface").
- **`compose`** — render each listed scope and lay them out horizontally,
  joined by `sep`. `"sep": "equiv"` draws a `≡`. Used for the "before ≡ after"
  simplification figure.

## CLI reference

```
cv_render.py <cv> [name] [options]
```

| Flag | Effect |
|---|---|
| `--list` | print every scope name in the `.cv` |
| `--batch <json>` | render every entry in a `diagrams.json` |
| `-o, --out <path>` | output svg path (single) or output dir (`--heroes`/`--gate-intros`/`--layout-demo`) |
| `--png` | also rasterize the single-circuit svg to png |
| `--scale <f>` | output px = viewBox × scale (default 2.0) |
| `--gate-colors` | fill gates with pastel band-palette colors (vs ink outline only) |
| `--hero <NAME>` | one gate "hero" symbol + name (e.g. `NOT`) |
| `--heroes` | all 7 gate hero symbols → `--out` dir (`NOT.png` … `XNOR.png`) |
| `--gate-intros` | all 7 hero+example intro figures → `--out` dir (`*-gate_circuitverse.png`) |
| `--layout-demo` | the subcircuit default-vs-organized layout pair → `--out` dir |
| `--seg-labeled` | the labeled 7-segment naming reference → `--out` |

## What the renderer does (so you can extend it)

- **Coordinate model.** Pin nodes (`allNodes` type 0/1) are **relative** to their
  element and rotated by `direction` (RIGHT `(x,y)`, DOWN `(-y,x)`, LEFT
  `(-x,-y)`, UP `(y,-x)`; SVG rotate 0/90/180/270). Intermediate wire nodes
  (type 2) are **absolute**. Multi-input gates store `inp` as a **list**.
  ⚠️ Any loop over scope element lists **must** guard `v[0].get("objectType")`
  or it also iterates `allNodes` and corrupts the bounds.
- **Wires.** CircuitVerse stores some gate-input wires as raw diagonals; the
  renderer Manhattan-routes them and taps buses perpendicularly (the alignment
  you used to fix by hand in Figma). Routing is contact-aware: two wires of
  different nets may only meet as a perpendicular crossing, so a bend candidate
  is rejected if any leg would overlap, nearly merge with, or end on another
  net's wire, pin, or junction point. Long spans try the plain L, half-grid
  Z-jogs (the clean lane in a 10-pitch matrix is between rows), then the
  flipped L; short hops (a few grid steps) skip the jogs and fall back to the
  author's original diagonal. A jog lane must sit at least a full grid step
  from the wire's own lanes (a 5-unit sidestep reads as a broken wire, not a
  jog) and may detour slightly outside the span (U-route). When the two feeds
  of a 2-input gate cross, the pins' draw positions are swapped — the gate is
  commutative, so both wires run straight instead of drawing a meaningless X.
  Nets that reach no element pin (abandoned editor leftovers) and dangling
  tails under two grid steps are not drawn at all. A slant is honest, a false
  junction is not.
  Subcircuit pins snap onto their box edge and are approached perpendicular to
  it; 7-seg display pins stay at their raw interior positions and the
  paper-filled display body masks the wire tails, so hookups read as ending at
  the frame (gate-style, no pin dots). The invariant is checkable:
  `CV_DEBUG_SEGS=/tmp/segs.jsonl` during a render dumps routed geometry, and
  `scripts/check_cv_junctions.py /tmp/segs.jsonl` fails on any cross-net touch.
- **Gate leads.** Each gate pin gets a short lead *into* the gate (snapped to the
  dominant axis) and the gate is drawn on top, so wires meet it flush with no
  dots on the gate. Connection dots appear only at real junctions/terminals/I/O.
- **Simulation.** A union-find net solve + gate fixpoint colors powered wires red.
  ⚠️ It does **not** trace through `SubCircuit` black boxes, so a display fed by
  a subcircuit renders unlit — fine for structural/abstraction diagrams.
- **SubCircuit boxes.** Resolved to the referenced scope's name (`SUBCIRCUIT_NAMES`,
  built from `str(scope id) → name`) and the label wraps to the box width.
- **Visual system.** I/O boxes: powered = solid look isn't used — they are sharp
  white boxes with a colored outline + matching digit (red `1`, ink `0`). Gate
  identity is SHAPE; `--gate-colors` adds pastel fills. Names in Young Serif,
  digits in Fira Code.

## Naming conventions

- Simple gate examples (`NOT`, `OR`) → `*-gate_circuitverse.png` (the gate-intro figure).
- Composite gates (AND/NAND/NOR/XOR/XNOR built from primitives) →
  `*-gate-composite_circuitverse.png`.
- Gate hero symbols for tables → `NOT.png` … `XNOR.png`.

## Gotchas

- **cairosvg uses *system* fonts, not web fonts.** Young Serif + Fira Code must
  be installed (`~/Library/Fonts` + `fc-cache -f`) or text falls back to a wrong
  face. The `≡` glyph is **not** in Young Serif — it is drawn, not typed.
- **`renders/cv-out/` is git-ignored** (regenerable). Only the copies placed in
  `src/.../images/` are committed.
- **`cairosvg` install** may need `pip install --break-system-packages cairosvg`
  on a PEP-668 ("externally managed") Python.
- After re-exporting the `.cv`, re-run `--batch` — scope **ids** can change, which
  matters for SubCircuit name resolution.
