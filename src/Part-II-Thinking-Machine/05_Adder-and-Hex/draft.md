## Module 5: The 4-Bit Adder & the Hexadecimal Upgrade

### Module 5 Summary

-   **Narrative Beat:** Time for real math. We will build the first circuit that lets our machine calculate, then watch that success immediately expose a bigger system problem. Solving that problem will force us to upgrade our display and, in the process, learn the number system low-level programmers use every day.
-   **Learning Goals:**
    -   Understand how binary addition produces both a **sum** bit and a **carry** bit.
    -   Build a reusable 1-bit **full adder** and chain four of them into a 4-bit ripple-carry adder.
    -   Diagnose a system-level bug that appears only after the adder is connected to the display.
    -   Learn why **hexadecimal** is a natural shorthand for 4-bit values.
    -   Upgrade the decoder and ROM from Module 4 without rebuilding the whole display from scratch.
-   **Lesson Overview:**
    -   Lesson 5.1: The theory of binary addition
    -   Lesson 5.2: The lab – Building the 4-bit ripple-carry adder
    -   Lesson 5.3: The integration test & the first bug
    -   Lesson 5.4: The programmer's solution – Speaking hexadecimal
    -   Lesson 5.5: The lab – The hexadecimal upgrade
-   **Minecraft Artifact:** A working 4-bit ripple-carry adder connected to a hexadecimal display.
-   **The Payoff:** The calculation `8 + 4`, which originally broke our display, will now appear correctly as `C`.

---

### Module 5 Introduction

Part I gave us an input system and an output system. We can now speak to the machine and the machine can answer back. That is a huge milestone, but so far our computer is still passive. It can only *translate*.

In this module, that changes.

We are going to build the mathematical heart of the processor: the **adder**. This is the first circuit in the course that feels unmistakably like computation. It takes two numbers, transforms them, and produces a new one.

But this module is also our first taste of what real engineering feels like. You can build two perfect subsystems, connect them together, and still discover a bug. That is exactly what will happen here. Our adder will work. Our display will work. And the combined system will still fail in a fascinating way.

That failure will teach us two big ideas at once:

1.  **Integration reveals truths that isolated testing cannot.**
2.  **A modular design makes future upgrades much easier.**

Let’s begin by learning the grammar of binary arithmetic.

---

### Lesson 5.1: The theory of binary addition

> **Key Takeaway:** Binary addition follows the same column-by-column logic as decimal addition. The only new rule you must internalize is that `1 + 1 = 0` with a carry of `1`.

When we add in decimal, each column can create a carry into the next one. Binary works the same way. The difference is that each column has only two symbols to work with: `0` and `1`.

Here are the four possible outcomes for adding two bits:

| Input A | Input B | Sum | Carry-Out |
| :---: | :---: | :---: | :---: |
| `0` | `0` | `0` | `0` |
| `0` | `1` | `1` | `0` |
| `1` | `0` | `1` | `0` |
| `1` | `1` | `0` | `1` |

That last row is the important one. When both inputs are `1`, the result cannot fit in a single bit. So we write `0` in the current column and carry `1` to the next column.

Let’s work through `5 + 3`:

```text
  0101   (5)
+ 0011   (3)
------
```

We add from right to left:

1.  **Ones column:** `1 + 1 = 0`, carry `1`
2.  **Twos column:** `0 + 1 + 1 = 0`, carry `1`
3.  **Fours column:** `1 + 0 + 1 = 0`, carry `1`
4.  **Eights column:** `0 + 0 + 1 = 1`

So the result is `1000`, which is `8`.

#### The full-adder viewpoint

In real hardware, each column after the first must add **three** inputs:

-   $A$
-   $B$
-   `CarryIn`

And it must produce **two** outputs:

-   `Sum`
-   `CarryOut`

That little 3-input, 2-output circuit is called a **full adder**. It is the LEGO brick of arithmetic.

Its logic is:

-   **Sum:** $A \oplus B \oplus CarryIn$
-   **Carry-Out:** $(A \land B) \lor (CarryIn \land (A \oplus B))$

There is a nice intuition hiding here:

-   The **Sum** bit is `1` when an **odd number** of the three inputs are `1`.
-   The **Carry-Out** bit is `1` when **at least two** of the three inputs are `1`.

That is exactly what we need the hardware to do.

---

### Lesson 5.2: The lab – Building the 4-bit ripple-carry adder

> **Key Takeaway:** A multi-bit adder is built by chaining identical 1-bit full adders together so the carry can “ripple” from one stage to the next.

> **A note for the curious: why skip the half adder?**
>
> Many digital logic courses introduce the **half adder** first. That is a valid teaching path, but in this course I want to bias toward reusable parts. A half adder is only useful when there is no carry coming in. A **full adder** works everywhere. Once you understand it, you can build the whole adder out of one repeated module.

#### The concept: the 1-bit full adder

A full adder has:

-   inputs: $A$, $B$, `CarryIn`
-   outputs: `Sum`, `CarryOut`

A standard implementation uses:

-   two XOR gates
-   two AND gates
-   one OR gate

Build that once, test it thoroughly, and then repeat it.

![1-Bit Full Adder CircuitVerse Diagram](./images/full-adder_circuitverse.png)
*Figure: A standard 1-bit full adder. Two XOR stages generate the Sum bit, while the AND/OR network generates Carry-Out. Shown computing `1 + 1 + 0`: the two ones make Sum `0` and hand a `1` to Carry-Out.*

#### Lab Part A: Build a 1-bit full adder module

1.  Lay out three labeled inputs: $A$, $B$, and `CarryIn`.
2.  Build the XOR path for the **Sum** output:
    -   First compute $A \oplus B$.
    -   Then XOR that result with `CarryIn`.
3.  Build the carry path:
    -   One AND gate computes $A \land B$.
    -   A second AND gate computes $CarryIn \land (A \oplus B)$.
    -   OR those two results together to produce `CarryOut`.
4.  Label the two outputs clearly.
5.  Test all eight input combinations.

A quick test plan:

| A | B | CarryIn | Expected Sum | Expected CarryOut |
| :---: | :---: | :---: | :---: | :---: |
| `0` | `0` | `0` | `0` | `0` |
| `0` | `0` | `1` | `1` | `0` |
| `0` | `1` | `0` | `1` | `0` |
| `0` | `1` | `1` | `0` | `1` |
| `1` | `0` | `0` | `1` | `0` |
| `1` | `0` | `1` | `0` | `1` |
| `1` | `1` | `0` | `0` | `1` |
| `1` | `1` | `1` | `1` | `1` |

![1-Bit Full Adder Minecraft Build](./images/full-adder_minecraft.png)
*Figure: The 1-bit full adder module in Minecraft, set to the same `1 + 1 + 0` as the diagram above — both input lamps lit, the Sum lamp dark, and the Carry-Out lamp glowing.*

#### Lab Part B: Assemble the 4-bit ripple-carry adder

![4-Bit Ripple-Carry Adder CircuitVerse Diagram](./images/4-bit-rca_circuitverse.png)
*Figure: Four full-adder modules chained into a 4-bit ripple-carry adder. Each stage's Carry-Out feeds the next stage's Carry-In. Shown computing `0101 + 0011` (the `5 + 3` from Lesson 5.1): the carry ripples through every stage and the result reads `1000`.*

1.  Create two 4-bit input buses: **Input A** and **Input B**.
2.  Place four copies of your full adder in a row, one for each bit position.
3.  Wire the least-significant stage:
    -   Connect $A_0$ and $B_0$.
    -   Tie its `CarryIn` to `0`.
4.  Wire the next three stages:
    -   Connect $A_1$/$B_1$, then $A_2$/$B_2$, then $A_3$/$B_3$.
    -   Connect each stage’s `CarryOut` to the next stage’s `CarryIn`.
