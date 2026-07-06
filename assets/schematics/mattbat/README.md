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

## Additional source worlds (downloaded 2026-07-06, not yet extracted)

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
