## Module 5: The 4-Bit Adder & the Hexadecimal Upgrade

### Module 5 Summary

-   **Learning Goals:**
    -   Understand how binary addition produces both a **sum** bit and a **carry** bit.
    -   Build a reusable 1-bit **full adder** and chain four of them into a 4-bit ripple-carry adder.
    -   Diagnose a fault that only appears once two individually correct subsystems are connected.
    -   Learn why **hexadecimal** is a natural shorthand for 4-bit values.
    -   Upgrade the decoder and ROM from Module 4 without rebuilding the whole display from scratch.
-   **Lesson Overview:**
    -   Lesson 5.1: The theory of binary addition
    -   Lesson 5.2: The lab – Building the 4-bit ripple-carry adder
    -   Lesson 5.3: The integration test
    -   Lesson 5.4: The programmer's solution – Speaking hexadecimal
    -   Lesson 5.5: The lab – The hexadecimal upgrade
    -   Lesson 5.6: The payoff
-   **Build:** A working 4-bit ripple-carry adder connected to a hexadecimal display.
-   **Final Test:** The calculation `8 + 4` produces `1100`, and the upgraded display shows it correctly as `C`.

---

### Module 5 Introduction

Part I gave us an input system and an output system. We can now speak to the machine and the machine can answer back. But so far our computer is still passive. Hand it a five and it hands you a five right back, just written in a different alphabet. It can only *translate*.

In this module, that changes.

We're going to build the part of the processor that does arithmetic: the **adder**. This is the first circuit in the course that feels unmistakably like computation. It takes two numbers, transforms them, and produces a new one.

This module also carries a lesson that only turns up once you connect things: two subsystems can each be correct on their own and still not agree at the seam where they meet.

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

That last row is the important one. When both inputs are `1`, the result can't fit in a single bit. So we write `0` in the current column and carry `1` to the next column.

Let’s work through `5 + 3`, writing the carries above the columns the way you would on paper:

$$
\begin{array}{cccccl}
  & \scriptstyle\textcolor{gray}{1} & \scriptstyle\textcolor{gray}{1} & \scriptstyle\textcolor{gray}{1} & & \scriptstyle\textcolor{gray}{\text{carries}} \\
  & 0 & 1 & 0 & 1 & \quad(5) \\
+ & 0 & 0 & 1 & 1 & \quad(3) \\
\hline
  & 1 & 0 & 0 & 0 & \quad(8)
\end{array}
$$

We add from right to left:

1.  **Ones column:** `1 + 1 = 0`, carry `1`
2.  **Twos column:** `0 + 1 + 1 = 0`, carry `1`
3.  **Fours column:** `1 + 0 + 1 = 0`, carry `1`
4.  **Eights column:** `0 + 0 + 1 = 1`

So the result is `1000`, which is `8`.

#### The full-adder viewpoint

In real hardware, each column after the first must add **three** inputs:

-   `A`
-   `B`
-   `CarryIn`

And it must produce **two** outputs:

-   `Sum`
-   `CarryOut`

That little 3-input, 2-output circuit is called a **full adder**. It is the LEGO brick of arithmetic.

Its logic is, in the two notations from Module 3:

| Output | In words | In symbols |
| :--- | :--- | :--- |
| **Sum** | $A \text{ XOR } B \text{ XOR } CarryIn$ | $A \oplus B \oplus CarryIn$ |
| **Carry-Out** | $(A \text{ AND } B) \text{ OR } (CarryIn \text{ AND } (A \text{ XOR } B))$ | $(A \land B) \lor (CarryIn \land (A \oplus B))$ |

There's a nice intuition hiding here:

-   The **Sum** bit is `1` when an **odd number** of the three inputs are `1`.
-   The **Carry-Out** bit is `1` when **at least two** of the three inputs are `1`.

