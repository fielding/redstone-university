# RU Project Map — How Everything Fits Together

> **Purpose:** One document tying together the course, the RU-v1 spec, the in-world
> assets (testbench, reference references, canonical builds), the build language,
> and the render pipeline. Companion to `architecture.md` (the machine spec) and
> `curriculum.md` (the course plan). Drafted 2026-07-05 from the testbench campaign
> findings + the reference world import.

---

## 1. The four layers

Everything in the project lives in one of four layers, each with a distinct job:

| Layer | Artifact(s) | Job | Status |
| :-- | :-- | :-- | :-- |
| **The Course** | `course/` (Parts I–IV, Modules 0–13) | Teach: narrative, theory, labs | Drafts exist for all modules |
| **The Spec** | `architecture.md` (RU-v1) | Single source of truth for the machine | Draft; 13 open questions, several now answerable (§5) |
| **The Realizations** | (a) testbench machine, (b) design studies (private), (c) canonical book builds | Prove it works / explore alternatives / what readers actually build | (a) proven, (b) exported, (c) **not started — the main build work ahead** |
| **The Pipeline** | `renders/STYLE.md`, `docs/image-pipelines/`, `/render-figures` | Turn builds into book figures | Locked look; operational |

The critical distinction learned this campaign: **the testbench machine and the
canonical book builds are different artifacts with different jobs.** The testbench
(bot-built, sprawling, instrumented) exists to *validate the architecture* — and it
has. The canonical builds (hand-buildable, modular, color-coded) exist for *readers*
— and they inherit the testbench's verified logic without inheriting its bot-deploy
fragility, because a human building block-by-block never hits bulk-placement
stale-state issues.

---

## 2. Module ↔ spec ↔ assets map

| Module | Artifact (course) | Spec section | Testbench proof | Notes |
| :-- | :-- | :-- | :-- | :-- |
| 0 Toolkit | lamp circuit | — | — | |
| 1 Input | 4-bit lever panel | §10 front panel | (drivers used throughout) | |
| 2 NOT/OR/AND | gate set | — | `components.js` verified 18/18 (with M3) | |
| 3 XOR/NAND/NOR/XNOR | gate set | — | `components.js` (XOR = dust-bridge design) | |
| 3b Interlude | compact design | — | — | Compact = aside, not vehicle |
| 4 Decoders/Display | 7-seg system | §3 (decoder reused by RAM) | RAM's 4→16 decoder verified | |
| 4b Interlude | abstraction | — | the `offset()`/template pattern *is* this | |
| 5 Adder + Hex | 4-bit adder | §4 | `alu.js` faSlice | |
| 6 Adv. arithmetic | adder/subtractor | §4 (SUB), carry lamp | `alu.js` ADD/SUB 8/8 | |
| 7 Comparator/Flags | comparator + 2-bit flag reg | §5 | Z=NOR4 in `alu.js`; flag latch pending integration | |
| 8 MUX | 4-bit 2:1 MUX | §6 selectors | `mux2` verified; **but see §5.3** — integration used gated-OR instead | |
| 9 ALU | grand assembly | §4 | `alu.js` 8/8 standalone | |
| 10 Register | scratchpad reg + pulse limiter + flag latch | §2 | register template 7/7; **capture-on-release semantics characterized (§5.1)** | |
| 11 RAM | 16×4 RAM | §3 | `ram.js` 3/3; write-settle timing characterized | |
| 12a Infrastructure | clock, PC, sequencer, selectors, panel | §2 (PC), §6, §7, §10 | PC 8/8; seq ring 7/7 standalone (**flattened to bot-driven phases in integration — see §5.6**); selectors integrated | |
| 12b Language + program | ISA, decoder, validation, countdown | §8, §9 | control matrix 19/19; **integrated: fetch 5/5, LDI A ✓, LDI B ✓, HLT ✓**; ADD/SUB/LDA/LDB/STA/JMP/JIZ + countdown pending | The remaining bring-up is realization work, not design risk |
| 13 Double-dabble | BCD converter | — | — | |

**Testbench code as executable blueprints:** `tools/ru-testbench/{components,alu,ram,pc,control,integrate}.js`
are machine-readable geometry for every component — each verified in-world. They are
the *ground truth* the canonical builds get redesigned from (relayout for legibility;
same logic).

---

## 3. The build language (decided)

