## Module 12a: The Infrastructure – Clock, Counter, and Control Paths

### Module 12a Summary

-   **Narrative Beat:** Before the computer can understand a program, it needs timing, routing, and discipline. In this module, we build the machine's heartbeat, its program counter, its phase sequencer, the last of its registers, and the routing network that lets all the major subsystems cooperate.
-   **Learning Goals:**
    -   Build a controllable system clock with **RUN**, **HALT**, **STEP**, and **RESET** behavior.
    -   Understand the four jobs of the **Program Counter**: hold, increment, load, and reset.
    -   Build a one-hot **three-phase sequencer** for `T0`, `T1`, and `T2`.
    -   Build the machine's three remaining registers: the **Instruction Register**, the **Argument Register**, and **Register B**.
    -   Identify the five routing decisions inside the machine, and pick the right idiom, one-hot gating or a 2:1 selector, for each.
    -   Understand how **Program mode** and **Run mode** share the same hardware safely.
    -   Validate the fetch path for two-nibble instructions on a 4-bit bus.
-   **Lesson Overview:**
    -   Lesson 12a.1: The heartbeat – RUN, HALT, STEP, and RESET
    -   Lesson 12a.2: The Program Counter – Hold, increment, load, reset
    -   Lesson 12a.3: The phase sequencer – T0, T1, T2
    -   Lesson 12a.4: The fetch registers – IR, AR, and Register B
    -   Lesson 12a.5: The selectors – The five routing decisions inside the machine
    -   Lesson 12a.6: The front panel and fetch cycle
-   **Minecraft Artifact:** A controllable clock, a loadable 4-bit Program Counter, a three-phase sequencer, the machine's three remaining registers (IR, AR, and Register B), and the routing network that prepares the computer to run programs.

---

### Module 12a Introduction

Our machine now has memory. It has an ALU. It has a scratchpad register and a pair of latched flags.

What it still does not have is **discipline**.

If all of those parts changed whenever they felt like it, the computer would be useless. A real machine needs timing so that every subsystem knows *when* to act, and it needs routing so that every bus knows *what* it is carrying.

This module is about that infrastructure.

We are not defining the instruction set yet. We are not writing the first program yet. We are building the machinery that makes those things possible at all.

By the end of this module, the computer will have:

-   a heartbeat
-   a counter that can step through memory
-   a sequencer that divides instruction execution into phases
-   the rest of its registers
-   and the routing network that tells the buses where to go

This is the chapter where the machine stops being a pile of components and starts becoming an organized system.

---

### Lesson 12a.1: The heartbeat – RUN, HALT, STEP, and RESET

> **Key Takeaway:** The clock is not just an oscillator. It is the master timing signal that decides when the state of the machine is allowed to change.

A computer is full of stateful parts:

-   registers
-   RAM rows
-   the Program Counter
-   the phase sequencer
-   the flag latch

If all of them changed at arbitrary times, the system would become chaotic.

The **clock** fixes that by providing a repeating pulse.

Between pulses, combinational logic has time to settle. On a pulse, the machine commits a new state. That is the rhythm of the whole computer.

#### Lab & Experiment: Build the system clock

1.  Build a repeater loop that generates a visible Redstone pulse.
2.  Add a **RUN / HALT** lever.
3.  Gate the repeater-loop output so that:
    -   **RUN** lets pulses through
    -   **HALT** freezes the machine
4.  Add a **STEP** button that injects exactly one pulse while halted.
5.  Add a **RESET** button that does not clock the whole machine, but instead resets the control state:
    -   Program Counter to `0000`
    -   phase sequencer back to `T0`

Build the RUN/HALT gate as a proper AND on the clock's output — a **clock enable** — rather than by breaking the loop itself. The lever is only the first input of that AND: two more signals will join it before the machine is finished (the MODE lever in Lesson 12a.6, and the HLT instruction's halt latch in Module 12b). One AND gate with three inputs is the machine's single answer to "is time allowed to pass right now?"