Test both rules on the heaviest column you will ever meet, `1 + 1 + 1`: an odd count of ones makes Sum `1`, and at least two ones raise the carry, so the column answers `1` and carries `1`.

Builders usually give the shared piece of that logic a name. Call $P = A \oplus B$, with P for *propagate*, and the two rules compress to $Sum = P \oplus CarryIn$ and $CarryOut = (A \land B) \lor (P \land CarryIn)$. The carry side is doing two jobs: $A \land B$ *generates* a brand-new carry, and $P \land CarryIn$ *propagates* one that arrived from the column to the right. Keep those two words; they make the wiring much easier to remember.

That's exactly what we need the hardware to do.

---

### Lesson 5.2: The lab – Building the 4-bit ripple-carry adder

> **Key Takeaway:** A multi-bit adder is built by chaining identical 1-bit full adders together so the carry can “ripple” from one stage to the next.

> **A note for the curious: why skip the half adder?**
>
> Many digital logic courses introduce the **half adder** first. That's a valid teaching path, but in this course I want to bias toward reusable parts. A half adder is only useful when there's no carry coming in. A **full adder** works everywhere. Once you understand it, you can build the whole adder out of one repeated module. For the vocabulary's sake: the first XOR and AND pair inside a full adder *is* a half adder. We just never package it as its own build.

#### The concept: the 1-bit full adder

A full adder has:

-   inputs: `A`, `B`, `CarryIn`
-   outputs: `Sum`, `CarryOut`

Its complete definition is the truth table, all eight input combinations:

| A | B | CarryIn | Sum | CarryOut |
| :---: | :---: | :---: | :---: | :---: |
| `0` | `0` | `0` | `0` | `0` |
| `0` | `0` | `1` | `1` | `0` |
| `0` | `1` | `0` | `1` | `0` |
| `0` | `1` | `1` | `0` | `1` |
| `1` | `0` | `0` | `1` | `0` |
| `1` | `0` | `1` | `0` | `1` |
| `1` | `1` | `0` | `0` | `1` |
| `1` | `1` | `1` | `1` | `1` |

Check Lesson 5.1's two rules against any row: Sum is `1` in exactly the odd-count rows, and CarryOut in every row with at least two ones. The table is also your test plan; when the build is done, you will walk all eight rows.

A standard implementation uses:

-   two XOR gates
-   two AND gates
-   one OR gate

Build that once, test it thoroughly, and then repeat it.

![1-Bit Full Adder CircuitVerse Diagram](./images/full-adder_circuitverse.png)
*Figure: A standard 1-bit full adder. Two XOR stages generate the Sum bit, while the AND/OR network generates Carry-Out. Shown computing `1 + 1 + 0`: the two ones make Sum `0` and hand a `1` to Carry-Out.*

#### Lab Part A: Build a 1-bit full adder module

1.  Lay out three labeled inputs: `A`, `B`, and `CarryIn`.
2.  Build the XOR path for the **Sum** output:
    -   First compute $A \oplus B$.
    -   Then XOR that result with `CarryIn`.
3.  Build the carry path:
    -   One AND gate computes $A \land B$.
    -   A second AND gate computes $CarryIn \land (A \oplus B)$.
    -   OR those two results together to produce `CarryOut`.
4.  Label the two outputs clearly.
5.  Test all eight rows of the truth table above. Every row that passes is a row you never have to doubt again.

![1-Bit Full Adder Minecraft Build](./images/full-adder_minecraft.png)
*Figure: The 1-bit full adder module in Minecraft, set to the same `1 + 1 + 0` as the diagram above: both input lamps lit, the Sum lamp dark, and the Carry-Out lamp glowing.*

![1-Bit Full Adder (top-down)](./images/full-adder-aerial_minecraft.png)
*Figure: The same `1 + 1 + 0` from directly above: the `A` and `B` levers at the bottom both on, the Carry-In lever at the right off, and the same verdict as the iso, Sum dark and Carry-Out lit.*

