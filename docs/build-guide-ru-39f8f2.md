# RU-v1 Integration Build Guide (working doc for ru-39f8f2)

Block-level, Bedrock-safe build instructions for every piece of hardware
`architecture.md` marks ⚠ OPEN, plus the measurements to take while building.
Everything here composes primitives the course has already built — the Module 8
MUX, the Module 10 repeater-lock cell and pulse limiter, the Module 11 decoder
and gated-OR read bus — so nothing needs a new mechanism. Each section ends
with a **Record** list: the facts to write back into `architecture.md` §11.

Companion references while in-world: `architecture.md` §9 (the control matrix
is the wiring map for §6 below) and 12b.4 (countdown program, acceptance test).

---

## 0. Primitives recap and Bedrock ground rules

**Repeater-lock cell** (Module 10, Lesson 10.3): one data repeater carries the
bit; a second repeater points into its side. Lock powered = hold, unpowered =
transparent. The user-facing STORE line goes through a torch before the lock
repeater, so lock is ON by default and a STORE pulse briefly opens the cell.
Cross-edition safe.

**Pulse limiter** (Module 10): built from Part I gates as
`OUT = IN AND NOT(delayed IN)`:

1. Split the incoming line at a junction.
2. Branch 1 goes straight to one input of an AND gate (Module 3 build).
3. Branch 2 goes through a repeater set to **2 ticks**, then a torch inverter
   (dust → block → torch), into the AND's other input.
4. The AND output pulses high for roughly the branch-2 delay (~2–3 ticks) on
   each rising edge of the input, regardless of how long the input stays high.

Every register/RAM write strobe in this guide passes through one of these.
Longer pulse needed? Add repeater ticks on branch 2.

**2:1 MUX, 4-bit** (Module 8): per bit, `Y = (A AND NOT S) OR (B AND S)`; four
slices share one select line. 4:1 = cascaded 2:1 blocks (Module 9 tree).

**Gated-OR bus merge** (Module 11): per bit, each source is ANDed with its
select, then merged onto shared dust with a repeater per source acting as a
diode so sources can't backfeed each other.

**4-to-16 decoder** (Module 11): the display decoder's active-low outputs plus
a per-line torch inverter bank giving active-high `Select 0..F`.

**Bedrock rules for everything below:**

- Never let two dust lines race to the same block in the same tick and depend
  on the order — Bedrock's dust update order is not the one you debugged in
  someone's Java video. Where order matters, enforce it with repeater delay.
- Repeaters are your diodes and your buffers. Any bus that fans out to more
  than one consumer gets a repeater at the head of each branch (this also
  resets signal strength to 15).
- No quasi-connectivity anywhere (Bedrock doesn't have it; nothing in this
  guide needs it). No observers needed either — stay in the course's
  torch/repeater/dust vocabulary.
- Keep the clock slow during bring-up. Fast pulsing burns out torches
  (they self-extinguish), and every strobe chain here contains torches.

---

## 1. Register B (closes Open Question 2)

This is Module 10 Lab Part B, built a second time.

1. Tile four repeater-lock cells beside (or mirroring) Register A.
2. **Data input:** the 4-bit output of selector S2 (§4.2). If S2 isn't built
   yet, temporarily feed four levers so the register can be tested standalone.
3. **Strobe:** a shared `LD_B` line through a pulse limiter, driven by the
   decoder (§5). For standalone testing, a button into the limiter.
4. **Output:** a 4-bit bus to the ALU's **Bus B** inputs — this replaces
   whatever levers/temporary feed Module 9's Bus B currently has.

