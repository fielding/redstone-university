## Appendix A: Solutions

This appendix provides solutions to the practice problems in the Redstone University curriculum, organized by problem number for easy reference.

### Practice Problem 0.4.1: Knowledge Check

1.  What two essential functions does a Redstone Repeater perform?
2.  An engineer powers a block with a line of Redstone Dust. Will a piece of dust placed on top of that block receive power? Why or why not?
3.  What Redstone component is our primitive NOT gate?

**Answer:**

1.  It boosts a signal back to strength `15` and acts as a one-way diode.
2.  No. The dust only weakly powers the block, which cannot transmit power to adjacent dust.
3.  The Redstone Torch.


---


### Practice Problem 1.4.1: Knowledge Check

1. What is the largest number a 5-bit input interface could input? (Hint: The next bit would be the `16`s place).
2. What is the decimal value of the binary number `1100`?
3. How would you represent the number `10` in binary?

**Answer:**

1. The largest number a 5-bit input interface could input is **`31`**. (In binary: `11111`, which is $16 + 8 + 4 + 2 + 1 = 31$.)
2. The decimal value of the binary number `1100` is **`12`**. ($8 + 4 + 0 + 0 = 12$.)
3. The number `10` in binary is **`1010`**. ($8 + 0 + 2 + 0 = 10$.)


---


### Practice Problem 2.2.1: Boolean Expression Evaluation

Given the Boolean expression $A \text{ OR } (\text{NOT } B)$ : $A \lor (\neg B)$, evaluate the output for all possible input combinations and create a truth table. Then, build a Minecraft circuit to verify your results.

**Answer:**

**Truth Table for $A \text{ OR } (\text{ NOT } B)$ : $A \lor (\neg B)$:**

| $A$ | $B$ | $\text{ NOT } B$ | $A \text{ OR } (\text{ NOT } B)$ |
|:---:|:---:|:---:|:---:|
| `0` | `0` | `1` | `1` |
| `0` | `1` | `0` | `0` |
| `1` | `0` | `1` | `1` |
| `1` | `1` | `0` | `1` |

**Minecraft Circuit**: Use a lever for input $A$ and another for input $B$. Place a Redstone Torch on the output line of $B$ to create the signal for $\neg B$. Merge the signal from $A$ and the signal from $\neg B$ using Redstone Dust (an OR gate). Connect the final output to a lamp and test all combinations to verify.


---


### Practice Problem 2.3.1: Logic Gate Design Challenge

Design a circuit that implements the logic $A \text{ AND } (\text{NOT } B)$ : $A \land (\neg B)$ using only the NOT and OR primitives. Build it in Minecraft and verify with a truth table for all input combinations ($A$, $B$ = `0,0`; `0,1`; `1,0`; `1,1`).

**Answer:**

**Truth Table for $A \text{ AND } (\text{NOT } B)$:**

| $A$ | $B$ | $\text{ NOT } B$ | $A \text{ AND } (\text{ NOT } B)$ |
|:---:|:---:|:---:|:----------:|
| `0` | `0` | `1` | `0` |
| `0` | `1` | `0` | `0` |
| `1` | `0` | `1` | `1` |
| `1` | `1` | `0` | `0` |


**Boolean Expression**: The expression $A \text{ AND } (\text{NOT } B)$ : $A \land (\neg B)$ is equivalent to $\text{NOT}(\text{NOT } A \text{ OR } B)$ : $\neg(\neg A \lor B)$ by De Morgan’s Law.

**Minecraft Circuit**: This requires building a composite AND gate where one of the inputs is inverted first.
1. Create inputs for $A$ and $B$.
2. Use a Redstone Torch on the $B$ input line to create the signal for $\neg B$.
3. Feed the original $A$ signal and the new $\neg B$ signal into a standard composite AND gate (built from two NOTs and an OR, as shown in the lesson).
4. Connect the output to a lamp and test all four states.


---


### Practice Problem 2.4.1: Knowledge Check

1.  What are the two "primitive" logic gates that Minecraft provides directly through its game mechanics?
2.  What is the primary purpose of a truth table?
3.  What is the key difference in the rule for an OR gate versus an AND gate?

**Answer:**

1.  The **NOT** gate (a Redstone Torch) and the **OR** gate (merging Redstone Dust lines).
2.  A truth table's purpose is to define a gate's behavior for every possible combination of inputs. It is the ultimate source of truth for how a logic circuit functions.
3.  An **OR** gate outputs a `1` if *at least one* input is a `1`. An **AND** gate outputs a `1` only if *all* inputs are a `1`.


---