#### Lab Part B: Assemble the 4-bit ripple-carry adder

![4-Bit Ripple-Carry Adder CircuitVerse Diagram](./images/4-bit-rca_circuitverse.png)
*Figure: Four full-adder modules chained into a 4-bit ripple-carry adder. Each stage's Carry-Out feeds the next stage's Carry-In. Shown computing `0101 + 0011` (the `5 + 3` from Lesson 5.1): the carry ripples through every stage and the result reads `1000`.*

> **Orientation check:** the least-significant stage goes on the RIGHT. The carry is born there and ripples left, exactly like the columns in Lesson 5.1.

1.  Duplicate your Module 1 input panel so you have two independent 4-bit inputs. Label the first `A3 A2 A1 A0` and the second `B3 B2 B1 B0`.
2.  Place four copies of your full adder in a row, one for each bit position, and label the stages `FA0` through `FA3`, starting from the right.
3.  Wire `FA0`, the least-significant stage:
    -   Connect $A_0$ and $B_0$.
    -   Give its `CarryIn` a labeled terminal, `CIN`, and set it to `0`. It looks pointless today. Module 6 will drive it on purpose.
4.  Wire the next three stages:
    -   Connect $A_1$/$B_1$, then $A_2$/$B_2$, then $A_3$/$B_3$.
    -   Connect each stage’s `CarryOut` to the next stage’s `CarryIn`.
5.  Collect the four `Sum` outputs into a 4-bit result bus.
6.  Keep the final `CarryOut` wire accessible. We're going to need it in the next module.

![4-Bit Ripple-Carry Adder Minecraft Build](./images/4-bit-rca-aerial_minecraft.png)
*Figure: The full 4-bit ripple-carry adder in Minecraft, seen from above and computing the same `5 + 3` as the diagram. The least-significant stage on the right keeps the full adder's yellow; its three repeats are grayed to show they are copies, not new designs. The carry ripples right to left, and only the leftmost Sum lamp is lit: `1000`.*

#### The experiment

Run these cases before moving on. The carry columns are the debugging gold: `C1` is `FA0`'s CarryOut, `C2` is `FA1`'s, and so on, with `C4` the final CarryOut. If a result is wrong, check the carries and you'll know exactly which stage to blame.

| Test | Result | C1 | C2 | C3 | C4 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `0001 + 0001` | `0010` | `1` | `0` | `0` | `0` |
| `0011 + 0010` | `0101` | `0` | `1` | `0` | `0` |
| `0101 + 0011` | `1000` | `1` | `1` | `1` | `0` |
| `0111 + 0001` | `1000` | `1` | `1` | `1` | `0` |

If a result is off by exactly `2`, `4`, or `8`, the most likely problem is a broken carry link into that stage.

---

### Lesson 5.3: The Integration Test

> **Key Takeaway:** Two subsystems that each pass their own tests can still fail once connected, if one produces values the other never agreed to accept. Integration testing is where that shows up.

Let’s connect our new adder to the display system from Module 4. On paper, this is a victory lap: the adder computes, the display displays, and all that's left is four wires between two circuits we've already tested to death.

#### The test

A quick word before you place a single block: this step is small. You're not rebuilding anything you see in the figures. The adder exists. The display exists. The only new construction is the connection between them: four redstone lines, one bit each, from the adder’s four `Sum` outputs to the decoder’s four inputs.

![The adder wired to the display, from above](./images/integration-bug-aerial_minecraft.png)
*Figure: The whole integration from above, the four adder slices along the bottom and the display system at the top. Everything here is something you already built except the four wires carrying the Sum bits up the middle into the decoder.*

1.  Wire the adder’s 4-bit `Sum` bus into the input of your display decoder.
2.  Try a case that stays inside the decimal range we already support:
    -   $4 + 3$
    -   binary: `0100 + 0011 = 0111`
    -   expected display: `7`

That should work.

