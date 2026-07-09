# Minecraft figure build list — Parts II–IV

Part I is complete (figures live). Every module below currently has **zero**
Minecraft figures. Fielding hand-builds each artifact in the Bedrock circuit
lab; the bot only verifies/references. Build in dependency order — later
builds reuse earlier ones.

Figure tiers (see `renders/STYLE.md`):
- **small** — single component, **iso** only (e.g. a gate)
- **medium** — multi-component, **iso + top**
- **large** — full assembly, **iso + top** with the **color-coded composition
  legend**

Ground: always `remove` (keep the substrate the redstone rests on, drop the
floor + margin). Build on base blocks with a decorative floor below, like Part I.

## Part II — The Thinking Machine

- [ ] **M5** — 1-bit full adder — *small*
- [ ] **M5** — 4-bit ripple-carry adder — *medium*
- [ ] **M5** — hexadecimal display — *medium*
- [ ] **M6** — 4-bit adder/subtractor + carry/overflow lamp — *medium*
- [ ] **M7** — 4-bit equality comparator — *medium*
- [ ] **M7** — 2-bit status-flag circuit — *small*
- [ ] **M8** — 4-bit 2:1 multiplexer — *medium*
- [ ] **M9** — complete 4-bit ALU — *large (color-coded)*

## Part III — The Processor Core

- [ ] **M10** — 4-bit scratchpad register + STORE + 2-bit flag latch — *medium*
- [ ] **M11** — 16×4 RAM — *large (color-coded)*
- [ ] **M12a** — controllable clock — *small*
- [ ] **M12a** — 4-bit Program Counter — *medium*
- [ ] **M12a** — 3-phase sequencer — *medium*
- [ ] **M12a** — IR, AR, Register B (3 registers) — *small ×3*
- [ ] **M12b** — complete machine running the countdown — *large (color-coded)*

## Part IV — Post-Graduate

- [ ] **M13** — binary→BCD (double-dabble) + 2-digit decimal display — *medium→large*

## Compact-design arc (the "both versions" builds)

The legible→compact→stack teaching arc (drafted in M9 Lesson 9.5). Where used,
the module gets **three** builds instead of one:

- [ ] **M9** — legible 1-bit ALU slice — *small*
- [ ] **M9** — compact 1-bit slice (2-tall) — *small/medium, iso + top*
- [ ] **M9** — stacked 4-bit compact ALU — *large*
- [ ] **M5** — (optional) compact adder alongside the legible one
- [ ] **M11** — (optional) RAM bit-plane slice, if the slice idea is reused

## Per-figure handoff

For each build, tell the bot the world coordinates (or frame it in MiEx as
before). The bot then: adds the `shots.json` entry → runs `shots.py` → copies
the PNG into `src/<part>/<module>/images/` → references it in `draft.md`.
