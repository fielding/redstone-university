## Module 4: From Binary to Pictures: Building a Digital Display

### Module 4 Summary

-   **Narrative Beat**: We've learned the computer's language. Now, let's build a translator so it can talk back to us. This is our first major engineering project, where we'll turn abstract binary signals into a number we can actually read.
-   **Learning Goals**:
    -   Understand the distinct roles of a decoder and an encoder.
    -   Grasp the engineering trade-offs between a "brute-force" design and an elegant, compact design.
    -   Master "active-low" logic and its practical application in Redstone.
    -   Build a functional Diode Matrix and understand its role as a form of Read-Only Memory (ROM).
-   **Lesson Overview**:
    -   Lesson 4.1: The Goal: Building Our 7-Segment Display
    -   Lesson 4.2: The Master Plan: A Two-Stage Translation
    -   Lesson 4.3: The Decoder Lab: A Simple "Brute-Force" Build
    -   Lesson 4.4: The Decoder Solution: An Elegant, Compact Design
    -   Lesson 4.5: The Encoder: Building a "Diode Matrix" ROM
    -   Lesson 4.6: The Grand Payoff: The Final Connection
-   **Minecraft Artifact**: A working two-stage translator: a 4-to-10 BCD decoder and a 7-segment display encoder, forming a complete digital display system.

---

### Module 4 Introduction

In the previous modules, you learned how to speak to your computer in binary and how to manipulate those signals with logic gates. But a computer that can only listen isn't very satisfying. We want it to talk back! This is our first large-scale engineering project, and with it comes a new way of thinking about building.

> **Our New Rule: The Power of Abstraction**
>
> In **Modules 2 and 3**, we built every gate from scratch to understand how it worked. From this point forward, we will operate at a higher level of abstraction.
>
> When a diagram or instruction says to "Build an AND gate," **how you choose to build it is now up to you.**
>
> -   You can build the verbose, easy-to-read version from the previous modules.
> -   You can use a smaller, more efficient version from Interlude I.
> -   You can design your own!
>
> As long as your component functions according to its truth table, it is a valid build. This freedom is a major step in your journey from student to engineer. The preceding **Interlude I: The Art of Compact Design**, gives you the foundation for making these choices.
>
> If you are ever unsure, the verbose builds from the previous modules are guaranteed to work.

---

### Lesson 4.1: The Goal: Building Our 7-Segment Display

> **Key Takeaway**: A 7-segment display is a standard output device that uses seven independent segments to form numbers. Understanding how to control it manually is the first step to controlling it automatically.

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_7-segment-display.png" alt="7-segment display in CircuitVerse" width="512px"/><br/><em>Figure: The symbol for a 7-segment display on CircuitVerse (left) and its function in a basic circuit (right), taking seven inputs and lighting up the segments based on the pattern.</em></div><br/>

Our computer can hear us, but it can’t talk back. So far, all our work is invisible, buried in wires and circuits. How do we make our computer show us numbers in a way we understand?

The answer is the **7-segment display**, a classic output device found in everything from digital clocks to microwaves. It uses seven independently controlled segments, labeled `a` through `g`, arranged in an '8' pattern.

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_7-segment-display_labeled.png" alt="7-segment display labeled" width="512px"/><br/><em>Figure: The standard labeling for the segments of a 7-segment display.</em></div><br/>

By lighting up specific combinations of these seven segments, we can display any digit from `0` to `9`.

---

#### Lab: Building the Physical Display

Let’s start by building the physical canvas for our numbers.

1.  **Construct the Segments**: In Minecraft, place Redstone Lamps in the "8" shape shown above. For good visibility, making each segment 3 lamps long is a great choice.
2.  **Isolate the Segments**: Carefully surround the lamp segments with a non-conductive block like Wool or Concrete. I use black concrete to make the segments stand out.
3.  **Create Manual Controls**: To power each segment, run a Redstone Repeater into the middle lamp. For now, place a solid block behind each repeater and attach a Lever to it. This gives you manual control for testing.

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_7-segment-display_minecraft.png" alt="7 Segment Display in Minecraft" width="512px"/><br/><em>Figure: The display's construction stages. From left to right: the basic lamp layout, the layout isolated with concrete, powering the middle lamps of each segment, and a close-up of the repeater and lever used to control a single segment.</em></div><br/>

#### Practice Lab: Becoming a Human Encoder

Before we build the complex logic to control this display automatically, let's get a feel for it ourselves. Use the levers you just installed to "draw" the following digits. This exercise will build your intuition for exactly what our machine needs to accomplish.

> **Note**: The levers are on the back of the display, so keep that in mind when flipping specific segments. It might help to label the segments with a sign by the lever that controls it for this exercise.

