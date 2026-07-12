## Module 6: Advanced Arithmetic – Overflow and Subtraction

### Module 6 Summary

-   **Narrative Beat:** Our adder works, but now we are going to discover its limits. We will push a 4-bit machine past what 4 bits can hold, learn how to detect that event, and then use the elegant trick of Two's Complement to teach the very same hardware how to subtract.
-   **Learning Goals:**
    -   Understand what it means for a fixed-width result to **overflow**.
    -   Use the adder’s final carry line as a visible arithmetic warning signal.
    -   Learn how negative numbers are represented in binary with **Two's Complement**.
    -   Convert our existing adder into a combined adder/subtractor with only a small amount of extra logic.
-   **Lesson Overview:**
    -   Lesson 6.1: The theory – When numbers get too big
    -   Lesson 6.2: The lab – Discovering and handling overflow
    -   Lesson 6.3: The theory – The magic of Two's Complement
    -   Lesson 6.4: The lab – Building the adder/subtractor unit
-   **Minecraft Artifact:** A 4-bit adder/subtractor with a carry-out indicator lamp.

---

### Module 6 Introduction

One of the great lessons of computer engineering is that every machine lives inside constraints.

Our machine is not a limitless calculator. It is a **4-bit** calculator. That means every answer must fit inside a 4-bit container unless we explicitly build extra hardware to handle more.

In this module, we are going to make those limits visible.

First, we will deliberately break our adder by asking it to produce a result that does not fit in 4 bits. The good news is that the machine already knows this happened. The clue has been sitting there on the final `CarryOut` wire all along.

Then we will tackle an even more beautiful idea: subtraction without building a brand-new subtractor. Using **Two's Complement**, we can transform subtraction into addition and reuse almost everything we already built.

This is one of those modules where the abstraction level jumps. After it clicks, a lot of low-level computing starts to feel much less mysterious.

---

### Lesson 6.1: The theory – When numbers get too big

> **Key Takeaway:** Overflow happens when the true result of a calculation needs more bits than the machine has available to store it.

Our computer’s arithmetic lane is 4 bits wide. That gives us these unsigned values:

-   smallest: `0000` = `0`
-   largest: `1111` = `15`

So what happens if we ask for:

-   `12 + 5`
-   hexadecimal: `C + 5`
-   binary: `1100 + 0101`

The true result is `17`, which in binary is `10001`.

That is a **5-bit** answer.

Our adder actually computes this correctly. The problem is that our main result bus can only display the lower 4 bits: `0001`. The missing fifth bit appears on the final carry line.

#### A note on terminology

In beginner-friendly courses, the final carry is often described as an **overflow warning**, and that is a useful intuition here.

More precisely:

-   for **unsigned arithmetic**, that final carry means the result spilled beyond four bits
-   for **signed Two's Complement arithmetic**, overflow has a slightly subtler meaning

For now, we will use a simple and practical rule:

> If the arithmetic result does not fit cleanly in four bits, the final carry line is important information and you should not ignore it.

That is enough to make the machine more honest.

---

### Lesson 6.2: The lab – Discovering and handling overflow

> **Key Takeaway:** The final carry wire from the adder is not useless extra output. It is the machine telling you that the real answer extended beyond the visible 4-bit result bus.

#### Lab Part A: Discover the bug

1.  Keep your system wired as it was at the end of Module 5.
2.  Take the final `CarryOut` wire from the most-significant full adder stage.
3.  Connect it to a separate Redstone Lamp labeled **Carry-Out**.
4.  Run this test:
    -   Input A: `1100` (`C`, or 12)
    -   Input B: `0101` (`5`)

Expected observation:

-   The 4-bit result bus shows `0001`
-   The hex display shows `1`
-   The Carry-Out lamp is **ON**

<div align="center"><img src="./images/overflow-bug-minecraft.png" alt="Overflow Bug Minecraft Build" width="512px"/><br/><em>Figure: The arithmetic result does not fit in four bits. The main display only shows the low four bits, while the carry lamp reveals that a fifth bit existed.</em></div><br/>

This is the “aha” moment. The machine did not fail. **We misread it.**

It gave us a 5-bit answer:

-   carry lamp = leading `1`
-   display = trailing `0001`

Together, that is `10001`.

#### Lab Part B: Use the carry lamp intentionally

