## Module 4: From Binary to Pictures: Building a Digital Display

### Module 4 Summary

-   **Narrative Beat**: We've learned the computer's language. Now, let's build a translator so it can talk back to us. This is our first major engineering project, where we'll turn abstract binary signals into a number we can actually read.
-   **Learning Goals**:
    -   Understand the distinct roles of a decoder and a ROM.
    -   Grasp the engineering trade-offs between a "brute-force" design and an elegant, compact design.
    -   Master "active-low" logic and its practical application in Redstone.
    -   Build a functional Diode Matrix and understand its role as a form of Read-Only Memory (ROM).
-   **Lesson Overview**:
    -   Lesson 4.1: The Goal: Building Our 7-Segment Display
    -   Lesson 4.2: The Master Plan: A Two-Stage Translation
    -   Lesson 4.3: The Decoder Lab: A Simple "Brute-Force" Build
    -   Lesson 4.4: The Decoder Lab, Part 2: An Elegant, Compact Solution
    -   Lesson 4.5: The ROM: Programming the "Diode Matrix"
    -   Lesson 4.6: The Grand Payoff: System Integration
-   **Minecraft Artifact**: A working two-stage translator: a 4-to-10 BCD decoder and a 7-segment pattern ROM, forming a complete digital display system.

---

### Module 4 Introduction

In the previous modules, you learned how to speak to your computer in binary and how to manipulate those signals with logic gates. But a computer that can only listen isn't very satisfying. We want it to talk back! This is our first large-scale engineering project, and with it comes a new way of thinking about building.

> **Our New Rule: The Power of Abstraction**
>
> In **Modules 2 and 3**, we built every gate from scratch to understand how it worked. From this point forward, we'll operate at a higher level of abstraction.
>
> When a diagram or instruction says to "Build an AND gate," **how you choose to build it is now up to you.**
>
> -   You can build the verbose, easy-to-read version from the previous modules.
> -   You can use a smaller, more efficient version from Interlude I.
> -   You can design your own.
>
> As long as your component functions according to its truth table, it's a valid build. The preceding **Interlude I: The Art of Compact Design**, gives you the foundation for making these choices.
>
> If you're ever unsure, the verbose builds from the previous modules are guaranteed to work.

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
2.  **Isolate the Segments**: Carefully surround the lamp segments with your block of choice. I use black concrete to make the segments stand out.
3.  **Create Manual Controls**: To power each segment, run a Redstone Repeater into the middle lamp. For now, place a solid block behind each repeater and attach a Lever to it. This gives you manual control for testing.

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_7-segment-display_minecraft.png" alt="7 Segment Display in Minecraft" width="512px"/><br/><em>Figure: The display's construction stages. From left to right: the basic lamp layout, the layout isolated with concrete, powering the middle lamps of each segment, and a close-up of the repeater and lever used to control a single segment.</em></div><br/>

#### Practice Lab: Becoming a Human ROM

Before we build the logic to control this display automatically, let's do the job by hand to get a feel for how it works. Consider yourself the Mechanical Turk of this build: the human hidden inside the cabinet, working the levers so the machine appears to run itself. Use the levers you just installed to "draw" the following digits. By the end you will know exactly what our machine has to pull off once it takes over.

> **Note**: The levers are on the back of the display, so keep that in mind when flipping specific segments. It might help to label the segments with a sign by the lever that controls it for this exercise.

1.  Flip the levers for segments **`b`** and **`c`**. You should see the digit **`1`**.
2.  Now, try to display the digit **`7`**. (You will need segments `a`, `b`, and `c`).
3.  Next, create the digit **`4`**. (This requires segments `f`, `g`, `b`, and `c`).
4.  **Challenge**: Try to form the digit **`8`**. What do you notice? Now try to form the digit **`2`**.

---

### Lesson 4.2: The Master Plan: A Two-Stage Translation

> **Key Takeaway**: Complex engineering problems are best solved by breaking them down into smaller, simpler, manageable stages. The "plan" for our ROM is essentially a lookup table.

Now that we have our display, how do we control it? Our computer thinks in 4-bit binary, but our display needs 7 separate signals. Connecting the 4-bit input directly to the 7 segments would be a nightmare.