<div align="center"><img src="./images/controllable-clock-minecraft.png" alt="Controllable Clock Minecraft Build" width="512px"/><br/><em>Figure: A controllable Redstone clock. The RUN/HALT control decides whether the free-running clock reaches the machine, while STEP and RESET support careful bring-up and debugging.</em></div><br/>

#### Why STEP matters so much

A slow Redstone clock is still fast enough to hide mistakes.

Single-step mode lets you watch the machine advance one phase at a time. That turns debugging from "something weird happened" into "I know exactly which phase went wrong."

#### A practical safety rule

Treat **HALT** as the default while you are wiring and debugging. Run mode is for demonstrations. Step mode is for understanding.

---

### Lesson 12a.2: The Program Counter – Hold, increment, load, reset

> **Key Takeaway:** The Program Counter is not just a counter. It is a small state machine that must support four distinct behaviors: hold, increment, load, and reset.

The **Program Counter (PC)** stores the address of the next memory nibble to fetch.

For our computer, it must be able to do four jobs:

1.  **Hold** its current value
2.  **Increment** by `1`
3.  **Load** a new value for jumps (in the finished machine, that value comes from the **Argument Register**, which we build in Lesson 12a.4)
4.  **Reset** to `0000`

#### Why we are not using a full adder here

We *could* build PC incrementing by feeding the PC through a dedicated `+1` adder and loading the result back into a register.

But the Minecraft computer-building community uses a more compact approach: a synchronous counter built from **toggle behavior** and the same repeater-locking ideas we already trust.

That is the approach we will use.

#### The synchronous counter idea

Each PC bit is built from a small repeater-locking flip-flop style cell.

-   bit 0 toggles whenever increment is active
-   bit 1 toggles when increment is active **and** bit 0 was `1`
-   bit 2 toggles when increment is active **and** bits 0 and 1 were both `1`
-   bit 3 toggles when increment is active **and** bits 0, 1, and 2 were all `1`

That carry chain is what makes the counter add `1`.

#### The load path

Before each PC bit captures a new state, a 2:1 selector chooses between:

-   the normal increment path
-   the direct load path (fed by the Argument Register once the machine is assembled)

That is what makes jumps possible.

#### Lab & Experiment: Build the 4-bit PC

1.  Build the 4-bit synchronous counter core.
2.  Add the load path so the PC can capture a value from its load inputs.
3.  Add reset logic that forces the PC to `0000`.
4.  Test all four operations separately:
    -   Hold
    -   Increment
    -   Load
    -   Reset

A good manual test sequence is:

1.  Reset the PC -> `0000`
2.  Step the machine three times -> `0001`, `0010`, `0011`
3.  Put `1010` on the PC's load inputs (temporary levers are fine for now) and pulse PC load -> PC becomes `1010`
4.  Step once more with increment active -> PC becomes `1011`

If that works, the PC is ready.

---

### Lesson 12a.3: The phase sequencer – T0, T1, T2

> **Key Takeaway:** A one-hot phase sequencer gives the computer a clean internal rhythm: fetch opcode, fetch argument, execute.

Our instructions are 8 bits wide, but our data bus is only 4 bits wide.

So every instruction is fetched in **two pieces**:

-   opcode nibble
-   argument nibble

That means the machine naturally falls into three phases:

-   **T0:** Fetch opcode
-   **T1:** Fetch argument
-   **T2:** Execute

#### The one-hot ring counter

The simplest way to build this timing system in Minecraft is a **ring counter**.

We create three latch stages connected in a loop and initialize them like this:

-   `T0 = 1`
-   `T1 = 0`
-   `T2 = 0`

On each clock pulse, the single active `1` moves forward:

-   `T0 -> T1`
-   `T1 -> T2`
-   `T2 -> T0`

This gives us one-hot timing lines, meaning exactly one phase is active at a time.

#### Lab & Experiment: Build the three-phase sequencer