1.  Flip the levers for segments **`b`** and **`c`**. You should see the digit **`1`**.
2.  Now, try to display the digit **`7`**. (You'll need segments `a`, `b`, and `c`).
3.  Next, create the digit **`4`**. (This requires segments `f`, `g`, `b`, and `c`).
4.  **Challenge**: Try to form the digit **`8`**. What do you notice? Now try to form the digit **`2`**.

---

### Lesson 4.2: The Master Plan: A Two-Stage Translation

> **Key Takeaway**: Complex engineering problems are best solved by breaking them down into smaller, simpler, manageable stages. The "plan" for our encoder is essentially a lookup table.

Now that we have our display, how do we control it? Our computer thinks in 4-bit binary, but our display needs 7 separate signals. Connecting the 4-bit input directly to the 7 segments would be a nightmare.

Instead, let’s think like engineers and break the problem into two much simpler, more manageable stages:

1.  **Decoder**: This first stage will act as an "identifier". Its only job is to look at the 4-bit binary input and determine *which* number (`` `0` ``-`` `9` ``) it represents. It will then activate a single, unique output line corresponding to that number. Because it recognizes decimal digits stored as 4-bit binary patterns, this kind of circuit is called a **BCD (Binary-Coded Decimal) decoder** — remember that name; it will matter in Part II.
2.  **Encoder**: This second stage will act as the "mapper". It receives the simple signal from the decoder (e.g., "the number is `` `3` ``!") and "maps" the signal to the correct combination of the 7 segments.

This modular, two-stage approach is the heart of good engineering. It's easier to build, easier to test, and far easier to fix if something goes wrong.

**Our Signal Flow**:
`[4-bit Input] → [**Decoder**] → [1 of 10 Lines] → [**Encoder/ROM**] → [7 Segment Signals] → [Display]`

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_digital-display-subcircuit-abstractions_circuitverse.png" alt="Digital Display Subcircuit Abstractions" width="512px"/><br/><em>Figure: The overall system in CircuitVerse, using subcircuit abstractions for the decoder, encoder, and display to show the high-level signal flow.</em></div><br/>

---

### Lesson 4.3: The Decoder Lab: A Simple "Brute-Force" Build

> **Key Takeaway**: A decoder can be built by assigning one AND gate to recognize each unique binary input. This "brute-force" method is clear but does not scale well.

Before we tackle our full 4-bit to 10-line decoder, let's build a smaller, simpler version to prove the concept. We are going to build a **2-bit to 4-line decoder**. This circuit will take a 2-bit binary input (`00`, `01`, `10`, `11`) and light up one of four corresponding output lamps ($L0$, $L1$, $L2$, $L3$) representing those values in decimal (`0`, `1`, `2`, `3`).

By scaling down the problem, we can focus on the core logic without getting overwhelmed. This is a common engineering practice: start small, prove the concept, then scale up. I'm calling this a "brute-force" method because we will build a separate AND gate for each output, rather than using a more elegant design, which we will learn in the next lesson.

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_2-to-4-decder_circuitverse.png" alt="2-to-4 Decoder in CircuitVerse" width="512px"/><br/><em>Figure: The brute-force 2-to-4 decoder in CircuitVerse, using AND gates to recognize each binary pattern.</em></div><br/>

#### The Logic on Paper

-   **Inputs**: $B1$ (the "`2`s" place), $B0$ (the "`1`s" place)
-   **Outputs**: $L0$, $L1$, $L2$, $L3$
-   **Logic Gates**: We need one 2-input AND gate for each output.
    -   $L0$ (for `00` or `0`) = $\text{NOT } B1 \text{ AND } \text{NOT } B0$ : $\neg B1 \land \neg B0$
    -   $L1$ (for `01` or `1`) = $\text{NOT } B1 \text{ AND } B0$ : $\neg B1 \land B0$
    -   $L2$ (for `10` or `2`) = $B1 \text{ AND } \text{NOT } B0$ : $B1 \land \neg B0$
    -   $L3$ (for `11` or `3`) = $B1 \text{ AND } B0$ : $B1 \land B0$

---

#### Lab: Building the 2-to-4 Decoder

**Step 1: The 2-Bit Bus**

1.  Set up two standard inputs using a Redstone Lamp with a lever on one side. Label them $B1$ and $B0$.
2.  From these levers, create a **4-line bus**. For each input, run one line of Redstone dust from the back of the lamp (for the true signal, e.g., $B1$) and another line into a NOT gate (for the inverted signal, e.g., $\neg B1$).
3.  You now have four parallel lines carrying the signals $B1$, $\neg B1$, $B0$, and $\neg B0$. Use colored wool to keep them organized.

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_2-to-4-decoder-1_minecraft.png" alt="2-to-4 Decoder Step 1" width="512px"/><br/><em>Figure: 4-line bus with inputs $B1$ and $B0$ and their inversions.</em></div><br/>

**Step 2: Build and Test the First Gate ($L0$)**

1.  Choose your favorite 2-input AND gate design from **Module 2** or **Interlude I** and build it.
2.  Connect the gate's two inputs to the $\neg B1$ line and the $\neg B0$ line on your bus. Be careful with your wiring!
3.  Place a Redstone Lamp at the output of the AND gate. This is your $L0$ output.
4.  **Test it!** Set your input levers to `` `00` `` ($B1$=OFF, $B0$=OFF). The $L0$ lamp should turn ON. Now, flip either lever. The lamp should turn OFF. This proves your first gate is wired correctly.

![2-to-4 Decoder Step 2, isometric](https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_2-to-4-decoder-2_minecraft.png)
<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_2-to-4-decoder-2-aerial_minecraft.png" alt="2-to-4 Decoder Step 2, aerial" width="512px"/><br/><em>Figure: Single AND gate connected to the $\neg B1$ and $\neg B0$ lines of the bus. The input is set to `` `11` ``, so the $L0$ lamp is OFF. It would be on if the input were `` `00` ``.</em></div><br/>

**Step 3: Build the Remaining Gates**

1.  Build three more identical 2-input AND gates next to the first one.
2.  Wire them according to the logic table:
    -   **Gate for $L1$**: Connect its inputs to the $\neg B1$ and $B0$ bus lines.
    -   **Gate for $L2$**: Connect its inputs to the $B1$ and $\neg B0$ bus lines.
    -   **Gate for $L3$**: Connect its inputs to the $B1$ and $B0$ bus lines.
3.  Place a Redstone Lamp on the output of each gate.

**Step 4: The Grand Test**

Now, cycle through all four possible inputs with your levers:

-   `` `00` `` → Only the $L0$ lamp should be ON.
-   `` `01` `` → Only the $L1$ lamp should be ON.
-   `` `10` `` → Only the $L2$ lamp should be ON.
-   `` `11` `` → Only the $L3$ lamp should be ON.

Excellent work! You've built a working decoder.

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_2-to-4-decoder-3_minecraft.png" alt="2-to-4 Decoder Step 3" width="512px"/><br/><em>Figure: Final working 2-to-4 decoder, with the input set to `` `11` ``, so only the $L3$ lamp is ON.</em></div><br/>

#### Lesson Summary: The Problem of Scale

Take a look at the space your 2-to-4 decoder occupies. Now, imagine our real goal: a 4-to-10 decoder. We would need **ten** 4-input AND gates, which are much larger than the simple gates we just used. The brute-force method works, but it does not scale well. It creates a massive, resource-hungry machine.

In the next lesson, we will learn a far more elegant and compact solution.

---

### Lesson 4.4: The Decoder Lab, Part 2: An Elegant, Compact Solution
> **Key Takeaway**: By using an "active-low" design and two clever types of "taps" (Repeater and Torch), we can build a decoder that is vastly smaller and more efficient.

Welcome to the engineer's solution. Instead of an "active-high" design, we will build an **active-low** design where the correct line turns **OFF**.

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_4-to-10-decoder_circuitverse.png" alt="4-to-10 Decoder in CircuitVerse" width="512px"/><br/><em>Figure: The compact 4-to-10 decoder in CircuitVerse, mirroring the Minecraft build with dual buses and NOR-like logic for efficiency.</em></div><br/>

#### The Core Concept: The Mismatch Detector

Each output line will function as a **"mismatch detector."** Its job is to power its own wire (turning its lamp OFF) if the input does **not** match the line's identity. The only time a lamp stays ON is when the input is a perfect match. A "tap" is simply our term for a connection that reads, or "taps into," the signal from one of the main bus lines.

Technically, the entire structure for each output line is a **Multi-Input NOR Gate**, but thinking of it as a "mismatch detector" is a great way to understand its function.

##### Two Types of Taps: The Key to the Design

We use two different methods to tap the bus. This clever approach allows a single bus line (e.g., `B1`) to do the work of the two separate `B1` and `!B1` lines we needed in the brute-force build, cutting our bus width in half.

1.  **The Repeater Tap (Checks for a `1`)**: A Repeater placed to tap a bus line will only activate if that bus line is **ON (`1`)**. We use this to detect a `1` where we expect a `0`.
2.  **The Torch Tap (Checks for a `0`)**: A Torch placed to tap a bus line will only activate if that bus line is **OFF (`0`)**. We use this to detect a `0` where we expect a `1`.

##### The Simple Rule for Building

> To program the wire for an output line `LN`:
> -   For every bit position that is **`0`** in its identity, place a **Repeater Tap**.
> -   For every bit position that is **`1`** in its identity, place a **Torch Tap**.

---

#### Lab & Experiment: Building the Compact 4-to-10 Decoder

##### The Setup: Building the Physical Structure

This design relies on a two-layer structure to keep the input and output lines separate.

1.  **Output Layer (Ground Level)**: Lay out `10` parallel lines of Redstone dust for your output lines (`L0` through `L9`). Leave at least one empty block between each line to prevent interference. At the end of each line, place a solid block, a Redstone torch on top, and a Redstone Lamp on top of the torch. All `10` lamps should be ON by default.

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_4-to-10-decoder-compact-1_minecraft.png" alt="Compact 4-to-10 Decoder Step 1" width="512px"/><br/><em>Figure: Screenshot showing the 10 output lines on the ground, step 1 of the compact 4-to-10 decoder.</em></div><br/>

2.  **Input Layer (Floating)**: Now, build a platform for your input bus two blocks off the ground (leaving a 1-block high air gap). On this platform, run your four parallel input bus lines (`B3` to `B0`) so they run perpendicularly across all `10` output lines below.

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_4-to-10-decoder-compact-2_minecraft.png" alt="Compact 4-to-10 Decoder Step 2" width="512px"/><br/><em>Figure: The two-tiered structure with four input bus lines (`B3` to `B0`) floating above the 10 output lines.</em></div><br/>

##### Programming the Lines: Placing the Taps

Now we will place our taps to connect the input and output layers, “programming” each output line to detect its unique binary identity. This is where the active-low logic comes to life. Each tap checks for a mismatch, and only the perfectly matched line stays unpowered (lamp ON).

-   **How to Build a Torch Tap**: At the correct intersection, place a Redstone torch on the side of the block that the input bus line rests on, directly above the output wire below. This tap activates (powers the output wire) when the bus line is OFF (`0`).
-   **How to Build a Repeater Tap**: This requires specific placement to achieve strong power. At the correct intersection, one block *before* the output wire, break the input bus line. On the ground level, place a solid block and put a Repeater on top of it, facing in the direction of signal flow. This "snaking" path is essential. It is important to note that the Repeater itself does not power the output wire directly; it powers the block it runs into, which then becomes strongly powered and can power the output wire.

Let’s apply this to one line to see it in action, then you’ll program the rest using the reference chart.

##### Programming Example: Line `L3` (Identity: `0011`)

To make the `L3` line detect the binary input `0011` (decimal `3`), we need to place taps according to its identity:

-   `B3` is `0`: Place a **Repeater Tap** (checks for a `1`, powers the wire if mismatched).
-   `B2` is `0`: Place a **Repeater Tap**.
-   `B1` is `1`: Place a **Torch Tap** (checks for a `0`, powers the wire if mismatched).
-   `B0` is `1`: Place a **Torch Tap**.

Here’s what it looks like once you’ve added the taps for `L3`:

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_4-to-10-decoder-compact-3_minecraft.png" alt="Compact 4-to-10 Decoder L3 Tapped" width="512px"/><br/><em>Figure: The `L3` line is now tapped for its `0011` identity. With the input set to `0000`, the Torch Taps on `B1` and `B0` activate, correctly detecting a mismatch, powering the `L3` wire and turning its lamp OFF. The `L0` lamp remains ON, as it's a perfect match.</em></div><br/>

To get a closer look at how the taps are placed, check out this isolated view of the `L3` line:

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_4-to-10-decoder-L3_minecraft.png" alt="Isolated L3 Line Close-Up" width="512px"/><br/><em>Figure: Close-up of the `L3` line with two Repeater Taps (`B3`, `B2`) and two Torch Taps (`B1`, `B0`), no inputs active.</em></div><br/>

This zoomed-in view shows exactly where to place each tap for `L3`. Notice the “snaking” path of the Repeater Taps, ensuring strong power, and the Torch Taps hanging off the side of the input bus blocks. Precision here is key! Double-check your placements to avoid crossed signals.

To verify the `L3` line works as intended, you can add levers to test it independently before connecting all lines. Set the inputs to `0011` (matching `L3`’s identity):

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_4-to-10-decoder-L3-test_minecraft.png" alt="Testable L3 Line" width="512px"/><br/><em>Figure: Isolated `L3` line with levers set to `0011`, lighting the `L3` lamp to confirm correct tap placement.</em></div><br/>

In this test, the levers mimic the input `0011`. The `L3` lamp lights up because no taps activate (no mismatches), leaving the wire unpowered. Try flipping any lever (for example, to `0010`), and the lamp should turn OFF as a tap detects a mismatch. This hands-on test builds confidence before scaling to all 10 lines.

##### Complete All Lines: Using the Reference Chart

Apply the rule and build methods to the remaining `9` lines. Use the chart below to verify your placements. This is your blueprint.

| Bus Line | `L0` | `L1` | `L2` | `L3` | `L4` | `L5` | `L6` | `L7` | `L8` | `L9` |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **`B3` (8)** | R | R | R | R | R | R | R | R | T | T |
| **`B2` (4)** | R | R | R | R | T | T | T | T | R | R |
| **`B1` (2)** | R | R | T | T | R | R | T | T | R | R |
| **`B0` (1)** | R | T | R | T | R | T | R | T | R | T |

*(R = Repeater Tap, T = Torch Tap)*

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_4-to-10-decoder-compact-complete_minecraft.png" alt="Compact 4-to-10 Decoder" width="512px"/><br/><em>Figure: The complete 4-to-10 compact decoder in action, with input `0011` lighting only the `L3` lamp.</em></div><br/>

##### Test Your Work!

Cycle through inputs `0000` to `1001`. Verify that only one lamp is lit for each input.

---

#### Practice Problem 4.4.1: Design on Paper

Before you build, an engineer must be able to plan. For output line **`L6` (Identity: `0110`)**, what taps would you need? List out which type of tap (Repeater or Torch) is required for each of the four bus lines (`B3`, `B2`, `B1`, `B0`).

<details>
<summary><strong>Show Solution</strong></summary>

Applying our rule:
-   `B3` is `0`: Requires a **Repeater Tap**.
-   `B2` is `1`: Requires a **Torch Tap**.
-   `B1` is `1`: Requires a **Torch Tap**.
-   `B0` is `0`: Requires a **Repeater Tap**.

</details>

#### Practice Problem 4.4.2: Debug Challenge

You've built your decoder, but something is wrong. When you set the input levers to **`1001`** (for the number `9`), you notice that the lamp for `L9` is on (which is correct), but the lamp for **`L8`** is *also* on (which is incorrect).

What is the single most likely mistake in your build that would cause this specific error?

<details>
<summary><strong>Show Solution</strong></summary>

**The Logic**: The $L_8$ lamp should turn OFF when the input is `1001`. For $L_8$ to turn off, its wire needs to be powered. This means one of its "mismatch" taps must have activated.

**The Identity of `L8` is `1000`.** Let's compare this to the input `1001`.
-   `B3` is `1`, `L8` expects `1`. No mismatch.
-   `B2` is `0`, `L8` expects `0`. No mismatch.
-   `B1` is `0`, `L8` expects `0`. No mismatch.
-   `B0` is `1`, `L8` expects `0`. **This is a mismatch.**

The tap for `B0` on the `L8` line is supposed to detect this mismatch and power the `L8` wire. Since `L8` expects a `0` for `B0`, the rule says it must have a **Repeater Tap**.

**The Conclusion**: The fact that the `L8` lamp is still ON means its mismatch detector for the `B0` bit failed. The most likely cause is that you **forgot to place the Repeater Tap** from the `B0` bus line to the `L8` output wire. Without that tap, the wire never gets powered, and the lamp stays on.

</details>

---

### Lesson 4.5: The Encoder: Programming a "Diode Matrix" ROM

> **Key Takeaway**: An encoder can be built as a physical Read-Only Memory (ROM) using a "diode matrix," where the layout of the wiring permanently stores the data for how to draw each number.

We now have a working decoder that gives us a single **unpowered** (active-low) line for any given number. The next step is to build our "mapper," the encoder that will take this single signal and draw the correct digit on our display.

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_10-to-7-encoder_circuitverse.png" alt="10-to-7 Encoder in CircuitVerse" width="512px"/><br/><em>Figure: The 10-to-7 encoder in CircuitVerse, using a diode matrix structure to map the active input line to the correct segment pattern.</em></div><br/>

#### The Concept: A Physical Lookup Table

This stage is effectively a physical **Read-Only Memory (ROM)**. The "address" is the active-low line from the decoder, and the "data" that it looks up is the pattern of segments for that number. We will build this using a structure called a **Diode Matrix**.

First, let's create the plan on paper. This lookup table is the blueprint for our build.

**7-Segment Display Segment Table**

| Digit | `a` | `b` | `c` | `d` | `e` | `f` | `g` |
|:-----:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
|  `9`  |  X  |  X  |  X  |  X  |     |  X  |  X  |
|  `8`  |  X  |  X  |  X  |  X  |  X  |  X  |  X  |
|  `7`  |  X  |  X  |  X  |     |     |     |     |
|  `6`  |  X  |     |  X  |  X  |  X  |  X  |  X  |
|  `5`  |  X  |     |  X  |  X  |     |  X  |  X  |
|  `4`  |     |  X  |  X  |     |     |  X  |  X  |
|  `3`  |  X  |  X  |  X  |  X  |     |     |  X  |
|  `2`  |  X  |  X  |     |  X  |  X  |     |  X  |
|  `1`  |     |  X  |  X  |     |     |     |     |
|  `0`  |  X  |  X  |  X  |  X  |  X  |  X  |     |
*(X = segment ON)*

##### The Logic: Inverting the Inversion

This is where our active-low signal becomes very powerful.

-   Our input is a single LOW line from the decoder.
-   Our goal is to turn this one LOW signal into multiple HIGH signals to power the correct display segments.
-   We can do this perfectly with **Redstone Torches**. When the input line from the decoder is LOW, any torch placed along it will turn **ON**.

This gives us a very simple rule: to turn a segment ON for a given number, we just need to place a torch at the intersection of that number's line and that segment's line.

---

#### Lab & Experiment: Building the Diode Matrix

##### 1. The Setup: The Output Layer

Start by building the foundation for your Diode Matrix: the output lines that will control the 7-segment display.

-   **Segment Output Layer (Ground Level)**: Lay out 7 parallel lines of Redstone dust, one for each segment (`a` through `g`). These will carry signals to the display. Leave a 1-block gap between each line to prevent interference. Add Redstone Repeaters every `15` blocks to keep the signals strong, as these lines may need to travel to your display.

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_10-to-7-encoder-1_minecraft.png" alt="Encoder Output Layer" width="512px"/><br/><em>Figure: The 7 parallel segment output lines (`a` through `g`) on the ground, with repeaters for signal strength.</em></div><br/>

This ground layer is the backbone of your encoder, carrying the signals that will light up the display segments. Double-check that each line is isolated to avoid crossed signals.

##### 2. The Grid: Adding the Input Layer

Now, add the input layer to complete the Diode Matrix grid. Eventually these lines will connect to the decoder’s active-low lines.

-   **Decoder Input Layer (Floating)**: Build a platform of solid blocks one level directly above the ground layer (no air gap). On this platform, run 10 horizontal lines of Redstone dust for the decoder outputs (`L9` down to `L0`), perpendicular to the 7 segment lines below. Place a Redstone Lamp at the end of each input line to visualize which line is active (LOW).

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_10-to-7-encoder-2_minecraft.png" alt="Encoder Two-Layer Structure" width="512px"/><br/><em>Figure: The two-layer Diode Matrix structure, with 7 segment output lines on the ground and 10 input lines (`L9`–`L0`) above, lamps showing input activity.</em></div><br/>

This two-layer grid is your ROM’s framework. The lamps are optional but give a nice visual for what is happening. When a lamp is ON, its line is LOW (active). Take a moment to admire the clean, perpendicular layout as it is the key to programming the segment patterns efficiently.

##### 3. Programming the Matrix: Placing the Torch Taps

Now, you’ll “burn” the lookup table into the hardware by placing torch taps at the correct intersections. This is where you physically encode the segment patterns for each digit.

-   **The Rule**: For each number line `LN`, consult the lookup table. For every segment that should be **ON** for that number, place a torch tap.
-   **How to Build the Tap**: At the correct intersection, place a **Redstone Torch on the side of the block** that the horizontal input line (`LN`) rests on. Position the torch to power the segment line on the ground below.

##### Programming Example: Line `L9`

Let’s program the `L9` line (digit `9`) as an example. According to the lookup table, digit `9` needs segments `a, b, c, d, f, g` to be ON. Place six torch taps along the `L9` line, one at each intersection with those segment lines.

Here’s a close-up of the `L9` line with its taps in place:

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_10-to-7-encoder-L9_minecraft.png" alt="Encoder L9 Taps Close-Up" width="512px"/><br/><em>Figure: Close-up of the `L9` line with six torch taps programming segments `a, b, c, d, f, g` for digit 9.</em></div><br/>

This zoomed-in view shows exactly where to place the torch taps for `L9`. Each torch is attached to the side of the block supporting the `L9` line, powering the segment lines below (`a, b, c, d, f, g`). These torches are your ROM’s “data” by each representing a specific segment that lights up when `L9` goes LOW. To test it, place a lever at the start of the `L9` line and set all other lines to ON (using levers). When you turn the `L9` lever OFF (simulating the decoder’s active-low signal), the `L9` lamp should light up, and the segment lines `a, b, c, d, f, g` should activate. You can place temporary redstone lamps at the segment line ends to verify. If any segment doesn’t light, double-check your torch placements against the lookup table.

##### Complete the Matrix

Repeat this process for all 10 lines (`L0`–`L9`), using the lookup table to place torches for each digit’s segment pattern. Work methodically to avoid mistakes. This is like programming a game cartridge, where every torch is a bit of stored data. Precision is key to ensure each line activates the correct segments.

> ##### Engineering Note: The Self-Isolating Design
> You might wonder if we need repeaters to isolate the segment lines from each other like we did in our basic OR gate. In this specific design, we don’t! The Redstone Torches we use as taps are naturally **one-way devices**. They send power *out* to the segment line, but power from another torch cannot flow *backwards* through them. The torches act as the diodes in our “Diode Matrix,” making the design incredibly elegant and efficient.

##### 4. Test Your Work

Before connecting the encoder to the decoder, test all lines (`L0`–`L9`) independently, as you did for `L9`. Place a lever at the start of each line, set all others to ON, and turn the tested line OFF. Verify that the segment patterns match the lookup table (e.g., `L3` should light `a, b, c, d, g` for digit `3`). Here’s what the fully programmed Diode Matrix looks like:

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_10-to-7-encoder-complete_minecraft.png" alt="Complete 10-to-7 Encoder" width="512px"/><br/><em>Figure: The complete 10-to-7 encoder with all torch taps placed, showing the `L3` line active (input `0011`) and segments `a, b, c, d, g` powered for digit 3.</em></div><br/>

This is your finished ROM, with every line programmed to map decoder inputs to segment outputs. The `L3` line is active here (LOW), lighting up the correct segments for a `3`. Cycle through inputs `L0`–`L9` to confirm each digit’s pattern. If any segments don’t light as expected, revisit your torch placements using the lookup table. You’ve just built a physical memory that “stores” the display patterns for all 10 digits!

#### Real-World Connection: BIOS and Game Cartridges

The "Diode Matrix" you've just built is a simple but powerful form of **Read-Only Memory (ROM)**. The "program" is physically burned into the circuit's layout by the placement of the torches. This exact principle was fundamental to early computing. A computer's **BIOS chip**, which tells it how to boot up, is a form of ROM. Old video game cartridges were also ROMs, with the entire game's data permanently stored in the hardware's structure. You've built the same technology!

#### Software Connection: Substitution Boxes in Cryptography

In software, ROM-like functionality is often implemented with static lookup tables in the form of precomputed, unchanging arrays stored in read-only memory segments of the compiled binary. This ensures efficiency and prevents accidental modifications, much like our hardware Diode Matrix.

A prime real-world example is the Substitution Box (S-box) in the Advanced Encryption Standard (AES), a cornerstone algorithm for secure data transmission (e.g., HTTPS, VPNs) and storage. The S-box is a fixed 256-entry table that maps input bytes to output bytes, introducing nonlinearity crucial for cryptographic security. This table is hardcoded and immutable, mirroring data "burned" into ROM.

Here's a Python snippet showing the AES S-box as a lookup table, common in libraries like PyCryptodome:

```python
def aes_sbox_substitute(byte):
    # Fixed AES S-box lookup table (256 entries, hexadecimal values)
    sbox = [
        0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
        0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
        0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
        0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
        0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
        0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
        0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
        0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
        0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
        0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
        0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
        0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
        0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
        0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
        0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
        0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
    ]
    return sbox[byte]

# Example usage in AES encryption round (simplified)
input_byte = 0x53  # Example input (e.g., 'S' in ASCII)
substituted = aes_sbox_substitute(input_byte)  # Returns 0xed (237 in decimal)
print(hex(substituted))  # Outputs: 0xed
```

This implementation is authentic and deployed in real-world cryptographic software, prioritizing performance and reliability. The table's fixed nature echoes ROM, as modifications would invalidate the standard. In embedded or hardware-accelerated scenarios, this data may indeed reside in physical ROM for added efficiency.

#### Practice Problem 4.5.1: Design on Paper

You are programming the line for the digit **`2`**. According to the lookup table, which perpendicular segment lines need a torch tap from the horizontal `L2` line?

<details>
<summary><strong>Show Solution</strong></summary>

The digit `2` uses segments **`a`, `b`, `d`, `e`, and `g`**. Therefore, you would place torch taps at the intersections of the `L2` line and the perpendicular lines for those five segments.

</details>

#### Practice Problem 4.5.2: Debug Challenge

When you test your encoder by providing a LOW signal to the `L4` line, you expect to see the digit `4` (segments `b, c, f, g`). Instead, the display shows `b, c, f` but **segment `g` remains dark**. What is the most likely cause of this error?

<details>
<summary><strong>Show Solution</strong></summary>

If a segment that should be ON is OFF, it means it is not receiving power. The most likely cause is simple: you **forgot to place the torch tap** at the intersection of the horizontal `L4` line and the perpendicular segment `g` line. Without that torch, there is nothing to power the line when `L4` goes low.

</details>

---

### Lesson 4.6: The Grand Payoff: System Integration

> **Key Takeaway**: Connecting individual, tested modules into a complete, working system is the final and most rewarding step of any engineering project.

The moment of truth has arrived. You’ve built and tested the decoder to identify numbers, the encoder to map them to segment patterns, and the 7-segment display to show the results. Now, it’s time to connect these modules and watch your digital display come to life, transforming binary inputs into human-readable digits. Taking modular pieces and creating a cohesive system, this is engineering at its finest!

---

#### Lab & Experiment: The Final Connection

This final step is all about making the connections between all of the components from this module. The wiring may get a bit messy, but as long as the signals flow correctly, you are good to go!

1. **Connect Decoder to Encoder**: Carefully connect the `10` active-low output lines from your **Decoder** (`L0`–`L9`) to the `10` horizontal input lines of your **Encoder/ROM**. Use Redstone Repeaters as needed to ensure the signals remain strong over long distances. Label your lines to avoid mix-ups.
2. **Connect Encoder to Display**: Connect the `7` output lines from your **Encoder/ROM** (`a`–`g`) to the control inputs of the **7-segment Display** you built in Lesson 4.1. This may require creative wiring to route signals to the display’s repeaters, but ensure each segment line connects to its corresponding input (e.g., `a` to the `a` segment). Test each connection with a temporary lever to confirm the segment lights up.

Here’s what your fully connected system should look like, with the input set to `0011` to display a `3`:

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_complete-digital-display_minecraft.png" alt="Complete Digital Display Isometric" width="512px"/><br/><em>Figure: The complete digital display system in action, with input `0011` activating the `L3` line and lighting segments `a, b, c, d, g` to form a glowing “3”.</em></div><br/>

Take a moment to admire this masterpiece! Your modular design has paid off, making this complex system manageable and functional.

##### Let’s Trace the Signal: `3` (`0011`)

To solidify your understanding, let’s trace the signal through the entire system with the input set to `0011` (decimal `3`):

1. You flip the input levers to `0011` (`B3=0`, `B2=0`, `B1=1`, `B0=1`).
2. **In the Decoder**: The mismatch detector for the `L3` line (identity `0011`) finds a perfect match. All its taps (Repeaters on `B3`, `B2`; Torches on `B1`, `B0`) are OFF, so the `L3` wire becomes **unpowered (LOW)**. Every other line (`L0`–`L2`, `L4`–`L9`) has at least one tap activated, powering their wires HIGH.
3. **In the Encoder**: The HIGH lines keep their torches off. The `L3` line, being LOW, turns ON the torches at its intersections with segments `a, b, c, d, g` (per the Lesson 4.5 lookup table).
4. Those five torches send power down their respective segment lines.
5. **At the Display**: The signals reach the 7-segment display, lighting up segments `a, b, c, d, g` to form a perfect `3`.

From above, you can see how compactly your system fits together:

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_complete-digital-display-aerial_minecraft.png" alt="Complete Digital Display Aerial" width="512px"/><br/><em>Figure: Aerial view of the compact digital display system, with input `0011` producing a “3”. The modular layout connects the decoder, encoder, and display efficiently.</em></div><br/>

This top-down view highlights the elegance of your modular design. The decoder’s input bus, the encoder’s torch matrix, and the display’s segments are tightly packed yet clearly organized. While the torches in the encoder grid are less visible from this angle, refer to the Lesson 4.5 lookup table to confirm their placements.

Here is the full schematic in CircuitVerse without subcircuit abstractions, showing the detailed wiring from 4-bit input through decoder and encoder to the 7-segment display. The layout and implementation align with our Minecraft build, and the input is currently set to `0011`, making the instructions above directly applicable.

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_complete-digital-display_circuitverse.png" alt="Full System in CircuitVerse" width="512px"/><br/><em>Figure: The end-to-end binary-to-display system in CircuitVerse, integrating all components from this module and displaying '3' for input `0011`.</em></div><br/>

Cycle through inputs `0000` to `1001` and watch the display light up each digit perfectly.

Congratulations! You’ve engineered a complete system that translates 4-bit binary into human-readable digits. This is a massive milestone in digital electronics, and you should be proud of your work. Your ability to break down a complex problem into modular components and wire them together is a hallmark of great engineering.

---

### Module 4 Checkpoint

#### Practice Problem 4.7.1: Knowledge Check

1.  Why is a two-stage (Decoder → Encoder) design generally better than a single, complex circuit?
2.  What is the purpose of the **Repeater Tap** in our compact decoder? Why can't we just use Redstone dust?
3.  In our Diode Matrix ROM, what does placing a **Torch Tap** at an intersection physically represent?

<details>
<summary><strong>Show Solution</strong></summary>

1.  It breaks the problem down into smaller, independent modules (modularity). This makes each part easier to design, build, and debug.
2.  The Repeater Tap creates a "strongly powered" block, which is necessary to power the Redstone dust on the output line across the 1-block air gap. Simple dust would create a "weakly powered" block, which cannot.
3.  It represents a single "bit" of stored information. Specifically, it's a command to "turn this segment ON when this number line is selected (LOW)."

</details>

#### Practice Problem 4.7.2: Decoder Design

You want to add a special output line, `LE`, that lights up only for even numbers (`0`, `2`, `4`, `6`, `8`). You realize that for all even numbers, the `B0` bit is always `0`. What is the single tap you would need to build a simple detector for this?

<details>
<summary><strong>Show Solution</strong></summary>

You want the lamp to be ON only when `B0` is `0`. Our active-low system turns the lamp on when the line is unpowered. You would need a single **Repeater Tap** from the `B0` line. When `B0` is `1` (odd), the repeater powers the `LE` line and turns the lamp off. When `B0` is `0` (even), the repeater is off, the line is unpowered, and the lamp turns on.

</details>

#### Practice Problem 4.7.3: Encoder Design

The letter 'A' can be made with segments `a, b, c, e, f, g`. According to the design of our ROM, which segment line is the *only one* that would **not** have a torch tap placed on it from the `LA` input line?

<details>
<summary><strong>Show Solution</strong></summary>

The line for the letter 'A' would need to activate every segment *except* for segment **`d`**. Therefore, `d` is the only segment line that would not get a torch tap.

</details>

#### Practice Problem 4.7.4: Reverse Engineering

You see a line in a decoder that has Torch Taps on `B2` and `B1`, and Repeater Taps on `B3` and `B0`. What decimal number is this line designed to detect?

<details>
<summary><strong>Show Solution</strong></summary>

Torches are for `1`s, Repeaters are for `0`s. So the identity is `0110`. This is the binary for decimal **6**.

</details>

#### Practice Problem 4.7.5: Debug Challenge

In the world download for this module, you will find a section labeled "Module 4 Debug Challenge." The display system is fully connected. When you input **`0010`** (for the number 2), the display incorrectly shows a **`6`**.

**Trace the logic**:
  - The digit `2` should be `a, b, g, e, d`.
  - The digit `6` is `a, c, d, e, f, g`.

What is the single most likely point of failure in the system that would cause this specific error? (Hint: The problem is in the Encoder/ROM).

<details>
<summary><strong>Show Solution</strong></summary>

**The Logic**:
When the input is `2`, the `L2` line from the decoder correctly goes LOW. This is supposed to activate the torches for segments `a, b, d, e, g`.

The display shows a `6`, meaning segments `c` and `f` are ON when they should be OFF, and segment `b` is OFF when it should be ON.

**The Conclusion**:
This points to a catastrophic failure in the "programming" of the `L2` line in your Diode Matrix. You have wired it incorrectly.
-   You have likely **accidentally placed** torch taps from the `L2` line to the segment lines for `c` and `f`.
-   You have likely **forgotten to place** the torch tap from the `L2` line to the segment line for `b`.

</details>

#### Key Terms

- **Active-Low Logic**: A design principle where the "active" or "on" state is represented by a LOW (unpowered) signal.
- **BCD (Binary-Coded Decimal)**: A method of representing the decimal digits `0`–`9` using a 4-bit binary code.
- **Decoder**: A circuit that takes a multi-bit binary input and activates a single, corresponding output line. Our decoder acts as an **Identifier**.
- **Diode Matrix**: A grid of input and output lines where components (like our taps) are placed at intersections to create a programmable logic device, often used as a ROM.
- **Encoder**: A circuit that takes a single active input line and translates it into a multi-bit coded output. Our encoder acts as a **Mapper**.
- **Modularity**: The engineering practice of designing a system in independent, interchangeable components. This makes the system easier to design, test, and upgrade.
- **ROM (Read-Only Memory)**: A type of storage where data is permanently programmed into the hardware's structure.
- **Tap (Repeater/Torch)**: Our term for a connection that reads a signal from a bus line to control another wire.
- **7-segment display**: An arrangement of seven light segments that can be combined to display numbers and some letters.

---

### Module 4 Conclusion

This was a massive milestone. You didn't just build a circuit; you engineered a complete system. By breaking a complex problem down into distinct, logical stages, you built something complex in a way that was manageable, testable, and understandable. You have now mastered the concepts of binary-to-decimal decoding and using a hardware ROM to drive an output, two fundamental building blocks of digital electronics.

**What’s Next?**

You have successfully completed **Part I** of this course! You possess a complete input and output system, and you are fluent in the language of logic.

In **Part II: The Thinking Machine**, we will take our first steps into building the brain of our computer. We'll start in **Module 5**, where we will construct a 4-bit adder to perform our first real mathematical calculation. But as you'll soon discover, making our display show the answer will present a fascinating new bug to solve, leading us to our first major system upgrade.