**Test** (Module 10's experiment, on this instance): put `1011` on the input,
pulse `LD_B`, verify the ALU sees `1011` on Bus B; change input to `0011`
without pulsing, verify Bus B still reads `1011`.

**Record:** where Reg B physically lives; that it is an exact Module 10 Lab B
duplicate; the decision on where the course instructs it (recommendation:
Module 10 Lab B gains a "build it twice" step — cheapest fix, and 12a stays
infrastructure-only).

## 2. Instruction Register (closes half of Open Question 1)

Four more repeater-lock cells.

1. **Placement:** as close to the RAM read-bus exit as practical — IR's output
   run to the decoder (§5) is the longest new wiring in the machine; minimize
   the input side.
2. **Data input:** tap the 4-bit **Memory Output Bus** after the Module 11
   gated-OR merge. Put a repeater on each tapped line (diode — the IR must
   never backfeed the read bus).
3. **Strobe:** `LD_IR`, pulse-limited, derived from T0 with a settle delay —
   exact timing in §7.1. For standalone testing, a button.
4. **Output:** 4-bit bus into the decoder's 4-to-16 input (§5). Lamps on all
   four bits — you will stare at these constantly during bring-up.

## 3. Argument Register (closes the other half of Open Question 1)

Identical build to the IR, one block row over.

1. **Data input:** same Memory Output Bus tap, own diode repeaters.
2. **Strobe:** `LD_AR`, pulse-limited, derived from T1 (§7.1).
3. **Output fan-out — this is the one register with three consumers:**
   - → S3, RAM address selector (§4.3)
   - → S4, the PC's load bus (§4.4)
   - → S1 and S2, the `LDI` data paths (§4.1, §4.2)

   Give each branch its own repeater at the fan-out point. Lamps on all four
   bits here too.

**Test for both (before decoder exists):** drive the RAM address levers in
Program mode to select a known row, then manually pulse `LD_IR` / `LD_AR` and
verify each register captures the addressed nibble and holds it when the
address levers change.

**Record:** confirm the strobe names `LD_IR`/`LD_AR` (currently marked
"invented" in §2 of architecture.md); where the build lab lands (proposed: new
section in 12a between 12a.3 and 12a.4 — the registers are prerequisites for
wiring the selectors); and the Q13 naming fix — 12a.2's "load bus" and 12a.4's
"argument bus" are both *the AR output bus*; pick "AR output" and unify.

## 4. The five selectors (closes Open Questions 3 and 4)

All five are Module 8 MUX blocks. The encodings below are the recommended
build; whatever you actually wire, **write the real per-stage tables into
architecture.md §6** — that is the whole point of Q3.

### 4.1 S1 — Register A input (3 sources)

architecture.md proposes "4:1 with one input unused." Two cascaded 2:1 blocks
are cheaper and easier to verify — recommend building that and correcting §6:

1. **Stage 1** (2:1, select `SelA0`): input 0 = Memory Output Bus,
   input 1 = AR output. (`SelA0` = 1 only for `LDI A`.)
2. **Stage 2** (2:1, select `SelA1`): input 0 = stage-1 output,
   input 1 = ALU Result Bus. (`SelA1` = 1 for `ADD`/`SUB`.)
3. Stage-2 output → Register A's four data repeaters.

| Instruction | SelA1 | SelA0 | A loads from |
| :-- | :-: | :-: | :-- |
| LDA | 0 | 0 | Memory Output Bus |
| LDI A | 0 | 1 | AR |
| ADD / SUB | 1 | x | ALU Result Bus |

### 4.2 S2 — Register B input (2:1)

One 4-bit MUX: `SelB` = 0 → Memory Output Bus (`LDB`), 1 → AR (`LDI B`).
Output → Register B (§1).

### 4.3 S3 — RAM address (three sources; this decides Q4)

Recommend the **cascaded** structure over a flat 3:1 — the MODE override stays
physically separate from the run-time decision, which makes §10's mode table
directly verifiable:

1. **Stage 1** (2:1, select `SelMemAddr`, decoder-driven): 0 = PC output
   (default, covers T0/T1), 1 = AR output (T2 of `LDA`/`LDB`/`STA`).
2. **Stage 2** (2:1, select = MODE lever): Run = stage-1 output,
   Program = the four manual **Address levers**.
3. Stage-2 output → the Module 11 address decoder input.

### 4.4 S4 — PC input

Already built inside the PC (12a.2's per-bit 2:1 load selector). The only work:
wire the **AR output bus** into its load side and confirm nothing else drives
it. `SelPC`/`PC_LOAD` timing comes from the decoder (§5).

### 4.5 S5 — RAM data-in (2:1)

One 4-bit MUX, select = MODE lever: Run = Register A output (the `STA` path),
Program = the four manual **Data levers**. Output → the RAM rows' data-in.

**Test each selector standalone:** distinct patterns on both inputs (e.g.
`1010` vs `0101`), flip the select, verify the output swaps cleanly with no
bit bleeding through from the deselected source (a missing diode repeater in
the MUX's OR-merge shows up exactly here).

**Record:** the real structure (cascaded vs flat) and the per-stage select
tables for all five — replacing every ⚠ table in architecture.md §6; whether
S1 ended up 4:1 or cascaded 2:1 (correct §6's wording either way).

## 5. Control decoder and matrix (closes Open Questions 7 and 9)

Two stages, per 12b.2's "explicit network of decode lines" option — built as a
literal diode matrix so the in-world wiring *is* architecture.md §9 row by row.

### 5.1 Opcode decode

1. Build a second copy of the Module 11 **4-to-16 decoder** (active-low
   display decoder + torch inverter bank), input = IR output bus.
2. Label the active-high outputs `OP0..OPF`. Only `OP0–OP9` and `OPF` will be
   wired to anything. **Opcodes A–E get no wiring at all — they decode to
   NOP for free.** That answers Q9; record it as the deliberate behavior.

### 5.2 Phase gating and the matrix

1. AND each *used* opcode line with **T2** (one Module 3 AND gate per line) to
   produce `EX0..EX9, EXF` ("execute lines"). T0/T1 behavior never consults
   the opcode, so only T2 gets gated lines.
2. Run the execute lines as parallel horizontal dust lanes. Run the control
   rails perpendicular: `SelA0, SelA1, SelB, SelMemAddr, SelPC, ALU_SUB`
   (levels) and `ld_a*, ld_b*, ld_f*, ram_wr*, pc_load*` (pre-strobe lines,
   lower-case here to distinguish from the pulse-limited outputs).
3. At every intersection where §9 has a "•", place **one repeater** from the
   execute lane into the control rail. That repeater is the "diode" — the
   whole §9 table becomes a grid you can visually diff against the doc.
4. **Levels vs strobes:**
   - *Selector rails and `ALU_SUB`* are held levels for the whole of T2 —
     take them straight off the rails.
   - *Write rails* (`ld_a*, ld_b*, ld_f*, ram_wr*, pc_load*`) each terminate
     in **one pulse limiter**, and the limiter's output is the real strobe.
     The limiter fires on the rail's rising edge; §7 controls when that edge
     arrives within T2.
5. **JIZ:** the `pc_load*` rail is fed by `EX6` (JMP) directly, and by
   `EX7 AND Z_latched` (one more AND gate) for JIZ. Same for `SelPC`.
6. **F1/F0 (Q7):** recommend **hardwiring `F1 = F0 = 1`** at the ALU — remove
   or fix the Module 9 front-panel levers — so the decoder drives only the
   `ALU_SUB` rail (`EX5` → SUB). This matches 12b.2's spec exactly and deletes
   two failure modes. If you instead keep the levers, they become a "machine
   won't add" trap; record whichever you do, plus the levers' fate for §10.
7. **HLT:** `EXF` (via a pulse limiter) sets an SR latch — cross-coupled
   torch pair, or a repeater-lock cell with its D input wired high and RESET
   arranged to strobe it while D is forced low. The latch's `HALTED` output
   feeds the clock gate: `clock runs = RUN_lever AND NOT HALTED` (and see §8
   for the MODE term). **RESET clears the latch.** Recommended resumption
   semantics to record for Q10: HLT is cleared *only* by RESET; the RUN/HALT
   lever is an independent manual gate that does not clear it.

**Test (decoder standalone, clock halted):** force IR to each opcode with
temporary levers, force T2 high, and check the §9 row lights up on the rails —
every "•" present, everything else dark. Then force opcodes `A`–`E` and verify
*all* rails stay dark. This one test closes most of the matrix's risk before
any integration.

**Record:** the decoder's physical form (matrix vs gate network) for 12b.2;
F1/F0 disposition (§4, §9 of architecture.md); undefined-opcode behavior
(12b.1); the HLT latch mechanism and resume rule (12a.1, 12b).

## 6. Fetch-phase strobes — PC_INC and the T0/T1 ordering (closes Q11)

T0 and T1 each need two events **in order**: latch the nibble, *then*
increment the PC. Build each phase's events off one delay ladder so the order
is structural, not accidental:

```
T0 line ──┬─ delay d1 ─→ pulse limiter ─→ LD_IR
          └─ delay d1 + d2 ─→ pulse limiter ─→ PC_INC   (T0's copy)

T1 line ──┬─ delay d1 ─→ pulse limiter ─→ LD_AR
          └─ delay d1 + d2 ─→ pulse limiter ─→ PC_INC   (T1's copy)
```

- The two `PC_INC` sources merge through diode repeaters into the PC's
  increment input.
- **d1** must cover the RAM read settling into the latch's data repeater:
  S3 stage-1 switch back to PC (after a T2 that used AR) + address decoder +
  row select + gated-OR merge + the bus run to IR/AR. Start at **4 repeater
  ticks** and tune (below).
- **d2** just has to clear the latch strobe: strobe width + 1–2 ticks margin.
  Start at **4 ticks**.

**How to tune d1 in-world:** Program mode, load memory so consecutive
addresses hold *different, asymmetric* nibbles (e.g. `8,5,9,1` per the 12a.5
lab). Run mode, RESET, single-STEP, and watch the IR/AR lamps. Wrong or stale
nibble in IR at T0 → d1 too small (latch opened before RAM settled) — add
ticks. Then verify PC lamps only advance *after* the latch lamps update.

**Record:** the final tick values for d1/d2 and the ordering statement
"RAM settles → IR/AR latch → PC increments" with those numbers, into
architecture.md §7 (replacing the first ⚠ OPEN) and 12a.5.

## 7. Execute-phase strobes — the flag-latch timing (closes Q5, the critical one)

### 7.1 The design

Fire `LD_A` and `LD_F` from **the same pulse limiter output**. One strobe
line, two destinations (Reg A's four lock-torches and the flag latch's two).

Why this is safe by construction: the hazard needs the flag latch to still be
open when Reg A's new value has made the round trip
*Reg A output → ALU (borrow chain) → Z NOR → flag-latch data repeater*. That
round trip crosses the entire 4-bit subtractor — well over 6 redstone ticks —
while the shared strobe holds both latches open for only ~2–3 ticks. The
latches are closed long before the corrupted Z can arrive. The failure mode
architecture.md worries about can only be built by *deriving `LD_F`
separately, later than `LD_A`* — so don't; one limiter, one strobe.

Two physical rules to keep the guarantee:

1. Keep the dust runs from the limiter to Reg A's torches and to the flag
   latch's torches within a tick of each other (roughly equal length, same
   number of repeaters).
2. If you ever widen the strobe (e.g. debugging), remember the ceiling: strobe
   width must stay **below** the Reg A→ALU→flags round trip. Measure the round
   trip once (below) and write it down.

The execute ladder mirrors §6: `T2 → delay d3 → limiter → LD_A+LD_F`, where
**d3** covers ALU settle after Bus B / SelA are stable. The ALU has been
settling since the operands last changed (T2 of the *previous* ADD/SUB at the
latest), so d3 mostly covers the SelA1 selector switch; start at 4 ticks.
`RAM_WR` (STA) and `PC_LOAD` (JMP/JIZ) get their own `T2 → d3 → limiter`
taps off their §5 rails.

### 7.2 The bench test (run this before full integration)

The poison case, on a manual rig — clock halted, decoder bypassed with
buttons:

1. `LDI A, 1`-equivalent: force A = `0001`. Force B = `0001`, ALU in SUB.
2. Wait for the ALU lamps to settle (result `0000`, live Z lamp ON).
3. Press the shared `LD_A`+`LD_F` strobe **once**.
4. Pass: A reads `0000` **and the latched Z lamp reads 1**.
   Fail (latched Z = 0): the latch captured the post-writeback recompute
   (0 − 1 = F, Z=0) — strobe too wide or `LD_F` path slower than the round
   trip. Narrow the limiter / equalize the runs and repeat.

**Measure and record:** the strobe width in ticks, the measured round-trip
delay (add repeaters on a test line until a pulse injected at Reg A's output
reappears at the flag latch input — count ticks), and the statement that
`LD_A`/`LD_F` share one strobe. Goes into architecture.md §5 and §7 (second
⚠ OPEN), Module 10 Lab C, 12b.2, 12b.4.

## 8. MODE gating (closes Open Question 6)

Recommended spec — one master rule plus the three overrides that already
exist, so the whole question collapses to a single AND gate:

| Resource | Program mode | Run mode |
| :-- | :-- | :-- |
| Master clock gate | **OFF** — `clock = RUN_lever AND MODE_run AND NOT HALTED` | per lever |
| Phase ring, PC | frozen (no clock pulses reach them) | clocked |
| S3 stage 2 | Address levers | stage-1 (PC/AR) |
| S5 | Data levers | Reg A |
| WRITE button | enabled (`WRITE AND MODE_program` into the RAM write limiter) | dead |
| Decoder strobes | can't fire — ring is frozen, and pulse limiters only fire on edges | live |
| S1, S2, S4 selects; ALU_SUB | don't-care (their strobes can't fire) | per decoder |

Belt-and-braces (cheap, recommended): also AND the `ram_wr*` decoder rail
with `MODE_run`, so even a mid-T2 freeze can't leave a write path armed.

**Verify in-world:** flip to Program mode *during* a running program (yes,
rudely, mid-phase), poke all Address/Data levers and WRITE, flip back to Run,
RESET, and confirm the machine still executes correctly from address 0 —
i.e., Program mode can't corrupt anything except the rows you deliberately
wrote. **Record** the final table into architecture.md §10 (replacing the
three ⚠ rows) and 12a.5.

## 9. Display tap (closes Open Question 12)

Recommend: **canonical display = Register A on the hex display**, which
Module 10 already wired — zero new hardware, and during the countdown A holds
the live count anyway. Optionally add a second bank of 4 lamps tapped
**directly off RAM row E's four cell outputs** (before the gated-OR merge —
the shared Memory Output Bus only shows the currently addressed row, so a
"display on RAM[E]" must tap the row itself). Record the choice in 12b.4.

## 10. Integration order and acceptance tests

Follow 12b.3's bring-up order exactly — it goes local-to-global:

1. Standalone tests as listed per section above (registers → selectors →
   decoder rails → fetch ladder → the §7.2 flag bench test).
2. Fetch-path validation: the 12a.5 lab (`8,5,9,1` in memory, single-step,
   watch IR/AR/PC lamps).
3. Single instructions, clock halted, STEP only:
   `LDI A` → `LDI B` → `ADD` → `SUB` → `LDA` → `LDB` → `STA` → `JMP` →
   `JIZ` → `HLT`. `STA` is the flagged timing risk — if the written row is
   wrong or partial, take the 12a.3/12b.3 escape hatch: add a T3 ring stage,
   move `RAM_WR`'s ladder tap to T3, leave address/data setup on T2.
   (If you do this, it's a §7 architecture.md change — record it.)
4. **The acceptance test — countdown (12b.4):** Program mode, load the
   program table (addresses 0–F per 12b.4, `RAM[E] = 5`), Run mode, RESET,
   single-step one full loop iteration checking each phase against the §9
   matrix trace, then flip RUN and let it free-run.
   - **Pass:** display counts 5→4→3→2→1→0 and the clock stops (HLT) with
     PC parked at `C`/`D`'s fetch.
   - **Never halts, counts 0,F,E,…:** Q5 regression — flag latch captured
     post-writeback Z. Re-run §7.2.
   - **Garbage instructions / wild jumps:** Q11 regression — fetch ladder d1
     too small, or PC incrementing before the latch. Re-run §6 tuning.
   - **RAM[E] display wrong but A correct:** STA timing — see step 3.

## 11. Write-back checklist (the actual deliverable of ru-39f8f2)

architecture.md first, then conform the drafts:

| Done | Open Q | architecture.md edit | Draft(s) to conform |
| :-: | :-: | :-- | :-- |
| ☐ | 1 | §2: IR/AR rows — real strobe names, "built in" location | 12a (new lab), 12a.5, 12b.2 |
| ☐ | 2 | §2: Reg B row | Module 10 Lab B |
| ☐ | 3 | §6: all five selector tables from the real wiring | 12a.4 |
| ☐ | 4 | §6 S3: actual structure (cascaded 2:1 recommended) | 12a.4, 12a.5 |
| ☐ | 5 | §5, §7: shared LD_A/LD_F strobe, width + round-trip ticks | 10 Lab C, 12b.2, 12b.4 |
| ☐ | 6 | §10: full MODE gating table | 12a.5 |
| ☐ | 7 | §4, §9: F1/F0 hardwired `11` (or actual) | 12b.2, Module 9 note |
| ☐ | 8 | §5: carry lamp "never latched, never consumed" — confirmed | 12b (state it explicitly) |
| ☐ | 9 | §8: opcodes A–E decode to NOP (unwired matrix rows) | 12b.1 |
| ☐ | 10 | §9: HLT latch mechanism; resume = RESET only | 12a.1, 12b |
| ☐ | 11 | §7: fetch ordering with measured d1/d2 tick values | 12a.5 |
| ☐ | 12 | — (12b.4 decision): canonical display = Reg A | 12b.4 |
| ☐ | 13 | §6 S4: unify "load bus/argument bus/AR" → AR output | 12a.2, 12a.4, 12b |

Strike each ⚠ OPEN in the doc body as you go; when the table is all checked,
§11 of architecture.md collapses to nothing, the DRAFT banner comes off, and
Part III line-editing (plus ru-a738cc's images) unblocks.