Instead, let’s do what engineers do with every problem this hairy and break it into two much simpler stages:

1.  **Decoder**: This first stage will act as an "identifier". Its only job is to look at the 4-bit binary input and determine *which* number (`` `0` ``-`` `9` ``) it represents. It will then activate a single, unique output line corresponding to that number. Because it recognizes decimal digits stored as 4-bit binary patterns, this kind of circuit is called a **BCD (Binary-Coded Decimal) decoder**. Remember that name. It will matter in Part II.
2.  **ROM**: This second stage will act as the "mapper". It receives the simple signal from the decoder (e.g., "the number is `` `3` ``!") and looks up the correct combination of the 7 segments in permanently stored wiring. A quick word on naming: a stage like this sometimes gets loosely called an *encoder*, but strictly speaking an encoder is the inverse of a decoder. We'll name this stage for what we actually build: a **ROM**, a Read-Only Memory whose contents *are* the mapping.

This modular, two-stage approach is the heart of good engineering. It's easier to build, easier to test, and far easier to fix if something goes wrong.

**Input contract:** this decoder defines an output only for the valid BCD patterns `0000` through `1001` (0 through 9). Feed it `1010` through `1111` and no line is selected, so the display just stays blank. That isn't a bug, it's the decoder's stated range, and we come back to it on purpose in Part II, once our arithmetic can produce all sixteen 4-bit patterns.

**Our Signal Flow**:
`[4-bit BCD Input: 0000–1001] → [**Decoder**] → [1 of 10 Lines] → [**ROM**] → [7 Segment Signals] → [Display]`

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_digital-display-subcircuit-abstractions_circuitverse.png" alt="Digital Display Subcircuit Abstractions" width="512px"/><br/><em>Figure: The overall system in CircuitVerse, using subcircuit abstractions for the decoder, ROM, and display to show the high-level signal flow.</em></div><br/>

---

### Lesson 4.3: The Decoder Lab: A Simple "Brute-Force" Build

> **Key Takeaway**: A decoder can be built by assigning one AND gate to recognize each unique binary input. This "brute-force" method is clear but doesn't scale well.

Before we tackle our full 4-bit to 10-line decoder, let's build a smaller, simpler version to prove the concept. We're going to build a **2-bit to 4-line decoder**. This circuit will take a 2-bit binary input (`00`, `01`, `10`, `11`) and light up one of four corresponding output lamps (`L0`, `L1`, `L2`, `L3`) representing those values in decimal (`0`, `1`, `2`, `3`).

By scaling down the problem, we can focus on the core logic without getting overwhelmed. This is a common engineering practice: start small, prove the concept, then scale up. I'm calling this a "brute-force" method because we'll build a separate AND gate for each output, rather than using a more elegant design, which we'll learn in the next lesson.

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_2-to-4-decder_circuitverse.png" alt="2-to-4 Decoder in CircuitVerse" width="512px"/><br/><em>Figure: The brute-force 2-to-4 decoder in CircuitVerse, using AND gates to recognize each binary pattern.</em></div><br/>

#### The Logic on Paper

-   **Inputs**: `B1` (the "`2`s" place), `B0` (the "`1`s" place)
-   **Outputs**: `L0`, `L1`, `L2`, `L3`
-   **Logic Gates**: We need one 2-input AND gate for each output.
    -   $L0$ (for `00` or `0`) = $\text{NOT } B1 \text{ AND } \text{NOT } B0$ : $\neg B1 \land \neg B0$
    -   $L1$ (for `01` or `1`) = $\text{NOT } B1 \text{ AND } B0$ : $\neg B1 \land B0$
    -   $L2$ (for `10` or `2`) = $B1 \text{ AND } \text{NOT } B0$ : $B1 \land \neg B0$
    -   $L3$ (for `11` or `3`) = $B1 \text{ AND } B0$ : $B1 \land B0$

---

#### Lab: Building the 2-to-4 Decoder

**Step 1: The 2-Bit Bus**

