## Module 9: The ALU – The Grand Assembly

### Module 9 Summary

-   **Why This Module:** This is the capstone of Part II. We will gather every major arithmetic and logic circuit we have built so far, run them in parallel, and forge them into the processor’s working core: the **Arithmetic Logic Unit**.
-   **Learning Goals:**
    -   Understand the architecture of a simple bus-based 4-bit ALU.
    -   Organize multiple operations into parallel calculation lanes.
    -   Use layered multiplexers to select the ALU’s official output.
    -   Attach status flag logic so the ALU reports more than just a numeric result.
-   **Lesson Overview:**
    -   Lesson 9.1: The blueprint for a brain
    -   Lesson 9.2: The lab – Assembling the calculation lanes
    -   Lesson 9.3: The lab – Building the output selector
    -   Lesson 9.4: The final integration and testing
-   **Build:** A complete 4-bit ALU that can perform AND, OR, XOR, ADD, and SUB, while also producing Zero and Negative flags.

---

### Module 9 Introduction

Everything in Part II has been pointing here.

-   Module 5 gave us addition.
-   Module 6 expanded that into subtraction.
-   Module 7 taught the machine how to report on its own results.
-   Module 8 gave us the switch we need to choose among competing paths.

Now we assemble the whole thing.

The **Arithmetic Logic Unit**, or **ALU**, is the active heart of a processor. It is the block that performs arithmetic, logic, and comparison-supporting work. When people say a CPU can “do math” or “evaluate a condition,” they are really talking about the ALU.

In this module, we will not build one giant, monolithic circuit. We will build something much better: a carefully organized machine with parallel lanes, clear control signals, and a selector that chooses which result becomes official.

This is one of the most satisfying kinds of engineering. You already know all the pieces. The reward is in seeing them become a single system.

---

### Lesson 9.1: The blueprint for a brain

> **Key Takeaway:** A simple ALU works by performing multiple candidate operations in parallel and then selecting one final result with control signals.

Our ALU will begin with two 4-bit input buses:

-   **Bus A**
-   **Bus B**

Those same two buses will feed several **calculation lanes** at the same time.

#### Our four lanes

We will build four visible result lanes:

1.  **AND lane**
2.  **OR lane**
3.  **XOR lane**
4.  **Arithmetic lane**

The arithmetic lane is special because it can do two jobs:

-   **ADD** when `SUB = 0`
-   **SUB** when `SUB = 1`

So although we only have four visible lanes, we effectively get **five** operations:

| F1 | F0 | SUB | Operation |
| :---: | :---: | :---: | :--- |
| `0` | `0` | `x` | AND |
| `0` | `1` | `x` | OR |
| `1` | `0` | `x` | XOR |
| `1` | `1` | `0` | ADD |
| `1` | `1` | `1` | SUB |

The `SUB` line only matters when the selector is pointed at the arithmetic lane.

#### Why parallel lanes are a good design

We are not turning circuits on and off one at a time. All lanes can compute continuously from the same inputs. That gives us two big benefits:

1.  the design is more modular and easier to debug
2.  the final control logic becomes a selection problem instead of a construction problem

That second point matters. Rather than asking, “How do I build a brand-new circuit for each operation?” we ask, “Which already-computed result should I forward?”

That is classic computer architecture thinking.

![ALU Architecture Diagram](./images/alu-architecture-circuitverse.png)
*Figure: A high-level ALU architecture. The A and B buses feed several calculation lanes in parallel, and a selector chooses which lane becomes the final output.*

---

### Lesson 9.2: The lab – Assembling the calculation lanes

> **Key Takeaway:** The first stage of an ALU build is to make every desired operation available as its own clean, testable 4-bit lane.

#### Lab & Experiment

1.  **Lay out the shared inputs**
    -   Create long, clearly labeled 4-bit buses for **A** and **B**.
    -   Make sure each lane can tap those buses cleanly.
2.  **Build the arithmetic lane**
    -   Reuse your adder/subtractor from Module 6.
    -   Keep its `SUB` control line accessible.
    -   Preserve the final carry lamp if you want an optional arithmetic indicator.
3.  **Build the AND lane**
    -   Four AND gates in parallel, one per bit.
4.  **Build the OR lane**
    -   Four OR gates in parallel.
