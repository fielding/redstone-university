## Module 8: The Multiplexer – The Digital Switch

### Module 8 Summary

-   **Narrative Beat:** We have built several powerful circuits, but power without control is chaos. This module introduces the component that lets the processor choose which path to follow and which result to pay attention to: the **multiplexer**.
-   **Learning Goals:**
    -   Understand a multiplexer as a digitally controlled selector switch.
    -   Build a 1-bit 2-to-1 MUX from NOT, AND, and OR gates.
    -   Scale that idea into a 4-bit bus-wide MUX.
    -   See how small control signals can steer much larger data paths.
-   **Lesson Overview:**
    -   Lesson 8.1: The theory – The power of choice
    -   Lesson 8.2: The lab – Building a 1-bit MUX
    -   Lesson 8.3: The lab – Scaling up to a 4-bit MUX
-   **Minecraft Artifact:** A 4-bit 2-to-1 multiplexer.

---

### Module 8 Introduction

Up to now, we have spent most of our time learning how to *compute* things.

-   We can add.
-   We can subtract.
-   We can compare.
-   We can generate flags.

But what happens when several of those results exist at once?

If the adder, the AND circuit, and the XOR circuit are all producing outputs in parallel, how does the computer choose which one should move forward? We need a device that can steer data without changing the data itself.

That device is the **multiplexer**, usually shortened to **MUX**.

A MUX is the digital version of a selector knob or railway switch. It chooses one input and forwards it to the output. This sounds simple, and it is, but it is one of the most important control components in all of computer architecture.

---

### Lesson 8.1: The theory – The power of choice

> **Key Takeaway:** A 2-to-1 multiplexer uses one select signal to choose which of two data inputs reaches the output.

A **2-to-1 MUX** has:

-   two data inputs: `A` and `B`
-   one select input: `S`
-   one output: `Y`

Its behavior is:

-   if $S = 0$, then $Y = A$
-   if $S = 1$, then $Y = B$

That behavior can be written as a truth table:

| S | A | B | Y |
| :---: | :---: | :---: | :---: |
| `0` | `0` | `0` | `0` |
| `0` | `0` | `1` | `0` |
| `0` | `1` | `0` | `1` |
| `0` | `1` | `1` | `1` |
| `1` | `0` | `0` | `0` |
| `1` | `0` | `1` | `1` |
| `1` | `1` | `0` | `0` |
| `1` | `1` | `1` | `1` |

#### How we build it from basic gates

We use two AND gates as gatekeepers and an OR gate as the final combiner:

-   left gatekeeper: $A \land \neg S$
-   right gatekeeper: $B \land S$
-   combine them: $Y = (A \land \neg S) \lor (B \land S)$

Why does this work?

-   If `S = 0`, then $\neg S = 1$
    -   left path becomes $A \land 1 = A$
    -   right path becomes $B \land 0 = 0$
    -   output becomes $A \lor 0 = A$
-   If `S = 1`, then $\neg S = 0$
    -   left path becomes $A \land 0 = 0$
    -   right path becomes $B \land 1 = B$
    -   output becomes $0 \lor B = B$

So a MUX is really a very disciplined way of opening exactly one path while closing the other.

---

### Lesson 8.2: The lab – Building a 1-bit MUX

> **Key Takeaway:** A 1-bit multiplexer is the direct physical implementation of the expression $Y = (A \land \neg S) \lor (B \land S)$.

#### Lab & Experiment

<div align="center"><img src="./images/1-bit-mux-circuitverse.png" alt="1-Bit MUX CircuitVerse Diagram" width="512px"/><br/><em>Figure: A 1-bit 2-to-1 MUX. The select line and its inverse control which of the two data paths is allowed through.</em></div><br/>

1.  Create three input levers labeled `A`, `B`, and `S`.
2.  Build a NOT gate on the select line to generate $\neg S$.
3.  Build the first AND gate for $A \land \neg S$.
4.  Build the second AND gate for $B \land S$.
5.  Feed both AND outputs into a final OR gate.
6.  Connect the OR output to a lamp labeled `Y`.

#### The experiment

Run the following tests slowly and deliberately:

1.  Set `S = 0`.
    -   Flip $A$ on and off.
    -   Verify that $Y$ follows $A$ exactly.
    -   Verify that $B$ does nothing.
2.  Set `S = 1`.
    -   Flip $B$ on and off.
    -   Verify that $Y$ follows $B$ exactly.
    -   Verify that $A$ does nothing.

<div align="center"><img src="./images/1-bit-mux-minecraft.png" alt="1-Bit MUX Minecraft Build" width="512px"/><br/><em>Figure: A 1-bit MUX in Minecraft. The select line determines whether the output copies input A or input B.</em></div><br/>

#### A good debugging question

If the output always follows $A$ and never follows $B$, check two places first:

-   Is the $\neg S$ inverter working?
-   Is $S$ actually reaching the AND gate on the $B$ path?

MUX bugs are often just control-line bugs.

---

### Lesson 8.3: The lab – Scaling up to a 4-bit MUX

