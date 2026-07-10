# redstone.university — website

The Astro site that serves the course at [redstone.university](https://redstone.university).

## How content gets here

Lessons are authored at the repository root in `src/` — this directory never
holds hand-edited course content. `scripts/sync-content.mjs` copies the course
into `web/src/content/course/` before every dev run and build; that folder is
generated, so don't edit it or commit it. Set `STRICT_IMAGES=1` to make the
sync fail on missing images instead of just reporting them.

## Commands

Run from `web/`:

| Command           | What it does                                  |
| ----------------- | --------------------------------------------- |
| `npm install`     | install dependencies                          |
| `npm run dev`     | sync content, then start the dev server       |
| `npm run build`   | sync content, type-check, build to `dist/`    |
| `npm run preview` | serve the built site locally                  |

Unreleased course parts are gated on the live site; to preview them locally,
run `PREVIEW_ALL_PARTS=true npm run dev` (see `src/utils/gating.ts`).

## Deploys

Pushes to `main` deploy the site via `.github/workflows/deploy.yml`
(GitHub Pages). The course PDF and `course/` directory are built by a separate
workflow — see the root README and `.github/CONTRIBUTING.md` before
contributing.
