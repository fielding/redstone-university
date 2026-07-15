#!/usr/bin/env python3
"""
RU-v1 register-transfer-level simulator — canonical LOGIC verification of the
architecture described in architecture.md.

It transcribes, faithfully and independently:
  - the ISA (architecture.md §8)
  - the control matrix (§9), T0/T1 fetch + per-opcode T2
  - the datapath selectors S1..S5 (§6)
  - the 3-phase one-hot sequencer T0/T1/T2 (§7)
  - the ALU: F1/F0 hardwired 11 (arithmetic), decoder drives only SUB (§4)
  - the flag latch: Z=NOR4, N=MSB, latched by ADD/SUB (§5)
  - the HLT latch stopping the clock (§9)
  - the capture-before-writeback resolution for ADD/SUB (§7): the flag captures
    the ALU result and Reg A captures that same result on the shared T2 edge.

It then runs the literal 12b.4 countdown and a per-instruction ISA battery.

SCOPE — read this before trusting it:
  This proves the DESIGN is logically correct. It deliberately does NOT model
  redstone signal propagation, decay, coupling, or timing budgets — those are
  physical-implementation concerns handled by the in-world build, NOT the
  architecture. "Logic-correct" is not "redstone-correct." See
  docs/physical-build-resume.md for the state of the physical machine.

Run:  python3 verification/ru_v1_sim.py     (exit code 0 == all pass)
"""
import sys

MASK = 0xF
MNEM = {0x0: "NOP", 0x1: "LDA", 0x2: "LDB", 0x3: "STA", 0x4: "ADD", 0x5: "SUB",
        0x6: "JMP", 0x7: "JIZ", 0x8: "LDI A", 0x9: "LDI B", 0xF: "HLT"}


class RU:
    """Cycle-stepped RU-v1. One pulse() == one phase of the T0/T1/T2 ring."""

    def __init__(self, ram):
        self.RAM = list(ram) + [0] * (16 - len(ram))
        self.PC = self.IR = self.AR = self.A = self.B = 0
        self.Z = self.N = self.HALT = 0
        self.phase = 0                       # 0=T0, 1=T1, 2=T2
        self.exec_log = []                   # one entry per executed instruction

    def alu(self, sub):                      # §4: arithmetic lane, SUB line selects -/+
        res = ((self.A - self.B) if sub else (self.A + self.B)) & MASK
        return res, (1 if res == 0 else 0), (res >> 3) & 1

    def pulse(self):                         # §7 sequencer: advance one phase
        if self.HALT:
            return False
        if self.phase == 0:                  # T0 fetch opcode: SelMemAddr=PC, LD_IR, PC_INC
            self.IR = self.RAM[self.PC] & MASK
            self.PC = (self.PC + 1) & MASK
            self.phase = 1
        elif self.phase == 1:                # T1 fetch arg: SelMemAddr=PC, LD_AR, PC_INC
            self.AR = self.RAM[self.PC] & MASK
            self.PC = (self.PC + 1) & MASK
            self.phase = 2
        else:                                # T2 execute (§9 matrix)
            self._exec()
            self.phase = 0
        return True

    def _exec(self):
        op, arg = self.IR, self.AR
        pc_at = (self.PC - 2) & MASK
        if   op == 0x1: self.A = self.RAM[arg] & MASK          # LDA  SelMemAddr=AR, SelA=Mem, LD_A
        elif op == 0x2: self.B = self.RAM[arg] & MASK          # LDB  SelMemAddr=AR, SelB=Mem, LD_B
        elif op == 0x3: self.RAM[arg] = self.A & MASK          # STA  SelMemAddr=AR, SelMemIn=RegA, RAM_WR
        elif op == 0x4:                                        # ADD  SelA=ALU, LD_A, LD_F, ALU_SUB=0
            res, z, n = self.alu(0); self.Z, self.N = z, n; self.A = res
        elif op == 0x5:                                        # SUB  SelA=ALU, LD_A, LD_F, ALU_SUB=1
            res, z, n = self.alu(1); self.Z, self.N = z, n; self.A = res
        elif op == 0x6: self.PC = arg & MASK                   # JMP  SelPC=AR, PC_LOAD
        elif op == 0x7:                                        # JIZ  PC<-AR iff latched Z==1
            if self.Z == 1: self.PC = arg & MASK
        elif op == 0x8: self.A = arg & MASK                    # LDI A  SelA=AR, LD_A
        elif op == 0x9: self.B = arg & MASK                    # LDI B  SelB=AR, LD_B
        elif op == 0xF: self.HALT = 1                          # HLT  HALT_SET latch
        # 0x0, 0xA-0xE: structural NOP (empty matrix rows, §9)
        self.exec_log.append(dict(pc=pc_at, op=op, arg=arg, A=self.A, B=self.B,
                                  Z=self.Z, RAM=list(self.RAM)))

    def run(self, max_instr=500):
        n = 0
        while not self.HALT and n < max_instr:
            before = len(self.exec_log)
            while self.pulse() and len(self.exec_log) == before:
                pass
            n += 1
        return not self.HALT                 # False if the runaway guard tripped


