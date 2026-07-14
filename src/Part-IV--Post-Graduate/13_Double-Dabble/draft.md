## Module 13: The "Real World" Display – The Double Dabble Algorithm

### Module 13 Summary

-   **Why This Module:** We solved our display problem earlier with hexadecimal, the elegant programmer’s solution. In this post-graduate module, we revisit that same problem from the hardware side and build a human-friendly decimal display path.
-   **Learning Goals:**
    -   Understand why binary results are not automatically suitable for multi-digit decimal display.
    -   Learn the idea behind **Binary Coded Decimal (BCD)** and the **Double Dabble** algorithm.
    -   Build a ROM-based binary-to-BCD converter tailored to our 4-bit machine.
    -   Drive two separate decimal displays from a single 4-bit binary result.
-   **Lesson Overview:**
    -   Lesson 13.1: The theory – From hex to human
    -   Lesson 13.2: The lab – A ROM-based binary-to-BCD converter
    -   Lesson 13.3: The final assembly and payoff
-   **Build:** A binary-to-BCD converter that turns one 4-bit input into two BCD digits for a two-digit decimal display.

---

### Module 13 Introduction

Welcome to post-graduate studies.

By this point, our computer already works. It computes, stores, branches, and runs a real program. That means everything in this module is, in a sense, extra.

But it is the kind of extra challenge that teaches you a lot about real engineering.

Back in Module 5, when `8 + 4` produced `1100`, we solved the display problem by teaching the machine to speak **hexadecimal**. That was absolutely the right engineering move at the time. It was elegant, compact, and perfectly matched to a 4-bit system.

Still, humans do not usually read `C` and think “twelve.” A calculator or clock would show `12`.

That means we now face a subtler challenge:

> How do we translate one binary number into **two decimal digits**?

This is where the engineering trade-off becomes very real. Human convenience often costs hardware complexity. In this module, you will feel that trade-off directly.

---

### Lesson 13.1: The theory – From hex to human

> **Key Takeaway:** A binary number must be converted into separate decimal digits before a multi-digit decimal display can show it correctly.

Suppose the ALU outputs `1101`.

That is:

-   `13` in decimal
-   `D` in hexadecimal

A hex display is happy. A human-friendly two-digit decimal display is not, because it needs two separate values:

-   **Tens digit:** `1`
-   **Ones digit:** `3`

Those two decimal digits must each be encoded independently.

#### Binary Coded Decimal (BCD)

In **BCD**, each decimal digit gets its own 4-bit code.

So decimal `13` becomes:

-   tens digit `1` → `0001`
-   ones digit `3` → `0011`

That is very different from ordinary binary `1101`, even though both represent the same quantity.

#### The Double Dabble idea

The classic hardware algorithm for binary-to-BCD conversion is the **Double Dabble** algorithm, also called **shift-and-add-3**.

Its core idea is:

1.  shift the binary input through a BCD workspace one bit at a time
2.  before each shift, if any BCD digit is `5` or greater, add `3` to that digit

That rule sounds odd at first, but it is what keeps the BCD digits valid as the shifting process unfolds.

#### Why we are using a ROM instead

Building a full sequential Double Dabble machine in Minecraft would be possible, but it would be much more complex than the educational value is worth for our 4-bit system.

And here is the lovely engineering shortcut:

-   our input space is only **16 values** (`0` through `15`)
-   we already know how to build **lookup tables** with decoders and ROMs

So we will do something very practical:

-   learn the theory of Double Dabble
-   implement the conversion as a compact **ROM lookup table**

That gives us the same visible behavior for our machine’s input range, while keeping the build understandable.

---

### Lesson 13.2: The lab – A ROM-based binary-to-BCD converter

> **Key Takeaway:** For a small input range, a decoder plus ROM can act as a complete binary-to-BCD converter.

#### The architecture

We already know how to do this pattern:

1.  use a decoder to identify which input value is present
2.  use a ROM matrix to map that identity to the desired outputs

For this converter:

-   **Input:** one 4-bit binary value
-   **Decoder output:** one active line from `L0` to `LF`
-   **ROM output:** eight total bits
    -   four for the tens digit: `T3 T2 T1 T0`
    -   four for the ones digit: `O3 O2 O1 O0`

#### The full conversion table

Here is the exact lookup table our ROM must implement:

| Input | Decimal | Tens BCD | Ones BCD |
| :---: | :---: | :---: | :---: |
| `0` | `0` | `0000` | `0000` |
| `1` | `1` | `0000` | `0001` |
| `2` | `2` | `0000` | `0010` |
| `3` | `3` | `0000` | `0011` |
| `4` | `4` | `0000` | `0100` |
| `5` | `5` | `0000` | `0101` |
| `6` | `6` | `0000` | `0110` |
| `7` | `7` | `0000` | `0111` |
| `8` | `8` | `0000` | `1000` |
| `9` | `9` | `0000` | `1001` |
| `A` | `10` | `0001` | `0000` |
| `B` | `11` | `0001` | `0001` |
| `C` | `12` | `0001` | `0010` |
| `D` | `13` | `0001` | `0011` |
| `E` | `14` | `0001` | `0100` |
| `F` | `15` | `0001` | `0101` |

That table is the entire truth of the converter.

#### Lab & Experiment

![Binary to BCD ROM Diagram](./images/binary-to-bcd-rom.png)
*Figure: A binary-to-BCD converter built from a decoder and an 8-bit-wide ROM matrix. One active input line drives the correct tens and ones outputs.*

**Part A: Build the decoder**


1.  Build a full 4-to-16 decoder.
2.  Label its outputs `L0` through `LF`.

**Part B: Build the 8-output ROM matrix**


1.  Create 16 horizontal input lines from the decoder.
2.  Create 8 vertical output lines:
    -   `T3, T2, T1, T0`
    -   `O3, O2, O1, O0`
3.  Use the same torch-tap ROM technique from Module 4.

**Part C: Program the lines**


Examples:

-   For input `LD` (decimal `13`):
    -   tens digit is `0001` → energize `T0`
    -   ones digit is `0011` → energize `O1` and `O0`
-   For input `LF` (decimal `15`):
    -   tens digit is `0001` → energize `T0`
    -   ones digit is `0101` → energize `O2` and `O0`
-   For input `L9` (decimal `9`):
    -   tens digit is `0000` → no tens outputs
    -   ones digit is `1001` → energize `O3` and `O0`

The pleasing thing about this ROM is that the tens outputs are very simple:

-   for inputs `0` through `9`, tens = `0000`
-   for inputs `A` through `F`, tens = `0001`

So the real programming complexity mostly lives in the ones digit.

**Part D: Test the converter before integrating**


Use eight lamps on the outputs and test at least these values:

-   input `1001` (`9`) → tens `0000`, ones `1001`
-   input `1010` (`10`) → tens `0001`, ones `0000`
-   input `1101` (`13`) → tens `0001`, ones `0011`
-   input `1111` (`15`) → tens `0001`, ones `0101`

Do not skip this standalone test. It is much easier to debug the converter before it is attached to two display systems.

---

### Lesson 13.3: The final assembly and payoff

> **Key Takeaway:** Once the binary value has been converted to two BCD digits, the rest is just ordinary display driving using the BCD display pipeline we already know.

#### Lab & Experiment

1.  Build or reuse **two** BCD-to-7-segment display systems.
    -   left display = tens
    -   right display = ones
2.  Feed the ALU’s 4-bit result bus into the binary-to-BCD converter.
3.  Feed the converter’s four tens outputs into the left display.
4.  Feed the converter’s four ones outputs into the right display.

#### The final payoff

Now repeat the kind of calculation that earlier forced us into hexadecimal.

Try:

-   `9 + 4`
-   binary result from the ALU: `1101`
-   decimal value: `13`

The system should now behave like this:

1.  The converter recognizes `1101`.
2.  It outputs:
    -   tens = `0001`
    -   ones = `0011`
3.  The left display shows `1`.
4.  The right display shows `3`.

Together, they show:

**`13`**

![Double Dabble Final Build](./images/double-dabble-final-minecraft.png)
*Figure: The completed decimal-output system. A single 4-bit binary result is converted into separate tens and ones digits and displayed as an ordinary decimal number.*

That is a deeply satisfying finish because it closes a loop in the course. We encountered the display problem early, solved it the elegant way, and now return to solve it the human way.

---

### Module 13 Conclusion

This module is a wonderful reminder that engineering is always about trade-offs.

Hexadecimal was the right answer when we wanted a compact, direct match to the machine’s 4-bit world. Decimal output is the right answer when we want a display that feels natural to human eyes. Neither is universally “better.” They serve different audiences.

By building this converter, you have seen how extra human convenience often costs extra hardware. That is one of the deepest themes in the whole project.

You have now completed the full technical arc of Redstone University, from the smallest logic primitives to a programmable machine with a polished human-facing output path. Congratulations.

---

### Module 13 Checkpoint

#### Practice Problem 13.4.1: Knowledge Check

1.  What problem does a binary-to-BCD converter solve?
2.  For decimal `13`, what are the two 4-bit BCD digits?
3.  Why is a ROM-based solution a good fit for our 4-bit machine?

<details>
<summary><strong>Show Solution</strong></summary>

1.  It converts a single binary value into separate decimal digits that can each be displayed independently.
2.  Tens = `0001`, Ones = `0011`.
3.  Because our input range is tiny, only 16 possible values, a lookup-table implementation is straightforward, understandable, and easy to verify.

</details>

#### Practice Problem 13.4.2: Debug challenge

Your converter displays `15` correctly, but for input `1101` it shows `11` instead of `13`.

What is the most likely ROM programming mistake?

<details>
<summary><strong>Show Solution</strong></summary>

For input `1101` (decimal `13`), the correct outputs are tens `0001` and ones `0011`.

If the display shows `11`, then the tens digit is probably correct but the ones digit is missing the `O1` activation. The most likely mistake is that the `LD` input line was programmed to energize `O0` but not `O1`.

</details>

#### Practice Problem 13.4.3: The programmer

How would software extract the tens and ones digits from an integer value such as `13`?

<details>
<summary><strong>Show Solution</strong></summary>

Using integer division and modulo:

```python
value = 13

tens = value // 10
ones = value % 10
```

That is the software version of the hardware conversion problem.

</details>

#### Real-world connection: Clocks, calculators, and display drivers

Many human-facing devices, digital clocks, calculators, microwave timers, and scoreboards, must ultimately display decimal digits even though their internal logic works in binary. Real products often include dedicated display-driver hardware or controller firmware whose entire job is to bridge that gap between machine-friendly representation and human-friendly representation.

#### Software connection: Formatting is a translation problem too

Even in software, displaying a number to a human is not the same thing as storing it internally. A program may keep a value as binary in memory, but when it prints that value, it performs a conversion into decimal text characters. Your hardware converter is the physical equivalent of that formatting step.

#### Key Terms
-   **Binary Coded Decimal (BCD)**: A representation in which each decimal digit is stored as its own 4-bit binary value.
-   **Binary-to-BCD conversion**: The process of translating a binary number into separate decimal digits encoded in BCD.
-   **Display driver**: Hardware or software that converts internal values into signals suitable for a visual display.
-   **Double Dabble**: A classic shift-and-add-3 algorithm for converting binary numbers into BCD.
-   **Lookup table**: A structure that maps each possible input directly to its desired output.
-   **ROM**: Read-only memory; in this module, a fixed hardware lookup table implementing the conversion.
