# Redstone University: The Curriculum

**Project Vision:** To demystify computer science by guiding learners to build a tangible, 4-bit computer in Minecraft. The course prioritizes understanding foundational theory (Boolean algebra, digital logic) before applying it in satisfying, practical builds, with a strong emphasis on modular, expandable design.

---

## Part I: The Foundations – The Human Interface (5 Modules)
*(The goal of this Part is to learn the language of the machine and build a complete system for manual input and visual output.)*

### Module 0 (Optional): The Redstone Toolkit – Orientation Day
-   **Narrative Beat:** Before we can build our computer, we need to know our tools.
-   **Learning Goals:** Identify core Redstone components, grasp the rules of power, and build a test circuit.
-   **Lessons:**
    -   Lesson 0.1: The Engineer's Toolkit
    -   Lesson 0.2: How Redstone Thinks: The Rules of Power
    -   Lesson 0.3: Lab: The Fundamental Circuit
-   **Minecraft Artifact:** A working on/off lamp circuit.

### Module 1: Speaking in 1s and 0s – The Input Interface
-   **Narrative Beat:** To talk to our computer, we must first learn its native language: binary.
-   **Learning Goals:** Understand binary, build a physical input interface, and practice conversions.
-   **Lessons:**
    -   Lesson 1.1: The Theory – Why Computers Use Binary
    -   Lesson 1.2: The Lab – Building Our 4-Bit Input Interface
    -   Lesson 1.3: Drills & Games – Strengthening Your Binary Intuition
-   **Minecraft Artifact:** A working 4-bit manual input panel.

### Module 2: The Grammar of Circuits – Foundational Logic Gates
-   **Narrative Beat:** We have a language, but no words. We'll build the fundamental "verbs" of logic: NOT, OR, and AND.
-   **Learning Goals:** Master truth tables, understand primitives, and build a composite gate from scratch.
-   **Lessons:**
    -   Lesson 2.1: The Rules of Thought
    -   Lesson 2.2: The Primitives – Building NOT and OR Gates
    -   Lesson 2.3: The First Composite Gate – Building an AND Gate
-   **Minecraft Artifact:** A working set of NOT, OR, and AND gates.

### Module 3: The Art of Logic – Simplification and Special Gates
-   **Narrative Beat:** We know the words; now we learn poetry. We'll learn how to make our circuits efficient and build advanced gates like XOR.
-   **Learning Goals:** Apply Boolean laws to simplify circuits and build XOR, NAND, NOR, and XNOR gates.
    -   Lesson 3.1: The Laws of Logic & The Power of Simplification
    -   Lesson 3.2: The Special Operator – Building an XOR Gate
    -   Lesson 3.3: Software Superpowers – The XOR Trick for Programmers
    -   Lesson 3.4: The Negated Gates – NAND, NOR, and XNOR
-   **Minecraft Artifact:** A working set of the advanced and universal logic gates.

### Module 4: Translators & Our First Display
-   **Narrative Beat:** The machine needs to talk back. We'll apply our full logic toolkit to build a translator that turns binary into readable digits.
-   **Learning Goals:** Understand decoders, encoders, and Read-Only Memory (ROM).

-   **Minecraft Artifact:** A complete 7-segment display system.

*(Includes Interlude I: The Art of Compact Design and Interlude II: The Power of Abstraction)*

---

## Part II: The Thinking Machine – Building the Processor (5 Modules)
*(The goal of this Part is to construct the entire mathematical and logical brain of our computer, the Arithmetic Logic Unit (ALU), capable of not only calculation but also decision-making.)*

### Module 5: The 4-Bit Adder & The Hexadecimal Upgrade
-   **Narrative Beat:** Time for math! We'll build an adder, discover its limitations with our display, and upgrade our system to a new language—Hexadecimal—to fix it.
-   **Learning Goals:** Build a ripple-carry adder, discover "out of range" bugs, learn hexadecimal, and appreciate modular design by upgrading the decoder and encoder.
-   **Minecraft Artifacts:** A 4-bit adder connected to an upgraded 4-to-16 decoder and hex-capable display.
-   **The Payoff:** The calculation `$8+4$` initially fails, but after the upgrade, it correctly displays a `$C$`.

### Module 6: Advanced Arithmetic – Overflow and Subtraction
-   **Narrative Beat:** We'll push our adder to its breaking point, learn to detect "overflow," and then, with a mathematical trick, teach it how to subtract.
-   **Learning Goals:** Understand arithmetic overflow, the carry bit, and Two's Complement for negative numbers.
-   **Minecraft Artifact:** A unified adder/subtractor unit with an overflow indicator light.

