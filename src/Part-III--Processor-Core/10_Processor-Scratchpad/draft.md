## Module 10: The processor's scratchpad – Building a register

### Module 10 Summary

-   **Narrative Beat:** Our ALU can think, but it still cannot remember. In this module, we solve that by building the machine's first true memory element: a register that can hold a 4-bit value after the inputs change.
-   **Learning Goals:**
    -   Understand the difference between **combinational** and **sequential** logic.
    -   Learn the theory of a **gated D-latch** and why feedback creates memory.
    -   Build the compact Minecraft version of that idea using a **repeater-locking D-latch**.
    -   Understand why a level-sensitive latch needs a **short write pulse**.
    -   Assemble a 4-bit scratchpad register and a 2-bit flag latch.
-   **Lesson Overview:**
    -   Lesson 10.1: The theory – From stateless to stateful
    -   Lesson 10.2: The first memory cell – The gated D-latch on paper
    -   Lesson 10.3: The Minecraft implementation – Repeater locking and pulse limiting
    -   Lesson 10.4: The lab – Building the scratchpad register and flag latch
-   **Minecraft Artifact:** A working 4-bit scratchpad register with a STORE button, plus a 2-bit flag latch for `Z` and `N`.

---

### Module 10 Introduction

Part II gave us a powerful processor core, but it also exposed the next missing ingredient.

Our ALU is powerful, but forgetful.

Change the inputs, and the result changes instantly. Nothing is preserved. That is exactly what we would expect from combinational logic, but it is a disaster if we want to do multi-step work. A real computer must be able to calculate something, **hold onto it**, and use it again later.

This module is where we leave the world of purely stateless circuits and step into the world of **memory**.

We will begin with the theory the honest way, by asking how a circuit could remember a bit at all. Then we will make an important engineering move. Instead of building a huge literal gate-level latch in Minecraft, we will switch to the compact, community-proven design used in real Redstone computers: **repeater locking**.

This is not a change in concept. It is an abstraction step. The logic is the same. The implementation is simply much better suited to Minecraft.

Once this module is complete, the machine will no longer just react. It will have a place to keep a thought.

---

### Lesson 10.1: The theory – From stateless to stateful

> **Key Takeaway:** A memory circuit is a circuit whose output depends not only on its current inputs, but also on what happened before.

So far, every circuit in the course has been **combinational**:

-   an AND gate outputs whatever the current inputs demand
-   a MUX outputs whatever the current select line and inputs demand
-   the ALU outputs whatever the current buses and control lines demand

There is no persistence. No history. No stored value.

A **sequential** circuit is different. Its current output depends partly on its **previous state**.

That means the circuit must contain some kind of loop that lets information remain present after the original input is gone.

#### Feedback is the key

The core trick of memory is **feedback**.

If part of a circuit’s output is routed back in a controlled way so it can influence its own future behavior, the circuit can settle into a stable state and remain there.

That stable state *is* memory.

#### The behavior we want

The 1-bit memory cell we are after should have three important signals:

-   **`D` (Data):** the bit we want to store
-   **`WE` (Write Enable):** the control signal that tells the cell when to accept new data
-   **`Q`:** the currently stored bit

Its desired behavior is simple:

-   when `WE = 1`, the cell is **open** or **transparent**
    -   `Q` follows `D`
-   when `WE = 0`, the cell is **closed**
    -   `Q` keeps its previous value

That is the first real form of memory our machine needs.

---

### Lesson 10.2: The first memory cell – The gated D-latch on paper

> **Key Takeaway:** The gated D-latch is the theoretical bridge between pure logic gates and practical computer memory.

The textbook version of our memory cell is the **gated D-latch**.

At the gate level, a D-latch is built by taking a memory loop and placing control logic in front of it so the input only reaches the loop when Write Enable is active.

![Gated D-Latch CircuitVerse Diagram](./images/gated-d-latch-circuitverse.png)
*Figure: A gated D-latch. The Write Enable line controls whether the input data may influence the internal feedback loop.*

The important thing to understand is not the exact arrangement of every gate, but the behavior it produces:

-   with `WE` active, the circuit is transparent
-   with `WE` inactive, the feedback loop preserves the last state

This gives us the exact semantics we need for a register.

#### Why we are not going to build the literal gate-level version in Minecraft

We *could* build a gate-level D-latch directly from AND, OR, and NOT gates.

But this is one of those moments where Minecraft pushes us toward a better engineering choice.

A literal gate-by-gate latch would be:

-   large
-   awkward to tile four times side by side
-   harder to debug
-   less representative of how Minecraft redstone computers are usually built in practice

So we are going to follow the same abstraction rule we adopted earlier in the course:

> Understand the idea in full, then use the best implementation for the medium.

In Minecraft, that best implementation is repeater locking.

---

### Lesson 10.3: The Minecraft implementation – Repeater locking and pulse limiting

> **Key Takeaway:** Repeater locking gives us a compact Minecraft implementation of a level-sensitive D-latch, but it also introduces an important constraint: the write signal must be a short pulse.

#### The repeater-locking D-latch

A repeater in Minecraft has a special property: if another repeater powers it from the side, it becomes **locked**. A locked repeater holds its current state and ignores changes at its input.

That gives us a beautiful Minecraft memory cell:

-   one repeater carries the **data** signal
-   a second repeater points into its side and acts as the **lock**

When the lock repeater is powered, the data repeater freezes.
When the lock repeater is unpowered, the data repeater becomes transparent and the output follows the input.

This is the Minecraft version of a D-latch.

#### A small but important convention change

There is one subtle twist.

In the repeater-locking design:

-   **lock powered** = hold state
-   **lock unpowered** = transparent

That is the opposite of the user-facing convention we want for a button labeled **STORE**.

So internally we invert the STORE signal with a torch:

-   **STORE pulse ON** -> torch turns OFF -> lock releases -> latch becomes transparent
-   **STORE pulse ends** -> torch turns ON again -> lock re-engages -> latch freezes the final value

This gives us an intuitive user-facing control while preserving the real repeater-lock behavior underneath.

> **Bedrock / Java Note**
>
> Repeater locking is one of the nicest cross-edition mechanisms in Redstone. It works the same way in Bedrock and Java, which is one reason it is so common in Minecraft computer builds.

#### Why pulse width matters

The repeater-locking latch is **level-sensitive**.

That means if STORE stays active for too long, the latch remains transparent for too long. The output will keep following the input until the pulse ends.

So a long STORE pulse does **not** mean “save once and wait.”
It means “keep listening the whole time.”

That is why we need a **pulse limiter**.

#### The pulse limiter

A pulse limiter, or monostable circuit, converts a button press or other long signal into a short, clean write strobe.

For our machine, a 1-tick or 2-tick pulse is enough.

That short pulse gives the latch just enough time to see the value on the bus, and then it closes again before the bus has time to wander to something else.

---

### Lesson 10.4: The lab – Building the scratchpad register and flag latch

> **Key Takeaway:** A register is just several memory cells sharing the same write pulse so they all capture a multi-bit value together.

#### Lab Part A: Build a single repeater-locking memory cell

1.  Build one data repeater.
2.  Place a second repeater so it points into the side of the data repeater.
3.  Feed the data input `D` into the front of the data repeater.
4.  Feed the user-facing STORE signal through a torch before it reaches the lock repeater.
5.  Attach a lamp to the output `Q`.

Now test the behavior:

1.  Put `D = 1` on the input.
2.  Press STORE briefly.
3.  Verify `Q = 1`.
4.  Change `D = 0` without pressing STORE.
5.  Verify `Q` stays `1`.
6.  Press STORE again.
7.  Verify `Q` changes to `0`.

If that works, you have a real Minecraft memory cell.

#### Lab Part B: Build the 4-bit scratchpad register

1.  Tile four of your memory cells side by side.
2.  Create a 4-bit data input bus.
3.  Feed one bit of the bus into each data repeater.
4.  Tie all four STORE inputs to the same pulse-limited STORE line.
5.  Collect the four outputs into a 4-bit output bus.

At this point, you have a 4-bit register.

![4-Bit Register Minecraft Build](./images/4-bit-register-minecraft.png)
*Figure: A 4-bit register built from four repeater-locking memory cells. The shared STORE pulse lets the whole 4-bit word be captured at once.*

#### Lab Part C: Build the 2-bit flag latch

The same memory idea also gives us a perfect place to store processor flags.

1.  Build two more repeater-locking cells.
2.  Feed the current **Zero Flag** into one cell and the current **Negative Flag** into the other.
3.  Add a shared **FLAGS STORE** pulse.
4.  Label the outputs `Z` and `N`.

This tiny 2-bit register will let the control unit look at the **previous** arithmetic result, not just whatever happens to be on the wires right now.

#### The experiment

Run these tests in order:

