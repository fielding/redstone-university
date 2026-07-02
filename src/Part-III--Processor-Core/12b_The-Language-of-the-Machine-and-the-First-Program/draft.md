## Module 12b: The Language of the Machine – Instructions and the First Program

### Module 12b Summary

-   **Narrative Beat:** The infrastructure is ready. Now we teach the machine its tiny language, build the decoder that turns opcodes into action, and watch it run its first real program on its own.
-   **Learning Goals:**
    -   Define a compact instruction set that fits our 4-bit bus and unified RAM.
    -   Understand how the control decoder turns opcodes and phases into pulses and selector settings.
    -   Test each instruction in isolation before trusting the full machine.
    -   Run a real countdown loop that uses arithmetic, RAM, flags, branching, and halt.
-   **Lesson Overview:**
    -   Lesson 12b.1: The instruction set – Speaking RU-v1
    -   Lesson 12b.2: The decoder – Turning opcodes into control signals
    -   Lesson 12b.3: Single-instruction validation
    -   Lesson 12b.4: The first real program – Countdown to zero
-   **Minecraft Artifact:** A complete 4-bit stored-program computer that can execute a countdown loop.
-   **The Ultimate Payoff:** Watching the computer count down to zero and then halt because a latched flag changed the Program Counter.

---

### Module 12b Introduction

The machine now has timing. It has sequence. It has registers, RAM, selectors, and a front panel.

What it still lacks is a **language**.

A computer is not useful just because it has parts. It becomes useful when those parts can be driven by a small, precise vocabulary of instructions.

This module is where we define that vocabulary and then prove that the whole architecture works.

We will start by defining the instruction set. Then we will build the decoder that translates an opcode into control signals. After that, we will test instructions one by one, the same way a careful engineer brings up any complex system.

Finally, we will run the first real program in the course.

This is the point where the machine stops being "a computer we could probably make work" and becomes **a computer that demonstrably works**.

---

### Lesson 12b.1: The instruction set – Speaking RU-v1

> **Key Takeaway:** An instruction set is a compact agreement between the programmer and the hardware about what each opcode means and how many memory cells it occupies.

Our RAM is 4 bits wide, so every instruction must be fetched in **two nibbles**:

-   one nibble for the **opcode**
-   one nibble for the **argument**

That means every instruction occupies **two consecutive RAM addresses**.

This is important enough to make explicit:

> In RU-v1, instruction start addresses are the even addresses: `0`, `2`, `4`, `6`, `8`, `A`, `C`, and `E`.

Jump targets should always point to one of those opcode addresses.

#### The RU-v1 instruction set

| Opcode (Hex) | Mnemonic | Meaning |
| :---: | :--- | :--- |
| `0` | `NOP` | Do nothing |
| `1` | `LDA [addr]` | Load RAM at `[addr]` into Register A |
| `2` | `LDB [addr]` | Load RAM at `[addr]` into Register B |
| `3` | `STA [addr]` | Store Register A into RAM at `[addr]` |
| `4` | `ADD` | Compute `A <- A + B` |
| `5` | `SUB` | Compute `A <- A - B` |
| `6` | `JMP [addr]` | Load PC with `[addr]` |
| `7` | `JIZ [addr]` | Load PC with `[addr]` if the latched Zero Flag is `1` |
| `8` | `LDI A, [data]` | Load the argument nibble directly into Register A |
| `9` | `LDI B, [data]` | Load the argument nibble directly into Register B |
| `F` | `HLT` | Halt the computer |

#### A note on the second nibble

Even instructions like `ADD`, `SUB`, and `HLT` still occupy two RAM addresses.

That means their second nibble exists in memory, but the machine simply ignores it.

Keeping that layout uniform makes the fetch cycle much simpler.

#### Which instructions update the Flag Register?

For this version of the machine, the **Flag Register** is updated by the instructions that write an ALU arithmetic result back into Register A:

-   `ADD`
-   `SUB`

That keeps the flag semantics simple and predictable.

---

### Lesson 12b.2: The decoder – Turning opcodes into control signals

> **Key Takeaway:** The instruction decoder is where meaning becomes action. It translates an opcode and the current phase into the pulses and selector settings that drive the computer.

By this point, the machine already knows *how* to move data around. What the decoder contributes is the answer to this question:

> Which movements and pulses should happen for this instruction, in this phase?

#### What the decoder looks at

The decoder must consider:

-   the opcode in **IR**
-   the current phase (`T0`, `T1`, or `T2`)
-   the latched **Zero Flag** for `JIZ`

#### What the decoder controls

The decoder must be able to drive:

-   Register A input selection and load pulse
-   Register B input selection and load pulse
-   ALU mode (`ADD` or `SUB`)
-   Flag Register store pulse
-   RAM address selection
-   RAM data-in source selection
-   RAM write pulse
-   Program Counter load signal
-   Halt control

At a high level:

-   `T0` and `T1` are mostly fixed infrastructure behavior
-   `T2` is where the opcode-specific behavior happens

