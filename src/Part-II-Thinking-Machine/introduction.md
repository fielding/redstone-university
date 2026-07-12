## Part II: The Thinking Machine – Building the Processor

Part I left you with something real: a machine you can talk to in binary, and a display that answers in digits. That is the entire human interface of a computer, and you built every block of it.

Now we build the part that thinks.

Part II has one goal: the **Arithmetic Logic Unit**, the ALU. It's the part of a processor that actually computes. When a CPU adds, subtracts, compares, or decides anything at all, the ALU is doing the work. We'll build ours piece by piece across five modules, and every piece is a working machine on its own before it joins the whole.

### Our Mission for Part II

The path there runs through real engineering problems, not around them:

-   **Module 5 (The Adder & The Hexadecimal Upgrade):** a 4-bit adder, our first real arithmetic, and an integration bug that ends with the whole display system learning to speak hexadecimal.

-   **Module 6 (Advanced Arithmetic):** push the adder to its limits, learn what overflow actually is, and teach the machine to subtract using two's complement.

-   **Module 7 (Comparators and Status Flags):** the hardware that lets the machine report on its own results. Status flags look small. All of programming stands on them.

-   **Module 8 (The Multiplexer):** the processor's "steering wheel", a digital switch that selects which operation's answer counts.

-   **Module 9 (The ALU – The Grand Assembly):** the capstone. Everything from Modules 5 through 8, assembled into one controllable unit.

By the end of Part II the computing core is done, and everything after it is about bringing that core to life.

Let's begin by teaching our machine how to do math.
