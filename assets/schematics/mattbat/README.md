# mattbatwings 8-bit computer — reference schematics

Reference implementations extracted from **mattbatwings' "8-bit computer"** world
download (world dated Feb–Mar 2023, Minecraft 1.19; loaded and upgraded to 1.21.6
on the agents-lab Paper server as `world-mattbat-8bit`). Extracted 2026-07-06 via
FastAsyncWorldEdit. **Credit: mattbatwings** — these are his designs, kept here as
study references for design-comparison callouts in the course, not as course
artifacts. Do not republish as-is.

The build sits at spawn, roughly x −96..8, y 88..112, z 2..62. It is a Ben
Eater–style 8-bit machine built as **8 identical bit-slices stacked vertically**
(one bit per 2-block layer, y 88–101; verified by layer autocorrelation: adjacent
layers ~0% similar, period-2 layers 95–98% similar). Because the machine is
bitwise-uniform, a single bit-slice fully characterizes each subsystem's design —
the `-ref-*-bitslice` files are the "single component unit" references.

| File | Contents | Bounds (world coords) |
| :-- | :-- | :-- |
| `mattbat-8bit-full.schem` | The entire computer (281,853 blocks) | −102,86,−4 → 14,118,68 |
| `mattbat-red-left.schem` | Register-file section (red framing) | −88,86,0 → −46,104,40 |
| `mattbat-purple-right.schem` | RAM / control-ROM grid (purple framing) | −26,86,0 → 10,104,40 |
| `mattbat-center-logic.schem` | ALU + flags + control core | −50,86,0 → −24,108,42 |
| `mattbat-ref-register-bitslice.schem` | ONE bit of the register file (2-layer slice + support layer) | −88,93,2 → −46,95,40 |
| `mattbat-ref-ram-bitplane.schem` | ONE bit-plane of the RAM/ROM grid | −26,93,2 → 10,95,40 |
| `mattbat-ref-alu-bitslice.schem` | ONE bit of the ALU/flags/control core | −50,93,2 → −28,95,42 |

Notes for course use:

- **Comparators everywhere.** His compact style leans on comparators (subtract
  mode / signal-strength tricks) — a deliberate contrast with RU-v1's
  torch-and-repeater pedagogy. Good callout material for the compact-design
  interlude (3b): same function, radically different component vocabulary.
- **Vertical bit stacking** is his scaling axis; RU-v1 scales horizontally for
  legibility. Another useful compare/contrast.
- The wool color framing (red/purple/light-blue) is an annotation layer around
  the circuits, not part of them — the same "tint at composition" philosophy the
  course adopts (`docs/project-map.md` §3).
- Horizontal carving of single registers/words is not clean: the circuit layers
  are continuous (bus wiring runs through), so unit references are the vertical
  bit-slices above.

To inspect in-world: `//schem load <name>` then `//paste` (FAWE), or open
`world-mattbat-8bit` directly.

## Extracted component references (2026-07-06)

- **`alus/mattbat-alu-01..17.schem`** — all 17 standalone ALU designs from the
  "ALUs" world display strip, in strip order (west→east ≈ simple→advanced;
  04 is the big ~3,000-block build, 16/17 the tall late designs). Bounds from
  the offline survey, padded ±2.
- **`registers/mattbat-reg-01..10.schem`** — the 10 build clusters from the
  "Registers" world strip, in strip order (north→south). 01–03 are the large
  display-scale registers; 04–10 the smaller variants. reg-03 and reg-10 are
  wide clusters that may contain more than one adjacent design — split
  in-world if needed.

- **`pc/mattbat-pc-01..03.schem`** — the teaching-scale counter builds from
  CPU Episode 6 (the program-counter episode, per Fielding). pc-02 is the full
  PC (1,299 blocks, 91 repeaters + 53 comparators); pc-01/03 are slim counter
  towers (pc-01 uses 8 target blocks — unusual vocabulary, worth a look).
- **`ep5/mattbat-ep5-{line,array,spawn}.schem`** — CPU Episode 5 = **RAM**
  (confirmed by Fielding). `array` = small comparator-free memory-cell teaching
  piece (664 blocks); `spawn` = the RAM bank itself, 15k blocks: address/data
  bus plane feeding the layered cell bank (1,188 repeaters, 590 comparators);
  `line` = 262-block 16-lane bus bundle (960 repeaters, zero comparators).

- **`branch/mattbat-br-01..05.schem`** — CPU Episode 7 (**jumping/branching**)
  teaching builds. br-02..05 are block-identical copies (1,443 blocks, 100
  repeaters + 73 comparators — likely the same condition unit shown at
  successive lecture stages); br-01 is the slightly larger first version.
  Course fit: Module 7 flags + Module 12b JMP/JIZ comparisons.
- **`io/mattbat-io-01..05.schem`** — CPU Episode 10 (**input and output**)
  teaching builds. io-02 is a 16×16 lamp screen (256 lamps + 256 torches +
  64 levers, zero comparators); io-01 is comparator-dense port/encoder logic
  (300 comparators); io-03/04 small drivers; io-05 a dense repeater driver
  (209 repeaters). Course fit: Module 1 input panel, Module 4 display,
  Module 13 BCD output.

Exporters: `minecraft-agents/tools/ru-testbench/export_alus.js` /
`export_registers.js` / `export_boxes.js` (generic; offline-survey bounds →
FAWE `//copy` + `//schem save`). Survey tools: `survey2d.js` (per-block, any
1.20+ world), `survey_palette.js` (any version, section granularity). The episode worlds' big ~92k-block complexes
(machine-so-far states) were NOT extracted — render those straight from their
worlds via MiEx for "machine at stage N" figures.

## Additional source worlds (downloaded 2026-07-06)

Standalone component worlds from mattbatwings' newer tutorial series, unpacked
in `~/Downloads/`. Build bounds found by offline region scan
(`minecraft-agents/tools/ru-testbench/survey_offline.js` /
`survey_palette.js`):

| World | Version | Layout |
| :-- | :-- | :-- |
| `ALUs by mattbatwings` | 1.20.4 | 17 separate ALU designs in a strip x[−6..503], z[−80..−51], y[60..86] — small demos (~340 blocks) up to full ALUs (~3,000 blocks at x[65..101]) |
| `Registers by mattbatwings` | 1.18.2 | Register-design strip x[16..143], z[−624..−65], y[48..111] (section-granularity bounds; prismarine per-block parse fails on this version — use palette scanner or load in-world) |
| `CPU Episode 5` | 1.20.4 | Progressive CPU checkpoints along −z: five large complexes at z[−824..−686], [−635..−497], [−446..−376], [−333..−263], [−220..−150], x[−279..9] plus small lecture demos near spawn |
| `CPU Episode 6` | 1.20.4 | Three large checkpoints: z[−620..−482], [−415..−277], [−87..51], x[−129..14], plus small demos |

These are the better extraction source for single-component references (clean,
isolated designs vs. carving the integrated 8-bit machine). To extract: swap
server `LEVEL` in `minecraft-agents/docker-compose.yml`, restart, survey the
strip in-world to split individual builds, then FAWE `//copy` + `//schem save`.