1.  Build three repeater-locking latch stages in a loop.
2.  Add reset logic that initializes the ring to `T0 = 1`, `T1 = 0`, `T2 = 0`.
3.  Put lamps on the three outputs.
4.  Step the clock and verify the sequence cycles cleanly.

If you see more than one lamp on at once, or none of them on, you have a sequencing error.

> **Bedrock Note**
>
> Our base architecture uses three phases. If later testing shows that `STA` needs an extra settling phase on your Bedrock layout, the clean fix is to add one more stage to the ring and create `T3`. The architecture survives that change easily.

> **Integration Note**
>
> A ring that passes every test on its own can still misbehave the first time it meets the rest of the machine. Once long control lines start tapping the phase outputs, that new wiring can feed power back into the ring and latch it solid. So when integration time comes in Module 12b: bring the machine up by driving phases with **STEP**, and connect the free-running clock **last**, after every phase's behavior has been verified in place.

---

### Lesson 12a.4: The fetch registers – IR, AR, and Register B

> **Key Takeaway:** Fetching an instruction in two nibbles only works if each nibble has somewhere to land. The machine needs three more registers, and every one of them is a copy of the block you built in Module 10.

Think about what the two-nibble fetch actually requires.

At `T0`, RAM produces the opcode nibble. The machine must hold onto it, because the opcode has to keep steering the decoder for the entire instruction. At `T1`, RAM produces the argument nibble, and the machine must hold onto that too, because at `T2` it may become a RAM address, a jump target, or a literal value.

Two nibbles that must survive past their fetch phase means two registers:

-   the **Instruction Register (IR)** holds the opcode nibble
-   the **Argument Register (AR)** holds the argument nibble

And there is one more gap to close. The ALU computes on two buses, but so far only **Bus A** has a register behind it (the Module 10 scratchpad, our Register A). Bus B has been driven by levers. For the machine to compute `A + B` on its own, the second operand needs a home:

-   **Register B** holds the ALU's second operand

#### Where each register's output goes

| Register | Loaded during | Output feeds |
| :-- | :-- | :-- |
| IR | `T0` (fetch opcode) | the instruction decoder (Module 12b) |
| AR | `T1` (fetch argument) | the RAM address path, the PC load path, and the register input gating (for `LDI`) |
| Register B | `T2` of `LDB` / `LDI B` | the ALU's Bus B |

#### Lab & Experiment: Build IR, AR, and Register B

There is no new circuit in this lab, and that is the point. You proved the 4-bit repeater-locking register in Module 10. The machine needs three more, so you build three copies.

1.  Build three 4-bit registers exactly like Module 10 Lab B.
2.  Give each one its own pulse-limited store line, and label them: `LD_IR`, `LD_AR`, `LD_B`.
    Keep them separate. Each strobe means something different, and in Module 12b the control unit will fire them at different phases.
3.  Test each register standalone with temporary levers on its data inputs: store a value, change the levers, confirm the value holds, store again.
4.  Position them with their consumers in mind: IR near where the decoder will live, AR near the RAM address path and the PC, Register B feeding the ALU's Bus B.
5.  Connect Register B's output to Bus B and retire the levers that have been driving it since Module 9.

<div align="center"><img src="./images/fetch-registers-minecraft.png" alt="Fetch Registers Minecraft Build" width="512px"/><br/><em>Figure: Three more copies of the Module 10 register: IR, AR, and Register B, each with its own labeled, pulse-limited store line.</em></div><br/>

This is the least glamorous lab in Part III, and it might also be the strongest argument for abstraction in the whole course. The machine needed three more memory elements, and you got all three by copying a block you already trust.

---

### Lesson 12a.5: The selectors – The five routing decisions inside the machine

> **Key Takeaway:** A computer is full of tiny decisions about which bus should feed which subsystem. Our machine makes five of them, using two idioms: one-hot gating for register inputs, and 2:1 selectors for binary choices.

