# Live 3D figures

Every placed Minecraft render in the course can also be shown as a live 3D
build: on the site, the figure's PNG is upgraded in place to an orbitable view
of the same build, drawn in the schematic look of `scripts/render_usd.py`.
This folder is the dev viewer for that work; the production code lives in
the site.

## How it fits together

```
renders/usd/<shot>.usd           MiEx export (git-ignored cache, from shots.py)
   |  scripts/usd_to_scene.py    geometry steps of render_usd.py, no Blender
   v
viewer/builds/<shot>.rub          every shot, compact binary (git-ignored)
   |  --publish                  placed + referenced + not held
   v
web/public/figures/3d/            committed: builds + component textures
web/src/data/live-figures.json    committed: page -> image -> build map
   |
   v
web/src/scripts/live-figures.js   upgrades the <img> on course pages
web/src/lib/ru3d/                 renderer (shared with this dev viewer)
```

| Piece | Role |
|---|---|
| `scripts/usd_to_scene.py` | Parses MiEx's ASCII USD (stdlib only) and ports the geometry steps of `render_usd.py`: stray trim, `hide`, ground `remove`/`remove2`/`crop` with pad synthesis, power-colored vector wires, bounds clipping. Writes `.rub` files: gzip + JSON header + quantized int16 positions (the whole set is about 1 MB). `--publish` copies what the site needs. |
| `scripts/live3d_qa.py` | Judges whether each live figure shows the same circuit as its book PNG, and writes the hold list. |
| `renders/live3d-hold.json` | Figures kept static on the site, each with the measured reason. Read by `--publish`. |
| `web/src/lib/ru3d/` | `format.js` (decoder), `shaders.js` (palettes, GLSL), `figure.js` (one figure: scene, cameras, ink post-pass, export), `legend.js` (region legend, port of `stamp_legend`). |
| `web/src/scripts/live-figures.js` | Site behavior: lazy activation, context cap, touch and keyboard handling, fallbacks. |
| `web/scripts/check-live-figures.mjs` | Behavior checks against a built site. |
| `viewer/index.html`, `viewer.js` | Dev viewer: every build, style toggles, the Blender PNG side by side. |
| `viewer/snap.mjs` | Headless PNG renders through the same code (Node 22 + Chrome). |
| `viewer/textures/` | Vanilla block textures (source set; publish copies only the 9 component textures the placed builds use). |

## Workflows

After placing or re-rendering a Minecraft figure (`/render-figures`):

```bash
python3 scripts/usd_to_scene.py --all                                    # convert
node viewer/snap.mjs --placed --out-dir renders/out-three/placed         # render every placed figure live
python3 scripts/live3d_qa.py --write-hold                                # compare with the book PNGs
python3 scripts/usd_to_scene.py --all --publish                          # refresh the site's copy
```

Before a release that touches the figures or the renderer:

```bash
cd web && npx astro build && npx astro preview --port 4321 &
node scripts/check-live-figures.mjs --base http://127.0.0.1:4321      # full matrix, headless Chrome
npm i --no-save playwright && npx playwright install webkit firefox chromium
node scripts/check-live-figures-xbrowser.mjs http://127.0.0.1:4321    # WebKit, Firefox, iPhone, GPU Chromium
```

Verified 2026-11-26: all checks pass in headless Chrome (54), WebKit desktop,
Firefox, WebKit with iPhone 15 touch emulation, and Chromium on the Metal GPU
(44). Real Safari and a physical phone were not driven by automation.

Git LFS note: `*.png` lives in LFS and this clone skips smudging, so a
checkout can leave 128-byte pointer files in place of textures. `git lfs
checkout` restores them. CI checks out with `lfs: true`. A texture that fails
to load now draws its component in flat color and logs a `[live 3D]` warning,
which both check scripts treat as a failure.

The dev viewer, from the repo root:

```bash
python3 -m http.server 8765
open "http://localhost:8765/viewer/?shot=05_full-adder&view=iso"
```

## Behavior on the site

- **The PNG is the figure.** It stays in the markup and keeps the box, so
  there is no layout shift, and no-JS, no-WebGL, print, crawlers and screen
  readers all get the image. The live view sits exactly on top of it.
- **Lazy and capped.** A figure goes live when it comes within 400px of the
  viewport, at most 6 at once (browsers cap WebGL contexts near 16), and
  drops back to its PNG when it scrolls 1600px away. three.js (128 KB gzipped)
  loads on first use; the page itself carries 4 KB.
- **Input.** Mouse: drag orbits; click, then scroll, to zoom (the wheel scrolls
  the page otherwise). Touch: vertical swipes scroll the page and horizontal
  ones turn the build; "Tap to explore" hands all gestures to the figure until
  "done" or a tap elsewhere. Keyboard: Tab to the figure, arrows orbit (Shift
  for big steps), +/- zoom, T switches iso/top, R resets, Esc releases.
- **Views.** Shots with an iso and a top render get both, as toggle buttons.
- **Textures.** Components wear 9 vanilla Minecraft textures. `USE_TEXTURES`
  in `live-figures.js` switches them to flat colors.

## Fidelity

Camera framing matches current `render_usd.py` output to within a few pixels.
That took reproducing three Blender behaviors that look accidental but define
the book's look: height bands and framing both measure object bounding boxes
that the ground delete leaves stale (so the deleted platform still counts),
the tele push-back runs along (camera - bbox center) instead of the view axis,
and the fit uses each object's box corners, not the union box. Not reproduced:
Cycles ambient occlusion. Interior linework fades by on-screen block size in
the live view; exports keep full ink.

## The hold list

`live3d_qa.py` compares each placed book PNG with its live render on redstone
state (cell by cell, aligned per build), redstone presence, silhouette
overlap, and how far the build moves at the swap. As of 2026-11-25, 34 of 52
placed figures match and 18 are held. Every hold traced back to data, not
rendering: those book PNGs were rendered from an older world state (other
lever positions, other powered wires, a different base course) than the
build in today's USD cache. To release one, either re-render the book PNG
from the current world (a content change: check the caption) or put the world
back in the pictured state and re-export, then rerun the workflow above.