5.  **Build the XOR lane**
    -   Four XOR gates in parallel.
6.  **Label each output bus**
    -   AND result bus
    -   OR result bus
    -   XOR result bus
    -   Arithmetic result bus

![ALU Lanes Minecraft Build](./images/alu-lanes-minecraft.png)
*Figure: The ALU’s calculation lanes in parallel. Each lane sees the same A and B inputs and continuously computes its own candidate result.*

#### A recommended bring-up order

Before you build the selector, verify each lane independently:

-   AND test: `1100 AND 0101 = 0100`
-   OR test: `1100 OR 0101 = 1101`
-   XOR test: `1100 XOR 0101 = 1001`
-   ADD test: `1100 + 0101 = 0001` with carry active
-   SUB test: `1100 - 0101 = 0111`

If the final ALU misbehaves later, this early lane-by-lane testing will save you a huge amount of time.

---

### Lesson 9.3: The lab – Building the output selector

> **Key Takeaway:** A 4-to-1 selector can be built by composing the 2-to-1 MUX blocks from Module 8, proving the power of modular reuse.

We need to choose one of four 4-bit lanes.

The cleanest way to do that is with a **two-stage MUX tree** built from the exact 4-bit 2-to-1 MUX you already know how to make.

#### The selector plan

Use three 4-bit MUX blocks:

1.  **Left first-stage MUX**
    -   chooses between **AND** and **OR**
2.  **Right first-stage MUX**
    -   chooses between **XOR** and **Arithmetic**
3.  **Final second-stage MUX**
    -   chooses between the outputs of the two first-stage MUXes

#### Control mapping

Let the control bits be `F1` and `F0`.

-   `F0` controls the two first-stage MUXes
-   `F1` controls the final second-stage MUX

That gives this mapping:

| F1 F0 | Selected output |
| :---: | :--- |
| `00` | AND |
| `01` | OR |
| `10` | XOR |
| `11` | Arithmetic |

Then the separate `SUB` line decides whether the arithmetic lane behaves as ADD or SUB.

#### Lab & Experiment

1.  Build the first 4-bit MUX and feed it the AND and OR buses.
2.  Build the second 4-bit MUX and feed it the XOR and Arithmetic buses.
3.  Build the third 4-bit MUX and feed it the outputs of the first two MUXes.
4.  Create a small control panel with three levers:
    -   `F1`
    -   `F0`
    -   `SUB`
5.  Distribute `F0` to the first-stage MUXes.
6.  Distribute `F1` to the second-stage MUX.
7.  Keep the final 4-bit selector output clearly labeled as the **ALU Result Bus**.

![ALU MUX Minecraft Build](./images/alu-mux-minecraft.png)
*Figure: The ALU selector built from layered 4-bit MUX blocks. The control lines determine which lane reaches the final result bus.*

#### Why this design is satisfying

Notice what just happened:

-   Module 8 taught us a small routing primitive.
-   Module 9 used it as a large routing system.

That is the hallmark of a strong architecture. Small, trustworthy pieces scale.

---

### Lesson 9.4: The final integration and testing

> **Key Takeaway:** An ALU is not complete until its selected output is paired with status information that software can use for future decisions.

Now we turn the selector output into the ALU’s official output and attach the status flag logic from Module 7.

#### Lab & Experiment

1.  Take the final 4-bit result bus from your selector.
2.  Feed that bus into the **Zero Flag** circuit.
3.  Feed the most-significant result bit into the **Negative Flag** circuit.
4.  Label the outputs clearly:
    -   Result bus
    -   Zero (`Z`)
    -   Negative (`N`)
5.  If you preserved the arithmetic carry lamp from Module 6, keep it visible as an optional diagnostic output.

#### The full ALU test matrix

Use these shared inputs first:

-   `A = 1100` (`C`)
-   `B = 0101` (`5`)

Now test each mode:

| F1 F0 | SUB | Operation | Expected result | Z | N |
| :---: | :---: | :--- | :---: | :---: | :---: |
| `00` | `x` | AND | `0100` | `0` | `0` |
| `01` | `x` | OR | `1101` | `0` | `1` |
| `10` | `x` | XOR | `1001` | `0` | `1` |
| `11` | `0` | ADD | `0001` | `0` | `0` |
| `11` | `1` | SUB | `0111` | `0` | `0` |