1.  Set up two standard inputs using a Redstone Lamp with a lever on one side. Label them `B1` and `B0`.
2.  From these levers, create a **4-line bus**. For each input, run one line of Redstone dust from the back of the lamp (for the true signal, e.g., `B1`) and another line into a NOT gate (for the inverted signal, e.g., $\neg B1$).
3.  You now have four parallel lines carrying the signals `B1`, $\neg B1$, `B0`, and $\neg B0$. Use colored wool to keep them organized.

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_2-to-4-decoder-1_minecraft.png" alt="2-to-4 Decoder Step 1" width="512px"/><br/><em>Figure: 4-line bus with inputs `B1` and `B0` and their inversions.</em></div><br/>

**Step 2: Build and Test the First Gate (`L0`)**

1.  Choose your favorite 2-input AND gate design from **Module 2** or **Interlude I** and build it.
2.  Connect the gate's two inputs to the $\neg B1$ line and the $\neg B0$ line on your bus. Be careful with your wiring.
3.  Place a Redstone Lamp at the output of the AND gate. This is your `L0` output.
4.  **Test it!** Set your input levers to `` `00` `` (`B1`=OFF, `B0`=OFF). The `L0` lamp should turn ON. Now, flip either lever. The lamp should turn OFF. This proves your first gate is wired correctly.

![2-to-4 Decoder Step 2, isometric](https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_2-to-4-decoder-2_minecraft.png)
<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_2-to-4-decoder-2-aerial_minecraft.png" alt="2-to-4 Decoder Step 2, aerial" width="512px"/><br/><em>Figure: Single AND gate connected to the $\neg B1$ and $\neg B0$ lines of the bus. The input is set to `` `11` ``, so the `L0` lamp is OFF. It would be on if the input were `` `00` ``.</em></div><br/>

**Step 3: Build the Remaining Gates**

1.  Build three more identical 2-input AND gates next to the first one.
2.  Wire them according to the logic table:
    -   **Gate for `L1`**: Connect its inputs to the $\neg B1$ and `B0` bus lines.
    -   **Gate for `L2`**: Connect its inputs to the `B1` and $\neg B0$ bus lines.
    -   **Gate for `L3`**: Connect its inputs to the `B1` and `B0` bus lines.
3.  Place a Redstone Lamp on the output of each gate.

**Step 4: The Grand Test**

Now, cycle through all four possible inputs with your levers:

-   `` `00` `` → Only the `L0` lamp should be ON.
-   `` `01` `` → Only the `L1` lamp should be ON.
-   `` `10` `` → Only the `L2` lamp should be ON.
-   `` `11` `` → Only the `L3` lamp should be ON.

If all four checks pass, you've built a working decoder.

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_2-to-4-decoder-3_minecraft.png" alt="2-to-4 Decoder Step 3" width="512px"/><br/><em>Figure: Final working 2-to-4 decoder, with the input set to `` `11` ``, so only the `L3` lamp is ON.</em></div><br/>

<!-- TODO(fielding): first top-down figure in the book: add the one-line intro of
     the top-down convention here (suggested wording in tix). -->
<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_2-to-4-decoder-3-aerial_minecraft.png" alt="2-to-4 Decoder (top-down)" width="512px"/><br/><em>Figure: The same decoder from directly above: the full wiring path from the two input lines to the four output lamps.</em></div><br/>

#### Lesson Summary: The Problem of Scale

Take a look at the space your 2-to-4 decoder occupies. Now, imagine our real goal: a 4-to-10 decoder. We would need **ten** 4-input AND gates, which are much larger than the simple gates we just used. The brute-force method works, but it doesn't scale well. It creates a massive, resource-hungry machine.

In the next lesson, we build the same decoder at a fraction of the size.

---

### Lesson 4.4: The Decoder Lab, Part 2: An Elegant, Compact Solution
> **Key Takeaway**: By using an "active-low" design and two clever types of "taps" (Repeater and Torch), we can build a decoder that is vastly smaller and more efficient.

Instead of an "active-high" design, we'll build an **active-low** design where the correct line turns **OFF** while every other line stays powered. Hunting for the one dark wire sounds backwards. It's also the choice the whole compact design hangs on, and it hands the ROM in the next lesson exactly the kind of signal it wants.

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_4-to-10-decoder_circuitverse.png" alt="4-to-10 Decoder in CircuitVerse" width="512px"/><br/><em>Figure: The compact 4-to-10 decoder in CircuitVerse, mirroring the Minecraft build with dual buses and NOR-like logic for efficiency.</em></div><br/>