5.  Collect the four `Sum` outputs into a 4-bit result bus.
6.  Keep the final `CarryOut` wire accessible. We are going to need it in the next module.

![4-Bit Ripple-Carry Adder Minecraft Build](./images/4-bit-rca-aerial_minecraft.png)
*Figure: The full 4-bit ripple-carry adder in Minecraft, seen from above and computing the same `5 + 3` as the diagram — four copies of the same full-adder module in a row, the carry rippling from the least-significant stage on the right toward the most-significant on the left, and only the leftmost Sum lamp lit: `1000`.*

#### The experiment

Run these test cases before moving on:

-   `0001 + 0001 = 0010`
-   `0011 + 0010 = 0101`
-   `0101 + 0011 = 1000`
-   `0111 + 0001 = 1000`

If a result is off by exactly `2`, `4`, or `8`, the most likely problem is that one stage’s `CarryOut` is not reaching the next stage’s `CarryIn`.

---

### Lesson 5.3: The integration test & the first bug

> **Key Takeaway:** A bug can exist at the boundary between two correct subsystems. Integration testing is where you discover whether your design assumptions were actually true.

Now for the fun part. Let’s connect our new adder to the display system from Module 4.

#### The test

1.  Wire the adder’s 4-bit `Sum` bus into the input of your display decoder.
2.  Try a case that stays inside the decimal range we already support:
    -   $4 + 3$
    -   binary: `0100 + 0011 = 0111`
    -   expected display: `7`

That should work beautifully.

Now try this:

-   $8 + 4$
-   binary: `1000 + 0100 = 1100`
-   decimal: `12`

The adder works.

And the display goes blank.

![The integration bug in Minecraft](./images/integration-bug_minecraft.png)
*Figure: The moment it fails, in the world — `8` and `4` set on the input levers, the adder's carry lamp proving it computed `1100`, and the decimal display dark.*

![The display system receiving 1100](./images/4-bit-binary-to-display-abstract-1100_circuitverse.png)
*Figure: The bug, exactly as the hardware sees it. The adder hands the display system `1100` — but the 4-to-10 decoder only knows the ten patterns for `0` through `9`. No output line fires, the ROM stays quiet, and the display shows nothing.*

#### The diagnosis

This is our first real system bug, and it is a great one.

Nothing is wrong with the adder.
Nothing is wrong with the display.

The problem is that our display decoder from Module 4 is a **BCD decoder**. It only knows how to recognize the ten patterns for decimal digits `0` through `9`. It was never taught what `1010`, `1011`, `1100`, `1101`, `1110`, or `1111` mean.

We asked a correct subsystem to interpret a value that lies outside its vocabulary.

That is a deeply realistic engineering lesson. Hardware is only as capable as the assumptions built into it.

---

### Lesson 5.4: The programmer's solution – Speaking hexadecimal

> **Key Takeaway:** Hexadecimal is not a strange extra number system. It is simply the most compact human-readable way to write a 4-bit binary value.

We now have a choice.

We could build a more complicated decimal display system that shows numbers like `12` using two separate digits.

That is possible, and later in the course we *will* explore it.

But there is a much more elegant move available right now: meet the machine halfway.

A 4-bit number has exactly `16` possible values:

-   `0000` through `1111`
-   decimal `0` through `15`

Hexadecimal is base-16, so it gives us exactly one symbol for each possible 4-bit pattern:

| Binary | Decimal | Hex |
| :---: | :---: | :---: |
| `0000` | `0` | `0` |
| `0001` | `1` | `1` |
| `0010` | `2` | `2` |
| `0011` | `3` | `3` |
| `0100` | `4` | `4` |
| `0101` | `5` | `5` |
| `0110` | `6` | `6` |
| `0111` | `7` | `7` |
| `1000` | `8` | `8` |
| `1001` | `9` | `9` |
| `1010` | `10` | `A` |
| `1011` | `11` | `B` |
| `1100` | `12` | `C` |
| `1101` | `13` | `D` |
| `1110` | `14` | `E` |
| `1111` | `15` | `F` |