> **Key Takeaway:** A 4-bit MUX is simply four 1-bit MUXes that share the same select line and operate in parallel on a bus.

Our computer does not move around single bits very often. It moves 4-bit values. So now we scale the exact same idea up to a whole bus.

#### The core idea

Build four identical 1-bit MUX slices:

-   slice 0 handles bit 0
-   slice 1 handles bit 1
-   slice 2 handles bit 2
-   slice 3 handles bit 3

All four slices share the same select signal $S$.

That means the machine does not choose each bit individually. It chooses the **entire 4-bit word** at once.

#### Lab & Experiment

1.  Create two 4-bit input buses: **Bus A** and **Bus B**.
2.  Build four copies of your 1-bit MUX.
3.  Connect:
    -   $A_0$ and $B_0$ to the first slice
    -   $A_1$ and $B_1$ to the second slice
    -   $A_2$ and $B_2$ to the third slice
    -   $A_3$ and $B_3$ to the fourth slice
4.  Distribute the same select line $S$ and its inverse $\neg S$ to all four slices.
5.  Collect the four slice outputs into a single 4-bit output bus.

#### The experiment

Try these tests:

-   Bus A = `0101`, Bus B = `1100`, `S = 0` → output should be `0101`
-   Bus A = `0101`, Bus B = `1100`, `S = 1` → output should be `1100`
-   Bus A = `1111`, Bus B = `0000`, `S = 0` → output should be `1111`
-   Bus A = `1111`, Bus B = `0000`, `S = 1` → output should be `0000`

<div align="center"><img src="./images/4-bit-mux-minecraft.png" alt="4-Bit MUX Minecraft Build" width="512px"/><br/><em>Figure: A 4-bit 2-to-1 MUX. Four 1-bit slices work in parallel, all controlled by the same select line.</em></div><br/>

#### Why this matters for the ALU

In the next module, several different calculation lanes will be active at the same time. The MUX will be the judge that says, “use this result, ignore the others.”

That is a huge job for such a small-looking component.

---

### Module 8 Conclusion

You have now built one of the essential routing elements of digital design.

A multiplexer does not perform arithmetic. It does not store memory. It does something just as important: it creates **choice**. It lets a tiny control signal decide which much larger data signal is allowed to continue.

That is one of the central themes of computer architecture: small control, large effect.

In the next module, we will put that idea to work by assembling the ALU itself. Several different calculation lanes will run in parallel, and your new multiplexer will choose which result becomes the processor’s official answer.

---

### Module 8 Checkpoint

#### Practice Problem 8.4.1: Knowledge Check

1.  In plain language, what does a multiplexer do?
2.  What is the Boolean expression for a 2-to-1 MUX?
3.  If you wanted to choose among four different inputs instead of two, how many select bits would you need?

<details>
<summary><strong>Show Solution</strong></summary>

1.  A multiplexer chooses one of several inputs and forwards the selected one to its output.
2.  $Y = (A \land \neg S) \lor (B \land S)$
3.  You would need **2** select bits, because 2 bits can represent four choices: `00`, `01`, `10`, and `11`.

</details>

#### Practice Problem 8.4.2: The demultiplexer

A **demultiplexer** does the opposite of a MUX: it takes one input and routes it to one of multiple outputs.

For a 1-to-2 DEMUX with input $D$, select $S$, and outputs $Y_0$ and $Y_1$, write the two Boolean expressions.

<details>
<summary><strong>Show Solution</strong></summary>

-   $Y_0 = D \land \neg S$
-   $Y_1 = D \land S$

</details>

#### Practice Problem 8.4.3: Design challenge

How could you build a **4-to-1** 4-bit MUX using only the 4-bit 2-to-1 MUX you built in this module?

<details>
<summary><strong>Show Solution</strong></summary>

Use **three** 4-bit 2-to-1 MUX blocks:

1.  First stage:
    -   MUX 1 chooses between inputs 0 and 1
    -   MUX 2 chooses between inputs 2 and 3
2.  Second stage:
    -   MUX 3 chooses between the outputs of MUX 1 and MUX 2

One select bit controls the first-stage choices, and the other select bit controls the final choice.

</details>

#### Real-world connection: Bus routing inside processors

Inside a real CPU, multiplexers appear everywhere: selecting which register feeds the ALU, choosing the next program counter value, deciding whether an address comes from the PC or from an instruction operand, and routing results back into the right destination. A modern processor contains an enormous number of “what should this wire carry right now?” decisions, and MUXes are a standard answer.

#### Software connection: The ternary operator

In software, a tiny version of MUX-like behavior shows up in expressions such as:

```python
y = a if s == 0 else b
```

That is conceptually the same as a 2-to-1 multiplexer:

-   one control value decides
-   one of two possible data values is chosen
-   the chosen value becomes the output

#### Key Terms
-   **Data path**: The route along which actual data values travel through a digital system.
-   **Demultiplexer (DEMUX)**: A circuit that routes one input to one of several possible outputs.
-   **Multiplexer (MUX)**: A circuit that selects one of several inputs and forwards it to a single output.
-   **Select line**: The control signal that tells a multiplexer which input to choose.