#### The Core Concept: The Mismatch Detector

Each output line will function as a **"mismatch detector."** Its job is to power its own wire (turning its lamp OFF) if the input does **not** match the line's identity. The only time a lamp stays ON is when the input is a perfect match. A "tap" is simply our term for a connection that reads, or "taps into," the signal from one of the main bus lines.

Technically, the entire structure for each output line is a **Multi-Input NOR Gate**, but thinking of it as a "mismatch detector" is a great way to understand its function.

##### Two Types of Taps: The Key to the Design

We use two different methods to tap the bus. This allows a single bus line (e.g., `B1`) to do the work of the two separate `B1` and `!B1` lines we needed in the brute-force build, cutting our bus width in half.

To be precise about what "activates" means here: each tap sits between a bus line above and an output wire below, and when a tap activates, it **powers the output wire underneath it**. A powered output wire means "mismatch detected," which turns that line's lamp OFF.

1.  **The Repeater Tap (Checks for a `1`)**: A Repeater tapping a bus line passes power through only when that bus line is **ON (`1`)**. So it powers the output wire, flagging a mismatch, whenever a `1` shows up where the line's identity expects a `0`.
2.  **The Torch Tap (Checks for a `0`)**: A Torch attached to a bus line inverts it, so the torch lights only when that bus line is **OFF (`0`)**. It powers the output wire, flagging a mismatch, whenever a `0` shows up where the line's identity expects a `1`.

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

Now we'll place our taps to connect the input and output layers, “programming” each output line to detect its unique binary identity. Each tap checks for a mismatch, and only the perfectly matched line stays unpowered (lamp ON).

-   **How to Build a Torch Tap**: At the correct intersection, place a Redstone torch on the side of the block that the input bus line rests on, directly above the output wire below. This tap activates (powers the output wire) when the bus line is OFF (`0`).
-   **How to Build a Repeater Tap**: This requires specific placement to achieve strong power. At the correct intersection, one block *before* the output wire, break the input bus line. On the ground level, place a solid block and put a Repeater on top of it, facing in the direction of signal flow. This "snaking" path is essential. The Repeater itself doesn't power the output wire directly. It powers the block it runs into, which then becomes strongly powered and can power the output wire.

Let’s apply this to one line to see it in action, then you can program the rest using the reference chart.

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

Notice the “snaking” path of the Repeater Taps and the Torch Taps hanging off the side of the input bus blocks. Double-check your placements to avoid crossed signals.

To verify the `L3` line works as intended, you can add levers to test it independently before connecting all lines. Set the inputs to `0011` (matching `L3`’s identity):

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_4-to-10-decoder-L3-test_minecraft.png" alt="Testable L3 Line" width="512px"/><br/><em>Figure: Isolated `L3` line with levers set to `0011`, lighting the `L3` lamp to confirm correct tap placement.</em></div><br/>

In this test, the levers mimic the input `0011`. The `L3` lamp lights up because no taps activate (no mismatches), leaving the wire unpowered. Try flipping any lever (for example, to `0010`), and the lamp should turn OFF as a tap detects a mismatch.

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

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_4-to-10-decoder-compact-complete-aerial_minecraft.png" alt="Compact 4-to-10 Decoder (top-down)" width="512px"/><br/><em>Figure: The compact decoder from above: the four input lines crossing all ten output columns.</em></div><br/>

##### Test Your Work

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

### Lesson 4.5: The ROM: Programming the "Diode Matrix"

> **Key Takeaway**: Our mapper stage is a physical Read-Only Memory (ROM), built as a "diode matrix" where the layout of the wiring permanently stores the data for how to draw each number.

