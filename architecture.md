# Redstone University Machine — Architecture Reference (RU-v1)

> **Purpose:** Single source of truth for the machine. The module drafts must conform to this document; when they disagree, correct this doc first, then the drafts.
> **Status:** DRAFT — items marked ⚠ OPEN are unverified against the in-world build. Signal names not found in the drafts are invented here and marked ⚠.

---

## 1. Overview

RU-v1 is a 4-bit, two-register, accumulator-style stored-program computer. A 16×4 RAM holds both program and data (von Neumann, unified memory). Instructions are 8 bits, fetched as two nibbles (opcode, then argument) across a 4-bit bus, driven by a three-phase one-hot sequencer (T0 fetch opcode, T1 fetch argument, T2 execute). The ALU computes AND/OR/XOR/ADD/SUB in parallel lanes; only ADD/SUB are exposed by the ISA. Z and N flags are latched into a 2-bit Flag Register by ADD/SUB and consumed by JIZ.

```
                 Manual ADDR levers (Program mode)
                          |
   PC ──────┐        ┌────▼─────────┐
   (4-bit)  ├─[RAM ADDR SEL]──► RAM 16×4 ──► Memory Output Bus ─┬─► IR ⚠ (4-bit, opcode)
   AR ──────┘             ▲    │  ▲                             ├─► AR ⚠ (4-bit, argument)
    ▲                     │    │  └─[RAM DATA-IN SEL]◄── Reg A  ├─► [REG A IN SEL]
    │ (loaded at T1)      │    │           ▲                    └─► [REG B IN SEL]
    │                     │    │     Manual DATA levers
   [PC IN SEL]◄── AR      │    │
    ▲   ▲                 │    ▼ (read = gated-OR dust-merge bus)
    │   └── increment     │
   IR ─► Control Decoder ─┴─► all selector/strobe lines (per phase T0/T1/T2)
            ▲
   Flag Reg (Z,N) ◄─latch─ ALU flags (Z=NOR4, N=Y3)
            │                  ▲
            └─(JIZ)      ALU ◄─┴─ Bus A = Reg A out, Bus B = Reg B out
                          │
                  ALU Result Bus ─► [REG A IN SEL] ─► Reg A ─► hex display / RAM data-in
```

## 2. Registers

| Name | Width | Built in | Write enable | Notes |
| :-- | :-- | :-- | :-- | :-- |
| Reg A (scratchpad/accumulator) | 4 | Module 10 (Lab B) | `LD_A` (pulse-limited STORE) | Repeater-locking latch; STORE inverted by torch internally. Feeds ALU Bus A, RAM data-in, display. |
| Reg B | 4 | ⚠ OPEN — never explicitly built; Module 10 builds *one* scratchpad register | `LD_B` ⚠ | Implied by ALU (Bus B) and `LDB`/`LDI B`. Presumably a second copy of the Module 10 register; no lab instructs it. |
| Flag Register (Z, N) | 2 | Module 10 (Lab C) | `LD_F` (draft name: **FLAGS STORE**) | Latches live Z/N from ALU. Holds "previous arithmetic result" for JIZ. |
| PC | 4 | Module 12a.2 | `PC_INC`, `PC_LOAD`, `RESET` | Synchronous toggle counter (repeater-locking cells + carry chain), 2:1 load selector per bit. Hold/increment/load/reset. |
| IR (Instruction Register) | 4 | ⚠ OPEN — referenced in 12a.5 fetch cycle and key terms, **never built in any module**. Must be added, probably 12a. | `LD_IR` ⚠ invented name | Holds opcode nibble; feeds decoder. |
| AR (Argument Register) | 4 | ⚠ OPEN — same as IR; never built. | `LD_AR` ⚠ invented name | Holds argument nibble; feeds RAM addr selector, PC load path, Reg A/B input selectors. |
| Phase ring (T0/T1/T2) | 3 (one-hot) | Module 12a.3 | clock pulse; RESET → `100` | Three repeater-locking stages in a loop. Optional T3 extension for Bedrock STA timing. |

## 3. Memory

| Property | Value |
| :-- | :-- |
| Organization | 16 locations × 4 bits (16 copies of the Module 10 register) |
| Addressing | 4-bit Address Bus → reused 4-to-16 display decoder (active-low) → per-line torch inverter bank → active-high `Select 0..F` |
| Write path | `RowWrite_i = Select_i AND WRITE`; WRITE is a short pulse (pulse limiter, Module 10); inverted internally at each row's lock repeaters |
| Read path | Per-bit gated-OR: row bit AND row select, merged per bit position (physically a dust merge with one-way elements) → 4-bit **Memory Output Bus** |
| Address sources | PC (fetch), AR (execute for LDA/LDB/STA), manual Address levers (Program mode) — see §6 |
| Data-in sources | Reg A (STA), manual Data levers (Program mode) |