### Practice Problem 2.4.2: The Word Problem

A simple home security system should sound an alarm ($Y$) if the front door is opened ($A$) **OR** the back door is opened ($B$), but only when the system is armed ($C$).

Write the single Boolean expression for the alarm $Y$. Which gates would you need to build this?

**Answer:**

**Boolean Expression:** $Y = (A \lor B) \land C$

**Logic Gates Needed:** You would need one **OR** gate to combine the door sensors ($A \lor B$) and one **AND** gate to check if that result is true AND the system is armed ($C$).


---


### Practice Problem 2.4.3: The Build Challenge

Now bring Practice Problem 2.4.2 to life. Build the home security system in Minecraft: three levers for the front door ($A$), the back door ($B$), and the armed switch ($C$), with a lamp for the alarm ($Y$). The circuit should implement $Y = (A \lor B) \land C$ using only the primitive NOT and OR gates. This is your first three-input circuit, so take your time with the wiring.

**Answer:**

**Minecraft Circuit:**
1.  Create inputs for $A$, $B$, and $C$.
2.  Merge the dust lines from $A$ and $B$ (each through a repeater) into a single line. This **OR** gate produces the signal for $A \lor B$.
3.  Feed that merged signal and the $C$ signal into a composite **AND** gate (built from two NOTs and an OR, as shown in Lesson 2.3).
4.  Connect the output to a lamp for $Y$.

**Testing:** With $C$ (armed) OFF, the alarm should stay silent no matter what the doors do. With $C$ ON, opening either door (or both) should light the lamp. That's four quick checks: `C=0` with any doors, then `C=1` with $A$, with $B$, and with neither.


---


### Practice Problem 3.1.1: Circuit Simplification Challenge

Given the following expression, simplify it using Boolean laws:
$$ (A \lor B) \land (\neg A \lor \neg B) $$

**Answer:**

**Simplification Steps:**
1.  **Start with the expression:** $(A \lor B) \land (\neg A \lor \neg B)$
2.  **Apply De Morgan’s Law to the second term:** $(\neg A \lor \neg B)$ is equivalent to $\neg(A \land B)$.
3.  **The expression becomes:** $(A \lor B) \land \neg(A \land B)$
4.  **This is the definition of Exclusive OR (XOR).**
5.  **Final simplified expression:** $A \text{ XOR } B$ : $A \oplus B$


---


### Practice Problem 3.2.1: The Two-Switch Light System

Design a Minecraft circuit for a two-switch light system where flipping either switch toggles the light’s state. This requires implementing the logic $A \text{ XOR } B : A \oplus B$ using only NOT and OR gates.

**Answer:**

**Logic:** The light should be ON when exactly one switch is ON, which is the definition of $A \text{ XOR } B : A \oplus B$.

**Truth Table:**
| $A$ | $B$ | $A \text{ XOR } B$ |
|:---:|:---:|:----------------:|
| `0` | `0` | `0` |
| `0` | `1` | `1` |
| `1` | `0` | `1` |
| `1` | `1` | `0` |

**Minecraft Circuit:** Build the XOR circuit from this lesson. Connect levers for inputs $A$ and $B$, and a lamp for the output. Test by flipping each lever individually and verifying that the lamp's state toggles each time.


---


### Practice Problem 3.3.1: The Missing Number Challenge

Now that you've seen how the XOR trick works, try applying the same core principle to solve a different, but related, problem.

> **The Challenge:**
>
> You are given a list of numbers that contains every number from `0` to `n` exactly once, except for one number which is missing. Your task is to find that missing number.
>
> -   **Example List:** `nums = [3, 0, 1]`
> -   In this example, `n` would be `3`. The full range of numbers should be `[0, 1, 2, 3]`. The missing number is `2`.
>
> **Hint:**
> Think about the two groups of numbers you're dealing with: the list you *have* and the complete list you *should have*. How can you use XOR's self-canceling property to find the single difference between these two groups?

**Answer:**

**The Logic:**

The core idea is to XOR all the numbers that *should* be in the list against all the numbers that *are* actually in the list.

1.  First, we calculate the XOR sum of the complete sequence of numbers from 0 to `n`. For our example `[3, 0, 1]`, `n` is 3, so this would be `0 ^ 1 ^ 2 ^ 3`.
2.  Next, we calculate the XOR sum of the numbers in the list we were given: `3 ^ 0 ^ 1`.
3.  If we XOR these two results together, all the numbers that are present in both lists will pair up and cancel out, leaving only the number that was missing from the input list.

