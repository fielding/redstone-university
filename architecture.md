# Redstone University Machine — Architecture Reference (RU-v1)

> **Purpose:** Single source of truth for the machine. The module drafts must conform to this document; when they disagree, correct this doc first, then the drafts.
> **Status:** COMPLETE — all 13 open questions are resolved (§11). Items marked ✅ RESOLVED were verified against the in-world testbench build (integration campaign, 2026-07-05; evidence trail in tix `ru-39f8f2`, summary in `docs/project-map.md` §5); items marked ✅ RESOLVED (design) were decided on paper 2026-07-12 with stated precedent (Ben Eater SAP-1 lineage for the front panel, decoder-driven control per the redstone tradition) — their in-world verification is folded into the Part III physical validation pass (tix `ru-114a6c`). Testbench status at resolution: all components verified standalone; integrated machine passes fetch 5/5 and executes LDI A, LDI B, HLT end-to-end.

---

## 1. Overview

RU-v1 is a 4-bit, two-register, accumulator-style stored-program computer. A 16×4 RAM holds both program and data (von Neumann, unified memory). Instructions are 8 bits, fetched as two nibbles (opcode, then argument) across a 4-bit bus, driven by a three-phase one-hot sequencer (T0 fetch opcode, T1 fetch argument, T2 execute). The ALU computes AND/OR/XOR/ADD/SUB in parallel lanes; only ADD/SUB are exposed by the ISA. Z and N flags are latched into a 2-bit Flag Register by ADD/SUB and consumed by JIZ.