In practice, the decoder's job is to generate **brief load and write strobes**, not long enable levels. That matters because our registers and RAM rows are built from level-sensitive repeater-locking latches.

#### A useful way to think about T2

Here is the execute-phase meaning of a few instructions:

-   **`LDA [addr]`**
    -   RAM address selector chooses `AR`
    -   Register A input selector chooses RAM output
    -   Register A receives a load pulse
-   **`LDI B, [data]`**
    -   Register B input selector chooses the argument nibble
    -   Register B receives a load pulse
-   **`SUB`**
    -   ALU goes into subtract mode
    -   Register A input selector chooses ALU result
    -   Register A receives a load pulse
    -   Flag Register receives a store pulse
-   **`STA [addr]`**
    -   RAM address selector chooses `AR`
    -   RAM data-in selector chooses Register A
    -   RAM receives a write pulse
-   **`JIZ [addr]`**
    -   if `FlagZ = 1`, Program Counter input selector chooses `AR` and PC receives a load pulse
    -   if `FlagZ = 0`, the PC simply continues its normal fetch-driven increment behavior

#### How to build the decoder physically

There are two reasonable implementations:

1.  a ROM-like control matrix
2.  an explicit network of decode lines and AND gates

Either is valid. The important thing is not which aesthetic you choose, but that the control lines fired at T2 match the instruction table exactly.

---

### Lesson 12b.3: Single-instruction validation

> **Key Takeaway:** Before trusting the full computer, validate each instruction in isolation. That is how you separate architecture mistakes from integration mistakes.

Do not go straight from "the pieces exist" to "the whole machine should run a program."

Instead, validate instructions one at a time.

#### Recommended bring-up order

Test in this order:

1.  `LDI A, [data]`
2.  `LDI B, [data]`
3.  `ADD`
4.  `SUB`
5.  `LDA [addr]`
6.  `LDB [addr]`
7.  `STA [addr]`
8.  `JMP [addr]`
9.  `JIZ [addr]`
10. `HLT`

That order starts with the most local register-loading behaviors and gradually expands toward RAM, jumps, and full control flow.

#### What success looks like

-   `LDI A, 5` should put `0101` into Register A
-   `LDI B, 3` should put `0011` into Register B
-   `ADD` should replace A with `A + B`
-   `SUB` should replace A with `A - B` and store flags
-   `LDA [addr]` should fetch from RAM through the address selector and into Register A
-   `STA [addr]` should write Register A into the selected RAM location
-   `JMP [addr]` should load the PC with the new address
-   `JIZ [addr]` should jump only when the latched Zero Flag is `1`
-   `HLT` should stop the clock cleanly

#### The instruction most likely to be timing-sensitive

`STA` is the instruction to watch most carefully.

It has to do three things in the execute window:

1.  switch RAM addressing to the operand
2.  put Register A onto RAM's data-in path
3.  pulse RAM write-enable

In many layouts, especially at 4 bits, that fits comfortably inside `T2`.

> **Bedrock Note**
>
> If `STA` behaves unreliably on your final Bedrock layout, the clean fix is to add a fourth phase `T3`. Use `T2` to set up the address and data, and `T3` to pulse the RAM write signal. The architecture already supports that extension.

---

### Lesson 12b.4: The first real program – Countdown to zero

> **Key Takeaway:** A stored-program computer is real the moment it can fetch instructions from memory, change its own state, inspect a flag, and alter its own future behavior.

We are now ready for the first complete program.

This demo will do something small but profound:

-   read a value from RAM
-   subtract `1`
-   write the new value back
-   check the Zero Flag
-   branch when the count reaches `0`
-   halt

That is a real loop.

#### Memory layout

We will use RAM address `E` as the visible counter cell.

Before starting the machine, manually preload:

-   `RAM[E] = 5`

Then program memory like this:

| Address | Value | Meaning |
| :---: | :---: | :--- |
| `0` | `1` | `LDA [E]` opcode |
| `1` | `E` | argument |
| `2` | `9` | `LDI B, 1` opcode |
| `3` | `1` | argument |
| `4` | `5` | `SUB` opcode |
| `5` | `0` | ignored |
| `6` | `3` | `STA [E]` opcode |
| `7` | `E` | argument |
| `8` | `7` | `JIZ [C]` opcode |
| `9` | `C` | argument |
| `A` | `6` | `JMP [4]` opcode |
| `B` | `4` | argument |
| `C` | `F` | `HLT` opcode |
| `D` | `0` | ignored |
| `E` | `5` | current counter value |
| `F` | `0` | spare |

#### What the program does

1.  Load the current counter from `RAM[E]` into Register A
2.  Load literal `1` into Register B
3.  Subtract -> `A <- A - B`
4.  Store the new value back into `RAM[E]`
5.  If the latched Zero Flag is `1`, jump to the `HLT` opcode at address `C`
6.  Otherwise, jump back to `SUB` at address `4`

#### Why the jump target is `4`

The loop does **not** jump all the way back to `0`.

That is intentional.

Once Register A has been initialized from `RAM[E]`, the program can continue subtracting `1` from the current value already in A. The store to RAM keeps the visible counter cell synchronized for display and inspection.

