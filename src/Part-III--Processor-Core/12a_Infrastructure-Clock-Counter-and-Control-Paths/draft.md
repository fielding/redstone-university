## Module 12a: The infrastructure – Clock, counter, and control paths

### Module 12a Summary

-   **Narrative Beat:** Before the computer can understand a program, it needs timing, routing, and discipline. In this module, we build the machine's heartbeat, its program counter, its phase sequencer, and the bus selectors that let all the major subsystems cooperate.
-   **Learning Goals:**
    -   Build a controllable system clock with **RUN**, **HALT**, **STEP**, and **RESET** behavior.
    -   Understand the four jobs of the **Program Counter**: hold, increment, load, and reset.
    -   Build a one-hot **three-phase sequencer** for `T0`, `T1`, and `T2`.
    -   Identify the five selector networks that route data through the machine.
    -   Understand how **Program mode** and **Run mode** share the same hardware safely.
    -   Validate the fetch path for two-nibble instructions on a 4-bit bus.
-   **Lesson Overview:**
    -   Lesson 12a.1: The heartbeat – RUN, HALT, STEP, and RESET
    -   Lesson 12a.2: The Program Counter – Hold, increment, load, reset
    -   Lesson 12a.3: The phase sequencer – T0, T1, T2
    -   Lesson 12a.4: The selectors – The five routing decisions inside the machine
    -   Lesson 12a.5: The front panel and fetch cycle
-   **Minecraft Artifact:** A controllable clock, a loadable 4-bit Program Counter, a three-phase sequencer, and the selector network that prepares the computer to run programs.

---

### Module 12a Introduction

Our machine now has memory. It has an ALU. It has registers. It has flags.

What it still does not have is **discipline**.

If all of those parts changed whenever they felt like it, the computer would be useless. A real machine needs timing so that every subsystem knows *when* to act, and it needs routing so that every bus knows *what* it is carrying.

This module is about that infrastructure.

We are not defining the instruction set yet. We are not writing the first program yet. We are building the machinery that makes those things possible at all.

By the end of this module, the computer will have:

-   a heartbeat
-   a counter that can step through memory
-   a sequencer that divides instruction execution into phases
-   and the selector networks that tell the buses where to go

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

![Controllable Clock Minecraft Build](./images/controllable-clock-minecraft.png)
*Figure: A controllable Redstone clock. The RUN/HALT control decides whether the free-running clock reaches the machine, while STEP and RESET support careful bring-up and debugging.*

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
3.  **Load** a new value from the bus for jumps
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
-   the direct load path from the bus

That is what makes jumps possible.

#### Lab & Experiment: Build the 4-bit PC

1.  Build the 4-bit synchronous counter core.
2.  Add the load path so the PC can capture a value from the bus.
3.  Add reset logic that forces the PC to `0000`.
4.  Test all four operations separately:
    -   Hold
    -   Increment
    -   Load
    -   Reset

A good manual test sequence is:

1.  Reset the PC -> `0000`
2.  Step the machine three times -> `0001`, `0010`, `0011`
3.  Put `1010` on the load bus and pulse PC load -> PC becomes `1010`
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

---

### Lesson 12a.4: The selectors – The five routing decisions inside the machine

> **Key Takeaway:** A computer is full of tiny decisions about which bus should feed which subsystem. In our machine, five selector networks do that work.

By now we already know how to build a MUX. This module is where we use that idea over and over.

Our architecture needs five selector networks:

#### 1. Register A input selector

Register A can load from three meaningful sources:

-   RAM output (`LDA`)
-   the argument nibble (`LDI A`)
-   the ALU result (`ADD`, `SUB`)

In practice, we implement this as a 4:1 selector and simply leave one input unused.

#### 2. Register B input selector

Register B can load from two sources:

-   RAM output (`LDB`)
-   the argument nibble (`LDI B`)

#### 3. RAM address selector

During fetch, RAM must be addressed by the **Program Counter**.
During execute, RAM may need to be addressed by the **Argument Register** instead.

So the RAM address path needs a selector between:

-   PC
-   AR

