## Module 7: Comparators and Status Flags – The Dawn of Decision-Making

### Module 7 Summary

-   **Why This Module:** Our machine can already calculate, but calculation alone is not enough for programming. In this module, we will teach it how to *notice* something about its own results. That awareness is the foundation of branching, loops, and every `if` statement you have ever written.
-   **Learning Goals:**
    -   Understand why decision-making requires hardware that can evaluate conditions.
    -   Build a 4-bit equality comparator using XNOR and AND gates.
    -   Learn what **status flags** are and why CPUs use them instead of building dedicated hardware for every question.
    -   Build the logic for the **Zero** and **Negative** flags.
-   **Lesson Overview:**
    -   Lesson 7.1: From calculation to computation
    -   Lesson 7.2: The equality comparator
    -   Lesson 7.3: The art of awareness – An introduction to status flags
    -   Lesson 7.4: Building the flag logic
-   **Build:** A 4-bit equality comparator and a 2-bit status flag circuit.

---

### Module 7 Introduction

So far, our computer behaves like a very obedient calculator.

You choose the inputs.
You choose the operation.
It gives you a result.

That is useful, but it is not yet enough to support real programs.

A program becomes powerful when it can ask questions such as:

-   Is this value zero?
-   Did the subtraction produce a negative answer?
-   Are these two numbers the same?

Those questions are not abstract software magic. They must be answered somewhere in hardware.

This module is where the machine begins to develop a primitive kind of self-awareness. We will first build a direct comparator so the logic is easy to see. Then we will learn the more scalable CPU approach: let the ALU do a calculation and produce a few tiny bits of metadata called **flags**.

Those flags are the bridge between arithmetic and decision-making.

---

### Lesson 7.1: From calculation to computation

> **Key Takeaway:** A computer becomes far more powerful when it can change its behavior based on the outcome of a previous operation.

Imagine a game program.

-   If the player’s health reaches `0`, show the “Game Over” screen.
-   While there are still enemies on screen, keep the music playing.
-   If two passwords match, unlock the account.

All of these behaviors depend on a condition.

At the hardware level, that means the machine must be able to answer yes/no questions about data. This is the physical basis of **control flow**.

Up to this point, our machine has been linear. Signals go in, logic happens, signals come out. But in a real computer, the result of one operation influences what happens next. That is what turns mere calculation into **computation**.

To get there, we need two related tools:

1.  a way to compare values directly
2.  a compact way to summarize the result of an ALU operation

We will build both.

---

### Lesson 7.2: The equality comparator

> **Key Takeaway:** Two multi-bit values are equal if and only if every corresponding pair of bits is equal.

The simplest question a computer can ask is:

> Are these two values the same?

For 4-bit numbers, that means:

-   $A_3$ must equal $B_3$
-   $A_2$ must equal $B_2$
-   $A_1$ must equal $B_1$
-   $A_0$ must equal $B_0$

We already have the perfect gate for checking whether two bits match: **XNOR**.

-   if the two inputs are the same, XNOR outputs `1`
-   if they are different, XNOR outputs `0`

So the plan is:

1.  Compare each pair of bits with an XNOR gate.
2.  Feed all four XNOR outputs into an AND gate.
3.  If all four bit-pairs matched, the final output will be `1`.

#### The theory

The equality output is:

$Equal = (A_3 \odot B_3) \land (A_2 \odot B_2) \land (A_1 \odot B_1) \land (A_0 \odot B_0)$

where $\odot$ represents XNOR.

That expression says exactly what we want: **all four pairs must match**.

---

#### Lab & Experiment: Building the 4-bit equality comparator

<div align="center"><img src="./images/comparator-circuitverse.png" alt="4-Bit Equality Comparator CircuitVerse Diagram" width="512px"/><br/><em>Figure: A 4-bit equality comparator. Each bit-pair is checked with XNOR, and the four match signals are combined through an AND gate.</em></div><br/>