def hx(v):
    return format(v & MASK, 'X')


# ---- literal 12b.4 countdown (architecture.md §9): counter at RAM[E]=5, HLT at [C]
COUNTDOWN = [0x1, 0xE, 0x9, 0x1, 0x5, 0x0, 0x3, 0xE,
             0x7, 0xC, 0x6, 0x4, 0xF, 0x0, 0x5, 0x0]


def verify_countdown(verbose=True):
    m = RU(COUNTDOWN)
    ran = m.run()
    if verbose:
        for e in m.exec_log:
            mn = MNEM.get(e['op'], f"op{hx(e['op'])}")
            print(f"    @{hx(e['pc'])} {mn:<6} arg={hx(e['arg'])}"
                  f"  A={hx(e['A'])} B={hx(e['B'])} Z={e['Z']} RAM[E]={hx(e['RAM'][0xE])}")
    seq = [hx(m.exec_log[0]['A'])] + [hx(e['A']) for e in m.exec_log if e['op'] == 0x5]
    ok = seq == ['5', '4', '3', '2', '1', '0'] and m.HALT == 1 and m.RAM[0xE] == 0
    if verbose:
        print(f"\n    Reg A display: {' -> '.join(seq)}   RAM[E] final: {hx(m.RAM[0xE])}"
              f"   halted: {m.HALT == 1}   (ran to completion: {ran})")
        print(f"    >>> COUNTDOWN VERIFIED: {ok}")
    return ok


def verify_isa(verbose=True):
    res = []

    def check(name, cond):
        res.append(cond)
        if verbose:
            print(f"    [{'PASS' if cond else 'FAIL'}] {name}")

    m = RU([0x8, 0x7, 0x9, 0x3, 0xF]); m.run()
    check("LDI A,7 -> A=7", m.A == 7)
    check("LDI B,3 -> B=3", m.B == 3)
    m = RU([0x8, 0x6, 0x9, 0x5, 0x4, 0x0, 0xF]); m.run()
    check("6 ADD 5 -> A=0xB, Z=0", m.A == 0xB and m.Z == 0)
    m = RU([0x8, 0x4, 0x9, 0x4, 0x5, 0x0, 0xF]); m.run()
    check("4 SUB 4 -> A=0, Z=1", m.A == 0 and m.Z == 1)
    m = RU([0x8, 0x9, 0x3, 0xD, 0x8, 0x0, 0x1, 0xD, 0xF]); m.run()
    check("STA[D]<-9 then LDA[D] -> A=9", m.A == 9 and m.RAM[0xD] == 9)
    m = RU([0x2, 0xD, 0xF]); m.RAM[0xD] = 0xA; m.run()
    check("LDB[D] with RAM[D]=A -> B=0xA", m.B == 0xA)
    m = RU([0x6, 0x4, 0xF, 0x0, 0x8, 0x2, 0xF]); m.run()
    check("JMP[4] skips HLT@2 -> LDI A,2 runs", m.A == 2 and m.HALT == 1)
    m = RU([0x8, 0x0, 0x9, 0x0, 0x5, 0x0, 0x7, 0xA, 0xF, 0x0, 0x8, 0x3, 0xF]); m.run()
    check("JIZ taken (Z=1) -> jumps past HLT to LDI A,3", m.A == 3 and m.HALT == 1)
    m = RU([0x8, 0x1, 0x9, 0x0, 0x5, 0x0, 0x7, 0xC, 0xF, 0x0, 0x8, 0x9, 0xF]); m.run()
    check("JIZ not-taken (Z=0) -> falls through to HLT@8", m.HALT == 1 and m.A == 1)
    m = RU([0x0, 0x0, 0xA, 0x0, 0x8, 0x6, 0xF]); m.run()
    check("NOP + opcode A are structural NOPs -> LDI A,6 runs", m.A == 6)
    m = RU([0xF, 0x0, 0x8, 0x9]); m.run()
    check("HLT halts before the following LDI A", m.A == 0 and m.HALT == 1)
    if verbose:
        print(f"\n    ISA CHECKS: {sum(res)}/{len(res)} passed")
    return all(res)


def main():
    print("=" * 72)
    print("RU-v1 ARCHITECTURE VERIFICATION  (RTL model of architecture.md)")
    print("=" * 72)
    print("\n[1] LITERAL 12b.4 COUNTDOWN  (counter at RAM[E]=5, HLT at [C])\n")
    a = verify_countdown()
    print("\n[2] PER-INSTRUCTION ISA CHECKS (all datapaths)\n")
    b = verify_isa()
    print("\n" + "=" * 72)
    ok = a and b
    print("VERDICT:", "ALL PASS — RU-v1 design executes the ISA + countdown"
          if ok else "FAILURES ABOVE")
    print("=" * 72)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