`(0 ^ 1 ^ 2 ^ 3) ^ (3 ^ 0 ^ 1)` can be rearranged as `(0^0) ^ (1^1) ^ (3^3) ^ 2`, which simplifies to `2`.

**The Python Code:**

```python
def missingNumber(nums):
    n = len(nums)
    expected_xor_sum = 0
    for i in range(n + 1):
        expected_xor_sum ^= i

    actual_xor_sum = 0
    for num in nums:
        actual_xor_sum ^= num

    return expected_xor_sum ^ actual_xor_sum
```


---


### Practice Problem 3.4.1: Universal Gate Challenge

Build an $A \text{ AND } B$ ($A \land B$) gate using only NOR gates. Verify it with a truth table in Minecraft for all four input combinations.

**Answer:**

**Logic:** From our universal gate table, we know the expression is $(A \text{ NOR } A) \text{ NOR } (B \text{ NOR } B)$.

**Truth Table Verification:**

| $A$ | $B$ | $A \text{ NOR } A$ ($\neg A$) | $B \text{ NOR } B$ ($\neg B$) | $(\neg A) \text{ NOR } (\neg B)$ | Final Output ($A \land B$) |
|:---:|:---:|:---:|:---:|:---:|:---:|
| `0` | `0` | `1` | `1` | `0` | `0` |
| `0` | `1` | `1` | `0` | `0` | `0` |
| `1` | `0` | `0` | `1` | `0` | `0` |
| `1` | `1` | `0` | `0` | `1` | `1` |

**Minecraft Circuit:** Build three NOR gates. The first takes input $A$ on both of its inputs (creating a NOT gate). The second does the same for input $B$. The outputs of these first two gates become the inputs for the third, final NOR gate, which produces the correct AND result.


---


### Practice Problem 3.5.1: Knowledge Check

1.  What is the key difference in the output of an OR gate versus an XOR gate when both inputs are `1`?
2.  Which two gates are considered "universal," and what is the name of this powerful property?
3.  Using De Morgan's Law, what is the equivalent expression for $\neg(A \land B)$?

**Answer:**

1.  When both inputs are `1`, an **OR** gate outputs `1`, while an **XOR** gate outputs `0`.
2.  The **NAND** gate and the **NOR** gate. The property is called **Functional Completeness**.
3.  The equivalent expression is $\neg A \lor \neg B$.


---


### Practice Problem 3.5.2: The Simplification Challenge

An engineer has designed a circuit with the expression: $Y = (A \text{ AND } C) \text{ OR } (A \text{ AND } B \text{ AND } C) \text{ OR } (A \text{ AND } (\text{NOT } B) \text{ AND } C)$ ($Y = (A \land C) \lor (A \land B \land C) \lor (A \land \neg B \land C)$).

Simplify this expression to its most efficient form using Boolean laws. (Hint: Look for a common factor in all three terms first).

**Answer:**

1.  **Start with the expression:** $Y = (A \land C) \lor (A \land B \land C) \lor (A \land \neg B \land C)$
2.  **Factor out the common term $(A \land C)$:** $Y = (A \land C) \land (1 \lor B \lor \neg B)$
3.  **Apply Inverse Law ($B \lor \neg B = 1$):** $Y = (A \land C) \land (1 \lor 1)$
4.  **Apply Idempotent/Annihilator Law ($1 \lor 1 = 1$):** $Y = (A \land C) \land 1$
5.  **Apply Identity Law:** $Y = A \land C$

The entire complex circuit simplifies down to a single AND gate with inputs $A$ and $C$.


---


### Practice Problem 3.5.3: The Universal Gate Challenge

Build an $A \text{ OR } B$ ($A \lor B$) gate using only **NAND** gates. Provide the Boolean expression for your build and verify it with a truth table.

**Answer:**

**Boolean Expression:** From our universal gate table, the expression is $(A \text{ NAND } A) \text{ NAND } (B \text{ NAND } B)$.

**Truth Table Verification:**

| $A$ | $B$ | $A \text{ NAND } A$ ($\neg A$) | $B \text{ NAND } B$ ($\neg B$) | $(\neg A) \text{ NAND } (\neg B)$ | Final Output ($A \lor B$) |
|:---:|:---:|:---:|:---:|:---:|:---:|
| `0` | `0` | `1` | `1` | `0` | `0` |
| `0` | `1` | `1` | `0` | `1` | `1` |
| `1` | `0` | `0` | `1` | `1` | `1` |
| `1` | `1` | `0` | `0` | `1` | `1` |


---


### Practice Problem 3.5.4: The Software Challenge