We now have a working decoder that pulls exactly one line low for each valid BCD digit, `0` through `9`. (Inputs `1010` through `1111` match no line, exactly as the Lesson 4.2 contract says.) The next step is to build our "mapper": the ROM that takes this single signal and draws the correct digit on our display. This job is so common that the classic real-world chip for it, the 7447, is sold as a "BCD-to-seven-segment decoder/driver". It does the same external job ours does, turning a BCD digit into seven segment signals, though its innards are ordinary logic rather than a diode matrix. We build ours as memory.

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_10-to-7-rom_circuitverse.png" alt="10-to-7 ROM in CircuitVerse" width="512px"/><br/><em>Figure: The 10-to-7 ROM in CircuitVerse, using a diode matrix structure to map the active input line to the correct segment pattern.</em></div><br/>

#### The Concept: A Physical Lookup Table

This stage is effectively a physical **Read-Only Memory (ROM)**. The "address" is the active-low line from the decoder, and the "data" that it looks up is the pattern of segments for that number. We'll build this using a structure called a **Diode Matrix**.

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

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_10-to-7-rom-1_minecraft.png" alt="ROM Output Layer" width="512px"/><br/><em>Figure: The 7 parallel segment output lines (`a` through `g`) on the ground, with repeaters for signal strength.</em></div><br/>

##### 2. The Grid: Adding the Input Layer

Now, add the input layer to complete the Diode Matrix grid. Eventually these lines will connect to the decoder’s active-low lines.

-   **Decoder Input Layer (Floating)**: Build a platform of solid blocks one level directly above the ground layer (no air gap). On this platform, run 10 horizontal lines of Redstone dust for the decoder outputs (`L9` down to `L0`), perpendicular to the 7 segment lines below. Place a Redstone Lamp at the end of each input line to visualize which line is active (LOW).

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_10-to-7-rom-2_minecraft.png" alt="ROM Two-Layer Structure" width="512px"/><br/><em>Figure: The two-layer Diode Matrix structure, with 7 segment output lines on the ground and 10 input lines (`L9`–`L0`) above, lamps showing input activity.</em></div><br/>

The lamps are optional, but they give a nice visual for what's happening: when a lamp is ON, its line is LOW (active).

##### 3. Programming the Matrix: Placing the Torch Taps

Now, “burn” the lookup table into the hardware by placing torch taps at the correct intersections. “Burn” is the industry’s actual verb for this, and it started out literal: programming an early PROM chip meant blowing microscopic fuses inside it with a jolt of current. Ours just takes torches.

-   **The Rule**: For each number line `LN`, consult the lookup table. For every segment that should be **ON** for that number, place a torch tap.
-   **How to Build the Tap**: At the correct intersection, place a **Redstone Torch on the side of the block** that the horizontal input line (`LN`) rests on. Position the torch to power the segment line on the ground below.

##### Programming Example: Line `L9`

Let’s program the `L9` line (digit `9`) as an example. According to the lookup table, digit `9` needs segments `a, b, c, d, f, g` to be ON. Place six torch taps along the `L9` line, one at each intersection with those segment lines.

Here’s a close-up of the `L9` line with its taps in place:

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_10-to-7-rom-L9_minecraft.png" alt="ROM L9 Taps Close-Up" width="512px"/><br/><em>Figure: Close-up of the `L9` line with six torch taps programming segments `a, b, c, d, f, g` for digit 9.</em></div><br/>

These torches are the ROM’s data: each one stores “this segment lights when `L9` goes LOW.” To test the line, place a lever at the start of `L9` and set all other lines to ON (using levers). When you turn the `L9` lever OFF (simulating the decoder’s active-low signal), the `L9` lamp should light up, and the segment lines `a, b, c, d, f, g` should activate. Temporary redstone lamps at the segment line ends make this easy to check. If any segment doesn’t light, double-check your torch placements against the lookup table.

##### Complete the Matrix

Repeat this process for all 10 lines (`L0`–`L9`), using the lookup table to place torches for each digit’s segment pattern. Work methodically. Every torch is a bit of stored data.

> ##### Engineering Note: The Self-Isolating Design
> You might wonder if we need repeaters to isolate the segment lines from each other like we did in our basic OR gate. In this specific design, we don’t! The Redstone Torches we use as taps are naturally **one-way devices**. They send power *out* to the segment line, but power from another torch can't flow *backwards* through them. The torches act as the diodes in our “Diode Matrix.”