We have two routing tools by now.

Module 8 gave us the **MUX**: encode a choice into select bits, and the selector routes one input through.

Module 11 quietly gave us the other one. Look back at how the RAM read bus works: every row's bits pass through an AND gate with that row's select line, and all the gate outputs merge onto one shared bus. No encoder, no tree, just *gate each source, then merge*. That idiom is called a **gated-OR merge**, and it is about to do most of the routing work in the machine.

#### The one-hot gating idiom

For register inputs, we do not build an encoded MUX at all.

Each candidate source gets one **control rail**. Each source bus passes, per bit, through an AND gate with its rail, and the gate outputs merge onto the register's input. The control logic guarantees at most one rail is high at a time, so at most one source ever reaches the register.

Why prefer this over a MUX with encoded select bits? Two reasons.

1.  **There is nothing to encode.** The control unit we build in Module 12b naturally produces one line per meaning: "this is an `LDI A`," "this is an `ADD`." Those lines can drop straight onto the rails. A binary-encoded MUX would force us to build an encoder in front of it, only to decode the same information again inside.
2.  **You have already built it.** This is the RAM read bus idiom pointed at a register input. Same gates, same merge, new job.

#### The five routing decisions

##### 1. Register A input gating

Register A can load from three meaningful sources:

-   RAM output (`LDA`)
-   the Argument Register (`LDI A`)
-   the ALU result (`ADD`, `SUB`)

Three sources means two rails plus a default: gate the AR path with one rail and the ALU path with another, and let an inverted gate select the RAM output whenever neither rail is high. `LDA` never needs a rail of its own.

##### 2. Register B input gating

Register B can load from two sources:

-   RAM output (`LDB`)
-   the Argument Register (`LDI B`)

Same idiom, one rail: the AR path is gated by the rail, and RAM output is the default when the rail is low.

##### 3. RAM address selector

During fetch, RAM must be addressed by the **Program Counter**. During execute, RAM may need to be addressed by the **Argument Register** instead. And in Program mode, the human's manual Address levers must override both.

This one is a genuine either/or choice per bit, so we build it as 2:1 selectors: one stage choosing PC vs AR, cascaded into a MODE-controlled stage that hands the address lines to the manual levers in Program mode.

##### 4. Program Counter input selector

The PC usually takes its next value from the increment path. For jumps, it must instead load the target address from the Argument Register's output.

You already built this 2:1 selection into the PC in Lesson 12a.2. Now it has a real source to load from.

##### 5. RAM data-in selector

This is the selector that only becomes obvious once you add **Program mode**.

During normal execution, RAM data input comes from **Register A** for `STA`. During front-panel programming, RAM data input must come from the **manual Data levers** instead.

Another true either/or, so another 2:1 selector.

#### Which idiom, when

The pattern behind the five decisions is worth stating once, plainly:

-   When a register can be fed by several sources and the control unit already speaks in one-hot lines, use **gated-OR merges** driven by rails.
-   When the choice is genuinely binary, PC or AR, machine or human, use a **2:1 selector**.

#### Why this matters

It is tempting to think of the computer as "ALU plus RAM plus clock."

But just as important are the control decisions that say:

-   where a register gets its next value
-   what is currently addressing RAM
-   whether the PC increments or jumps
-   whether RAM is being programmed by the human or by the machine itself

Those are routing problems, and routing is what keeps the data path under control.

---

### Lesson 12a.6: The front panel and fetch cycle

> **Key Takeaway:** Program mode and Run mode are not separate machines. They are two ways of driving the same RAM through carefully chosen selector settings.

#### The front panel

Our human interface for this computer consists of:

-   a **MODE** lever (`Program` / `Run`)
-   four manual **Address** levers
-   four manual **Data** levers
-   a **WRITE** button
-   a **RESET** button
-   a **RUN / HALT** lever
-   a **STEP** button

In **Program mode**:

-   the RAM address selector is overridden by the manual Address levers
-   the RAM data-in selector chooses the manual Data levers
-   the WRITE button sends a short, pulse-limited write strobe to RAM
-   **the clock is held** — the MODE lever is the second input of the clock-enable AND from Lesson 12a.1, so the sequencer and PC freeze while you are inside the machine's memory

In **Run mode**:

-   the RAM address selector behaves normally, choosing between PC and AR
-   the RAM data-in selector behaves normally, choosing Register A during `STA`
-   the machine follows the clock and phase sequencer

#### MODE gates exactly four things

It is worth being precise, because it is much less than you might fear. The MODE lever drives:

1.  the address selector's final stage (manual levers vs the machine),
2.  the data-in selector (manual levers vs Register A),
3.  the **write-pulse source** — one more 2:1 selector, choosing the panel's WRITE button or the decoder's `STA` strobe,
4.  the clock enable.

Nothing else needs gating. Every register strobe and selector rail in the machine is generated by the decoder *from a phase pulse*, and Program mode holds the clock — a sequencer that never advances can never fire a strobe. Only the level-driven paths into RAM (address, data-in, write) exist independent of the clock, and those three are exactly what MODE muxes. This is the classic stored-program front panel: Ben Eater's SAP-1 uses the same three selectors on its program/run switch.

The write-source selector is also the safety rule, both ways at once: in Run mode the panel's WRITE button is dead (no accidental memory corruption while running), and in Program mode the decoder's `STA` strobe is dead (a frozen machine cannot fight your edits).

#### Why hold the clock?

You might wonder whether Program mode really needs to stop time — after all, you are overriding the address and data paths anyway. The answer comes from the bench: with the clock live, the PC is still driving its side of the address selector, and any leakage between the two sources corrupts the address you think you are writing to. Freezing the clock makes Program mode unconditional: while you are editing memory, the machine is off. When you flip back to Run mode, time resumes exactly where it stopped — which is why the procedure is always *program, then RESET, then run*.

#### The fetch cycle

Now we can state the machine's fetch behavior precisely.

##### T0: Fetch opcode

-   RAM address selector chooses **PC**
-   RAM output is loaded into the **Instruction Register (IR)**
-   PC increments

##### T1: Fetch argument

-   RAM address selector still chooses **PC**
-   RAM output is loaded into the **Argument Register (AR)**
-   PC increments

##### T2: Execute

-   the instruction decoder looks at IR
-   the data path is configured appropriately
-   registers, RAM, ALU, or PC perform the requested action

#### How long should a phase be?

Remember when each of our latches actually commits: at the instant its store pulse ends (Module 10). During `T0`, the whole chain, RAM row, read bus, register input, has to settle *while* the phase is active, so that IR captures a valid opcode when the strobe falls.

That gives us the phase-width rule: **each phase must be at least as long as the slowest data path it feeds.** Long bus runs drain slowly in Redstone, and a phase that ends too early captures whatever the wires looked like mid-flight. If you are unsure whether a path fits, single-step; a phase can be as long as your patience when you drive it by hand.

#### Lab & Experiment: Validate the fetch path

1.  Put the machine in Program mode.
2.  Manually load a few test nibbles into memory, for example:
    -   address `0` = `8`
    -   address `1` = `5`
    -   address `2` = `9`
    -   address `3` = `1`
3.  Switch to Run mode.
4.  Reset the PC and sequencer.
5.  Single-step and watch:
    -   T0 loads `8` into IR
    -   T1 loads `5` into AR
    -   next T0 loads `9` into IR
    -   next T1 loads `1` into AR

If that works, the fetch path is ready for real instructions.

---

### Module 12a Conclusion

You have built the machine's infrastructure.

That may sound less glamorous than building the ALU or the display, but in many ways it is the part that turns a collection of parts into a computer architecture. The machine now has timing, sequence, every register it will ever need, and a disciplined way to move information from one place to another.