#### Bring-up procedure

1.  Put the machine in Program mode.
2.  Manually load the program table into RAM.
3.  Make sure `RAM[E]` contains the initial value `5`.
4.  Switch to Run mode.
5.  Press RESET so that:
    -   PC = `0000`
    -   phase sequencer = `T0`
6.  HALT the clock and single-step through the first few instructions.
7.  Once the early fetch and execute behavior looks correct, flip RUN.

#### The payoff

If everything is wired correctly, the machine will now count down:

-   `5`
-   `4`
-   `3`
-   `2`
-   `1`
-   `0`

Then it will halt.

That output can be observed on:

-   a display attached to `RAM[E]`
-   or a debug display attached to Register A

Either is fine. The key point is that the machine, not the human, is now driving the sequence.

![Final Computer Minecraft Build](./images/final-computer-minecraft.png)
*Figure: The final integrated computer. The ALU, registers, RAM, front panel, clock, and control logic now work together as a complete stored-program system.*

This is the moment of truth.

The machine fetched instructions from memory, interpreted them, used arithmetic, updated flags, changed the Program Counter, and stopped itself. That is a stored-program computer.

---

### Module 12b Conclusion

You have built the machine this entire course was leading toward.

Not just a collection of circuits.
Not just an ALU.
Not just memory.

A computer.

It has a clock. It has state. It has a language. It can follow a sequence of stored instructions and alter its own future behavior based on a previous calculation.

And perhaps the most satisfying part is this: every layer of complexity was built from pieces that you understand. Nothing was hand-waved away. From logic gates to latches to registers to RAM to control flow, you assembled the whole story yourself.

In our post-graduate module, we will return to a human-facing problem we cleverly sidestepped earlier: how to display multi-digit decimal output more naturally. But the core curriculum is complete. You have built a programmable computer.

---

### Module 12b Checkpoint

#### Practice Problem 12b.5.1: Knowledge Check

1.  Why do RU-v1 jump targets point to even addresses?
2.  Which instructions update the Flag Register in this version of the machine?
3.  Why is `STA` the instruction most likely to force a fourth timing phase if one is needed?

<details>
<summary><strong>Show Solution</strong></summary>

1.  Because each instruction occupies two RAM addresses, so opcode nibbles begin at even addresses.
2.  `ADD` and `SUB`, the instructions that write arithmetic ALU results back into Register A.
3.  Because it must switch RAM addressing, place Register A onto the RAM data-in path, and pulse RAM write-enable within the execute window.

</details>

#### Practice Problem 12b.5.2: The programmer

Write RU-v1 code to compute `5 - 3` and store the result at RAM address `D`.

<details>
<summary><strong>Show Solution</strong></summary>

One valid program is:

| Address | Value | Meaning |
| :---: | :---: | :--- |
| `0` | `8` | `LDI A, 5` |
| `1` | `5` | argument |
| `2` | `9` | `LDI B, 3` |
| `3` | `3` | argument |
| `4` | `5` | `SUB` |
| `5` | `0` | ignored |
| `6` | `3` | `STA [D]` |
| `7` | `D` | argument |
| `8` | `F` | `HLT` |
| `9` | `0` | ignored |

</details>

#### Practice Problem 12b.5.3: Debug challenge

Your machine fetches the correct opcode into IR and the correct argument into AR, but every `LDA [addr]` instruction loads garbage into Register A.

What is the most likely missing data-path connection?

<details>
<summary><strong>Show Solution</strong></summary>

The most likely issue is that during execute, the **RAM address selector is not switching from PC to AR**. That means RAM is still reading from the instruction stream instead of from the intended data address.

</details>

#### Real-world connection: Micro-operations and sequencing

Real CPUs also break instruction execution into timed internal steps. Some designs hardwire those steps, while others store them as microcode. Either way, the processor must decide when to place an address on a bus, when to load a register, when to update flags, and when to alter the instruction pointer. You just built a Minecraft version of that same control discipline.

#### Software connection: Interpreters follow the same rhythm

A software interpreter or virtual machine often follows the same pattern as our hardware machine:

1.  fetch an instruction
2.  decode it
3.  execute it
4.  update the instruction pointer

The form is different, but the architecture is the same. That is why understanding a tiny hardware instruction cycle makes higher-level systems feel less mysterious too.

#### Key Terms
-   **Control decoder**: The logic that translates an opcode and timing phase into control signals.
-   **Execute phase**: The phase in which the current instruction actually changes machine state.
-   **Fetch phase**: The phase in which the machine reads the opcode or argument nibble from RAM.
-   **HLT**: The halt instruction that stops the machine's clock.
-   **Instruction set architecture (ISA)**: The defined collection of instructions the machine understands.
-   **Jump target**: The address loaded into the Program Counter by a jump instruction.
-   **Opcode**: The part of an instruction that specifies what operation to perform.
-   **RU-v1**: The instruction set used by the first complete Redstone University computer.
-   **Stored-program computer**: A computer that keeps its instructions in memory and fetches them automatically during execution.