#### 4. Program Counter input selector

The PC usually takes its next value from the increment path.
For jumps, it must instead load the target address from the argument bus.

So the PC input path needs a selector between:

-   increment path
-   jump/load path

#### 5. RAM data-in selector

This is the selector that only becomes obvious once you add **Program mode**.

During normal execution, RAM data input comes from **Register A** for `STA`.
During front-panel programming, RAM data input must come from the **manual data levers** instead.

That makes this the fifth selector in the machine.

#### Why this matters

It is tempting to think of the computer as "ALU plus RAM plus clock."

But just as important are the control decisions that say:

-   where a register gets its next value
-   what is currently addressing RAM
-   whether the PC increments or jumps
-   whether RAM is being programmed by the human or by the machine itself

Those are selector problems, and selectors are what keep the data path under control.

---

### Lesson 12a.5: The front panel and fetch cycle

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

In **Run mode**:

-   the RAM address selector behaves normally, choosing between PC and AR
-   the RAM data-in selector behaves normally, choosing Register A during `STA`
-   the machine follows the clock and phase sequencer

#### A safety rule

Gate the WRITE button so it only has an effect in **Program mode**. That prevents accidental memory corruption while the machine is running.

#### The fetch cycle

Now we can state the machine's fetch behavior precisely.

##### T0: Fetch opcode

-   RAM address selector chooses **PC**
-   RAM output is loaded into **Instruction Register (IR)**
-   PC increments

##### T1: Fetch argument

-   RAM address selector still chooses **PC**
-   RAM output is loaded into **Argument Register (AR)**
-   PC increments

##### T2: Execute

-   the instruction decoder looks at IR
-   the data path is configured appropriately
-   registers, RAM, ALU, or PC perform the requested action

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

That may sound less glamorous than building the ALU or the display, but in many ways it is the part that turns a collection of parts into a computer architecture. The machine now has timing, sequence, routing, and a disciplined way to move information from one place to another.

It also has something else important: a front panel. You can now load memory by hand, reset the machine, single-step it, and watch its internal rhythm unfold. That is the perfect setup for our next chapter.

In Module 12b, we will define the machine's instruction set, build the decoder that turns opcodes into control signals, and run our first real program.

---

### Module 12a Checkpoint

#### Practice Problem 12a.6.1: Knowledge Check

1.  What are the four required behaviors of the Program Counter?
2.  Why is a one-hot phase sequencer useful in a Redstone computer?
3.  Why does our machine need a RAM data-in selector in addition to the runtime data-path selectors?

<details>
<summary><strong>Show Solution</strong></summary>

1.  Hold, increment, load, and reset.
2.  Because it gives the machine a clear internal rhythm where exactly one phase is active at a time, making fetch and execute behavior easier to build and debug.
3.  Because RAM input comes from different places in different modes: Register A during `STA` in Run mode, and the manual data levers during Program mode.

</details>

#### Practice Problem 12a.6.2: The design question

Why do we use separate **IR** and **AR** registers instead of trying to keep the whole 8-bit instruction in one place?

<details>
<summary><strong>Show Solution</strong></summary>

Because our bus is only 4 bits wide. We fetch the instruction in two nibbles, so it is natural to store the opcode nibble in the Instruction Register and the second nibble in the Argument Register.

</details>

#### Practice Problem 12a.6.3: Debug challenge

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
-   **Front panel**: The human interface used to program, reset, halt, and step the computer.
-   **Instruction Register (IR)**: The register that stores the current opcode nibble.
-   **One-hot**: A signal convention in which exactly one line in a group is active at a time.
-   **Phase sequencer**: The control structure that cycles through `T0`, `T1`, and `T2`.
-   **Program Counter (PC)**: The register that stores the address of the next memory nibble to fetch.
-   **Program mode**: The operating mode in which the human manually writes values into RAM.
-   **Run mode**: The operating mode in which the machine uses its own control logic and clock to execute instructions.
-   **Selector network**: A collection of MUXes or equivalent routing logic that chooses which data path is active.
-   **Step**: A manually triggered single clock pulse used for debugging.