Now deliberately test the Zero Flag:

-   `A = 0101`
-   `B = 0101`
-   select Arithmetic with `SUB = 1`
-   expected result: `0000`
-   expected `Z = 1`

And deliberately test the Negative Flag:

-   `A = 0010`
-   `B = 0111`
-   select Arithmetic with `SUB = 1`
-   expected result: `1011`
-   expected `N = 1`

This is the moment where the machine starts to feel truly processor-like. It can perform several classes of operation and summarize the outcome in control-friendly bits.

---

### Lesson 9.5: Scaling up – the bit-slice

Back in Interlude I, we made you a promise: compact designs would matter "when
you need to build dozens of them for an arithmetic unit." You have now built
that arithmetic unit, and you built it wide, flat, and readable, exactly as
you should have. This lesson keeps the promise. We are going to take one bit
of your ALU, compress it, and then show you the scaling trick that real
machines, in Minecraft and in silicon, use to grow from 4 bits to 8, 16, or
64 without redesigning anything: **the bit-slice**.

#### The key observation

Look at your four calculation lanes. Bit 2's hardware is *identical* to bit
1's. The only thing that differs between bits is which wires they connect to:
their inputs, and the carry passing between neighbors. A machine like ours
isn't really "a 4-bit ALU"; it is **one 1-bit ALU, stamped four times**. That
repeating unit is called a bit-slice, and once you can build one slice, the
machine's width is just a number.

#### Building in the third dimension

So far, this course has been almost perfectly flat. Every circuit you have
built lives on one floor, because flat circuits are readable circuits. But
stacking slices means sending signals **up**, and vertical Redstone has its
own small vocabulary. Three tools and one warning:

-   **The dust staircase.** Dust climbs one block per step, diagonally. It is
    the vertical wire.
-   **Transparent blocks (glass, slabs).** Dust sits on them and climbs over
    them, but they refuse to pass power *through* themselves, which makes
    them perfect insulation between floors. A signal can climb past a floor
    it isn't allowed to touch.
-   **Reading through the floor.** Dust weakly powers the solid block beneath
    it, and a repeater can read that block from the other side. This is how a
    signal on one floor drops *into* the floor below without a staircase,
    the trick that makes 2-block-tall slices possible at all.
-   **The warning:** a solid block directly above dust cuts its diagonal
    climb. When floors are packed this tightly, every ceiling block is part
    of the circuit, whether you meant it to be or not.

*Figure placeholder: the three vertical idioms, rendered as a labeled
iso (staircase, glass tower, through-floor read).*

#### Signal strength as data

One more idea, and it is the deepest one in this lesson. Until now we have
treated Redstone power as binary: powered or not. But you know from Module 0
that power is really a number from 0 to 15, and compact designs exploit
that. A comparator in subtract mode doesn't just gate a signal; it does
*arithmetic on signal strengths*. Two comparators pointed at each other's
inputs compute |A − B|, which, for binary inputs, **is XOR**. One block,
where our verbose XOR needed a dozen.

This is why compact builds lean so heavily on the comparators you met in
Module 7, and it is also their price: a circuit that computes with strengths
can fail from one block of extra wire decay, and you can't see the failure
the way you can see a dark dust line. Compact designs are not smaller
versions of your circuits; they are a different *technology* built on the
same logic.

#### Lab & Experiment: the compact slice

*Draft note: build recipe + exact layer maps to be inserted from the verified
in-world build; figure placeholders below.*

1.  **Study the legible slice.** One bit of your ALU: two XORs, an AND-OR
    carry. You built it in Lesson 9.2; now draw its truth table one more time.
2.  **Build the compact slice from the layer map.** Two layers: a *rail
    layer* (inputs, first XOR, output lamp) and a *logic layer* (second XOR
    and carry). You are not designing this circuit; you are reading someone
    else's schematic and building it faithfully, which is itself an
    engineering skill. Verify it against the same truth table.
3.  **Stack four slices.** The carry climbs a dedicated column from each
    slice to the next; the bottom slice is special (nothing below it to
    listen to), and so is the top (its carry-out is your overflow signal).
    Verify with the same test matrix you used in Lesson 9.4.

