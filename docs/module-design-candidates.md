# Module design candidates — decision aid for roadmap step 4

Companion to `renders/out/candidates-contact-sheet.png` (rebuild:
`shots.py cand-alu-* cand-reg-*`, stitch snippet in git history) and
`assets/schematics/mattbat/{alus,registers}/`. Candidates are mattbatwings'
standalone tutorial designs, strip order ≈ simple→advanced. This doc exists to
frame the per-module choice: **RU-v1 layout / mattbat adapted / hybrid**.
Assessments below are from the renders + strip position; anything marked
"verify" needs an in-world look before adoption.

## What RU-v1 brings (the incumbent)

The testbench scripts (`ru-testbench/{components,alu,ram,pc,control}.js`) are
verified, torch-and-repeater, horizontally laid out designs — the pedagogy the
course is built around. Default remains: **RU-v1 for anything a reader builds
step-by-step**, because every mechanism in it is taught by an earlier module.
mattbat designs win where scale or contrast is the point.

## ALU candidates (Modules 5/6/9, interlude 3b)

| Candidate | Read from render | Course fit |
| :-- | :-- | :-- |
| alu-01/02/05 | compact vertical bit-stacks, comparator-heavy | 3b interlude exemplar (small enough to show whole) |
| alu-03 | mid-size, visible carry ladder | possible M6 compare/contrast figure |
| alu-04 | the big one (~3k blocks), machine-scale | M9 "what ALUs grow into" hero shot; too big to teach |
| alu-06/07 | tiny lecture props | probably skip |
| alu-08–11 | **flat horizontal designs** | closest to RU-v1 philosophy; strongest adaptation candidates for M9 if any mattbat ALU is adopted — vocabulary confirmed by schematic stats: torch-forward (24–29 torches, only 16 comparators, ~620–1,200 blocks); alu-07 is the most torch-pure (101 torches, 8 comparators) but sprawls |
| alu-12–17 | tall late-series with I/O columns | reference only; comparator-dense (73–97) like 01/02/05 |

**Vocabulary stats** (from `schem_stats.js`; no pistons/observers anywhere —
all pure dust logic): the strip cleanly divides into a comparator idiom
(alu-01/02/05/12–15: 41–81 comparators, essentially zero ground torches —
compact-interlude material) and a torch idiom (alu-07–11 — RU-v1-compatible).
alu-04 is 6,078 blocks / 474 repeaters: display scale only.

## Register candidates (Module 10)

| Candidate | Read from render | Course fit |
| :-- | :-- | :-- |
| reg-01/02 | display-scale multi-bit banks | M10 closing "a real register bank" figure; also M12 register-file comparison |
| reg-03a/b | 03a = large main-strip bank (like 01/02); 03b = separate side build at x~128 | rendered on the contact sheet |
| reg-04–10 | small single-register variants | granularity matches M10's teaching cell; candidates for the "other ways to hold a bit" aside — RU-v1's repeater-lock stays the taught design (capture-on-release semantics already characterized, §5.1 of the project map). Stats highlights: **reg-09** is nearly comparator-free (3 comparators, 61 repeaters, 650 blocks — the most RU-v1-compatible register in the set); **reg-05** is a tiny 127-block single cell; reg-04 is lamp-heavy (138 lamps — a display register) |

## Standing decisions this doc inherits

- Compact designs are an **aside, not the vehicle** (project map §2, module 3b).
- Composition legend treatment for any figure that assembles multiple modules
  (`renders/STYLE.md`).
- mattbat material is study reference, credited; never republished as course
  artifact (`assets/schematics/mattbat/README.md`).

## The decision table (fill in)

| Module | Choice (RU-v1 / adapt <cand> / hybrid) | Notes |
| :-- | :-- | :-- |
| 5 Adder | | |
| 6 Adder/Sub | | |
| 9 ALU | | |
| 10 Register | | |
| 11 RAM | | (no standalone candidates — 8-bit machine bitplane is the only mattbat reference) |
| 12 Machine | | RU-v1 is the spec; mattbat 8-bit full build = contrast hero |