It also has something else important: a front panel. You can now load memory by hand, reset the machine, single-step it, and watch its internal rhythm unfold. That is the perfect setup for our next chapter.

In Module 12b, we will define the machine's instruction set, build the decoder that turns opcodes into control signals, and run our first real program.

---

### Module 12a Checkpoint

#### Practice Problem 12a.7.1: Knowledge Check

1.  What are the four required behaviors of the Program Counter?
2.  Why is a one-hot phase sequencer useful in a Redstone computer?
3.  Why does our machine need a RAM data-in selector in addition to the runtime data-path selectors?
4.  Register A can load from three different sources. Why does its input network not need a MUX with encoded select bits?

<details>
<summary><strong>Show Solution</strong></summary>

1.  Hold, increment, load, and reset.
2.  Because it gives the machine a clear internal rhythm where exactly one phase is active at a time, making fetch and execute behavior easier to build and debug.
3.  Because RAM input comes from different places in different modes: Register A during `STA` in Run mode, and the manual data levers during Program mode.
4.  Because the machine uses one-hot gating: each source is ANDed with its own control rail and the results merge onto the register's input, with an inverted gate selecting RAM output as the default when no rail is high. The control unit already produces one line per meaning, so there is nothing to encode.

</details>

#### Practice Problem 12a.7.2: The design question

Why do we use separate **IR** and **AR** registers instead of trying to keep the whole 8-bit instruction in one place?

<details>
<summary><strong>Show Solution</strong></summary>

Because our bus is only 4 bits wide. We fetch the instruction in two nibbles, so it is natural to store the opcode nibble in the Instruction Register and the second nibble in the Argument Register.

</details>

#### Practice Problem 12a.7.3: Debug challenge

Your machine resets correctly and the phase sequencer cycles correctly, but during fetch it keeps reading the same memory location over and over.

What is the most likely subsystem to inspect first?

<details>
<summary><strong>Show Solution</strong></summary>

The **Program Counter increment path** is the first thing to inspect. If the PC is not incrementing, or if the RAM address selector is failing to choose the PC during fetch, the machine will keep reading the same address.

</details>

#### Real-world connection: Control plumbing matters

Real CPUs contain a huge amount of logic whose job is not to perform arithmetic directly, but to move data to the right places at the right times. Clocking, counters, selectors, and sequencing are part of that invisible plumbing. They are not flashy, but without them the processor cannot function.

#### Software connection: The instruction pointer and the event loop

At the software level, virtual machines and interpreters often have the same basic structure we are building here: an instruction pointer, a fetch step, a decode step, and a controlled state update. In hardware we call it a Program Counter and a phase sequencer. In software it might look like an event loop. The idea is the same.

#### Key Terms
-   **Argument Register (AR)**: The register that stores the second nibble of the current instruction.
-   **Clock**: The timing signal that coordinates state changes across the machine.
-   **Control rail**: A one-hot control line that gates one source onto a shared destination.
-   **Front panel**: The human interface used to program, reset, halt, and step the computer.
-   **Gated-OR merge**: A routing idiom in which each source is ANDed with its own select rail and the results merge onto a shared line; the RAM read bus and the register input networks both use it.
-   **Instruction Register (IR)**: The register that stores the current opcode nibble.
-   **One-hot**: A signal convention in which exactly one line in a group is active at a time.
-   **Phase sequencer**: The control structure that cycles through `T0`, `T1`, and `T2`.
-   **Program Counter (PC)**: The register that stores the address of the next memory nibble to fetch.
-   **Program mode**: The operating mode in which the human manually writes values into RAM.
-   **Register B**: The register that holds the ALU's second operand and drives Bus B.
-   **Run mode**: The operating mode in which the machine uses its own control logic and clock to execute instructions.
-   **Selector network**: The routing logic, gated-OR merges or 2:1 selectors, that chooses which data path is active.
-   **Step**: A manually triggered single clock pulse used for debugging.