## 4. ALU (Module 9)

Inputs: **Bus A** (= Reg A output in the integrated machine), **Bus B** (= Reg B output). Four parallel lanes; two-stage MUX tree selects the **ALU Result Bus** (F0 → first-stage MUXes, F1 → final MUX).

| F1 | F0 | SUB | Operation | Flags produced (combinational) | Used by ISA? |
| :-: | :-: | :-: | :-- | :-- | :-- |
| 0 | 0 | x | AND | Z, N | no |
| 0 | 1 | x | OR | Z, N | no |
| 1 | 0 | x | XOR | Z, N | no |
| 1 | 1 | 0 | ADD | Z, N (+ carry lamp, diagnostic) | `ADD` |
| 1 | 1 | 1 | SUB | Z, N (+ carry lamp, diagnostic) | `SUB` |

⚠ OPEN: the ISA never selects AND/OR/XOR. Are F1/F0 hardwired to `11` in the integrated machine, driven by the decoder, or left on the Module 9 front-panel levers? Draft 12b.2 says the decoder drives only "ALU mode (ADD or SUB)" — i.e., the `SUB` line.

## 5. Flags

| Flag | Set by (combinational source) | Latched when | Consumed by |
| :-- | :-- | :-- | :-- |
| Z (Zero) | 4-input NOR of ALU Result Bus `Y3..Y0` (Module 7) | `LD_F` pulse during T2 of **ADD** and **SUB** only (12b.1) | `JIZ` (latched value, not live) |
| N (Negative) | Wire from `Y3` (MSB) | Same `LD_F` pulse | Nothing in RU-v1 ISA (no JIN instruction); display/debug only |
| Carry/Overflow lamp | Final `CarryOut` of arithmetic lane (Module 6) | **Never latched** — live diagnostic lamp only (Module 9 calls it "optional diagnostic output") | Nothing; not a flag, not in ISA |

⚠ OPEN: timing of `LD_F` relative to `LD_A` — see §7 and Open Question 5. The countdown program's correctness depends on this.

## 6. Buses & selector networks (12a.4 — "the five routing decisions")

The drafts name the five selectors but give **no control truth tables or encodings**. All encodings below are proposed defaults — every table in this section is ⚠ OPEN.

**S1. Register A input selector** (4:1, one input unused)

| `SelA` ⚠ | Source | Used by |
| :-: | :-- | :-- |
| 00 | Memory Output Bus | LDA |
| 01 | AR (argument nibble) | LDI A |
| 10 | ALU Result Bus | ADD, SUB |
| 11 | (unused) | — |

**S2. Register B input selector** (2:1)

| `SelB` ⚠ | Source | Used by |
| :-: | :-- | :-- |
| 0 | Memory Output Bus | LDB |
| 1 | AR | LDI B |

**S3. RAM address selector** — draft describes it as PC-vs-AR *plus* a Program-mode override to the manual Address levers, i.e. effectively **three** sources. Structure (3:1, or 2:1 cascaded with a MODE-controlled 2:1) is ⚠ OPEN.

| MODE | `SelMemAddr` ⚠ | Address source |
| :-- | :-: | :-- |
| Program | x | Manual Address levers |
| Run | 0 | PC (T0, T1) |
| Run | 1 | AR (T2 of LDA, LDB, STA) |

**S4. PC input selector** (per-bit 2:1, built into the PC in 12a.2)

| `SelPC` ⚠ | Source |
| :-: | :-- |
| 0 | Increment path (toggle/carry chain) |
| 1 | Load path from AR (12a.2 says "the bus", 12a.4 "argument bus", 12b "AR" — taken to mean AR output) |

**S5. RAM data-in selector** (2:1)

| MODE | `SelMemIn` ⚠ | Source |
| :-- | :-: | :-- |
| Program | x | Manual Data levers |
| Run | — | Reg A (STA) |

## 7. Timing

- **Clock** (12a.1): free-running repeater loop, gated by **RUN/HALT** lever; **STEP** injects one pulse while halted; **RESET** forces PC=`0000` and phase ring to T0 (does not clock the machine).
- **Phase sequencer** (12a.3): 3-stage one-hot ring counter, advances one stage per clock pulse: T0 → T1 → T2 → T0. Optional T3 (Bedrock) if STA needs a separate write phase (12b.3 note).
- All register/RAM writes are **brief pulse-limited strobes**, not level enables (12b.2), because the storage is level-sensitive repeater locking.

| Phase | Action |
| :-- | :-- |
| T0 (fetch opcode) | RAM addressed by PC; Memory Output Bus → IR (`LD_IR` ⚠); PC increments |
| T1 (fetch argument) | RAM addressed by PC; Memory Output Bus → AR (`LD_AR` ⚠); PC increments |
| T2 (execute) | Decoder fires opcode-specific strobes per §9 |