1.  Create two 4-bit input buses, $A$ and $B$.
2.  Build four XNOR gates:
    -   compare $A_0$ with $B_0$
    -   compare $A_1$ with $B_1$
    -   compare $A_2$ with $B_2$
    -   compare $A_3$ with $B_3$
3.  Feed the four XNOR outputs into a 4-input AND gate.
4.  Connect the final output to a lamp labeled **A = B**.

#### The experiment

Run these tests:

-   $A = 1010$, $B = 1010$ → lamp ON
-   $A = 1010$, $B = 1011$ → lamp OFF
-   $A = 0000$, $B = 0000$ → lamp ON
-   $A = 1111$, $B = 0111$ → lamp OFF

<div align="center"><img src="./images/comparator-minecraft.png" alt="4-Bit Equality Comparator Minecraft Build" width="512px"/><br/><em>Figure: A 4-bit equality comparator in Minecraft. The output lamp is lit only when every bit on bus A matches the corresponding bit on bus B.</em></div><br/>

This circuit is a good direct answer to the question of equality.

But CPUs usually prefer a more flexible strategy: do one arithmetic operation, then inspect a few flags that describe the result.

---

### Lesson 7.3: The art of awareness – An introduction to status flags

> **Key Takeaway:** Status flags are tiny one-bit summaries of what just happened in the ALU. They let a computer make decisions without needing a separate large circuit for every kind of test.

A real processor does not usually build a dedicated equality comparator for every comparison instruction. Instead, it often performs a subtraction and then asks questions about the result.

For example:

-   To test whether $A = B$, compute $A - B$
-   If the result is `0000`, then the values were equal

That is elegant because the ALU is already there. We simply need a compact report describing what the ALU produced. That report lives in a small collection of one-bit signals called **status flags**.

In this course, we will build the two most important starter flags:

1.  **Zero Flag (`Z`)**
    -   `Z = 1` if the result bus is `0000`
    -   This is the hardware foundation of equality tests
2.  **Negative Flag (`N`)**
    -   `N = 1` if the most significant bit of the result is `1`
    -   In Two's Complement interpretation, that means the result is negative

A useful caution:

Our simplified machine uses only `Z` and `N`. Real CPUs often include additional flags such as Carry and Overflow so they can make richer signed and unsigned comparisons safely. For this course, `Z` and `N` are enough to unlock a huge leap in capability.

---

### Lesson 7.4: Building the flag logic

> **Key Takeaway:** The hardware for useful flags can be surprisingly small. A 4-input NOR detects zero, and a single wire can expose the sign bit.

#### The theory

Let the ALU result bus be $Y_3 Y_2 Y_1 Y_0$.

**The Zero Flag**


The Zero Flag should be `1` only when all bits are `0`.

That means:

$Z = \neg(Y_3 \lor Y_2 \lor Y_1 \lor Y_0)$

That is exactly the behavior of a **4-input NOR gate**.

**The Negative Flag**


In 4-bit Two's Complement, a value is negative when its most-significant bit is `1`.

So:

$N = Y_3$

That is not even really a “circuit.” It is just a wire tapping the sign bit.

---

#### Lab & Experiment: Building the status flag circuit

<div align="center"><img src="./images/flag-logic-circuitverse.png" alt="Flag Logic CircuitVerse Diagram" width="512px"/><br/><em>Figure: The status flag logic. A 4-input NOR produces the Zero Flag, while the most-significant bit is copied directly to create the Negative Flag.</em></div><br/>

1.  Create a 4-bit input bus that will eventually come from the ALU result.
2.  Build a 4-input NOR gate and connect it to all four lines.
3.  Connect its output to a lamp labeled **Zero (Z)**.
4.  Run a direct wire from the most-significant bit ($Y_3$) to a lamp labeled **Negative (N)**.
5.  Label both outputs clearly. These two bits together are your machine’s first status report.

#### The experiment

Test these cases:

| Result bus | Expected Z | Expected N |
| :---: | :---: | :---: |
| `0000` | `1` | `0` |
| `0101` | `0` | `0` |
| `1000` | `0` | `1` |
| `1011` | `0` | `1` |