```
                 Manual ADDR levers (Program mode)
                          |
   PC ──────┐        ┌────▼─────────┐
   (4-bit)  ├─[RAM ADDR SEL]──► RAM 16×4 ──► Memory Output Bus ─┬─► IR (4-bit, opcode)
   AR ──────┘             ▲    │  ▲                             ├─► AR (4-bit, argument)
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
| Reg B | 4 | ✅ RESOLVED — built in the testbench as a second Module 10 register; captures correctly (`LDI B` executes end-to-end). Build lab: Lesson 12a.4 (fetch registers, written 2026-07-06). | `LD_B` | Second copy of the Module 10 register, confirmed workable. Feeds ALU Bus B. |
| Flag Register (Z, N) | 2 | Module 10 (Lab C) | `LD_F` (draft name: **FLAGS STORE**) | Latches live Z/N from ALU. Holds "previous arithmetic result" for JIZ. |
| PC | 4 | Module 12a.2 | `PC_INC`, `PC_LOAD`, `RESET` | Synchronous toggle counter (repeater-locking cells + carry chain), 2:1 load selector per bit. Hold/increment/load/reset. |
| IR (Instruction Register) | 4 | ✅ RESOLVED — built in the testbench as a Module 10 register; fetch verified (captures opcodes from the Memory Output Bus, feeds the decoder; ops 8/9/15 decode). Build lab: Lesson 12a.4 (written 2026-07-06). | `LD_IR` | Holds opcode nibble; feeds decoder. |
| AR (Argument Register) | 4 | ✅ RESOLVED — same as IR: built and fetch-verified in the testbench (captures argument nibbles; feeds the Reg A/B input selectors — `LDI A`/`LDI B` execute). RAM-addr and PC-load consumers routed but not yet exercised. | `LD_AR` | Holds argument nibble; feeds RAM addr selector, PC load path, Reg A/B input selectors. |
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

✅ RESOLVED (design) — **F1/F0 are hardwired `11` (arithmetic lane) in the integrated machine; the decoder drives only the `SUB` line** (`ALU_SUB`), exactly as draft 12b.2 says. Module 9's F1/F0/SUB front-panel levers are retired at integration (they belong to the standalone Module 9 build; the integrated machine replaces the SUB lever with the decoder line and pins F1/F0). Precedent: decoder-driven ALU control is the norm in the redstone tradition (control-ROM rows drive the function lines); with a 2-operation ISA that reduces to one driven line plus two constants. The AND/OR/XOR lanes remain built and observable — they're teaching material and a reserved expansion seam (§12), not dead weight.

## 5. Flags

| Flag | Set by (combinational source) | Latched when | Consumed by |
| :-- | :-- | :-- | :-- |
| Z (Zero) | 4-input NOR of ALU Result Bus `Y3..Y0` (Module 7) | `LD_F` pulse during T2 of **ADD** and **SUB** only (12b.1) | `JIZ` (latched value, not live) |
| N (Negative) | Wire from `Y3` (MSB) | Same `LD_F` pulse | Nothing in RU-v1 ISA (no JIN instruction); display/debug only |
| Carry/Overflow lamp | Final `CarryOut` of arithmetic lane (Module 6) | **Never latched** — live diagnostic lamp only (Module 9 calls it "optional diagnostic output") | Nothing; not a flag, not in ISA |

✅ RESOLVED: timing of `LD_F` relative to `LD_A` — see §7. The register storage captures **on strobe release**, so the safe pattern is firing `LD_F` and `LD_A` from the same strobe while guaranteeing the *data* fans outlive the strobe fans (Open Question 5).

✅ RESOLVED (design) — **the carry/overflow lamp is a live diagnostic only, by deliberate design**: never latched, never consumed by any instruction. This is a real architectural choice, not an omission — many machines latch carry as a flag and branch on it (in the redstone tradition, BatPU-2's carry flag doubles as unsigned ≥). RU-v1 keeps the flag set to Z and N so the Flag Register stays a 2-bit Module 10 story; a carry flag is a natural extension exercise. 12b must state this explicitly (Open Question 8).

## 6. Buses & selector networks (12a.5 — "the five routing decisions")

The drafts name the five selectors but give **no control truth tables or encodings**. All five are now settled: S1/S2 ✅ RESOLVED from the testbench build; S3 ✅ RESOLVED (design) as the cascaded structure below; S4/S5 encodings recorded here as canonical (S4's PC side exercised across the fetch suite; the load path and S5's run path verify with JMP/STA in the Part III validation pass).

✅ RESOLVED — **S1/S2 are not binary-encoded MUX trees in the as-built machine.** They are **one-hot control rails driving per-source gated-OR merges**: each source bus passes through a per-bit AND gate (source bit AND its rail), and the gate outputs dust-merge at the register's input (the same gated-OR idiom as the RAM read path, §3). No encoder, no mux tree, and each rail has exactly one meaning — the control matrix (§9) drops directly onto them. Verified end-to-end for the AR paths (`LDI A`, `LDI B` execute); the Mem and ALU gate groups follow the identical pattern.

**S1. Register A input gating** (one-hot; default source = Memory)

| `SelA0` | `SelA1` | Source gated into Reg A | Used by |
| :-: | :-: | :-- | :-- |
| 0 | 0 | Memory Output Bus (via ~SelA0·~SelA1 gate) | LDA |
| 1 | 0 | AR | LDI A |
| 0 | 1 | ALU Result Bus | ADD, SUB |
| 1 | 1 | (never driven by the matrix) | — |

**S2. Register B input gating** (one-hot)

| `SelB` | Source gated into Reg B | Used by |
| :-: | :-- | :-- |
| 0 | Memory Output Bus (via ~SelB gate) | LDB |
| 1 | AR | LDI B |

**S3. RAM address selector** — ✅ RESOLVED (design): **two cascaded per-bit 2:1 stages.** Stage 1 (Run-mode source): PC vs AR on the `SelMemAddr` rail — this is exactly what the testbench built and fetch-verified (PC side exercised across the whole suite; AR side routed, verified with LDA/STA in Part III validation). Stage 2 (mode override): MODE selects Stage 1's output vs the manual Address levers. This is the structure Lesson 12a.5 already teaches, and it's the Ben Eater SAP-1 pattern (his 74LS157s select DIP switches vs the machine's address on the program/run switch). The testbench's shortcut — a manual address driver ORed into the live selector — is hereby retired as a known-bad idiom: it let the PC's output corrupt manually driven addresses (programming only worked with the PC reset). The cascade makes the override a true takeover. Expansion seam: a future bank-register stage sockets in as one more cascade level (§12).

| MODE | `SelMemAddr` | Address source |
| :-- | :-: | :-- |
| Program | x | Manual Address levers (Stage 2 override) |
| Run | 0 | PC (T0, T1) |
| Run | 1 | AR (T2 of LDA, LDB, STA) |

**S4. PC input selector** (per-bit 2:1, built into the PC in 12a.2)

| `SelPC` | Source |
| :-: | :-- |
| 0 | Increment path (toggle/carry chain) |
| 1 | Load path from AR (12a.2 says "the bus", 12a.4 "argument bus", 12b "AR" — taken to mean AR output) |

**S5. RAM data-in selector** (2:1)

| MODE | `SelMemIn` | Source |
| :-- | :-: | :-- |
| Program | x | Manual Data levers |
| Run | — | Reg A (STA) |

## 7. Timing

- **Clock** (12a.1): free-running repeater loop behind a single **clock-enable** AND: `CLK_EN = RUN lever AND NOT(HALT latch) AND MODE=Run` (✅ RESOLVED (design) — Open Questions 6/10). **STEP** injects one pulse when the free-running clock is disabled by the RUN lever; STEP is still blocked by the HALT latch and by Program mode (a halted machine is inert until RESET; a machine being programmed cannot be stepped). **RESET** forces PC=`0000`, phase ring to T0, and clears the HALT latch (does not clock the machine).
- **Phase sequencer** (12a.3): 3-stage one-hot ring counter, advances one stage per clock pulse: T0 → T1 → T2 → T0. Optional T3 (Bedrock) if STA needs a separate write phase (12b.3 note). Testbench note: the free-running ring verified standalone (7/7) but self-latched when first integrated (route taps + adjacency drove the phase nets); all integration bring-up was done with externally driven single-stepped phases. Course implication for 12a.3/12b.3: teach STEP-driven bring-up first and connect the free-running clock **last**, after every phase's behavior is verified. (Now taught: 12a.3 Integration Note, 12b.3 preface, 12b.4 bring-up step 7 — 2026-07-06.)
- All register/RAM writes are **brief pulse-limited strobes**, not level enables (12b.2), because the storage is level-sensitive repeater locking.

| Phase | Action |
| :-- | :-- |
| T0 (fetch opcode) | RAM addressed by PC; Memory Output Bus → IR (`LD_IR`); PC increments |
| T1 (fetch argument) | RAM addressed by PC; Memory Output Bus → AR (`LD_AR`); PC increments |
| T2 (execute) | Decoder fires opcode-specific strobes per §9 |

✅ RESOLVED — capture semantics (the key to all intra-phase ordering): the repeater-locking storage is transparent while its strobe is high and **captures on the strobe's falling edge** (unlock → follow → relock-captures). Two consequences, both verified in-world:

1. **T0/T1 fetch ordering** works with generous phase holds: RAM read settles *during* the strobe-high window and the latch captures the settled value at release. The ordering hazard is real but shows up as *settle-time* requirements, not sequencing circuitry: the RAM→bus→register path needs its full propagation time inside the phase window, and RAM writes need a data-settle window before the WRITE pulse (long data lanes drain slowly; a short settle writes the *previous* value's draining bits). Phase windows in the course build must be sized to the longest path, or the machine single-stepped.
2. **T2 of ADD/SUB — the data/strobe fall race.** Because capture happens at strobe *release*, the hazard is inverted from the draft's framing: whichever of {data fan, strobe fan} collapses first at T2's falling edge decides what gets captured. If the selector/data rails die before the register relocks, the register captures the collapse (observed live: a register captured all-zeros when its select rail fell ~simultaneously with its load strobe). **Safe pattern (as-built): fire `LD_A` and `LD_F` from the same T2 edge and add extra repeater delay to the *data*-side fans so data provably outlives the strobes.** This also resolves the flag hazard: Z/N are captured from the pre-writeback ALU result because the flag latch relocks before Reg A's new value can propagate back through the ALU (the writeback→ALU→flag round trip is much longer than the strobe-fall skew).

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

✅ RESOLVED (design) — opcodes `A`–`E` decode as NOP, **structurally**: they are empty control-matrix rows (§9). An opcode with no strobes dropped on its decoder line fires nothing at T2, so no state changes and the PC walks on — the same mechanism that makes unwritten memory (all zeros = NOP) harmless. 12b.1 already specifies this. The rows are physically reserved and never repurposed for routing (§12): adding a future instruction is dropping strobes onto an existing row. In-world spot-check (fetch an `A`–`E` opcode, assert no strobe fires) rides along in Part III validation.

## 9. Control matrix

One row per (instruction × phase). T0 and T1 are identical for all instructions. Signal names: `SelMemAddr/SelA/SelB/SelMemIn/SelPC` per §6 (canonical encodings); `LD_IR`/`LD_AR` canonical (built in Lesson 12a.4); `HALT_SET` = the HLT latch set line (§7); `LD_A`/`LD_B` = register STORE pulses, `LD_F` = FLAGS STORE, `RAM_WR` = WRITE pulse, `ALU_SUB` = Module 9 `SUB` line. "•" = strobe fires; "–" = inactive/don't-care. Run mode assumed throughout (Program mode overrides per §10).

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

F1/F0 column omitted **because hardwired `11`** (✅ RESOLVED, §4) — the matrix drives no ALU line except `ALU_SUB`.
`HALT_SET` ✅ RESOLVED: a **latch**, verified in the testbench (op15 decode sets it and it holds). Its inverted output is one input of the clock-enable AND (§7): `CLK_EN = RUN AND NOT(HALT latch) AND MODE=Run`. Composition with the RUN/HALT lever is a plain AND — the lever and the latch each independently stop the clock. **Resumption is RESET-only**: RESET clears the latch (and zeroes the PC), so a halted program restarts from the top; there is no un-halt toggle. Precedent: the redstone tradition's HLT is likewise "decode line stops the clock, reset to resume" — ours differs only in latching the stop (their PC parks on the HLT instruction, holding the line level; our multiphase machine latches at T2 instead, which the testbench confirmed works).

**Countdown sanity check** (12b.4 program, RAM[E]=5): T0/T1 fetch per row above; `LDA [E]`→A=5; `LDI B,1`→B=1; `SUB`→A=4, Z=0 latched; `STA [E]`→RAM[E]=4; `JIZ [C]` reads latched Z=0, falls through; `JMP [4]` loops to SUB. Iterates A=4,3,2,1; when SUB produces 0, Z=1 is latched, STA writes 0, JIZ jumps to `C`, HLT stops the clock. **Executes correctly under this matrix — the flag hazard is resolved by the capture-on-release timing pattern in §7 (same-strobe `LD_A`/`LD_F`, data outlives strobe).** Note also that "a display attached to RAM[E]" (12b.4) implies tapping row E's stored bits directly, since the shared Memory Output Bus only shows the currently addressed row. Testbench status: this matrix decodes and executes correctly for the verified rows (all-T0/T1 fetch, LDI A, LDI B, HLT).

## 10. Front panel & modes (12a.6)

Controls: **MODE** lever (Program/Run), 4 **Address** levers, 4 **Data** levers, **WRITE** button (pulse-limited), **RESET** button, **RUN/HALT** lever, **STEP** button. (Module 9's F1/F0/SUB levers are retired at integration — F1/F0 pinned `11`, SUB decoder-driven; see §4.)

✅ RESOLVED (design) — **MODE gates exactly four things**, and nothing else needs gating:

| Resource | Program mode | Run mode |
| :-- | :-- | :-- |
| RAM address selector (S3, Stage 2) | Manual Address levers | Stage 1 output: PC (T0/T1) / AR (T2) per decoder |
| RAM data-in selector (S5) | Manual Data levers | Reg A (STA) |
| RAM WRITE source | Front-panel WRITE button (pulse-limited) | Decoder STA strobe at T2 |
| Clock enable (§7) | **Held low** — clock, sequencer, and PC all freeze | `RUN AND NOT(HALT latch)` |
| Reg A/B selectors, PC selector, all `LD_*` strobes | **Ungated** — see below | Per decoder |

The WRITE row is one 2:1 on the write-pulse source (button vs decoder strobe), so each mode's write path excludes the other's — the 12a.6 safety rule (panel button dead in Run mode) and the STA lockout (decoder strobe dead in Program mode) are the two sides of the same selector. This is the Ben Eater SAP-1 front panel verbatim: his program/run switch drives three 74LS157 muxes — address, data-in, and write source — and nothing else.

Why the last row needs no gating: every register strobe and selector rail is generated by the decoder **from a phase pulse**, and Program mode holds the clock, so the sequencer never advances and no strobe can fire. Level-driven paths into RAM (address, data-in, write) are the only ones a frozen sequencer doesn't protect — which is exactly the set MODE muxes. One deliberate divergence from Ben Eater: he leaves his clock free-running during programming (his modules tolerate it); we gate it, because the testbench demonstrated the failure mode (a live PC ORed into manually driven addresses corrupted programming until the PC was reset) and because "the machine is off while you're inside its memory" is the cleaner thing to teach.

## 11. Open questions

1. ✅ RESOLVED — **IR and AR** built and fetch-verified in the testbench as Module 10 registers with `LD_IR`/`LD_AR` strobes. Editorial remainder done 2026-07-06: Lesson 12a.4 (fetch registers) builds IR, AR, and Reg B; the fetch cycle (12a.6) and 12b now reference built components.
2. ✅ RESOLVED — **Reg B**: a second Module 10 register works as-is (verified via `LDI B`). Lab lands in Lesson 12a.4 (2026-07-06); Module 10 Lab B carries a forward pointer.
3. ✅ RESOLVED for S1/S2 — the as-built machine uses **one-hot rails + per-source gated-OR merges**, not binary mux encodings (§6, recorded from the in-world build). Drafts updated 2026-07-06: Lesson 12a.5 teaches one-hot gating/gated-OR for register inputs. S3–S5 encodings recorded in §6 (2026-07-12).
4. ✅ RESOLVED (design, 2026-07-12) — **RAM address selector structure**: the cascaded form is canonical — Stage 1 per-bit 2:1 (PC vs AR, `SelMemAddr`; Stage 1 is testbench-built and PC-side-verified), Stage 2 per-bit 2:1 (MODE: machine vs manual levers). Already what 12a.5 teaches; §6/S3 updated. The testbench's ORed-in manual driver is retired as a known-bad idiom (live PC corrupted manual addresses). AR side + Stage 2 verify in Part III validation (`ru-114a6c`). Expansion seam: bank-register stage cascades in later (§12).
5. ✅ RESOLVED — **Flag-latch timing vs Reg A load.** The storage captures on strobe *release* (§7), which inverts the hazard: the danger is the data fan collapsing before the strobe fan at T2's falling edge, not post-writeback flag re-settling. As-built safe pattern: `LD_A` and `LD_F` fire from the same T2 edge, with added repeater delay on the data-side fans so data provably outlives the strobes. Verified live (a same-edge race captured zeros until the data-fan delay was added). Drafts now teach it explicitly (2026-07-06): Module 10 Lesson 10.3 ("capture on release") + Lab C note, 12b.2 strobe rule, checkpoint questions in both modules.
6. ✅ RESOLVED (design, 2026-07-12) — **MODE gating**: MODE gates exactly four things — S3 Stage 2 (address source), S5 (data-in source), the WRITE-pulse source (panel button vs decoder STA strobe, one 2:1), and the clock enable (Program mode holds clock, sequencer, and PC). All other selectors and strobes are decoder-generated from phase pulses and need no gating: a held clock means no strobe ever fires. Template: Ben Eater's SAP-1 program/run switch (three 74LS157 muxes: address, data-in, write); we add the clock gate because the testbench demonstrated the live-PC corruption mode. Spec in §7/§10; verify in `ru-114a6c`.
7. ✅ RESOLVED (design, 2026-07-12) — **F1/F0 hardwired `11`; decoder drives only `ALU_SUB`;** Module 9's front-panel ALU levers retire at integration. Matches 12b.2's existing decoder spec. Precedent: decoder-driven ALU control (control-ROM rows drive function lines), degenerate case for a 2-op ISA. §4/§9/§10 updated.
8. ✅ RESOLVED (design, 2026-07-12) — **Carry/overflow lamp stays a live diagnostic**: never latched, never consumed, as a deliberate contrast with carry-flag machines (e.g. BatPU-2, where latched carry doubles as unsigned ≥). Z/N-only keeps the Flag Register a 2-bit story. Stated in §5; 12b must say it explicitly (draft task).
9. ✅ RESOLVED (design, 2026-07-12) — **Undefined opcodes `A`–`E` are structural NOPs**: empty control-matrix rows fire no strobes, so nothing changes state and PC walks on — same mechanism that makes all-zero memory harmless. Rows stay physically reserved (§12). In-world spot-check rides with `ru-114a6c`.
10. ✅ RESOLVED (2026-07-12; latch testbench-verified 2026-07-05) — **HLT**: `HALT_SET` is a latch set at T2 of op15; its inverted output ANDs into the clock enable alongside the RUN/HALT lever and MODE (`CLK_EN = RUN AND NOT(HALT) AND MODE=Run`). **Resumption is RESET-only** (RESET clears the latch and zeroes the PC); no un-halt toggle. §7/§9 updated; affects 12a.1, 12b.
11. ✅ RESOLVED (2026-07-12; capture semantics testbench-verified) — **Intra-phase fetch ordering** is a settle-time budget, not sequencing circuitry (§7). Everything actionable is done: capture-on-release verified in-world, phase-width rule taught in 12a.6, strobe rule in 12b.2. Course builds size phase windows to the longest path or single-step.
12. ✅ RESOLVED (design, 2026-07-12) — **Final display**: the flagship build's canonical output is the **Reg A hex display** (wired since Module 10, and the countdown's live value is in Reg A anyway). The RAM[E] direct-row-tap display stays what 12b.4 already frames it as: an optional extension with the tap requirement explained. No further decision pending.
13. ✅ RESOLVED (editorial, 2026-07-06) — **PC load source naming.** All three terms meant the AR output; drafts unified on "Argument Register (AR) output" (12a.2 load path, 12a.5 selector 4, 12b).

## 12. Expansion contracts

RU-v1 ends at Part III: the machine above, complete, running its program. **None of the expansions below are v1 work.** This section exists so that v1's *layout* never forecloses them — each contract is a constraint on how we build, not on what we build. (Decision 2026-07-12; future-track outline in tix `ru-53d617`.)

The binding fact behind all of them: the 4-bit operand field means the ISA can name exactly 16 addresses and 16 opcodes. RAM capacity, register width, and instruction count are all cheap to grow physically (slice replication); the *naming* limits are the walls, and the seams below are where each wall opens.

1. **Reserved control-matrix rows.** Opcodes `A`–`E` stay physically empty decoder rows (structural NOPs, §9) — never repurposed for routing, cable runs, or support blocks. Adding an instruction later = dropping strobes onto an existing row, zero relayout.
2. **Buses on fixed pitch, slice direction declared.** All 4-bit buses and slice arrays (registers, ALU, RAM columns, selectors) keep uniform per-bit pitch, with the width-extension direction (where bits 4–7 would go) declared in the build docs and kept clear. Widening to 8-bit is then slice *insertion*, not rerouting. Note for the future track: at 8-bit words, opcode+operand fit one word and the two-nibble fetch collapses to a single fetch — so nothing outside the fetch subsystem may assume two-nibble instructions.
3. **S3 stays a cascade.** The address selector's cascaded-2:1 structure (§6) is load-bearing for expansion: a bank/page register (the PDP-8/Game Boy-MBC move — high address bits from a small latch) sockets in as one more cascade stage. Never collapse the cascade into a merged/OR structure, however tempting the block count.
4. **Declared sockets, unpopulated.** The flagship build reserves (as marked empty volumes with bus-adjacent interface positions, documented in the build guide): (a) a **bank-register socket** beside S3, and (b) a **cartridge socket** — a bounding box where a hand-built ROM plate (blocks + repeaters, the same idiom as the hex display's ROM stage) would meet the memory bus as pages 1+, with page 0 remaining the front-panel RAM. Cost in v1: a few blocks of kept-clear space and two paragraphs of documentation.
5. **Flag Register extension point.** The carry lamp's signal path (final CarryOut, §5) stays cleanly tappable — a future carry flag is "one more Module 10 bit + one more torch row in the matrix," not a rewire.