##### 4. Test Your Work

Before connecting the ROM to the decoder, test all lines (`L0`–`L9`) independently, as you did for `L9`. Place a lever at the start of each line, set all others to ON, and turn the tested line OFF. Verify that the segment patterns match the lookup table (e.g., `L3` should light `a, b, c, d, g` for digit `3`). Here’s what the fully programmed Diode Matrix looks like:

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_10-to-7-rom-complete_minecraft.png" alt="Complete 10-to-7 ROM" width="512px"/><br/><em>Figure: The complete 10-to-7 ROM with all torch taps placed, showing the `L3` line active (input `0011`) and segments `a, b, c, d, g` powered for digit 3.</em></div><br/>

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_10-to-7-rom-complete-aerial_minecraft.png" alt="Complete 10-to-7 ROM (top-down)" width="512px"/><br/><em>Figure: The programmed diode matrix from above: ten input columns crossing seven segment rows; every rimmed torch tap is one stored bit.</em></div><br/>

#### Real-World Connection: BIOS and Game Cartridges

The "Diode Matrix" you've just built is a simple form of **Read-Only Memory (ROM)**. The "program" is physically burned into the circuit's layout by the placement of the torches. This exact principle was fundamental to early computing. A computer's **BIOS chip**, which tells it how to boot up, is a form of ROM. Old video game cartridges were also ROMs, with the entire game's data permanently stored in the hardware's structure. You've built the same underlying idea, even though the physical storage in a real chip works differently.

#### Software Connection: Substitution Boxes in Cryptography

Software leans on the same trick: a precomputed lookup table that never changes, baked into the program. A good example is the S-box inside AES, the encryption standard protecting most of your web traffic. It's a fixed 256-entry table that maps each input byte to an output byte, though some implementations store that table literally while others compute it on the fly or use dedicated CPU instructions. That's the same idea as the display ROM you just built, only wider: 256 entries of 8 bits instead of 10 entries of 7.

Here's the S-box as a Python lookup table, trimmed to the first row:

```python
# The AES S-box: a fixed 256-entry lookup table (first 16 entries shown)
sbox = [
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    # ... 240 more entries
]

def aes_sbox_substitute(byte):
    return sbox[byte]

print(hex(aes_sbox_substitute(0x0b)))  # 0x2b
```

In hardware, an AES S-box might be a ROM, might be plain combinational logic, or might be something else tuned to the chip's speed and area. The diode matrix is just the cleanest way to picture it.

#### Practice Problem 4.5.1: Design on Paper

You're programming the line for the digit **`2`**. According to the lookup table, which perpendicular segment lines need a torch tap from the horizontal `L2` line?

<details>
<summary><strong>Show Solution</strong></summary>

The digit `2` uses segments **`a`, `b`, `d`, `e`, and `g`**. Therefore, you would place torch taps at the intersections of the `L2` line and the perpendicular lines for those five segments.

</details>

#### Practice Problem 4.5.2: Debug Challenge

When you test your ROM by providing a LOW signal to the `L4` line, you expect to see the digit `4` (segments `b, c, f, g`). Instead, the display shows `b, c, f` but **segment `g` remains dark**. What is the most likely cause of this error?

<details>
<summary><strong>Show Solution</strong></summary>

If a segment that should be ON is OFF, it means it's not receiving power. The most likely cause is simple: you **forgot to place the torch tap** at the intersection of the horizontal `L4` line and the perpendicular segment `g` line. Without that torch, there's nothing to power the line when `L4` goes low.

</details>

---

### Lesson 4.6: The Grand Payoff: System Integration

> **Key Takeaway**: Connecting individual, tested modules into a complete, working system is the final and most rewarding step of any engineering project.

You’ve built and tested the decoder to identify numbers, the ROM to map them to segment patterns, and the 7-segment display to show the results. All that's left is to wire the three together.

---

#### Lab & Experiment: The Final Connection

This final step is all about making the connections between the components from this module. The wiring may get a bit messy, but as long as the signals flow correctly, you're good to go.