So when the adder outputs `1100`, we do not need to think “the display failed.”
We can think “the machine just said `C`.”

That is why hexadecimal is everywhere in low-level programming, debugging, and computer architecture. It lines up perfectly with the machine’s natural word sizes.

---

### Lesson 5.5: The lab – The hexadecimal upgrade

> **Key Takeaway:** Because our display was built as two clean stages, we can upgrade it surgically instead of rebuilding it from scratch.

This is one of the most satisfying moments in the course. We are about to benefit directly from the modular architecture we chose in Module 4.

![Hexadecimal Display System Abstract Diagram](./images/4-bit-binary-to-hexadecimal-display-abstract_circuitverse.png)
*Figure: The upgraded display system as two clean stages — a 4-to-16 decoder feeding a hex decoder/driver. Shown reading `0101` and displaying `5`.*

#### Lab Part A: Upgrade the decoder

1.  Return to your 4-to-10 decoder.
2.  Extend it into a full **4-to-16 binary decoder**.
3.  Add six new output lines:
    -   `LA` for `1010`
    -   `LB` for `1011`
    -   `LC` for `1100`
    -   `LD` for `1101`
    -   `LE` for `1110`
    -   `LF` for `1111`
4.  Use the same tap logic from Module 4. Each new line simply recognizes one more identity pattern.

![4-to-16 Decoder CircuitVerse Diagram](./images/4-to-16-decoder_circuitverse.png)
*Figure: The full 4-to-16 binary decoder. Sixteen output lines, one per 4-bit pattern — here the input `1111` activates line `LF`.*

#### Lab Part B: Upgrade the ROM

1.  Extend the encoder/ROM so it now accepts all sixteen decoder lines.
2.  Program the segment patterns for `A` through `F`.
3.  Test each new letter one at a time before reconnecting the full system.

A common 7-segment convention is:

-   `A`: segments `a, b, c, e, f, g`
-   `B`: segments `c, d, e, f, g`  
    *(Many 7-segment displays render this as a lowercase-looking `b`.)*
-   `C`: segments `a, d, e, f`
-   `D`: segments `b, c, d, e, g`  
    *(Often rendered like a lowercase-looking `d`.)*
-   `E`: segments `a, d, e, f, g`
-   `F`: segments `a, e, f, g`

![The hex letters on a 7-segment display](./images/hex-letters-7seg_circuitverse.png)
*Figure: The six letter patterns on the display — `A` through `F`, with `B` and `D` in their lowercase-looking forms.*

![7-Segment Hex Decoder/Driver CircuitVerse Diagram](./images/7-segment-hex-decoder-driver_circuitverse.png)
*Figure: The extended decoder/driver ROM — all sixteen line inputs, one OR column per segment.*

![Hexadecimal Display System Aerial View](./images/hex-display-aerial_minecraft.png)
*Figure: The upgraded display system from above — the 4-bit input bus enters at the right, the 4-to-16 decoder's sixteen lines run down into the diode-matrix ROM, and the seven segment lines exit to the display.*

#### The payoff test

Repeat the test that failed earlier:

-   Input A: `1000` (`8`)
-   Input B: `0100` (`4`)
-   Adder output: `1100`

Now the system should behave like this:

1.  The decoder recognizes `1100` and activates line `LC`.
2.  The ROM maps `LC` to the segment pattern for `C`.
3.  The display lights up a bright, unmistakable `C`.

Bug fixed. System upgraded. No rebuild required.

![The payoff schematic](./images/rca-hex-display_circuitverse.png)
*Figure: The whole system as one schematic — the ripple-carry adder feeding the upgraded display chain, computing `8 + 4` and driving a `C`.*

![The payoff in Minecraft](./images/rca-hex-display_minecraft.png)
*Figure: The module artifact — the 4-bit adder wired to the hexadecimal display, computing `8 + 4` and showing `C`.*