A useful interpretation check:

-   `1011` displays as `B` in hex
-   but as a signed 4-bit Two's Complement value, it means `-5`
-   so the Negative flag should absolutely be ON

For now, this is a **live status circuit** rather than a stored register. It reflects whatever value is currently on the result bus. Later, the control logic can choose to **latch** these bits into a tiny flag register at the moment an ALU instruction completes, preserving them for branch decisions.

---

### Module 7 Checkpoint

#### Practice Problem 7.5.1: Knowledge Check

1.  Why are status flags usually more economical than building a separate large comparator for every possible condition?
2.  What gate is used to build the Zero Flag circuit?
3.  If the result bus is `1001`, what should the `Z` and `N` flags be?

<details>
<summary><strong>Show Solution</strong></summary>

1.  Because one ALU operation can produce a result **and** a small collection of useful condition bits at the same time. That lets the CPU reuse existing arithmetic hardware instead of building a bulky dedicated circuit for every question.
2.  A **4-input NOR** gate.
3.  `Z = 0` and `N = 1`.

</details>

#### Practice Problem 7.5.2: Design challenge

Without using the dedicated equality comparator from Lesson 7.2, how could a CPU test whether $A = B$ using only an ALU and flags?

<details>
<summary><strong>Show Solution</strong></summary>

The CPU can compute $A - B$ in the ALU and then inspect the **Zero Flag**.

-   If the result is `0000`, then $A = B$
-   If the result is anything else, then $A \neq B$

</details>

#### Practice Problem 7.5.3: Debug challenge

Your Zero Flag lamp turns ON correctly for `0000`, but it also turns ON for `1000`.

What is the most likely kind of wiring error?

<details>
<summary><strong>Show Solution</strong></summary>

The most likely problem is that the Zero Flag circuit is **not seeing all four bits**. One of the input lines, likely the most-significant bit, is probably missing from the NOR gate input network. If `Y_3` is disconnected, then `1000` would be misread as if it were `0000`.

</details>

#### Real-world connection: The processor status register

Real CPUs maintain a small set of condition bits after arithmetic operations. These flags live in a dedicated status or condition-code register and are used by branch instructions such as “jump if zero” or “jump if negative.” You are now building the exact conceptual machinery behind that behavior. When a processor takes a branch, it is often because one tiny bit was set or cleared by the previous ALU operation.

#### Software connection: `if` statements become compare-and-branch

High-level code like this:

```python
if x == y:
    do_something()
```

does not survive all the way down to hardware as a mystical “if.” It typically becomes something like:

1.  compare `x` and `y` (often by subtraction)
2.  set flags
3.  branch if the appropriate flag is true

That is exactly why status flags matter. They are one of the key places where software structure touches physical hardware behavior.

#### Key Terms
-   **Comparator**: A circuit that answers a relationship question about two values, such as whether they are equal.
-   **Condition code**: Another common name for a status flag bit used by control flow instructions.
-   **Equality comparator**: A comparator whose output is `1` only when two inputs are identical.
-   **Flag**: A single-bit signal that summarizes some property of an ALU result.
-   **Most significant bit (MSB)**: The leftmost bit of a binary value, which carries the largest place value.
-   **Negative Flag (`N`)**: A flag that copies the most-significant bit of the result in a Two's Complement interpretation.
-   **Status register**: The conceptual collection of flag bits describing the outcome of the latest operation.
-   **Zero Flag (`Z`)**: A flag that is `1` exactly when the result bus is all zeros.

---

### Module 7 Conclusion

This is one of the most important conceptual modules in the whole course.

You did not just add a few more lights to the machine. You built the hardware basis of decision-making. The computer can now say more than “here is the answer.” It can also say “the answer was zero” or “the answer was negative.”

That tiny bit of metadata is what lets software branch, loop, and react.

In the next module, we will build one more crucial control component: the **multiplexer**, the digital switch that lets the machine choose which of several data paths it wants to use. After that, we will finally assemble the complete ALU.