*Figure placeholder: legible slice and compact slice side by side, same
tint on the matching subcircuits.*
*Figure placeholder: the 4-stack, exploded view, carry column highlighted.*
*Figure placeholder: top-down view of one slice; note that this single
image documents the entire machine.*

#### Why we still built it flat first

You could not have debugged the compact slice as your first adder. When your
flat adder misbehaved, you could *see* the stuck carry. In the compact stack,
that same bug lives inside a sandwich of floors, encoded as a signal
strength. Engineers everywhere work this way: design readable, then compress
with confidence, because the truth table, not the layout, is the circuit.
From here on, when a module's final build grows to machine scale, we will
offer both shapes: the flat build you can trace, and the sliced build you
can stack.

---

### Module 9 Checkpoint

#### Practice Problem 9.6.1: Knowledge Check

1.  Why is it useful to compute several ALU lanes in parallel instead of trying to build only the selected operation on demand?
2.  In our ALU design, what do the bits `F1 F0 = 10` select?
3.  If the ALU result is `1000`, what should the `Z` and `N` flags be?

<details>
<summary><strong>Show Solution</strong></summary>

1.  Parallel lanes make the design more modular and simpler to control. The hardware computes candidate results continuously, and the selector only needs to choose which one to forward.
2.  `F1 F0 = 10` selects the **XOR** lane.
3.  `Z = 0` and `N = 1`.

</details>

#### Practice Problem 9.5.2: The expansion

You want to add a new ALU function: **NOT A**.

Describe one reasonable way to expand the ALU to support it.

<details>
<summary><strong>Show Solution</strong></summary>

One good approach is:

1.  Build a new 4-bit lane consisting of four NOT gates driven from Bus A.
2.  Expand the selector so it can choose among five lanes instead of four.
3.  That likely means either:
    -   adding another control bit and a larger MUX structure, or
    -   reorganizing the lane tree into a bigger selector network.

</details>

#### Practice Problem 9.5.3: Debug challenge

Your ALU gives correct results for AND, OR, XOR, and ADD, but when you select SUB it still behaves like ADD.

What is the most likely missing or incorrect control connection?

<details>
<summary><strong>Show Solution</strong></summary>

The most likely issue is that the **SUB control line is not reaching the arithmetic lane**.

That line must do two jobs inside the adder/subtractor:

-   drive the XOR bank that conditionally inverts Bus B
-   drive the initial carry-in that adds the required `1`

If `SUB` never reaches that circuit, the arithmetic lane remains stuck in addition mode.

</details>

#### Real-world connection: What an ALU really is

In real processors, the ALU is one of the core execution units. It may support many more operations than ours: shifts, rotates, comparisons, add-with-carry, increment/decrement, and more. But the underlying idea is the same. A few control bits tell the unit which operation’s output should be considered the official result. Your Minecraft ALU is a faithful miniature of that principle.

#### Software connection: Bitwise operators map directly to hardware

When you write software such as:

```python
x = a & b
y = a ^ b
z = a | b
```

you are asking the processor for exactly the kinds of bitwise results your ALU now computes. Those operators are not metaphors. They map naturally onto simple parallel gate networks just like the ones you built here.

#### Key Terms
-   **ALU (Arithmetic Logic Unit)**: The processor subsystem that performs arithmetic and logical operations on binary data.
-   **Arithmetic lane**: The ALU subcircuit that performs addition and subtraction in this design.
-   **Control signal**: A signal that configures or steers a digital system rather than carrying ordinary data.
-   **Flag**: A one-bit summary of some property of the ALU result, such as zero or negative.
-   **Lane**: One parallel operation path inside the ALU.
-   **Opcode**: A code that specifies which operation a processor should perform.
-   **Result bus**: The final output bus carrying the ALU’s selected result.

---

### Module 9 Conclusion

You have now built the brain of your computer.

A real, structured ALU with parallel lanes, explicit control signals, selected output, and status reporting.

This is the point where the project begins to transform from “a collection of neat Redstone circuits” into “an actual computer architecture.” We now have a component that can meaningfully process data.

In Part III, we will surround that brain with memory and control. We will give it places to store values, places to fetch instructions from, and eventually a clocked rhythm that lets it run without your hands on every lever.

