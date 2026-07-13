# PDF release checklist

The evergreen rubric for `course/Redstone-University.pdf`. Every rule here must
hold for any release, regardless of what the content is that week. Page-specific
findings never belong in this file — they go in tix (tag `pdf`) and get closed
when fixed. The system is three artifacts:

- **This checklist** — what must always be true.
- **tix issues (tag `pdf`)** — what currently violates it.
- **The build log** — evidence: `scripts/build_pdf.py` runs the automated
  subset (marked `[auto]` below) on every build and fails on violations.

Page format decision (2026-07-12): **US Letter** for now. If an A4 edition is
ever added, it must be generated independently from source (never by scaling
the Letter PDF), with its own TOC/pagination pass.

## Build integrity

- [auto] No raw Markdown, LaTeX source, or template markers in the rendered
  text (`|:---`, `**`, `$$`, `\begin{`, `\text{`).
- [auto] No editorial placeholders: `TODO`, `TBD`, `[pending]`,
  `Figure placeholder`, `Draft note`.
- [auto] All fonts embedded; no system-font fallbacks (Young Serif / Literata /
  Hanken Grotesk / Fira Code / KaTeX only).
- Text searchable and selectable.
- TOC links, internal links, and bookmarks resolve.
- Metadata: title, author, language, subject.
- Opens clean in at least two readers (Preview + a browser).

## Pagination and flow

- No blank page without an intentional print purpose; intentional blanks carry
  no folio.
- [auto] The final page is not an orphaned line/citation/fragment.
- No accidentally sparse page (a few stranded lines with a blank body) — every
  sparse page must look designed (module closers, full-page figures).
- Headings keep at least their first content block (break-after: avoid).
- Tables repeat their header row when they break.
- Module/part/appendix openings follow one consistent page-start rule.

## Figures

- [auto] Every caption is numbered (`Figure <module>.<n>`), sequential within
  its module; zero generic `Figure:` captions.
- Every caption sits on the same page as its figure.
- [auto] No image extends past the page content box (clip audit).
- No figure scaled below readability: the smallest meaningful label must be
  legible at 100% zoom and on paper. Tall/complex schematics that can't meet
  this in portrait get landscape pages, detail panels, or appendix sheets.
- Figures referenced in prose exist, and numbered references point at the
  right figure.
- No instructional distinction relies on color alone — every figure must work
  in grayscale (legend colors get a second channel: labels, outlines, or
  hatching; this is a render-pipeline requirement, see `renders/STYLE.md`).
- Caption size/contrast survives a consumer printer.

## Tables, code, math

- Tables fit the text area; no clipped or overlapping cells.
- Math renders (no raw TeX), fits its container, and keeps KaTeX fonts.
- Code blocks keep indentation and don't wrap misleadingly.
- Inline-code chips are reserved for literals, identifiers, signals, and
  commands — not ordinary digits in prose. (Convention owner: Fielding.)

## Typography

- Consistent styles for body/headings/captions/notes/tables/code.
- Widows and orphans controlled (3-line minimums).
- Operators, subscripts, Boolean notation, dashes, and minus signs correct.
- Page numbers consistent; no header/footer collisions.

## Navigation

- Printed TOC stops at the intended hierarchy (Parts / Modules / Lessons /
  Appendices — not checkpoints, summaries, or key-terms).
- TOC page numbers match the export ([auto]-spot-checked in the build).
- Bookmark tree is useful, not exhaustive; meaningful titles.
- Prose cross-references use identifiers (Figure 5.12, Lesson 4.3), never
  hard-coded page numbers.

## Accessibility

- Document language set.
- Tagged PDF with heading/table/figure semantics and logical reading order —
  or the gap is explicitly recorded as a known release limitation.
- Alt text for figures where the toolchain supports it.

## Print validation (manual, once per release candidate)

- Grayscale-print one dense schematic page, one table-heavy page, one
  Minecraft-render page, one ordinary prose section.
- Confirm captions, fine wiring, gray text, and color distinctions survive.
- Confirm margins clear home-printer non-printable edges.

## Release scope

- Decide explicitly which modules ship: released-only vs full course. Draft
  modules with placeholders must never appear in a public artifact.

## Final optimization (only after layout is stable)

- Downsample images without damaging diagrams; keep vectors vector.
- Fonts, links, bookmarks survive optimization.
- Linearize for fast web view.
- Reopen and spot-check the optimized file; record version/checksum.
