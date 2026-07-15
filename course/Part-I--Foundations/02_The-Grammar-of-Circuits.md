## Module 2: The Grammar of Circuits – Foundational Logic Gates

### Module 2 Summary

-   **Learning Goals:**
    -   Understand the role of Minecraft's primitive logic gates (NOT and OR).
    -   Master the truth table, the chart that pins down exactly what a gate does for every input.
    -   Build a composite gate (AND) by combining primitives.
-   **Lesson Overview:**
    -   Lesson 2.1: The Rules of Thought
    -   Lesson 2.2: The Primitives – Building NOT and OR Gates
    -   Lesson 2.3: The First Composite Gate – Building an AND Gate
-   **Build:** A working set of the three foundational logic gates: NOT, OR, and AND.

---

### Module 2 Introduction

In our last module, we built an interface to speak to our computer in its native language: binary. But sending signals is only half the story. To make our machine *think*, it has to understand what those signals mean. We need to give it a grammar.

This module brings in one of the foundations the whole field stands on: **Boolean Algebra**, the math of True and False. Then we bring that theory to life by building the three "verbs" of logic: the **NOT**, **OR**, and **AND** gates.

---

### Lesson 2.1: The Rules of Thought

> **Key Takeaway:** Boolean algebra gives us a precise mathematical language for describing and manipulating the True/False states of digital circuits.

In the mid-1800s, a mathematician named George Boole developed a new kind of algebra. Unlike the algebra you're used to, where variables like $x$ and $y$ can be any number, Boole's variables were much simpler. They could only have two possible values: **True** or **False**.

This system, now called **Boolean Algebra**, spent about a century as a mathematical curiosity. Then engineers started building the first electronic computers out of on/off switches and realized Boole had already done their math for them, a hundred years early. In the abstract world of math, these values are the constants $1$ (True) and $0$ (False). In the physical world of our circuits, they're the literal signals `1` (ON) and `0` (OFF).

-   We treat our Redstone signals as Boolean variables, like $A$ or $B$.
-   A powered Redstone line has the physical value **True** (`1`).
-   An unpowered Redstone line has the physical value **False** (`0`).

Boolean algebra gives us a set of rules and operators to manipulate these variables. When we build those operators physically, we call them **logic gates**, and they're what the rest of this course is built from.

---

### Lesson 2.2: The Primitives – Building NOT and OR Gates

Every complex machine is built from simple parts. In digital logic, those parts are called **primitive gates**, and from a small set of them you can build any other gate. Our set is dictated by the mechanics of Minecraft itself, which gives us two logical operations right out of the box:

1.  **NOT:** A Redstone Torch naturally inverts a signal. This is our primitive NOT gate.
2.  **OR:** Redstone Dust naturally merges signals. If any line powering a central wire is ON, the whole wire becomes ON. This is our primitive OR gate.

From these two building blocks, **NOT** and **OR**, we build every other logic gate in the computer. You may have heard you can do the whole job with just NAND, or just NOR, and it's true: either one alone can express any logic there is. Real chips don't chase that kind of purity, though, they pull from whole libraries of gate types, each tuned for speed, area, and power. We're working in Redstone, where a torch inverts and dust merges, so NOT and OR are the primitives that fall out for free.

Now, let's build them.

---

#### How We Describe Each Gate

Each gate below follows the same format:

**Visual Introduction:**

-   **Abstract Symbol & Function:** We begin with an image showing the gate's standard engineering symbol alongside a simple circuit demonstrating its basic function.
-   **Composite Diagram (For Composite Gates Only):** For gates built from our primitives, we then show a detailed CircuitVerse diagram of how they're constructed using only NOT and OR gates.
-   **Minecraft Build:** Finally, we show a screenshot of the gate built in Minecraft, reflecting our "primitives-only" design philosophy.

**Formal Definition & Rules:**