1.  Put `1011` on the 4-bit bus.
2.  Press STORE.
3.  Verify the register output reads `1011`.
4.  Change the input bus to `0011`.
5.  Verify the output still reads `1011`.
6.  Press STORE again.
7.  Verify the output changes to `0011`.

Then test the flag latch:

1.  Drive the ALU or a temporary input so `Z = 1`, `N = 0`.
2.  Press FLAGS STORE.
3.  Change the live signals.
4.  Verify the latched `Z` and `N` outputs keep the stored state until the next pulse.

#### Final integration test

Now connect the scratchpad register into the larger machine.

1.  Feed the ALU’s result bus into the register’s data input.
2.  Feed the register’s output bus into your hex display.
3.  Perform an ALU operation, for example `9 + 2`, which produces `B`.
4.  Press STORE.
5.  Change the ALU inputs to something else, such as `1 + 2`.

If your register is working, the display should still show `B` until you explicitly store a new value.

That is exactly the behavior we need for a processor scratchpad.

---

### Module 10 Conclusion

You have built the first true memory structures in the computer.

That is a bigger milestone than it may feel like at first. Until now, every signal in the system has been transient. It existed only as long as the current inputs demanded it. With the register, the machine can preserve a result and carry it forward into the next step of a process.

You also made an important engineering move. You learned the full gate-level idea, then adopted the compact Minecraft implementation that real Redstone computers use. That is exactly the kind of abstraction good engineers rely on.

In the next module, we will scale this idea dramatically. One scratchpad is useful, but a real computer needs many memory locations. We will duplicate this register into an addressable array and build our RAM.

---

### Module 10 Checkpoint

#### Practice Problem 10.5.1: Knowledge Check

1.  What is the difference between combinational and sequential logic?
2.  In a repeater-locking latch, what does it mean when the lock repeater is powered?
3.  Why do we need a pulse limiter on STORE?

<details>
<summary><strong>Show Solution</strong></summary>

1.  **Combinational logic** depends only on current inputs. **Sequential logic** depends on current inputs and previously stored state.
2.  It means the data repeater is **locked** and holds its current state.
3.  Because the latch is level-sensitive. If STORE stays active too long, the latch remains transparent and the output keeps following the input instead of capturing a single clean value.

</details>

#### Practice Problem 10.5.2: The design question

Why is it still useful to study the gate-level D-latch even though our actual Minecraft build uses repeater locking?

<details>
<summary><strong>Show Solution</strong></summary>

Because the gate-level D-latch explains the underlying *idea* of memory: controlled feedback and a write-enable signal. The repeater-locking version is a compact Minecraft implementation of the same behavior. Understanding the theory keeps the abstraction honest.

</details>

#### Practice Problem 10.5.3: Debug challenge

Your register seems to "forget" its value the instant you change the input bus, even when you are not trying to store anything new.

What is the most likely class of error?

<details>
<summary><strong>Show Solution</strong></summary>

The most likely issue is that the latch is being left in its **transparent** state. In practice, that usually means the lock repeater is not being powered when it should be, or the STORE signal is not being inverted correctly before it reaches the lock line.

</details>

#### Real-world connection: CPU registers and flag registers

Modern CPUs contain small, very fast storage elements called **registers**. Some hold data values, some hold addresses, and some hold status information such as carry, zero, or negative flags. Our 4-bit scratchpad register and 2-bit flag latch are small Minecraft versions of those exact ideas.

#### Software connection: Assignment and preserved state

When you write code like this:

```python
x = 11
```

it feels like the value simply "belongs" to `x` from that moment on. Hardware has to earn that behavior. A value remains available after the assignment only because some memory element, a register, RAM cell, or cache line, physically stores it.

#### Key Terms
-   **Combinational logic**: Logic whose outputs depend only on present inputs.
-   **D-latch**: A memory element that stores one bit and can be opened or closed by a control signal.
-   **Feedback loop**: A connection in which part of a circuit’s output influences its future behavior.
-   **Flag Register**: A small register that stores status bits such as Zero and Negative for later control decisions.
-   **Pulse limiter**: A circuit that converts a long signal into a short, controlled pulse.
-   **Register**: A grouped collection of memory cells used to store a multi-bit value.
-   **Repeater locking**: A Redstone behavior in which a repeater powered from the side freezes the state of another repeater.
-   **Sequential logic**: Logic whose behavior depends on both present inputs and stored state.
-   **State**: The information currently remembered by a sequential circuit.
-   **Transparent**: The state of a latch when its output follows its input directly.
-   **Write strobe**: A short pulse used to capture data into a memory element.