1. **Connect Decoder to ROM**: Carefully connect the `10` active-low output lines from your **Decoder** (`L0`–`L9`) to the `10` horizontal input lines of your **ROM**. Use Redstone Repeaters as needed to keep the signals strong over long distances. Label your lines to avoid mix-ups.
2. **Connect ROM to Display**: Connect the `7` output lines from your **ROM** (`a`–`g`) to the control inputs of the **7-segment Display** you built in Lesson 4.1. This may require creative wiring to route signals to the display’s repeaters, but make sure each segment line connects to its corresponding input (e.g., `a` to the `a` segment). Test each connection with a temporary lever to confirm the segment lights up.

Here’s what your fully connected system should look like, with the input set to `0011` to display a `3`:

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_complete-digital-display_minecraft.png" alt="Complete Digital Display Isometric" width="512px"/><br/><em>Figure: The complete digital display system in action, with input `0011` activating the `L3` line and lighting segments `a, b, c, d, g` to form a glowing “3”.</em></div><br/>

Your modular design has paid off: every stage was built and tested on its own, so the final assembly is just wiring.

##### Let’s Trace the Signal: `3` (`0011`)

To solidify your understanding, let’s trace the signal through the entire system with the input set to `0011` (decimal `3`):

1. You flip the input levers to `0011` (`B3=0`, `B2=0`, `B1=1`, `B0=1`).
2. **In the Decoder**: The mismatch detector for the `L3` line (identity `0011`) finds a perfect match. All its taps (Repeaters on `B3`, `B2`; Torches on `B1`, `B0`) are OFF, so the `L3` wire becomes **unpowered (LOW)**. Every other line (`L0`–`L2`, `L4`–`L9`) has at least one tap activated, powering their wires HIGH.
3. **In the ROM**: The HIGH lines keep their torches off. The `L3` line, being LOW, turns ON the torches at its intersections with segments `a, b, c, d, g` (per the Lesson 4.5 lookup table).
4. Those five torches send power down their respective segment lines.
5. **At the Display**: The signals reach the 7-segment display, lighting up segments `a, b, c, d, g` to form a perfect `3`.

From above, you can see how compactly your system fits together:

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_complete-digital-display-aerial_minecraft.png" alt="Complete Digital Display Aerial" width="512px"/><br/><em>Figure: Aerial view of the compact digital display system, with input `0011` producing a “3”. The modular layout connects the decoder, ROM, and display efficiently.</em></div><br/>

The torches in the ROM grid are less visible from this angle, so refer to the Lesson 4.5 lookup table to confirm their placements.

Here's the full schematic in CircuitVerse without subcircuit abstractions, showing the detailed wiring from 4-bit input through decoder and ROM to the 7-segment display. The layout and implementation align with our Minecraft build, and the input is currently set to `0011`, making the instructions above directly applicable.

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/04_complete-digital-display_circuitverse.png" alt="Full System in CircuitVerse" width="512px"/><br/><em>Figure: The end-to-end binary-to-display system in CircuitVerse, integrating all components from this module and displaying '3' for input `0011`.</em></div><br/>

Cycle through inputs `0000` to `1001` and watch the display light up each digit. Then try `1010` through `1111`: the display should go blank, since those six patterns fall outside the BCD decoder's documented range.

Stop and take stock of what this machine actually does: you flip four levers, and a shape you can read appears on a wall of lamps. Every step of that translation, decoder, ROM, display, is something you built and tested on its own before connecting it. That decomposition is the reason a build this size worked on the first full test, or was fixable when it didn't.

---

### Module 4 Checkpoint

#### Practice Problem 4.7.1: Knowledge Check

1.  Why is a two-stage (Decoder → ROM) design generally better than a single, complex circuit?
2.  What is the purpose of the **Repeater Tap** in our compact decoder? Why can't we just use Redstone dust?
3.  In our Diode Matrix ROM, what does placing a **Torch Tap** at an intersection physically represent?

<details>
<summary><strong>Show Solution</strong></summary>

1.  It breaks the problem down into smaller, independent modules (modularity). This makes each part easier to design, build, and debug.
2.  The Repeater Tap creates a "strongly powered" block, which is necessary to power the Redstone dust on the output line across the 1-block air gap. Simple dust would create a "weakly powered" block, which can't.
3.  It represents a single "bit" of stored information. Specifically, it's a command to "turn this segment ON when this number line is selected (LOW)."