Two color systems at two scales, plus a composition rule:

1. **Wire-role colors** (already locked in `renders/STYLE.md`): white concrete
   platforms; colored concrete wiring lanes, one color per signal role, consistent
   within a build. This operates *inside* a component.
2. **Module-region tints** (new): individual components are built **plain** (course
   materials only). Color framing — muted floor plates + thin borders (concrete/
   terracotta over bright wool) — is added **only at composition time**, when
   sub-pieces assemble into a subsystem and the reader needs "which blob is which."
   The tint is scaffolding, not part of the logic; it is a **toggleable layer** so
   the same assembly renders plain (close-up detail figures) or tinted (overview
   figures).
3. **Fixed book-wide legend** (proposal — confirm before first tinted figure):
   registers = blue · ALU/arithmetic = orange · RAM = purple · control/decode =
   green · clock/sequencer = yellow · buses/frame = black · I/O panel = light gray.
   One legend across all chapters, so a reader who met the ALU as orange in Module 9
   instantly parses the orange region in the Module 12 full-machine render.
4. **Canonical = hand-buildable, modular, legible** (the reference / Ben Eater
   tradition). Spread-out "see every gate" layouts serve as explanatory *figures*
   and remain the teaching vehicle everywhere. **Compact designs enter the main
   line at the multi-bit assemblies** (decided 2026-07-07): M9/M10/M11 each close
   with the *bit-slice arc* — legible 1-bit unit (already built as the module's
   lab) → the same logic compacted into a 2-tall slice → stacked ×4. Compactness
   costs readability, not hand-buildability: the slice is built from an exact
   layer map, which teaches building faithfully from a schematic. Prerequisite
   lessons (new, once, in M9): vertical routing ("the third dimension") and
   signal-strength-as-data. 3b stays as the early seed/motivation.

Why hand-buildable is a correctness feature, not just pedagogy: the entire class of
failures that plagued the bot-built testbench (bulk-placement stale dust states)
*cannot happen* to a reader placing blocks one at a time.

---

## 4. Asset inventory

| Asset | Location | What it is |
| :-- | :-- | :-- |
| RU testbench world | `server/world-redstone-university` (preserved; currently swapped out) | Bot-built machine: all components + integrated datapath; fetch 5/5, LDI A/B + HLT execute |
| Design studies | kept privately outside the repo | Alternative-approach reference builds and study schematics informing the canonical design decisions (not course artifacts) |
| Testbench code | `~/src/hack/minecraft-agents/tools/ru-testbench/` | Executable component blueprints + test harnesses |
| Build guide | `docs/build-guide-ru-39f8f2.md` | The testbench campaign's build/bring-up plan |
| Render pipeline | `renders/STYLE.md`, `docs/image-pipelines/`, `/render-figures` | Locked look: silhouette outlines, vector dust, power-ramp mode |

The design studies are exploratory alternatives (8-bit, compact-leaning) — useful
for pressure-testing the canonical choices, not for pasting into the course as-is
(RU-v1 is 4-bit and prioritizes legibility).

---

## 5. What the testbench campaign feeds back into the book & spec

The integration campaign resolved or informed several of `architecture.md`'s open
questions **with in-world evidence**, and surfaced phenomena that belong in the book
as teaching moments. (Spec updates should flow into `architecture.md` per its own
"correct this doc first" rule.)

1. **Open Q5 — flag-latch vs Reg A timing (the critical one): answered.** The
   repeater-lock register captures **on strobe release** (unlock → follow → relock
   captures). Therefore *data must outlive the strobe*: at T2 release, if the data
   fan collapses before the lock lands, the register captures the collapse. Fix
   pattern (proven in-world): delay-4 repeaters on the *data* fan tail so data falls
   after the strobe path relocks. This directly resolves the countdown hazard in
   §7 — same-strobe or data-outlives-strobe designs are safe; "flags after
   writeback" is not.
2. **Open Q1/Q2 — IR, AR, Reg B never built:** all three were built in the testbench
   as Module-10-style registers with `LD_IR`/`LD_AR`/`LD_B` strobes; the proposed
   resolution (a 12a build lab adding them) is validated.