-   **Formal Definition:** The high-level concept and official terminology (e.g., "Conjunction").
-   **Symbols:** Common ways the operator is written in logical notation and programming languages.
-   **The Rule:** A plain-English sentence describing what the gate does.
-   **Truth Table:** A complete chart of every input combination and its output.
-   **Primitive Boolean Expression:** The specific algebraic expression that represents our composite build using only **NOT** and **OR**.

**Practical Application:**

-   **Lab & Experiment:** A hands-on test to verify your Minecraft build against the gate's truth table.
-   **Real-World Connection:** An example of where this logic is used in real technology.
-   **Software Connection:** An example of how the logical operator is used in a programming context.

---

#### Operator 1: NOT (The Inverter) - A Minecraft Primitive

> **Key Takeaway:** The NOT gate flips a single input, turning a `1` to a `0` or a `0` to a `1`. It's the logical equivalent of the word "opposite."

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/02_NOT-gate_circuitverse.png" alt="NOT Gate in CircuitVerse" width="512px"/><br/><em>Figure: The abstract symbol for the NOT gate (left) and its function in a basic circuit (right), taking a single input $A$ and producing an inverted output $Y$.</em></div><br/>

-   **Formal Definition:** The NOT gate, or **Inverter**, performs logical **Negation**. It takes one input and outputs its exact opposite.
-   **Symbols:**
    -   **Logical Notations:**
        -   *Text-based:* $\text{NOT } A$
        -   *Symbolic:* $\neg A$
    -   **Programming Operator:** `!A`
-   **The Rule:** If the input is True, the output is False. If the input is False, the output is True.
-   **Truth Table: NOT Gate**

| $A$ | $\text{NOT } A$ |
|:---:|:----:|
| `0` | `1` |
| `1` | `0` |


##### Lab & Experiment

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/02_NOT-gate_minecraft.png" alt="NOT Gate in Minecraft" width="512px"/><br/><em>Figure: A NOT gate in Minecraft using a Redstone Torch. The torch inverts the input, turning the lamp on when the lever is off and vice versa. This is the simplest physical realization of logical negation.</em></div><br/>

1.  **Build the circuit:**
    1.  Place a solid block with a Lever on it for input $A$. Using a Redstone Lamp as the solid block here provides a helpful visual indicator.
    2.  Attach a **Redstone Torch** to the side or back of the block. This torch *is* the NOT gate.
    3.  Run Redstone Dust from the torch to a Redstone Lamp for output $Y$.
2.  **Test the circuit:**
    -   Set lever $A$ to ON (`1`). Observe that the output lamp is OFF (`0`).
    -   Set lever $A$ to OFF (`0`). Observe that the output lamp is ON (`1`).
3.  **Verification:** The physical results match the truth table.

##### Real-World & Software Connection

NOT turns up anywhere a signal needs flipping, from the ring oscillators that generate a computer's clock to arithmetic itself: to negate a number in two's complement, you invert every bit and add 1, which is exactly the operation we build in Module 6. In code it's the humble `!`, flipping a condition the same way the torch flips a signal: `if not is_ready: ...`.

---

#### Operator 2: OR (The "At Least One" Gate) - A Minecraft Primitive

> **Key Takeaway:** The OR gate outputs a `1` if **at least one** of its inputs is a `1`. It’s how we express "either/or" conditions.

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/02_OR-gate_circuitverse.png" alt="OR Gate in CircuitVerse" width="512px"/><br/><em>Figure: The abstract symbol for the OR gate (left) and its function in a circuit (right). The output $Y$ is active if input $A$, $B$, or both are active.</em></div><br/>

-   **Formal Definition:** The OR gate performs logical **Disjunction**. Think of it as the optimistic gate; it checks if *at least one* of its inputs is True.
-   **Symbols:**
    -   **Logical Notations:**
        -   *Text-based:* $A \text{ OR } B$
        -   *Symbolic:* $A \lor B$
    -   **Programming Operator:** `A || B`