</details>

#### Practice Problem 4.7.2: Decoder Design

Within the valid BCD range (`0000` through `1001`), you want to add a special output line, `LE`, that lights for the even digits (`0`, `2`, `4`, `6`, `8`). Every even BCD digit has `B0` = `0`. What single tap would build a detector for this?

<details>
<summary><strong>Show Solution</strong></summary>

You want the lamp to be ON only when `B0` is `0`. Our active-low system turns the lamp on when the line is unpowered. You would need a single **Repeater Tap** from the `B0` line. When `B0` is `1` (odd), the repeater powers the `LE` line and turns the lamp off. When `B0` is `0` (even), the repeater is off, the line is unpowered, and the lamp turns on. That works only because of the BCD input contract: without it, the same detector would also light for the even 4-bit values 10, 12, and 14.

</details>

#### Practice Problem 4.7.3: ROM Design

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

In the world download for this module, you'll find a section labeled "Module 4 Debug Challenge." The display system is fully connected. When you input **`0010`** (for the number 2), the display incorrectly shows a **`6`**.

**Trace the logic**:
  - The digit `2` should be `a, b, g, e, d`.
  - The digit `6` is `a, c, d, e, f, g`.

Which row of the ROM should you inspect, and which tap differences would turn the correct pattern for `2` into the `6` you're seeing? (Hint: the problem is in the ROM).

<details>
<summary><strong>Show Solution</strong></summary>

**The Logic**:
When the input is `2`, the `L2` line from the decoder correctly goes LOW. This is supposed to activate the torches for segments `a, b, d, e, g`.

The display shows a `6`, meaning segments `c` and `f` are ON when they should be OFF, and segment `b` is OFF when it should be ON.

**The Conclusion**:
The decoder did its job and selected the `L2` line correctly. The fault is in that line's ROM programming, and it's three taps, not one:
-   Segment `b` should be ON but is OFF, so the `L2` → `b` torch tap is **missing**.
-   Segments `c` and `f` should be OFF but are ON, so the `L2` → `c` and `L2` → `f` taps were **added by mistake**.

So it's a misprogrammed `L2` row, three taps off, not a system failure.

</details>

#### Key Terms

- **Active-Low Logic**: A design principle where the "active" or "on" state is represented by a LOW (unpowered) signal.
- **BCD (Binary-Coded Decimal)**: A method of representing the decimal digits `0`–`9` using a 4-bit binary code.
- **Decoder**: A circuit that takes a multi-bit binary input and activates a single, corresponding output line. Our decoder acts as an **Identifier**.
- **Diode Matrix**: A grid of input and output lines where components (like our taps) are placed at intersections to create a programmable logic device, often used as a ROM.
- **Encoder**: In standard usage, the inverse of a decoder: it takes one active line among many and produces a compact binary code. We don't build one in this course. Mapper stages like our ROM are sometimes loosely called encoders, but the name properly belongs to the binary-code producer.
- **Modularity**: The engineering practice of designing a system in independent, interchangeable components. This makes the system easier to design, test, and upgrade.
- **ROM (Read-Only Memory)**: A type of storage where data is permanently programmed into the hardware's structure.
- **Tap (Repeater/Torch)**: Our term for a connection that reads a signal from a bus line to control another wire.
- **7-segment display**: An arrangement of seven light segments that can be combined to display numbers and some letters.

---

### Module 4 Conclusion

You engineered a complete system in this module, and by breaking it into distinct, logical stages, you kept it manageable, testable, and understandable. You now know how to decode a 4-bit BCD digit and how a hard-wired lookup table can drive a display, two fundamental building blocks of digital electronics.

**What’s Next?**

That completes **Part I** of this course. You have a complete input and output system, and you're fluent in the language of logic.

In **Part II: The Thinking Machine**, we take our first steps into building the brain of our computer, starting in **Module 5** with a 4-bit adder and our first real calculation. Keep the display handy. The moment we ask it to show an answer we didn't choose ourselves, a new bug surfaces, and chasing it down leads to our first major system upgrade.
