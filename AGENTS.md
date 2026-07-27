# Project agent memory

This file is the project's committed home for project-intrinsic agent knowledge: build, test, release, architecture, and sharp-edge notes that should travel with the code.

## Two consumers, one source

`src/**/*.md` is the course, and it feeds two independent pipelines:

- **The book/PDF** via `scripts/prepare_pdf.py` + `scripts/build_pdf.py`.
- **The website** in `web/`, an Astro static site. `web/scripts/sync-content.mjs`
  copies `src/` into `web/src/content/course/` on every `npm run build` and
  `npm run dev`, so `web/src/content/course/` is generated and must never be
  edited by hand.

**Do not add YAML frontmatter to the course markdown.** `prepare_pdf.py`
concatenates raw file bodies and the markdown-it instance in `build_pdf.py` has
no `front_matter` plugin, so a `---` block renders into the book as a rule plus
stray text. Anything the site needs but the book does not belongs on the web
side. Page titles live in `web/src/utils/titles.ts` for exactly this reason.

Each chapter's title is authored as the file's first `## ` heading (the book has
one `h1`). `web/plugins/rehype-page-title.mjs` promotes that heading to `h1` for
the web, and `titles.ts` mirrors it for `<title>`, link previews, and the
sidebar/pager short forms. Renaming a chapter heading means updating `titles.ts`
in the same change.

## Release gating

`web/src/utils/gating.ts` decides what the site publishes. Unreleased parts stay
visible in the sidebar as unlinked titles with a status badge, and get no routes.
Releasing a module is one entry in `LIVE_MODULES` (or `LIVE_PARTS` for a whole
part). Preview everything locally with `PREVIEW_ALL_PARTS=true npm run dev`.

## Sharp edges

- A course PDF is tracked with git-LFS and the LFS budget is exceeded, so in
  most worktrees it is a pointer file. Do not try to fetch it.
- `npm run build` in `web/` runs `astro check`; keep it at zero errors.

## Maintaining this file

Keep this file for knowledge useful to almost every future agent session in this project.
Do not repeat what the codebase already shows; point to the authoritative file or command instead.
Prefer rewriting or pruning existing entries over appending new ones.
When updating this file, preserve this bar for all agents and keep entries concise.