-   **The Rule:** The output is True if $A$ is True, OR $B$ is True, or if both are True.
-   **Truth Table: OR Gate**

| $A$ | $B$ | $A \text{ OR } B$ |
|:---:|:---:|:--------:|
| `0` | `0` | `0` |
| `0` | `1` | `1` |
| `1` | `0` | `1` |
| `1` | `1` | `1` |

##### Lab & Experiment

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/02_OR_gate_minecraft.png" alt="OR Gate in Minecraft" width="512px"/><br/><em>Figure: A Minecraft OR gate built by merging two Redstone Dust lines. The output lamp lights up if either lever is on, demonstrating "at least one" logic.</em></div><br/>

1.  **Build the circuit:**
    1.  Place two input blocks (e.g., Redstone Lamps with Levers) for $A$ and $B$, leaving a space between them.
    2.  Place a **Redstone Repeater** facing away from the back of each input block. This acts as a diode, preventing signals from flowing backward.
    3.  Run **Redstone Dust** from each repeater and merge them into a single output line. This merger *is* the OR gate.
    4.  Connect this output line to a Redstone Lamp for $Y$.

    > **Engineering Note: What is a diode?**
    > In electronics, a **diode** is a component that allows a signal to flow in only one direction, like a one-way valve or a turnstile for electricity. This property is essential for preventing signals from going where they aren't supposed to.
    >
    > In our OR gate, if we merge the dust lines directly, a signal from input $A$ could travel backwards up the other wire and power input $B$'s lamp, even if $B$'s lever is off. This is called "back-powering."
    >
    > The **Redstone Repeater** does exactly this job in Minecraft. Notice the small arrow on top of it; it will only allow a signal to pass in that direction. By placing a repeater on each input line, the signal can flow *out* towards the final lamp, but can't flow *backwards* to interfere with the other input.


2.  **Test the circuit:** Verify all four combinations from the truth table (`00`, `01`, `10`, `11`) and confirm the output lamp behaves as expected.

##### Real-World & Software Connection

OR logic is used for monitoring multiple conditions. A car's dashboard might light up if the `LeftDoorOpen` is true OR the `RightDoorOpen` is true. In programming, the `||` operator achieves this, allowing a block of code to run if any one of several conditions is met.

#### Practice Problem 2.2.1: Boolean Expression Evaluation

Given the Boolean expression $A \text{ OR } (\text{NOT } B)$ : $A \lor (\neg B)$, evaluate the output for all possible input combinations and create a truth table. Then, build a Minecraft circuit to verify your results.

<details>
<summary><strong>Show Solution</strong></summary>

**Truth Table for $A \text{ OR } (\text{ NOT } B)$ : $A \lor (\neg B)$:**

| $A$ | $B$ | $\text{ NOT } B$ | $A \text{ OR } (\text{ NOT } B)$ |
|:---:|:---:|:---:|:---:|
| `0` | `0` | `1` | `1` |
| `0` | `1` | `0` | `0` |
| `1` | `0` | `1` | `1` |
| `1` | `1` | `0` | `1` |

**Minecraft Circuit**: Use a lever for input $A$ and another for input $B$. Place a Redstone Torch on the output line of $B$ to create the signal for $\neg B$. Merge the signal from $A$ and the signal from $\neg B$ using Redstone Dust (an OR gate). Connect the final output to a lamp and test all combinations to verify.

</details>

---

### Lesson 2.3: The First Composite Gate – Building an AND Gate

> **Key Takeaway:** An AND gate outputs a `1` only if **all** of its inputs are a `1`. We will build it by combining our primitive NOT and OR gates.

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/02_AND-gate_circuitverse.png" alt="AND Gate in CircuitVerse" width="512px"/><br/><em>Figure: The abstract symbol for the AND gate (left) and its function. The output $Y$ is active only if both $A$ and $B$ are active.</em></div><br/>