⚠ OPEN — intra-phase ordering, T0/T1: must be *RAM read settles → IR/AR latch → PC increments*. If PC increments before the latch closes, the wrong nibble is captured. Drafts list the steps but never sequence them.

⚠ OPEN — intra-phase ordering, T2 of ADD/SUB. Proposed: **ALU settles → Reg A loads → flag latch stores**. **Hazard:** flags are combinational on the ALU result; once Reg A captures the new value, the ALU re-settles to (newA op B) and the flags change. If `LD_F` fires after that re-settle, the latched Z is wrong and the countdown loop never terminates (when A reaches 0: A←0, ALU recomputes 0−1=F, Z=0 latched, JIZ falls through forever). Safe options: (a) fire `LD_A` and `LD_F` from the same strobe, narrower than the Reg A→ALU→flag round-trip delay; (b) latch flags strictly before/with Reg A write-back. The drafts are silent; the in-world build's actual ordering must be recorded here.

## 8. Instruction set (RU-v1, 12b.1)

Instructions are 8 bits = opcode nibble + argument nibble at **two consecutive RAM addresses**; opcodes sit at even addresses `0,2,4,6,8,A,C,E`; jump targets must be even (opcode) addresses. ADD/SUB/HLT/NOP still occupy two cells; the second nibble is ignored.

| Opcode | Mnemonic | Operand | Description | Flags |
| :-: | :-- | :-- | :-- | :-- |
| `0` | NOP | ignored | Do nothing | — |
| `1` | LDA | addr | Reg A ← RAM[addr] | — |
| `2` | LDB | addr | Reg B ← RAM[addr] | — |
| `3` | STA | addr | RAM[addr] ← Reg A | — |
| `4` | ADD | ignored | A ← A + B | Z, N latched |
| `5` | SUB | ignored | A ← A − B | Z, N latched |
| `6` | JMP | addr | PC ← addr | — |
| `7` | JIZ | addr | PC ← addr if latched Z = 1 | — (reads Z) |
| `8` | LDI A | data | A ← data | — |
| `9` | LDI B | data | B ← data | — |
| `F` | HLT | ignored | Stop the clock | — |

⚠ OPEN: opcodes `A`–`E` are undefined. Proposed default: decode as NOP. Drafts are silent.

## 9. Control matrix

One row per (instruction × phase). T0 and T1 are identical for all instructions. Signal names: `SelMemAddr/SelA/SelB/SelMemIn/SelPC` per §6 (⚠ proposed encodings); `LD_IR`/`LD_AR`/`HALT_SET` ⚠ invented (IR/AR never built); `LD_A`/`LD_B` = register STORE pulses, `LD_F` = FLAGS STORE, `RAM_WR` = WRITE pulse, `ALU_SUB` = Module 9 `SUB` line. "•" = strobe fires; "–" = inactive/don't-care. Run mode assumed throughout (Program mode overrides per §10).

| Instr | Phase | SelMemAddr | SelA | SelB | SelMemIn | SelPC | LD_IR | LD_AR | LD_A | LD_B | LD_F | PC_INC | PC_LOAD | RAM_WR | ALU_SUB | HALT_SET |
| :-- | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| (all) | T0 | PC | – | – | – | – | • | – | – | – | – | • | – | – | – | – |
| (all) | T1 | PC | – | – | – | – | – | • | – | – | – | • | – | – | – | – |
| NOP | T2 | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – |
| LDA | T2 | AR | RAM | – | – | – | – | – | • | – | – | – | – | – | – | – |
| LDB | T2 | AR | – | RAM | – | – | – | – | – | • | – | – | – | – | – | – |
| STA | T2 | AR | – | – | RegA | – | – | – | – | – | – | – | – | • | – | – |
| ADD | T2 | – | ALU | – | – | – | – | – | • | – | • | – | – | – | 0 | – |
| SUB | T2 | – | ALU | – | – | – | – | – | • | – | • | – | – | – | 1 | – |
| JMP | T2 | – | – | – | – | AR | – | – | – | – | – | – | • | – | – | – |
| JIZ (Z=1) | T2 | – | – | – | – | AR | – | – | – | – | – | – | • | – | – | – |
| JIZ (Z=0) | T2 | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – |
| LDI A | T2 | – | AR | – | – | – | – | – | • | – | – | – | – | – | – | – |
| LDI B | T2 | – | – | AR | – | – | – | – | – | • | – | – | – | – | – | – |
| HLT | T2 | – | – | – | – | – | – | – | – | – | – | – | – | – | – | • |

⚠ OPEN: F1/F0 column omitted — assumed hardwired `11` (arithmetic lane) per §4.
⚠ OPEN: `HALT_SET` mechanism (latch that forces the clock gate off?) and how it composes with the RUN/HALT lever / how to resume after HLT — unspecified in drafts.