![The composed system computing 4 + 3](./images/rca-bcd-display_circuitverse.png)
*Figure: The composed system passing its first test: `0100 + 0011` ripples through the adder, the decoder recognizes `0111` and fires its line, and the display draws a `7`. Every stage is doing its job.*

Now try this:

-   $8 + 4$
-   binary: `1000 + 0100 = 1100`
-   decimal: `12`

The adder works.

And the display goes blank.

![The integration bug in Minecraft](./images/integration-bug_minecraft.png)
*Figure: The moment it fails, in the world: `8` and `4` on the input levers, the powered rails carrying the adder's `1100` into the decoder, and the display dark. Every subsystem did its job.*

![Inside the 4-to-10 decoder receiving 1100](./images/4-to-10-decoder-1100_circuitverse.png)
*Figure: Inside the decoder at the moment of failure. `1100` lights the input rails, and every one of the ten line-detectors, each built to recognize one pattern from `0` through `9`, finds something wrong with it. No line fires.*

#### The diagnosis

This one is worth slowing down on, because nothing here is actually broken.

Nothing is wrong with the adder.
Nothing is wrong with the display.

The problem is that our display decoder from Module 4 is a **BCD decoder**. It only knows how to recognize the ten patterns for decimal digits `0` through `9`. It was never taught what `1010`, `1011`, `1100`, `1101`, `1110`, or `1111` mean.

We asked a correct subsystem to interpret a value that lies outside its vocabulary. The adder and the decoder just ran the redstone version of Abbott and Costello's "Who's on First?" routine: neither one said a single wrong thing, and the answer still never got through.

Two lessons fall out of this failure:

1.  **Integration reveals truths that isolated testing can't.** Every test we ran on the adder passed. Every test we ran on the display passed. The mismatch lived in the space between them, where no test was looking.
2.  **Hardware is only as capable as the assumptions built into it.** The decoder isn't broken. It was built for a world where every answer fits in one decimal digit, and our adder just left that world.

There's a precise name for what broke: the **interface contract**. Each subsystem keeps its own promise, and the promises don't line up.

| Subsystem | Its contract |
| :--- | :--- |
| Adder `Sum` bus | may output any pattern from `0000` to `1111` |
| BCD decoder | defines behavior only for `0000` to `1001` |
| The gap | six patterns (`1010`–`1111`) the adder can output but the BCD decoder never defined |

So the fix has to start somewhere unusual: not in the circuit, but in the way we write numbers down.

---

### Lesson 5.4: The programmer's solution – Speaking hexadecimal

> **Key Takeaway:** Hexadecimal is the standard human-readable shorthand for 4-bit binary values: one symbol per nibble, no conversion arithmetic.

We now have a choice.

We could build a more complicated decimal display system that shows numbers like `12` using two separate digits.

That's possible, and it's real hardware. Humans buy calculators, not hex displays, so real machines pay this cost all the time: a whole converter circuit standing between the arithmetic and the screen. We build exactly that machine in Module 13, at the far end of the course.

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

So when the adder outputs `1100`, we don't need to think “the display failed.”
We can think “the machine just said `C`.”

> **Two different limits, one fixed today**
> Hexadecimal gives us a symbol for all sixteen patterns the adder's four `Sum` wires can carry. That's the limit we're fixing in this module.
> Some additions overflow into a fifth bit on `CarryOut`, and no notation can make a fifth bit fit in four. That's a different limit, and it's Module 6's whole opening act.

#### Why sixteen lines up and ten never will

Sixteen isn't an arbitrary choice. Sixteen is $2^4$, and that one fact does all the work: each hex digit covers exactly one **nibble**, a 4-bit group, no more and no less. Ten has no such relationship with binary, and that mismatch is the entire reason our decimal decoder ran out of vocabulary at `1010`.

The nibble alignment makes conversion mechanical. To read binary as hex, split it into nibbles and name each one from the table:

$$
\underbrace{1100}_{\text{C}}\;\;\underbrace{0011}_{\text{3}} \quad\rightarrow\quad \text{C3}
$$

No long division, no arithmetic. You already read numbers this way, by the way: nobody recites a phone number as ten raw digits. You say it in chunks, because chunks are what a human memory can actually hold onto, and the digits inside each chunk come along for free. Hex is that same chunking made official, with every group of four bits getting a single name. And it scales cleanly: an 8-bit value is two hex digits, a 16-bit value four, a full 64-bit value sixteen. That same grouping shows up all through low-level programming, debugging, and computer architecture.

One convention before we move on: in many programming languages, and everywhere in this course, hexadecimal wears a `0x` prefix, so `0xC` means “`C`, the number” rather than “`C`, the letter.” You will see that prefix for the rest of the course.

#### Try it

Read these in hex, one nibble at a time:

1.  `0110`
2.  `1111`
3.  `10100101` (split it into two nibbles first)

<details>
<summary><strong>Show Solution</strong></summary>

1.  `0110` is `0x6`.
2.  `1111` is `0xF`.
3.  `1010` is `A` and `0101` is `5`, so `0xA5`.

</details>

That's why hexadecimal is everywhere in low-level programming, debugging, and computer architecture. It lines up perfectly with the machine’s natural word sizes.

---

### Lesson 5.5: The lab – The hexadecimal upgrade

> **Key Takeaway:** Because our display was built as two clean stages, we can upgrade it surgically instead of rebuilding it from scratch.

Module 4's insistence on keeping the decoder and the ROM separate is about to pay off.

![The upgraded hexadecimal display system](./images/hex-display_minecraft.png)
*Figure: Where this lab ends: the display system rebuilt for hex, showing `C`. Everything in the deeper shades is what you are about to add; everything else is your Module 4 build, untouched.*

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

Four steps is genuinely all it takes, and that's the point: you already know this technique. You spent half of Module 4 learning it. The figures below are your references, each with its own job: the schematic shows the logic, the build shows the result, and the top-down view is the one to build from, because every torch and repeater position on the new lines is readable straight off it.

![4-to-16 Decoder CircuitVerse Diagram](./images/4-to-16-decoder_circuitverse.png)
*Figure: The full 4-to-16 binary decoder. Sixteen output lines, one per 4-bit pattern; here the input `1111` activates line `LF`.*

![4-to-16 Decoder Minecraft Build](./images/4-to-16-decoder_minecraft.png)
*Figure: The upgraded decoder in the world, built standalone before wiring it in. The original 4-to-10 decoder keeps its Module 4 color; the six new hex lines carry the deeper shade.*

![4-to-16 Decoder (top-down)](./images/4-to-16-decoder-aerial_minecraft.png)
*Figure: The decoder from above: the 4-bit bus rails crossing every line column, with the hex extension standing out in the deeper shade.*

#### Lab Part B: Upgrade the ROM

1.  Extend the ROM so it now accepts all sixteen decoder lines.
2.  Program the segment patterns for `A` through `F`.
3.  Test each new letter one at a time before reconnecting the full system.

A common 7-segment convention, with `b` and `d` drawn lowercase for a practical reason: an uppercase `B` on seven segments is identical to `8`, and an uppercase `D` is identical to `0`.

| Letter | Segments |
| :---: | :--- |
| `A` | `a, b, c, e, f, g` |
| `b` | `c, d, e, f, g` |
| `C` | `a, d, e, f` |
| `d` | `b, c, d, e, g` |
| `E` | `a, d, e, f, g` |
| `F` | `a, e, f, g` |

![The hex letters on a 7-segment display](./images/hex-letters-7seg_circuitverse.png)
*Figure: The six letter patterns on the display: `A` through `F`, with `B` and `D` in their lowercase-looking forms.*

Same drill as the decoder: the top-down view below carries the exact tap positions for the six new lines.