You are given a list where every number appears three times, except for one number that appears only once. Write a Python function using bitwise operators that finds the unique number. (Hint: The self-canceling property of XOR won't work directly. How can you count the `1`s in each bit position across all the numbers?)

**Answer:**

**The Logic:** If we sum the bits in each position (the 1s place, 2s place, 4s place, etc.) for all the numbers in the list, the sum for each bit of the triplicate numbers will be a multiple of 3. The unique number's bits will be the "remainders." We can use the modulo operator (`%`) to find these remainders.

**The Python Code:**
```python
def singleNumber_threes(nums):
    result = 0
    # Iterate through each of the 32 bits for a standard integer
    for i in range(32):
        bit_sum = 0
        for num in nums:
            # Check if the i-th bit is set in the current number
            if (num >> i) & 1:
                bit_sum += 1

        # If the sum is not a multiple of 3, the unique number's bit is 1
        if bit_sum % 3 != 0:
            # Reconstruct the result by setting the i-th bit
            result |= (1 << i)

    return result
```


---


### Practice Problem 4.4.1: Design on Paper

Before you build, an engineer must be able to plan. For output line **`L6` (Identity: `0110`)**, what taps would you need? List out which type of tap (Repeater or Torch) is required for each of the four bus lines (`B3`, `B2`, `B1`, `B0`).

**Answer:**

Applying our rule:
-   `B3` is `0`: Requires a **Repeater Tap**.
-   `B2` is `1`: Requires a **Torch Tap**.
-   `B1` is `1`: Requires a **Torch Tap**.
-   `B0` is `0`: Requires a **Repeater Tap**.


---


### Practice Problem 4.4.2: Debug Challenge

You've built your decoder, but something is wrong. When you set the input levers to **`1001`** (for the number `9`), you notice that the lamp for `L9` is on (which is correct), but the lamp for **`L8`** is *also* on (which is incorrect).

What is the single most likely mistake in your build that would cause this specific error?

**Answer:**

**The Logic**: The $L_8$ lamp should turn OFF when the input is `1001`. For $L_8$ to turn off, its wire needs to be powered. This means one of its "mismatch" taps must have activated.

**The Identity of `L8` is `1000`.** Let's compare this to the input `1001`.
-   `B3` is `1`, `L8` expects `1`. No mismatch.
-   `B2` is `0`, `L8` expects `0`. No mismatch.
-   `B1` is `0`, `L8` expects `0`. No mismatch.
-   `B0` is `1`, `L8` expects `0`. **This is a mismatch.**

The tap for `B0` on the `L8` line is supposed to detect this mismatch and power the `L8` wire. Since `L8` expects a `0` for `B0`, the rule says it must have a **Repeater Tap**.

**The Conclusion**: The fact that the `L8` lamp is still ON means its mismatch detector for the `B0` bit failed. The most likely cause is that you **forgot to place the Repeater Tap** from the `B0` bus line to the `L8` output wire. Without that tap, the wire never gets powered, and the lamp stays on.


---


### Practice Problem 4.5.1: Design on Paper

You are programming the line for the digit **`2`**. According to the lookup table, which perpendicular segment lines need a torch tap from the horizontal `L2` line?

**Answer:**

The digit `2` uses segments **`a`, `b`, `d`, `e`, and `g`**. Therefore, you would place torch taps at the intersections of the `L2` line and the perpendicular lines for those five segments.


---


### Practice Problem 4.5.2: Debug Challenge

When you test your encoder by providing a LOW signal to the `L4` line, you expect to see the digit `4` (segments `b, c, f, g`). Instead, the display shows `b, c, f` but **segment `g` remains dark**. What is the most likely cause of this error?

**Answer:**

If a segment that should be ON is OFF, it means it is not receiving power. The most likely cause is simple: you **forgot to place the torch tap** at the intersection of the horizontal `L4` line and the perpendicular segment `g` line. Without that torch, there is nothing to power the line when `L4` goes low.


---


### Practice Problem 4.7.1: Knowledge Check

1.  Why is a two-stage (Decoder → Encoder) design generally better than a single, complex circuit?
2.  What is the purpose of the **Repeater Tap** in our compact decoder? Why can't we just use Redstone dust?
3.  In our Diode Matrix ROM, what does placing a **Torch Tap** at an intersection physically represent?

**Answer:**

1.  It breaks the problem down into smaller, independent modules (modularity). This makes each part easier to design, build, and debug.
2.  The Repeater Tap creates a "strongly powered" block, which is necessary to power the Redstone dust on the output line across the 1-block air gap. Simple dust would create a "weakly powered" block, which cannot.
3.  It represents a single "bit" of stored information. Specifically, it's a command to "turn this segment ON when this number line is selected (LOW)."


---


### Practice Problem 4.7.2: Decoder Design

You want to add a special output line, `LE`, that lights up only for even numbers (`0`, `2`, `4`, `6`, `8`). You realize that for all even numbers, the `B0` bit is always `0`. What is the single tap you would need to build a simple detector for this?

**Answer:**

You want the lamp to be ON only when `B0` is `0`. Our active-low system turns the lamp on when the line is unpowered. You would need a single **Repeater Tap** from the `B0` line. When `B0` is `1` (odd), the repeater powers the `LE` line and turns the lamp off. When `B0` is `0` (even), the repeater is off, the line is unpowered, and the lamp turns on.


---


### Practice Problem 4.7.3: Encoder Design

The letter 'A' can be made with segments `a, b, c, e, f, g`. According to the design of our ROM, which segment line is the *only one* that would **not** have a torch tap placed on it from the `LA` input line?

**Answer:**

The line for the letter 'A' would need to activate every segment *except* for segment **`d`**. Therefore, `d` is the only segment line that would not get a torch tap.


---


### Practice Problem 4.7.4: Reverse Engineering

You see a line in a decoder that has Torch Taps on `B2` and `B1`, and Repeater Taps on `B3` and `B0`. What decimal number is this line designed to detect?

**Answer:**

Torches are for `1`s, Repeaters are for `0`s. So the identity is `0110`. This is the binary for decimal **6**.


---


### Practice Problem 4.7.5: Debug Challenge

In the world download for this module, you will find a section labeled "Module 4 Debug Challenge." The display system is fully connected. When you input **`0010`** (for the number 2), the display incorrectly shows a **`6`**.

**Trace the logic**:
  - The digit `2` should be `a, b, g, e, d`.
  - The digit `6` is `a, c, d, e, f, g`.

What is the single most likely point of failure in the system that would cause this specific error? (Hint: The problem is in the Encoder/ROM).

**Answer:**

**The Logic**:
When the input is `2`, the `L2` line from the decoder correctly goes LOW. This is supposed to activate the torches for segments `a, b, d, e, g`.

The display shows a `6`, meaning segments `c` and `f` are ON when they should be OFF, and segment `b` is OFF when it should be ON.

**The Conclusion**:
This points to a catastrophic failure in the "programming" of the `L2` line in your Diode Matrix. You have wired it incorrectly.
-   You have likely **accidentally placed** torch taps from the `L2` line to the segment lines for `c` and `f`.
-   You have likely **forgotten to place** the torch tap from the `L2` line to the segment line for `b`.


---


### Practice Problem 5.7.1: Knowledge Check

1.  What is the difference between the `Sum` output and the `CarryOut` output of a full adder?
2.  What is the hexadecimal symbol for binary `1110`?
3.  Why did our original display fail on the result `1100`?

**Answer:**

1.  The **Sum** output is the current bit of the result for that column. The **CarryOut** output is the carry bit that must be passed into the next column to the left.
2.  The hexadecimal symbol is **`E`**.
3.  The original display used a **BCD decoder**, which only knew how to interpret the patterns for decimal `0` through `9`. It had no rule for `1100`.


---


### Practice Problem 5.7.2: Debug challenge

Your 4-bit adder works for `2 + 1`, `3 + 1`, and `4 + 1`, but `7 + 1` incorrectly produces `0000` instead of `1000`.

What is the single most likely fault in the adder?

**Answer:**

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


---


### Practice Problem 5.7.3: The upgrade, on paper

1.  Which decoder taps recognize `1011` (line `LB`)? Use Module 4's convention: torch taps for `1`s, repeater taps for `0`s.
2.  Which segments does the ROM light for `0xE`?
3.  Your upgraded system shows `8 + 4 = C` correctly, but `8 + 2` gives a blank display. Which single decoder line is the prime suspect?

**Answer:**

1.  Torch taps on `B3`, `B1`, and `B0`, and a repeater tap on `B2`, because `1011` has ones in the eights, twos, and ones places.
2.  `a, d, e, f, g`.
3.  The `LA` line, which should recognize `1010`. If it never fires, the ROM never hears about `A`, and the display stays dark, exactly like the original bug but for one value instead of six.


---


### Practice Problem 6.5.1: Knowledge Check

1.  What does the final carry line tell us in our 4-bit arithmetic system?
2.  What is the 4-bit Two's Complement representation of `-1`?
3.  Why is XOR the key gate in the adder/subtractor design?

**Answer:**

1.  It tells us that the arithmetic result extended beyond the visible 4-bit result bus. In practical terms, it warns that the calculation spilled out of the 4-bit container.
2.  `1111`
3.  Because XOR can act as a **controllable inverter**: with control `0` it passes the bit unchanged, and with control `1` it flips the bit.


---


### Practice Problem 6.5.2: The word problem

Compute `D - 5` using 4-bit Two's Complement arithmetic.

1.  Write `D` in binary.
2.  Find the Two's Complement representation of `-5`.
3.  Add the two values.
4.  What 4-bit result remains after discarding the final carry?

**Answer:**

1.  `D` is `1101`
2.  `5` is `0101`; invert to `1010`; add `1` to get `1011`, so `-5` is `1011`
3.  `1101 + 1011 = 1 1000`
4.  Discard the final carry and keep `1000`, which is `8` in unsigned interpretation and `-8` in 4-bit signed interpretation. In the context of `13 - 5`, we read it here as the low 4 bits of the unsigned result `8`.


---


### Practice Problem 6.5.3: Debug challenge

Your addition mode works perfectly, but in subtraction mode every answer is off by exactly `1`. For example, `7 - 2` produces `4` instead of `5`.

What is the most likely missing connection?

**Answer:**

The most likely fault is that the **Subtract control is not connected to the initial CarryIn** of the least-significant adder stage.

Inversion alone produces One's Complement. To get **Two's Complement**, the circuit must also add `1`.


---


### Practice Problem 7.5.1: Knowledge Check

1.  Why are status flags usually more economical than building a separate large comparator for every possible condition?
2.  What gate is used to build the Zero Flag circuit?
3.  If the result bus is `1001`, what should the `Z` and `N` flags be?

**Answer:**

1.  Because one ALU operation can produce a result **and** a small collection of useful condition bits at the same time. That lets the CPU reuse existing arithmetic hardware instead of building a bulky dedicated circuit for every question.
2.  A **4-input NOR** gate.
3.  `Z = 0` and `N = 1`.


---


### Practice Problem 7.5.2: Design challenge

Without using the dedicated equality comparator from Lesson 7.2, how could a CPU test whether $A = B$ using only an ALU and flags?

**Answer:**

The CPU can compute $A - B$ in the ALU and then inspect the **Zero Flag**.

-   If the result is `0000`, then $A = B$
-   If the result is anything else, then $A \neq B$


---


### Practice Problem 7.5.3: Debug challenge

Your Zero Flag lamp turns ON correctly for `0000`, but it also turns ON for `1000`.

What is the most likely kind of wiring error?

**Answer:**

The most likely problem is that the Zero Flag circuit is **not seeing all four bits**. One of the input lines, likely the most-significant bit, is probably missing from the NOR gate input network. If `Y_3` is disconnected, then `1000` would be misread as if it were `0000`.


---


### Practice Problem 8.4.1: Knowledge Check

1.  In plain language, what does a multiplexer do?
2.  What is the Boolean expression for a 2-to-1 MUX?
3.  If you wanted to choose among four different inputs instead of two, how many select bits would you need?

**Answer:**

1.  A multiplexer chooses one of several inputs and forwards the selected one to its output.
2.  $Y = (A \land \neg S) \lor (B \land S)$
3.  You would need **2** select bits, because 2 bits can represent four choices: `00`, `01`, `10`, and `11`.


---


### Practice Problem 8.4.2: The demultiplexer

A **demultiplexer** does the opposite of a MUX: it takes one input and routes it to one of multiple outputs.

For a 1-to-2 DEMUX with input $D$, select $S$, and outputs $Y_0$ and $Y_1$, write the two Boolean expressions.

**Answer:**

-   $Y_0 = D \land \neg S$
-   $Y_1 = D \land S$


---


### Practice Problem 8.4.3: Design challenge

How could you build a **4-to-1** 4-bit MUX using only the 4-bit 2-to-1 MUX you built in this module?

**Answer:**

Use **three** 4-bit 2-to-1 MUX blocks:

1.  First stage:
    -   MUX 1 chooses between inputs 0 and 1
    -   MUX 2 chooses between inputs 2 and 3
2.  Second stage:
    -   MUX 3 chooses between the outputs of MUX 1 and MUX 2

One select bit controls the first-stage choices, and the other select bit controls the final choice.


---


### Practice Problem 9.5.2: The expansion

You want to add a new ALU function: **NOT A**.

Describe one reasonable way to expand the ALU to support it.

**Answer:**

One good approach is:

1.  Build a new 4-bit lane consisting of four NOT gates driven from Bus A.
2.  Expand the selector so it can choose among five lanes instead of four.
3.  That likely means either:
    -   adding another control bit and a larger MUX structure, or
    -   reorganizing the lane tree into a bigger selector network.


---


### Practice Problem 9.5.3: Debug challenge

Your ALU gives correct results for AND, OR, XOR, and ADD, but when you select SUB it still behaves like ADD.

What is the most likely missing or incorrect control connection?

**Answer:**

The most likely issue is that the **SUB control line is not reaching the arithmetic lane**.

That line must do two jobs inside the adder/subtractor:

-   drive the XOR bank that conditionally inverts Bus B
-   drive the initial carry-in that adds the required `1`

If `SUB` never reaches that circuit, the arithmetic lane remains stuck in addition mode.


---


### Practice Problem 9.6.1: Knowledge Check

1.  Why is it useful to compute several ALU lanes in parallel instead of trying to build only the selected operation on demand?
2.  In our ALU design, what do the bits `F1 F0 = 10` select?
3.  If the ALU result is `1000`, what should the `Z` and `N` flags be?

**Answer:**

1.  Parallel lanes make the design more modular and simpler to control. The hardware computes candidate results continuously, and the selector only needs to choose which one to forward.
2.  `F1 F0 = 10` selects the **XOR** lane.
3.  `Z = 0` and `N = 1`.


---


### Practice Problem 10.5.1: Knowledge Check

1.  What is the difference between combinational and sequential logic?
2.  In a repeater-locking latch, what does it mean when the lock repeater is powered?
3.  Why do we need a pulse limiter on STORE?
4.  At what exact moment does a repeater-locking latch commit its stored value?

**Answer:**

1.  **Combinational logic** depends only on current inputs. **Sequential logic** depends on current inputs and previously stored state.
2.  It means the data repeater is **locked** and holds its current state.
3.  Because the latch is level-sensitive. If STORE stays active too long, the latch remains transparent and the output keeps following the input instead of capturing a single clean value.
4.  At the falling edge of the STORE pulse. The latch is transparent while the pulse is high and keeps whatever value is on the data line at the instant the pulse ends: capture on release.


---


### Practice Problem 10.5.2: The design question

Why is it still useful to study the gate-level D-latch even though our actual Minecraft build uses repeater locking?

**Answer:**

Because the gate-level D-latch explains the underlying *idea* of memory: controlled feedback and a write-enable signal. The repeater-locking version is a compact Minecraft implementation of the same behavior. Understanding the theory keeps the abstraction honest.


---


### Practice Problem 10.5.3: Debug challenge

Your register seems to "forget" its value the instant you change the input bus, even when you are not trying to store anything new.

What is the most likely class of error?

**Answer:**

The most likely issue is that the latch is being left in its **transparent** state. In practice, that usually means the lock repeater is not being powered when it should be, or the STORE signal is not being inverted correctly before it reaches the lock line.


---


### Practice Problem 11.5.1: Knowledge Check

1.  In a 16x4-bit RAM, what do the numbers `16` and `4` each mean?
2.  Why do we add an inverter bank after our existing decoder before using it for RAM?
3.  Why must register outputs be gated before joining the shared Memory Output Bus?

**Answer:**

1.  `16` is the number of distinct memory locations. `4` is the number of bits stored at each location.
2.  Because the display decoder is active-low, but RAM row selection is much easier to build and reason about with active-high select lines.
3.  Without read gating, multiple rows would try to contribute to the output bus at the same time, causing incorrect combined outputs.


---


### Practice Problem 11.5.2: The architecture question

Our RAM read bus is described as a gated OR. In Minecraft, why might the physical build not look like a giant textbook OR gate even though the logic is the same?

**Answer:**

Because in Minecraft, large OR behavior is often implemented with merged dust lines and one-way components rather than a single neat symbolic gate. The logic is still OR: any selected row that contributes a `1` can power the shared line. The physical implementation is just adapted to the medium.


---


### Practice Problem 11.5.3: Debug challenge

Your decoder appears to be selecting the right address, but pressing WRITE never changes the chosen row.

What is the most likely missing adaptation from the display decoder to the RAM system?

**Answer:**

The most likely problem is that you forgot the **inverter bank**. Without it, the decoder is still active-low. The selected line is LOW, so the AND gate for the row write path never sees a HIGH select signal and the write pulse never reaches the row.


---


### Practice Problem 12a.7.1: Knowledge Check

1.  What are the four required behaviors of the Program Counter?
2.  Why is a one-hot phase sequencer useful in a Redstone computer?
3.  Why does our machine need a RAM data-in selector in addition to the runtime data-path selectors?
4.  Register A can load from three different sources. Why does its input network not need a MUX with encoded select bits?

**Answer:**

1.  Hold, increment, load, and reset.
2.  Because it gives the machine a clear internal rhythm where exactly one phase is active at a time, making fetch and execute behavior easier to build and debug.
3.  Because RAM input comes from different places in different modes: Register A during `STA` in Run mode, and the manual data levers during Program mode.
4.  Because the machine uses one-hot gating: each source is ANDed with its own control rail and the results merge onto the register's input, with an inverted gate selecting RAM output as the default when no rail is high. The control unit already produces one line per meaning, so there is nothing to encode.


---


### Practice Problem 12a.7.2: The design question

Why do we use separate **IR** and **AR** registers instead of trying to keep the whole 8-bit instruction in one place?

**Answer:**

Because our bus is only 4 bits wide. We fetch the instruction in two nibbles, so it is natural to store the opcode nibble in the Instruction Register and the second nibble in the Argument Register.


---


### Practice Problem 12a.7.3: Debug challenge

Your machine resets correctly and the phase sequencer cycles correctly, but during fetch it keeps reading the same memory location over and over.

What is the most likely subsystem to inspect first?

**Answer:**

The **Program Counter increment path** is the first thing to inspect. If the PC is not incrementing, or if the RAM address selector is failing to choose the PC during fetch, the machine will keep reading the same address.


---


### Practice Problem 12b.5.1: Knowledge Check

1.  Why do RU-v1 jump targets point to even addresses?
2.  Which instructions update the Flag Register in this version of the machine?
3.  Why is `STA` the instruction most likely to force a fourth timing phase if one is needed?
4.  At the end of `T2`, both the data rails and the load strobes collapse. Why must the data rails be the ones that collapse last?

**Answer:**

1.  Because each instruction occupies two RAM addresses, so opcode nibbles begin at even addresses.
2.  `ADD` and `SUB`, the instructions that write arithmetic ALU results back into Register A.
3.  Because it must switch RAM addressing, place Register A onto the RAM data-in path, and pulse RAM write-enable within the execute window.
4.  Because our latches capture on the strobe's falling edge. If the data path dies first, the register relocks on the collapsing value instead of the result. Delaying the data-side fans guarantees every register captures a valid value.


---


### Practice Problem 12b.5.2: The programmer

Write RU-v1 code to compute `5 - 3` and store the result at RAM address `D`.

**Answer:**

One valid program is:

| Address | Value | Meaning |
| :---: | :---: | :--- |
| `0` | `8` | `LDI A, 5` |
| `1` | `5` | argument |
| `2` | `9` | `LDI B, 3` |
| `3` | `3` | argument |
| `4` | `5` | `SUB` |
| `5` | `0` | ignored |
| `6` | `3` | `STA [D]` |
| `7` | `D` | argument |
| `8` | `F` | `HLT` |
| `9` | `0` | ignored |


---


### Practice Problem 12b.5.3: Debug challenge

Your machine fetches the correct opcode into IR and the correct argument into AR, but every `LDA [addr]` instruction loads garbage into Register A.

What is the most likely missing data-path connection?

**Answer:**

The most likely issue is that during execute, the **RAM address selector is not switching from PC to AR**. That means RAM is still reading from the instruction stream instead of from the intended data address.


---


### Practice Problem 13.4.1: Knowledge Check

1.  What problem does a binary-to-BCD converter solve?
2.  For decimal `13`, what are the two 4-bit BCD digits?
3.  Why is a ROM-based solution a good fit for our 4-bit machine?

**Answer:**

1.  It converts a single binary value into separate decimal digits that can each be displayed independently.
2.  Tens = `0001`, Ones = `0011`.
3.  Because our input range is tiny, only 16 possible values, a lookup-table implementation is straightforward, understandable, and easy to verify.


---


### Practice Problem 13.4.2: Debug challenge

Your converter displays `15` correctly, but for input `1101` it shows `11` instead of `13`.

What is the most likely ROM programming mistake?

**Answer:**

For input `1101` (decimal `13`), the correct outputs are tens `0001` and ones `0011`.

If the display shows `11`, then the tens digit is probably correct but the ones digit is missing the `O1` activation. The most likely mistake is that the `LD` input line was programmed to energize `O0` but not `O1`.


---


### Practice Problem 13.4.3: The programmer

How would software extract the tens and ones digits from an integer value such as `13`?

**Answer:**

Using integer division and modulo:

```python
value = 13

tens = value // 10
ones = value % 10
```

That is the software version of the hardware conversion problem.


---




<hr class="pagebreak"/>