### Module 7: Comparators and Status Flags
-   **Narrative Beat:** Our machine can calculate, but it can't make decisions. It needs to ask questions: "Is this result zero?" We'll build circuits to compare numbers and "flags" to store the answers.
-   **Learning Goals:** Build a magnitude comparator ($A=B$) and understand the concept of a status register (Zero Flag, Negative Flag).
-   **Minecraft Artifact:** A 4-bit comparator and a 2-bit flag register.

### Module 8: The Multiplexer – The Digital Switch
-   **Narrative Beat:** Before we assemble the brain, we need to build its "steering wheel"—the Multiplexer, a circuit that lets us choose between different data paths.
-   **Learning Goals:** Understand the theory and application of a Multiplexer (MUX).
-   **Minecraft Artifact:** A functional 4-bit 2-to-1 MUX.

### Module 9: The ALU – The Grand Assembly
-   **Narrative Beat:** The grand assembly. We will forge all our arithmetic, comparison, and logic circuits into the final brain of our computer: the Arithmetic Logic Unit.
-   **Learning Goals:** Combine multiple functions into a single, controllable unit that sets status flags based on its results.
-   **Minecraft Artifact:** A complete ALU that can add, subtract, and perform logical operations, outputting both a result and status flags.

---

## Part III: The Automated Computer – Memory and Control (4 Modules)
*(The goal of this Part is to achieve true automation. We will add memory, timing, and control logic, transforming our powerful calculator into a genuine computer that can execute a stored program containing logic and loops.)*

### Module 10: The Processor's Scratchpad – Building a Register
-   **Narrative Beat:** Our ALU is a powerful but forgetful brain. We need to give it a "scratchpad" and a tiny flag latch so values and status bits can survive after the inputs change.
-   **Learning Goals:** Understand gated D-latch theory, implement repeater-locking memory in Minecraft, and construct a 4-bit register plus a 2-bit flag latch.
-   **Minecraft Artifact:** A functional 4-bit register and 2-bit flag latch.

### Module 11: Addressable Storage – Building RAM
-   **Narrative Beat:** A single scratchpad isn't enough for a real program. We will now scale up our register into a "notebook" with 16 numbered pages, building true Random Access Memory (RAM).
-   **Learning Goals:** Understand memory addressing, convert our active-low decoder into active-high row selects, and assemble a complete 16x4-bit RAM module with a gated-OR read bus.
-   **Minecraft Artifact:** A functional, addressable 16x4-bit RAM module.

### Module 12a: The Infrastructure – Clock, Counter, and Control Paths
-   **Narrative Beat:** Before the machine can follow instructions, it needs timing and discipline. We will build the clock, Program Counter, phase sequencer, front panel, and the selector networks that route data through the computer.
-   **Learning Goals:** Build a controllable clock, a loadable Program Counter, a three-phase sequencer, and the five selector networks required by the architecture.
-   **Minecraft Artifact:** The machine's timing and routing backbone, ready to fetch instructions.

### Module 12b: The Language of the Machine – Instructions and the First Program
-   **Narrative Beat:** The moment of truth. We will define the machine's instruction set, build the control decoder, and then watch the computer run its first real program, including a conditional jump based on a latched flag.
-   **Learning Goals:** Understand the fetch-decode-execute cycle in practice, validate each instruction, and run a countdown loop from RAM.
-   **Minecraft Artifact:** The final, complete, working 4-bit computer that can run a program with loops from RAM.
-   **The Ultimate Payoff:** Writing and watching a program that performs a countdown loop, demonstrating that the computer is making decisions based on the status flags built in Part II.

---

## Part IV: Post-Graduate Studies (Bonus Content)
*(For students who have completed the core curriculum and wish to explore advanced engineering challenges.)*

### Module 13: The "Real World" Display – The Double Dabble Algorithm
-   **Narrative Beat:** Remember the display bug from Module 5? We found a programmer's solution with Hex. Now, we build the complex engineer's solution that real digital clocks use.
-   **Learning Goals:** Build a proper Binary-to-BCD conversion circuit for multi-digit decimal display.
-   **Minecraft Artifact:** A Double Dabble circuit that converts a single binary input into two separate decimal digits.

### Potential Future Modules
-   **The Shifter:** Adding a barrel shifter to the ALU to perform bitwise shift operations (`` `<<` ``, `` `>>` ``), essential for efficient multiplication and division.
-   **Basic I/O:** Interfacing with the world beyond a display, such as using Note Blocks for sound output based on the computer's state.
-   **Subroutines:** Implementing a stack pointer and `` `CALL` ``/`` `RETURN` `` instructions to allow for reusable functions in your programs.