**Countdown sanity check** (12b.4 program, RAM[E]=5): T0/T1 fetch per row above; `LDA [E]`→A=5; `LDI B,1`→B=1; `SUB`→A=4, Z=0 latched; `STA [E]`→RAM[E]=4; `JIZ [C]` reads latched Z=0, falls through; `JMP [4]` loops to SUB. Iterates A=4,3,2,1; when SUB produces 0, Z=1 is latched, STA writes 0, JIZ jumps to `C`, HLT stops the clock. **Executes correctly under this matrix — but only if `LD_F` captures the pre-writeback flags (Open Question 5).** Note also that "a display attached to RAM[E]" (12b.4) implies tapping row E's stored bits directly, since the shared Memory Output Bus only shows the currently addressed row.

## 10. Front panel & modes (12a.5)

Controls: **MODE** lever (Program/Run), 4 **Address** levers, 4 **Data** levers, **WRITE** button (pulse-limited), **RESET** button, **RUN/HALT** lever, **STEP** button. (Module 9's F1/F0/SUB levers: fate in integrated machine ⚠ OPEN, see §4.)

| Resource | Program mode | Run mode |
| :-- | :-- | :-- |
| RAM address selector (S3) | Manual Address levers (override) | PC (T0/T1) / AR (T2) per decoder |
| RAM data-in selector (S5) | Manual Data levers | Reg A (STA) |
| RAM WRITE | Front-panel WRITE button (gated to Program mode only — 12a.5 safety rule) | Decoder STA strobe at T2 |
| Decoder STA strobe | ⚠ OPEN — presumably blocked, unspecified | Active |
| Clock / sequencer / PC | ⚠ OPEN — presumably held/halted in Program mode; drafts never say MODE gates the clock | Free-running or stepped |
| Reg A/B selectors, PC selector | ⚠ OPEN — unaffected by MODE? unspecified | Per decoder |

⚠ OPEN: the exact gating of each selector and strobe by the MODE lever is unspecified everywhere except S3, S5, and the WRITE button.

## 11. Open questions

1. **IR and AR are never built.** 12a.5 and 12b assume them (fetch cycle, decoder input, key terms), but no lab constructs them. Decide: add a build lab (proposed: new section in 12a, two more Module 10 registers with `LD_IR`/`LD_AR` strobes) — affects `12a_…/draft.md` Lesson 12a.5 and 12b.2.
2. **Reg B is never explicitly built.** Module 10 builds one scratchpad register; 12a.4/12b assume Registers A *and* B. Decide where the second register is instructed — affects `10_…/draft.md` Lab B or 12a.
3. **No selector truth tables.** All five selector encodings in §6 are invented. Record the real encodings/wiring from the in-world build — affects `12a_…/draft.md` Lesson 12a.4.
4. **RAM address selector arity.** Draft says PC-vs-AR plus a Program-mode override = three sources. Decide the physical structure (3:1 vs cascaded 2:1) — affects 12a.4/12a.5.
5. **Flag-latch timing vs Reg A load (critical).** The proposed T2 ordering "ALU settles → Reg A loads → flag latch stores" breaks the countdown loop if `LD_F` fires after the ALU re-settles on the new A (Z latches 0, JIZ never taken). Decide the real strobe ordering/width — affects `10_…/draft.md` Lab C, 12b.2, 12b.4.
6. **MODE gating.** Specify how the MODE lever gates each selector and strobe, and whether Program mode halts the clock / freezes PC and the sequencer — affects 12a.5.
7. **F1/F0 in the integrated machine.** Hardwired `11`, decoder-driven, or front-panel levers retained? The decoder spec (12b.2) only mentions the `SUB` line — affects 9 and 12b.2.
8. **Carry/overflow lamp.** Confirm it remains a live diagnostic only (Modules 6/9), never latched and never consumed; Module 7 states the machine uses only Z and N. If so, say it explicitly in 12b.
9. **Undefined opcodes `A`–`E`.** Decide behavior (proposed: NOP) — affects 12b.1.
10. **HLT mechanism and resumption.** How `HALT_SET` interacts with the RUN/HALT lever; how to restart after HLT (RESET only?) — affects 12a.1, 12b.
11. **Intra-phase ordering of fetch.** RAM-settle → IR/AR latch → PC increment within T0/T1 is required but never stated — affects 12a.5.
12. **Final display.** 12b.4 offers "display attached to RAM[E]" or "debug display attached to Register A"; Module 10 wires Reg A to the hex display. Decide the canonical display tap (note: showing RAM[E] requires tapping row E directly, not the shared read bus) — affects 12b.4.
13. **PC load source naming.** 12a.2 "load bus" / 12a.4 "argument bus" / 12b "AR" — confirm all three mean the AR output and unify the term.