Try these three tests:

1.  `1111 + 0001`
    -   visible result: `0000`
    -   carry lamp: ON
2.  `0111 + 0001`
    -   visible result: `1000`
    -   carry lamp: OFF
3.  `0010 + 0011`
    -   visible result: `0101`
    -   carry lamp: OFF

These examples train you to separate two questions:

1.  What are the low four bits of the result?
2.  Did the calculation spill out of the 4-bit container?

For now, our fix is simply to expose that signal clearly. Later, the control unit will be able to *react* to status information like this.

---

### Lesson 6.3: The theory – The magic of Two's Complement

> **Key Takeaway:** Two's Complement lets us represent negative numbers using ordinary binary patterns, which means subtraction can be performed as addition.

The trick is to rewrite subtraction:

-   $A - B$
-   becomes $A + (-B)$

So the real question is this:

> How do we encode `-B` as a 4-bit binary number?

The answer is **Two's Complement**.

#### The two-step rule for finding `-X`

1.  **Invert** every bit of $X$
2.  **Add `1`**

That is it.

#### Example: Find `-3`

Start with positive `3`:

-   `0011`

Invert every bit:

-   `1100`

Add `1`:

-   `1101`

So in 4-bit Two's Complement, `1101` represents `-3`.

#### Why this is so useful

Now we can do this:

```text
  1000   (8)
+ 1101   (-3)
------
 10101
```

Discard the extra carry bit on the left and we keep:

-   `0101` = `5`

That means:

-   `8 + (-3) = 5`
-   so the same adder can perform subtraction

#### The signed range of a 4-bit number

When we interpret 4 bits as a Two's Complement value, the range is:

-   smallest: `1000` = `-8`
-   largest: `0111` = `+7`

A few useful landmarks:

| Bit pattern | Unsigned meaning | Two's Complement meaning |
| :---: | :---: | :---: |
| `0000` | `0` | `0` |
| `0001` | `1` | `1` |
| `0111` | `7` | `7` |
| `1000` | `8` | `-8` |
| `1111` | `15` | `-1` |

This is an important mindset shift: **the wires do not change; only our interpretation changes.**

That is why the same 4-bit pattern can appear as `B` on a hex display and also mean `-5` in signed arithmetic.

---

### Lesson 6.4: The lab – Building the adder/subtractor unit

> **Key Takeaway:** XOR gates give us a controllable inverter, and the adder’s existing initial carry input gives us the “+1” required by Two's Complement. That is why an adder can become a subtractor so cheaply.

We want a single control signal, `Subtract`, that makes the circuit behave like this:

-   if `Subtract = 0`, compute $A + B$
-   if `Subtract = 1`, compute $A + (\neg B) + 1$, which is $A - B$

#### Lab Part A: Build the controllable inverter

The XOR gate does exactly what we need:

-   $B \oplus 0 = B$
-   $B \oplus 1 = \neg B$

Build steps:

1.  Take the 4-bit input bus for $B$.
2.  Before it reaches the adder, insert **four XOR gates**, one for each bit.
3.  Feed the corresponding bit of $B$ into one side of each XOR gate.
4.  Tie the other side of all four XOR gates together and connect them to a new control lever labeled **Subtract**.

When the lever is OFF, the XOR bank passes $B$ through unchanged.
When the lever is ON, the XOR bank flips every bit of $B$.

#### Lab Part B: Add the final `+1`

Two's Complement needs one more step after inversion: add `1`.

Conveniently, our ripple-carry adder already has a perfect place for that.

1.  Take the same **Subtract** signal.
2.  Route it to the `CarryIn` of the **least-significant** full adder stage.

Now the control lever does two jobs at once:

-   it tells the XOR bank to invert $B$
-   it injects the required `+1`

<div align="center"><img src="./images/adder-subtractor-circuitverse.png" alt="Adder-Subtractor CircuitVerse Diagram" width="512px"/><br/><em>Figure: The single `Subtract` control simultaneously inverts the B input through XOR gates and adds the required `1` by driving the initial carry-in.</em></div><br/>

#### The experiment

Run all of these tests:

1.  **Addition mode** (`Subtract = 0`)
    -   `0111 + 0010 = 1001` (`9`)
2.  **Subtraction mode** (`Subtract = 1`)
    -   `0111 - 0010 = 0101` (`5`)
