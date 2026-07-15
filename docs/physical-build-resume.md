# Physical redstone machine — status & resume guide

**Paused 2026-07-15.** The RU-v1 **architecture is verified in logic**
(`verification/ru_v1_sim.py`, all pass — ISA + literal 12b.4 countdown). This
doc is how to pick the **physical redstone build** back up if we ever want the
actual in-world machine finished. It does not need to be finished for the design
to be considered correct — that question is settled by the sim.

## Why it was paused

~80% of the physical effort went to redstone *physics* (signal decay past 15
blocks, net back-power coupling, stacked-rail vertical leaks, congestion), not
architecture. Verifying the *design* as logic took ~2 minutes and is done; the
physical machine is a separate course/demo artifact whose remaining work is the
two hardest, highest-risk pieces (LDA accumulator re-site, free-clock
integration). The blind agent-driven build loop is slow for spatial layout — if
resumed, **strongly consider building interactively in-world** (bugs are visible
at a glance) rather than the coordinate-code + export/paste/compile/probe loop.

## Where everything is

- **Golden model / oracle:** `verification/ru_v1_sim.py` (`RU.exec_log` gives the
  exact expected per-cycle trace to check any in-world run against).
- **Full campaign log (cross-session anchor):**
  `~/.claude/projects/-Users-fielding-src-hack-redstone-university/memory/ru-testbench-engineering.md`
- **Issue tracker:** `tix ru-7b5465` (every pass, root cause, and net-list is here).
- **Machine code:** `~/src/hack/minecraft-agents/tools/ru-testbench` (git, main).
  `integrate.js` (buildMachine), `exec_alu.js`, `exec_mem.js`, `control.js`,
  `pc.js`, `alu.js`, `ram.js`, `deploy.js`.
- **Harness + survey docs:** `~/src/hack/minecraft-agents/tools/mchprs-lab`
  (branch `phase3a-xinB-fix`): `jmp_pc_results.md`, `sta_results.md`,
  `regA_resite_design.md`, `phase3b_mem_results.md`, and the probe/export scripts.
- **Two servers (NEVER cross them):** Paper `:25565` (docker `mc-server`,
  world-redstone-university) = ground truth; MCHPRS `:25566` (redpiler
  `--io-only`) = ~60× faster logic tier for iteration.

## Done (validated in redstone, real redpiler compile)

- ALU ADD/SUB (relocated frame, isolating-OR junction, result latch, self-timed
  capture, flag latch) — 9/9 **at commit a52b23b**.
- LDI A/B (16 values), HLT, LDB addresses 0-7, RAM read-address bits 0-2.
- PC: count 0-15, JMP single-target 1/3/5/7, backward **loop**, resume-increment.
- JIZ (taken / not-taken), STA data path (RAM[AR]←RegA), STA op3-T2 data gate.

## The catch that paused us (read before resuming)

Recent JMP/JIZ/STA "validations" used lever-preload harnesses that **never ran
the real ALU/LDI guard (`phase3a_alu_single`) on the composite superset** — a
test-gap. On the countdown superset (buildMachine + `buildExecALU{gateOut,
relocate,flagLatch}`) that guard was **2/9** at HEAD `a671130` (all registers
bit3-stuck). One regression is already fixed (STA D-lane back-power gated by
op3-T2, commit `997ae32`, guard → **5/9**). **Standing rule going forward: run
`phase3a_alu_single` on the superset every pass — it is the gate.**

## Remaining work, in order

1. **Restore the ALU guard to 9/9.** Fix regression #1: RegA-bit3 / `LDI A→13`
   write-back coupling (the accumulator write-back drives Reg A bit3 even for
   LDI A). It is in `buildMachine`/`buildExecALU` (reproduces `--regs B`), range
   `a52b23b..2b16064`. Bisect for the net driving Reg A bit3 at (-156,-96).
2. **LDA** (Fielding-approved, do it LAST, ALU-guarded). Only viable path:
   PATH-3 north-gap **re-site** of the Reg-A mem gates (the south-pocket gates
   short into the `prst` PC-reset rail at z-182), then **wire-OR** the Mem source
   onto the ALU write-back landing (`-156,zc+2`) — the code comment invites it.
   Guard: `phase3a_alu_single` 9/9 on every export. Details in
   `regA_resite_design.md` + `phase3b_mem_results.md`.
3. **Confirm the panel-DATA RAM-programming harness** reliability on the current
   MCHPRS/protocol build (flagged unreliable + bot ECONNRESET on long runs) —
   the countdown needs it to load a program into RAM.
4. **Assemble + run the countdown on a free-running clock.** Free-clock
   integration is flagged risky: the phase ring self-latched when first
   integrated (§7), so all bring-up was single-stepped; connect the free clock
   last. Check every cycle against the golden model.
5. **(Optional) address bit 3** for the *literal* `RAM[E]`/`HLT[C]` program —
   the arout3/arsel2 collision, a human design pass (risks the LDI-bit2 path).
   Not needed for a 0-7 compressed countdown.
6. **Deploy to Paper (ground truth)** and run there: `deploy.js` L244 →
   `buildExecALU(plan,{gateOut,relocate,flagLatch})`; `--nets` list per the
   tix net-lists; `minz -232` pad; wipe plots between differently-sized pastes.

## Hard-won rules (do not relearn these the slow way)

- **One machine editor at a time.** Concurrent edits / two bots on one MCHPRS
  cause code↔world divergence and `//paste -u` cross-contamination.
- **Repeater rule:** a >15-cell unrepeatered run decays to 0. Repeat the first
  straight cell after every corner + every ~8 within a straight, never on a
  corner. Applies **vertically** too (stacked climb rails need pitch-3 in Y).
- **The offline audit is blind** to `net=null` wires and to *missing*
  connections — audit-clean ≠ electrically connected. Continuity-probe long hauls.
- **Fresh paste always** (`--skip-paste` shows stale-RAM garbage). Validate on a
  fresh export; never trust code↔world divergence.
- MCHPRS quirks: protocol 765 (pin mineflayer 1.20.4); gate on login+map_chunk
  (no update_health); read values via **lamps** (repeater blockstates dead under
  redpiler); inputs via **levers** (block placement resets redpiler); PLOT_SCALE=6.

## Honest effort estimate

Agent-driven at the observed pace: **realistically 1-2+ weeks more**, with
genuine uncertainty — every "one bounded fix" this campaign has surfaced another
(the pattern is physical integration coupling). The two hardest items (the LDA
accumulator re-site and free-clock integration) are still ahead. Built
**interactively in-world by a human**, likely a *handful of sessions*, because
the physics bugs that eat the agent loop are obvious on sight. Given the design
is already verified in logic, the physical machine is a demo/course artifact, not
a correctness question — resume it only if the in-world computer is worth that.