![Hexadecimal Display System Minecraft Build](./images/hex-display_minecraft.png)
*Figure: The complete upgraded display system in Minecraft — decoder, ROM, and 7-segment display.*

---

### Module 5 Conclusion

This module marks a turning point.

You built the first true arithmetic engine in the course. More importantly, you experienced the full engineering loop: design, build, integrate, fail, diagnose, and improve. That is not a detour from real computer engineering. That *is* real computer engineering.

You also saw the reward of modular design. Because the decoder and ROM were cleanly separated, expanding the system was an upgrade, not a restart.

Our machine can now add numbers and display every possible 4-bit result. In the next module, we are going to push that arithmetic system even harder, right up against the limits of a 4-bit machine, and discover what happens when the answer no longer fits.

---

### Module 5 Checkpoint

#### Practice Problem 5.6.1: Knowledge Check

1.  What is the difference between the `Sum` output and the `CarryOut` output of a full adder?
2.  What is the hexadecimal symbol for binary `1110`?
3.  Why did our original display fail on the result `1100`?

<details>
<summary><strong>Show Solution</strong></summary>

1.  The **Sum** output is the current bit of the result for that column. The **CarryOut** output is the carry bit that must be passed into the next column to the left.
2.  The hexadecimal symbol is **`E`**.
3.  The original display used a **BCD decoder**, which only knew how to interpret the patterns for decimal `0` through `9`. It had no rule for `1100`.

</details>

#### Practice Problem 5.6.2: Debug challenge

Your 4-bit adder works for `2 + 1`, `3 + 1`, and `4 + 1`, but `7 + 1` incorrectly produces `0000` instead of `1000`.

What is the single most likely fault in the adder?

<details>
<summary><strong>Show Solution</strong></summary>

The most likely fault is that the **carry from the third stage is not reaching the fourth stage**.

`7 + 1` is:

```text
0111
0001
----
1000
```

This result depends on the carry rippling through multiple stages. If one carry link is broken, the highest stage never receives the signal it needs to produce the leading `1`.

</details>

#### Real-world connection: Nibbles, hex dumps, and addresses

Hexadecimal is used everywhere because it compresses binary into chunks humans can actually read. One hex digit represents exactly one **nibble** (4 bits). Two hex digits represent a byte. That is why memory addresses, machine instructions, color values, and debug output are so often written in hex. When a programmer sees `0xC`, they are really seeing the 4-bit pattern `1100` wearing a friendlier face.

#### Software connection: Adding without `+`

A classic programming puzzle asks: how can you add two integers if the `+` operator is forbidden? The answer mirrors the hardware you just built.

-   XOR computes the **sum bits without carries**.
-   AND finds the **carry bits**.
-   Shifting the carry left moves it into the next column.
-   Repeat until there is no carry left.

```python
def get_sum(a: int, b: int) -> int:
    mask = 0xFFFFFFFF
    while b != 0:
        carry = (a & b) << 1
        a = (a ^ b) & mask
        b = carry & mask
    return a if a <= 0x7FFFFFFF else ~(a ^ mask)
```

That clever software trick is just a looped version of the same arithmetic logic your hardware adder performs all at once.

#### Key Terms
-   **Adder**: A digital circuit that performs binary addition.
-   **Binary-Coded Decimal (BCD)**: A representation in which each decimal digit `0` through `9` is stored as its own 4-bit binary pattern.
-   **Carry bit**: A bit that is generated when a column of addition exceeds what can be represented in that column and must spill into the next one.
-   **Full adder**: A 1-bit arithmetic circuit that adds $A$, $B$, and `CarryIn`, producing `Sum` and `CarryOut`.
-   **Hexadecimal**: A base-16 number system that maps perfectly onto 4-bit binary values.
-   **Nibble**: A group of 4 bits.
-   **Ripple-carry adder**: A multi-bit adder made by chaining full adders so the carry propagates from stage to stage.