3.  **Subtraction producing a negative result**
    -   `0010 - 0111 = 1011`

That last result is worth pausing on.

-   In hex, `1011` displays as `B`
-   In 4-bit Two's Complement, `1011` means `-5`

Same wires. Same bits. Different interpretation.

That exact idea will matter a lot in the next module, when we teach the machine to recognize whether a result is zero or negative.

---

### Module 6 Checkpoint

#### Practice Problem 6.5.1: Knowledge Check

1.  What does the final carry line tell us in our 4-bit arithmetic system?
2.  What is the 4-bit Two's Complement representation of `-1`?
3.  Why is XOR the key gate in the adder/subtractor design?

<details>
<summary><strong>Show Solution</strong></summary>

1.  It tells us that the arithmetic result extended beyond the visible 4-bit result bus. In practical terms, it warns that the calculation spilled out of the 4-bit container.
2.  `1111`
3.  Because XOR can act as a **controllable inverter**: with control `0` it passes the bit unchanged, and with control `1` it flips the bit.

</details>

#### Practice Problem 6.5.2: The word problem

Compute `D - 5` using 4-bit Two's Complement arithmetic.

1.  Write `D` in binary.
2.  Find the Two's Complement representation of `-5`.
3.  Add the two values.
4.  What 4-bit result remains after discarding the final carry?

<details>
<summary><strong>Show Solution</strong></summary>

1.  `D` is `1101`
2.  `5` is `0101`; invert to `1010`; add `1` to get `1011`, so `-5` is `1011`
3.  `1101 + 1011 = 1 1000`
4.  Discard the final carry and keep `1000`, which is `8` in unsigned interpretation and `-8` in 4-bit signed interpretation. In the context of `13 - 5`, we read it here as the low 4 bits of the unsigned result `8`.

</details>

#### Practice Problem 6.5.3: Debug challenge

Your addition mode works perfectly, but in subtraction mode every answer is off by exactly `1`. For example, `7 - 2` produces `4` instead of `5`.

What is the most likely missing connection?

<details>
<summary><strong>Show Solution</strong></summary>

The most likely fault is that the **Subtract control is not connected to the initial CarryIn** of the least-significant adder stage.

Inversion alone produces One's Complement. To get **Two's Complement**, the circuit must also add `1`.

</details>

#### Real-world connection: Integer wraparound

Real processors also work with fixed-width integers. An 8-bit register cannot hold every possible number; neither can a 32-bit one. When a result spills past the available width, the hardware keeps the low bits and exposes status information through flags. In many programming languages and machine architectures, this is why integer overflow, wraparound, and signed-vs-unsigned interpretation matter.

#### Software connection: Negation as `~x + 1`

At the software level, Two's Complement shows up in the classic identity for negation:

```python
def twos_complement_negate_4bit(x: int) -> int:
    return ((~x) + 1) & 0b1111
```

That code is just the software spelling of the hardware you built:

-   `~x` is the inversion step
-   `+ 1` is the injected carry-in step
-   `& 0b1111` keeps only the low 4 bits

#### Key Terms
-   **Carry bit**: The extra bit produced when a column of binary addition exceeds the capacity of that column.
-   **Fixed-width arithmetic**: Arithmetic performed in a container with a limited number of bits.
-   **Overflow**: The condition where the true result of a calculation needs more bits than are available in the destination width.
-   **Sign bit**: In a signed binary representation, the most significant bit that indicates the sign of the value.
-   **Two's Complement**: The standard binary representation for signed integers in which negation is performed by inverting the bits and adding `1`.
-   **Word size**: The natural width, in bits, of the values a machine processes at once.

---

### Module 6 Conclusion

You have just crossed a major conceptual bridge.

You learned that arithmetic hardware is always bounded by word size, and that a machine must somehow signal when a result spills beyond those bounds. You also learned one of the most elegant tricks in all of digital design: subtraction does not require a completely separate kind of circuit. It can emerge from addition with just a little cleverness.

That is a recurring theme in computer architecture. The most powerful designs are often not the ones with the most parts, but the ones that reuse the same parts in smart ways.

In the next module, we are going to give our machine a new kind of power. It will no longer just produce numbers. It will produce information *about* those numbers, letting it tell us whether a result was zero or negative. That is the first step from calculation toward decision-making.

