# Image pipelines

Every figure in the course is **generated**, not hand-drawn. Two pipelines feed
the book, both driven by a JSON config so adding a figure is "add an entry, run
one command, place the output":

| Pipeline | Source of truth | Config | Script | Output suffix |
|---|---|---|---|---|
| **CircuitVerse diagrams** | `~/Downloads/Redstone University.cv` | `renders/diagrams.json` | `scripts/cv_render.py` | `*_circuitverse.png` |
| **Minecraft renders** | the Bedrock world (via MiEx) | `renders/shots.json` | `scripts/shots.py` → `scripts/render_usd.py` | `*_minecraft.png` |

- [circuitverse-diagrams.md](circuitverse-diagrams.md) — schematic logic diagrams drawn straight from the CircuitVerse graph.
- [minecraft-renders.md](minecraft-renders.md) — isometric/aerial renders of the actual Redstone builds.

Generated figures live in `renders/` (scratch, git-ignored) and the chosen ones
are copied into `src/Part-*/<module>/images/`. **`src/` is the source of truth
for the book** — the site build (`web/scripts/sync-content.mjs`) copies `src/`
into the Astro content tree at build time, so a figure is only "in the book"
once it is copied into the relevant `src/.../images/` folder **and** referenced
from that module's `draft.md`.

## The golden rule

> Adding a figure = **(1)** add/extend a JSON entry, **(2)** run the script,
> **(3)** copy the output into `src/.../images/`, **(4)** reference it in
> `draft.md`. Never hand-edit a generated PNG; change the config or the script
> and re-run.

## Shared design system (both pipelines)

So every figure — diagram or render — reads as one family:

| Token | Value | Use |
|---|---|---|
| Signal red (on) | `#f0392a` | powered dust/wires, lit segments, powered I/O |
| Deep red (off) | `#5a1816` | unpowered dust/wires |
| Ink | `#30231e` | outlines, structure, labels (= site `--color-text`) |
| Paper | `#f5f1ea` | backgrounds, "powered" digit/label text |
| Faint | `#d2cdc5` | unlit segments, dashed abstraction boxes |
| Gate fills | render band-palette pastels | rose / sage / dusty-blue / amber |

Fonts (baked into the SVGs, so they must be installed for `cairosvg`):
**Young Serif** (display: gate/box names) and **Fira Code** (mono: digits).
See circuitverse-diagrams.md for font install notes.

## Directory map

```
renders/
  diagrams.json     # CircuitVerse pipeline config   (tracked)
  shots.json        # Minecraft pipeline config       (tracked)
  cv-out/           # CircuitVerse output (svg+png)    (git-ignored)
  out/              # Minecraft render output (png)    (git-ignored)
  usd/              # cached MiEx USD exports          (git-ignored)
scripts/
  cv_render.py      # .cv graph -> svg/png
  shots.py          # MiEx CLI export + Blender render orchestrator
  render_usd.py     # Blender headless renderer (USD -> png)
src/Part-*/<module>/images/
  *_circuitverse.png   # placed CircuitVerse diagrams
  *_minecraft.png      # placed Minecraft renders
```

## Status / future

These pipelines are **script-driven but human-in-the-loop** today — the
config-to-output step is deterministic, but choosing bounds (Minecraft) and
placing/naming outputs is manual. The `/render-figures` skill
(`.claude/skills/render-figures/`) walks an agent through the whole flow until
it is fully scripted. Moving the config→output step into CI/CD is feasible for
the CircuitVerse pipeline (pure Python + cairosvg); the Minecraft pipeline needs
Blender + the world file + MiEx, so it is desktop-only for now.