![7-Segment Hex Decoder/Driver CircuitVerse Diagram](./images/7-segment-hex-decoder-driver_circuitverse.png)
*Figure: The extended decoder/driver ROM: all sixteen line inputs, one OR column per segment.*

![Extended ROM Minecraft Build](./images/hex-rom_minecraft.png)
*Figure: The extended ROM in the world, built standalone. The tap pattern is the programming: the original digit lines keep their Module 4 color, and the six new letter lines carry the deeper shade.*

![Extended ROM (top-down)](./images/hex-rom-aerial_minecraft.png)
*Figure: The ROM from above: every tap is one stored bit, and the deeper-shaded lines are the letters `A` through `F` being added.*

![Hexadecimal Display System Aerial View](./images/hex-display-aerial_minecraft.png)
*Figure: The upgraded display system from above, set to `1100`: the bus enters the decoder along the top, its sixteen lines drop into the ROM below, and the collected segment lines exit into the panel. The deeper shades mark everything that was added for hex.*

---

### Lesson 5.6: The payoff

> **Key Takeaway:** The test that broke your system is the test that proves your fix. Always re-run your failures.

Repeat the test that failed earlier:

-   Input A: `1000` (`8`)
-   Input B: `0100` (`4`)
-   Adder output: `1100`

Now the system should behave like this:

1.  The decoder recognizes `1100` and activates line `LC`.
2.  The ROM maps `LC` to the segment pattern for `C`.
3.  The display lights up a `C`.

The bug is fixed and the system is upgraded, with no rebuild required.

One test isn't a regression suite, though. Run the spread:

| Test | Display | Why it matters |
| :--- | :---: | :--- |
| `4 + 3` | `7` | the old decimal range still works |
| `8 + 2` | `A` | the first pattern the old display could never say |
| `8 + 4` | `C` | the original failure, now the acceptance test |
| `8 + 7` | `F` | the very top of the 4-bit range |
| `F + 1` | `0` | the Sum wires wrap around to `0000` and `CarryOut` raises its hand. Hold that thought for Module 6 |

![The payoff schematic](./images/rca-hex-display_circuitverse.png)
*Figure: The whole system as one schematic: the ripple-carry adder feeding the upgraded display chain, computing `8 + 4` and driving a `C`.*

![The payoff in Minecraft](./images/rca-hex-display_minecraft.png)
*Figure: The module artifact: the 4-bit adder wired to the hexadecimal display, computing `8 + 4` and showing `C`.*

---

### Module 5 Checkpoint

#### Practice Problem 5.7.1: Knowledge Check

1.  What is the difference between the `Sum` output and the `CarryOut` output of a full adder?
2.  What is the hexadecimal symbol for binary `1110`?
3.  Why did our original display fail on the result `1100`?

<details>
<summary><strong>Show Solution</strong></summary>

1.  The **Sum** output is the current bit of the result for that column. The **CarryOut** output is the carry bit that must be passed into the next column to the left.
2.  The hexadecimal symbol is **`E`**.
3.  The original display used a **BCD decoder**, which only knew how to interpret the patterns for decimal `0` through `9`. It had no rule for `1100`.

</details>

#### Practice Problem 5.7.2: Debug challenge

Your 4-bit adder works for `2 + 1`, `3 + 1`, and `4 + 1`, but `7 + 1` incorrectly produces `0000` instead of `1000`.

What is the single most likely fault in the adder?

<details>
<summary><strong>Show Solution</strong></summary>

The most likely fault is that the **`FA2` CarryOut is not reaching `FA3` CarryIn**.

`7 + 1` is:

$$
\begin{array}{cccccl}
  & \scriptstyle\textcolor{gray}{1} & \scriptstyle\textcolor{gray}{1} & \scriptstyle\textcolor{gray}{1} & & \\
  & 0 & 1 & 1 & 1 & \quad(7) \\