Minecraft doesn't give us a single block that performs the AND operation, known formally as Conjunction (of Junction fame, with the same function the song promised: hooking things up). This is the first gate we have to earn, built from the parts we already have.

To connect the abstract concept of a gate to our physical build, we use a consistent visual format. Each composite gate is introduced with its standard, abstract symbol, which is how engineers represent it in high-level diagrams, followed by a detailed composite diagram showing how to construct it from our primitive NOT and OR gates. In these diagrams, a dashed outline encloses the group of primitives, showing how they work together to become equivalent to the single, abstract gate.

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/02_AND-gate-composite_circuitverse.png" alt="AND Gate Composite in CircuitVerse" width="512px"/><br/><em>Figure: The AND gate constructed from our primitives. This diagram shows how two NOT gates and one OR gate are combined to create the AND function.</em></div><br/>


-   **Formal Definition:** The AND gate performs logical **Conjunction**. It's the strict gate; its output is True only if *all* inputs are True.
-   **Symbols:**
    -   **Logical Notations:**
        -   *Text-based:* $A \text{ AND } B$
        -   *Symbolic:* $A \land B$
    -   **Programming Operator:** `A && B`
-   **The Rule:** The output is True only if $A$ is True AND $B$ is True.
-   **Truth Table: AND Gate**

| $A$ | $B$ | $A \text{ AND } B$ |
|:---:|:---:|:---------:|
| `0` | `0` | `0` |
| `0` | `1` | `0` |
| `1` | `0` | `0` |
| `1` | `1` | `1` |

-   **The Boolean Expression:** Our build implements the expression $\text{NOT}(\text{NOT } A \text{ OR } \text{NOT } B)$ : $\neg(\neg A \lor \neg B)$.
---

#### Lab & Experiment

<div align="center"><img src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/02_AND-gate-composite_minecraft.png" alt="AND Gate Composite in Minecraft" width="512px"/><br/><em>Figure: A composite AND gate in Minecraft. This build physically demonstrates how to achieve AND logic using only Redstone Torches (NOTs) and Dust (OR).</em></div><br/>

> **Note on Screenshots and Color Coding:**
> Our Minecraft circuit screenshots use a pseudo-isometric view to show as much of the build as possible. However, it can sometimes be hard to tell if a redstone torch is attached to the backside of a block. To make this clear, any block with a torch on its backside is colored red in the screenshot. Blocks with torches only on top are easy to see, so they use the build’s default color unless they also have a backside torch, in which case they’re red. For redstone lamps used as inputs (with a lever on one side and a torch or repeater on the other), we can't color code them obviously, but the instructions clearly indicate when a torch is on the backside of one of these input blocks.


1.  **Build the circuit:**
    1.  Create two inputs, $A$ and $B$, using Levers on Redstone Lamps.
    2.  Attach a Redstone Torch to the back of each input block. These are your two **NOT** gates, creating the signals for $\neg A$ and $\neg B$.
    3.  Run Redstone Dust from both torches so they merge at a central point. This is your **OR** gate, which implements $\neg A \lor \neg B$.
    4.  Run this merged dust line into a solid block.
    5.  Attach one final Redstone Torch to the front of that block. This is your final **NOT** gate, which inverts the entire expression.
    6.  Connect this final torch to an output lamp for $Y$.
2.  **Test the circuit:** Cycle through all four input combinations. The output lamp turns on only when both lever $A$ AND lever $B$ are ON.

#### Real-World & Software Connection

AND is the gate for safety and precision, the logic of "both, or nothing." An industrial press might run only when `GuardClosed` is true **AND** `StartButtonPressed` is true, so it can't come down on someone's hand. In code, `&&` does the same job: every condition has to hold before the next block runs.

#### Practice Problem 2.3.1: Logic Gate Design Challenge

Design a circuit that implements the logic $A \text{ AND } (\text{NOT } B)$ : $A \land (\neg B)$ using only the NOT and OR primitives. Build it in Minecraft and verify with a truth table for all input combinations ($A$, $B$ = `0,0`; `0,1`; `1,0`; `1,1`).

