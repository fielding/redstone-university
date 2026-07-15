# RU-v1 architecture verification

`ru_v1_sim.py` is a register-transfer-level simulator that verifies the RU-v1
machine **as logic**, straight from `architecture.md`. Run it:

```
python3 verification/ru_v1_sim.py      # exit 0 == all pass
```

It executes:

1. **The literal 12b.4 countdown** — the exact course program (counter at
   `RAM[E]=5`, `HLT` at `[C]`). Reg A displays `5 → 4 → 3 → 2 → 1 → 0`, then halts.
2. **A per-instruction ISA battery** (11 checks) — every datapath: `LDI A/B`,
   `ADD`, `SUB`-to-zero (Z latched), `STA`→`LDA` round-trip through RAM, `LDB`,
   `JMP`, `JIZ` taken *and* not-taken, structural-NOP opcodes, and `HLT`.

The model is a faithful transcription of the spec: ISA (§8), control matrix (§9),
selectors S1–S5 (§6), the T0/T1/T2 sequencer (§7), the ALU (§4, F1/F0 hardwired
`11`, decoder drives only `SUB`), the Z/N flag latch (§5), the HLT latch, and the
capture-before-writeback resolution for ADD/SUB (§7). If `architecture.md`
changes, update this model and keep it green — it is the course's executable
statement that "the design works."

## What this does and does NOT prove

- **Proves:** the *design* is logically correct — the ISA, datapaths, control
  matrix, sequencer, and the countdown all execute as specified. This is the
  architecture-level "verify our claims."
- **Does NOT prove:** that a physical **redstone** build works. Signal decay,
  net coupling, timing budgets, and layout are physical-implementation concerns,
  not architecture. Logic-correct ≠ redstone-correct.

## Golden model for the physical build

If/when the in-world redstone machine is finished, this sim is the **oracle**:
every in-world validation can be checked against its exact per-cycle trace
(`RU.exec_log`), which makes the physical build faster and regression-proof.
State of the physical machine and how to resume it:
**`docs/physical-build-resume.md`**.