+ & 0 & 0 & 0 & 1 & \quad(1) \\
\hline
  & 1 & 0 & 0 & 0 & \quad(8)
\end{array}
$$

This result depends on the carry rippling through multiple stages. If one carry link is broken, the highest stage never receives the signal it needs to produce the leading `1`.

</details>

#### Practice Problem 5.7.3: The upgrade, on paper

1.  Which decoder taps recognize `1011` (line `LB`)? Use Module 4's convention: torch taps for `1`s, repeater taps for `0`s.
2.  Which segments does the ROM light for `0xE`?
3.  Your upgraded system shows `8 + 4 = C` correctly, but `8 + 2` gives a blank display. Which single decoder line is the prime suspect?

<details>
<summary><strong>Show Solution</strong></summary>

1.  Torch taps on `B3`, `B1`, and `B0`, and a repeater tap on `B2`, because `1011` has ones in the eights, twos, and ones places.
2.  `a, d, e, f, g`.
3.  The `LA` line, which should recognize `1010`. If it never fires, the ROM never hears about `A`, and the display stays dark, exactly like the original bug but for one value instead of six.

</details>

#### Real-world connection: Nibbles, hex dumps, and addresses

Hexadecimal is used everywhere because it compresses binary into chunks humans can actually read. One hex digit represents exactly one **nibble** (4 bits). Two hex digits represent a byte. That's why memory addresses, machine instructions, color values, and debug output are so often written in hex. When a programmer sees `0xC`, they're really seeing the 4-bit pattern `1100` wearing a friendlier face.

#### Software connection: Adding without `+`

A classic programming puzzle asks: how can you add two integers if the `+` operator is forbidden? The answer mirrors the hardware you just built.

-   XOR computes the **sum bits without carries**.
-   AND finds the **carry bits**.
-   Shifting the carry left moves it into the next column.
-   Repeat until there is no carry left.

```python
def add_nonnegative(a: int, b: int) -> int:
    while b != 0:
        partial_sum = a ^ b        # sum bits, carries ignored
        carry = (a & b) << 1       # carry bits, moved one column left
        a, b = partial_sum, carry
    return a
```

This version assumes nonnegative integers. After Module 6 teaches fixed-width Two's Complement, the masked version that also handles negatives will make sense too.

That clever software trick is the same arithmetic your hardware adder performs by rippling the carry through a chain of gates. The software repeats it as loop passes; the hardware repeats it in space.

#### Key Terms
-   **Adder**: A digital circuit that performs binary addition.
-   **Binary-Coded Decimal (BCD)**: A representation in which each decimal digit `0` through `9` is stored as its own 4-bit binary pattern.
-   **Carry bit**: A bit that is generated when a column of addition exceeds what can be represented in that column and must spill into the next one.
-   **Full adder**: A 1-bit arithmetic circuit that adds `A`, `B`, and `CarryIn`, producing `Sum` and `CarryOut`.
-   **Hexadecimal**: A base-16 number system that maps perfectly onto 4-bit binary values.
-   **Interface contract**: The set of values and behaviors a subsystem promises to accept or produce. Integration bugs live where two correct contracts fail to line up.
-   **Nibble**: A group of 4 bits.
-   **Ripple-carry adder**: A multi-bit adder made by chaining full adders so the carry propagates from stage to stage.

---

### Module 5 Conclusion

You built the first true arithmetic engine in the course. More importantly, you experienced the full engineering loop: design, build, integrate, watch it fail, then diagnose and improve. That is not a detour from real computer engineering. That *is* real computer engineering.

You also saw the reward of modular design. Because the decoder and ROM were cleanly separated, expanding the system was an upgrade, not a restart.

Our machine can now add, and it can display every possible 4-bit result, `0x0` through `0xF`. In the next module, we're going to push that arithmetic system even harder, right up against the limits of a 4-bit machine, and discover what happens when the answer no longer fits.