<details>
<summary><strong>Show Solution</strong></summary>

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

</details>

---

### Module 2 Checkpoint

#### Practice Problem 2.4.1: Knowledge Check

1.  What are the two "primitive" logic gates that Minecraft provides directly through its game mechanics?
2.  What is the primary purpose of a truth table?
3.  What is the key difference in the rule for an OR gate versus an AND gate?

<details>
<summary><strong>Show Solution</strong></summary>

1.  The **NOT** gate (a Redstone Torch) and the **OR** gate (merging Redstone Dust lines).
2.  A truth table's purpose is to define a gate's behavior for every possible combination of inputs. It's the complete definition of how the circuit behaves, input by input.
3.  An **OR** gate outputs a `1` if *at least one* input is a `1`. An **AND** gate outputs a `1` only if *all* inputs are a `1`.

</details>

#### Practice Problem 2.4.2: The Word Problem

A simple home security system should sound an alarm ($Y$) if the front door is opened ($A$) **OR** the back door is opened ($B$), but only when the system is armed ($C$).

Write the single Boolean expression for the alarm $Y$. Which gates would you need to build this?

<details>
<summary><strong>Show Solution</strong></summary>

**Boolean Expression:** $Y = (A \lor B) \land C$

**Logic Gates Needed:** You would need one **OR** gate to combine the door sensors ($A \lor B$) and one **AND** gate to check if that result is true AND the system is armed ($C$).

</details>

#### Practice Problem 2.4.3: The Build Challenge

Now bring Practice Problem 2.4.2 to life. Build the home security system in Minecraft: three levers for the front door ($A$), the back door ($B$), and the armed switch ($C$), with a lamp for the alarm ($Y$). The circuit should implement $Y = (A \lor B) \land C$ using only the primitive NOT and OR gates. This is your first three-input circuit, so take your time with the wiring.

<details>
<summary><strong>Show Solution</strong></summary>

**Minecraft Circuit:**
1.  Create inputs for $A$, $B$, and $C$.
2.  Merge the dust lines from $A$ and $B$ (each through a repeater) into a single line. This **OR** gate produces the signal for $A \lor B$.
3.  Feed that merged signal and the $C$ signal into a composite **AND** gate (built from two NOTs and an OR, as shown in Lesson 2.3).
4.  Connect the output to a lamp for $Y$.

**Testing:** With $C$ (armed) OFF, the alarm should stay silent no matter what the doors do. With $C$ ON, opening either door (or both) should light the lamp. That's four quick checks: `C=0` with any doors, then `C=1` with $A$, with $B$, and with neither.

</details>

#### Key Terms

-   **Boolean Algebra**: A branch of mathematics for working with true/false values ($1$/$0$), using operators like AND, OR, and NOT.
-   **Composite Gate**: A logic gate that is constructed by combining primitive gates (e.g., an AND gate built from NOT and OR gates).
-   **Diode**: A component that lets a signal pass in only one direction. Redstone has no true diode, but the Repeater does the same job here, passing power toward the output without letting it back-feed into the other input line.
-   **Logic Gate**: A physical device that performs a Boolean logic operation on one or more inputs to produce a single output.
-   **Primitive Gate**: A basic, indivisible logic gate from which more complex gates are built. In our course, these are NOT and OR.
-   **Truth Table**: A chart showing every possible input combination for a logic circuit and its corresponding output.

---

### Module 2 Conclusion

You started with the abstract idea of Boolean Algebra and ended by building physical, working circuits that obey its laws. You now have the three foundational gates, NOT, OR, and AND, and you've used a move you will repeat for the rest of this course: building a component you don't have out of components you do.

In the next module, **The Art of Logic**, we'll expand our vocabulary with more specialized gates and learn the simplification techniques engineers use to make correct circuits efficient.