3. **Open Q3 — selector encodings:** the integrated machine did **not** use binary-
   encoded mux trees for S1/S2. It uses **one-hot control rails + gated-OR merges**
   (per-bit AND tiles whose outputs dust-merge at the register input): SelA0=AR,
   SelA1=ALU, neither=Mem. Simpler control matrix, no encoder needed. Recommend the
   spec adopt one-hot as the canonical encoding (it also reads better pedagogically:
   one rail = one meaning).
4. **Open Q10 — HLT mechanism:** `HALT_SET` is a latch (verified firing in-world);
   a momentary decode latches halt. Composition with RUN/HALT lever still to spec.
5. **Open Q11 — intra-phase ordering:** empirically characterized: RAM read must
   settle before the IR/AR strobe; write needs a data-settle window before the WRITE
   pulse (long D-lanes drain slowly); strobe pulses must be wide enough for the
   register machinery. Numbers exist in the testbench notes.
6. **Sequencer reality check:** the free-running ring self-latched when integrated;
   bring-up required single-stepped (externally driven) phases. Book implication:
   12a.3 should teach STEP-first bring-up and treat the free-running clock as the
   *last* thing you turn on — which is also the correct engineering habit.
7. **Phenomena worth sidebars** (all encountered live, all real Minecraft behavior
   readers will hit): signal decay and the 15-block repeater budget (the power-ramp
   dust render mode visualizes exactly this); redstone torch burnout under fast
   toggling (>8 state changes/30t) and why gate-heavy circuits misbehave under
   rapid-fire testing; dust connects diagonally up/down and a solid block above dust
   cuts the climb (cover stones as a routing tool); repeaters output only frontward
   — tap buses at dust cells, never beside a repeater; parallel dust lanes need
   2-block pitch.

---

## 6. Pipeline flow (build → figure)

```
testbench code (verified geometry)
        │  redesign for legibility + hand-buildability
        ▼
canonical module build (plain, wire-role colors)     ←— design studies consulted
        │  /render-figures (STYLE.md locked look)
        ├─► close-up detail figures (plain)
        ▼
subsystem assembly (+ module-region tint layer)
        │  /render-figures
        ├─► tinted overview figures (legend colors)
        ▼
full machine (Module 12) — tint layer = free segmentation for CV pipeline
```

---

## 7. Roadmap

1. **Confirm the color legend** (§3.3) — one decision, then it's frozen book-wide.
2. ✅ DONE (2026-07-06) — **Flow §5's answers into `architecture.md` and conform the
   drafts** (Q1/2/3/5, partial 9/10/11/12, editorial 13): a fetch-registers lesson
   (IR/AR/Reg B) was inserted as 12a.4, selectors renumbered to 12a.5 (now teaching
   one-hot gating/gated-OR), front panel to 12a.6; 12b gained the strobe rule,
   decode-as-NOP, the display-tap caveat, and clock-last bring-up; Module 10 now
   teaches capture-on-release. Remaining ⚠ items tracked in architecture.md §11.
3. ✅ DONE (2026-07-06) — **Alternative-design studies completed** (kept privately,
   outside the repo): per-component layout comparisons that informed the canonical
   design decisions. Key finding: compact vertical bit-slice stacking trades
   legibility for density — reinforcing the horizontal hand-buildable choice.
4. **Figures for Parts II–IV** (decided 2026-07-08). Part I is done and stays as
   is. Fielding hand-builds each remaining module's Minecraft artifact in the
   Bedrock circuit lab — the same workflow that produced Part I. Three figure
   tiers: **small** (single component — iso only), **medium** (multi-component —
   iso + top), **large** (full assembly — color-coded composition legend). The
   per-module build list is tracked in tix (tag `figures`); the tracker and a
   readable working copy are both kept privately outside the repo.
   Where the compact-design arc applies (M5 adder, M9 ALU, optionally M11), a
   module gets both the legible build and the compact slice + stack.
   The bot's role is **verification/reference only** — it does not produce
   figures. (The earlier "bot-built canonical module set" experiment is retired;
   its scratch renders were discarded.)
5. **Render + place per module** as each build lands: add the `shots.json`
   entry, run the pipeline (tier → views + ground `remove`), copy the PNG into
   the module's `images/`, reference it in `draft.md`.
6. **Capstone:** the assembled machine (M12b) as the large color-coded hero —
   logic is proven, so this is a deliberate build, not a research project.
7. **Testbench:** keep `world-redstone-university` frozen as the validation record;
   swap back only when a spec question needs another in-world experiment.
