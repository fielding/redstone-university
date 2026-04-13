## Module 11: Addressable storage – Building RAM

### Module 11 Summary

-   **Narrative Beat:** One scratchpad is not enough for a real computer. In this module, we will duplicate our register into an organized memory array, assign each location an address, and build the circuitry that lets us read and write exactly one location at a time.
-   **Learning Goals:**
    -   Understand memory **addressing** and the role of an address bus.
    -   Reuse our existing decoder by converting its **active-low** outputs into **active-high** row selects.
    -   Distinguish clearly between the **write path** and the **read path** in RAM.
    -   Build a tiny RAM prototype first, then scale it into a 16x4-bit memory module.
    -   Understand how a gated-OR read bus works in both theory and Minecraft practice.
-   **Lesson Overview:**
    -   Lesson 11.1: The theory – From a register to RAM
    -   Lesson 11.2: The select problem – Active-low and active-high signals
    -   Lesson 11.3: The lab – Building a tiny RAM prototype
    -   Lesson 11.4: Scaling up to 16x4 RAM
-   **Minecraft Artifact:** A functional 16x4-bit RAM module with addressable read and write behavior.

---

### Module 11 Introduction

The register from Module 10 gave our machine memory, but only in the smallest possible sense. It is one sticky note. Useful, yes, but not enough for a real program.

A computer needs many remembered values:

-   data
-   constants
-   temporary results
-   eventually, instructions themselves

So now we ask a natural scaling question:

> What if we take the register we already trust and build many copies of it?

That is exactly how this module works. We are not inventing an entirely new kind of memory. We are scaling a known good unit into an organized array, then adding the logic that lets us point to one location by **address**.

This is where the machine begins to feel larger than a single circuit. We are building the computer's notebook now.

---

### Lesson 11.1: The theory – From a register to RAM

> **Key Takeaway:** RAM is an array of storage locations plus control logic that lets the machine select exactly one location for reading or writing.

A 16x4-bit RAM stores:

-   **16 locations**
-   **4 bits per location**

The natural way to build that in our course is:

-   16 copies of the 4-bit register from Module 10

But that raises two immediate problems.

#### Problem 1: Which row do we mean?

If there are 16 registers sitting side by side, how do we tell the machine which one we want?

We solve that with an **address**.

A 4-bit address can represent 16 unique values:

-   `0000` through `1111`

So we create a 4-bit **Address Bus** and assign one address to each register.

#### Problem 2: How do we share one output bus?

Even after we select a row for writing, we still need to read from memory cleanly.

If every register always drove its output onto the same bus, the result would be chaos. Stored `1`s from many rows would leak together.

So RAM needs two distinct ideas:

-   a **write path** that stores new data into one selected row
-   a **read path** that allows only one selected row onto the output bus

That is what turns "many registers" into real memory.

---

### Lesson 11.2: The select problem – Active-low and active-high signals

> **Key Takeaway:** Our existing decoder is already useful for RAM, but because it was designed for an active-low display system, we must invert its outputs before using them as row-select signals.

We already built a beautiful 4-to-16 decoder earlier in the course.

That decoder was designed for the display system, where an output line goes **LOW** when it is selected. That was perfect for our active-low ROM and display logic.

RAM wants something different.

#### Why RAM wants active-high row selects

For each memory row, the basic write rule is:

$RowWrite_i = Select_i \land WRITE$

That means the selected row should receive the write pulse only when:

1.  its select line is active
2.  the global write signal is active

That logic is most natural when `Select_i` is **HIGH** for the chosen row.

But our display decoder does the opposite:

-   selected row = LOW
-   all other rows = HIGH

#### The fix: one inverter per line

So we simply add one NOT gate, one torch, on each decoder output.

That gives us:

-   decoder output LOW on the chosen line
-   torch output HIGH on the chosen line
-   active-high row select for RAM

This is not a workaround. It is standard engineering.

We built one kind of subsystem with one polarity convention. Now we are adapting it to another subsystem with different needs.

<div align="center"><img src="./images/ram-architecture-circuitverse.png" alt="RAM Architecture Diagram" width="512px"/><br/><em>Figure: A RAM module as an array of registers. The address decoder chooses one location, the inverter bank converts the select lines to active-high, write-enable controls storage, and the gated read path places only one row onto the shared output bus.</em></div><br/>

#### A note about write pulses and repeater locking

Because our registers use repeater locking internally, the row write pulse is still a **user-facing STORE pulse**.

So the signal path for one row is really:

1.  active-high row select
2.  AND with global WRITE
3.  invert internally before it reaches the row's lock repeaters

The AND gate decides **which row** should listen.
The inverter at the register decides **how** the repeater-lock latch interprets that pulse.

---

### Lesson 11.3: The lab – Building a tiny RAM prototype

> **Key Takeaway:** Build small first. A 2-row or 4-row RAM prototype reveals the real behavior of the read and write paths before you commit to the full 16-row build.

Before we build the full RAM, we are going to prove the architecture on a smaller version.

#### Lab Part A: Build a 2x4 RAM prototype

1.  Build **two** 4-bit registers.
2.  Create a 1-bit temporary address input.
3.  Use that bit and its inverse to produce two active-high row-select lines.
4.  Create a shared 4-bit **Data In Bus** and feed it to both rows.
5.  For each row, compute:

    `$RowWrite_i = Select_i \land WRITE$`

6.  Feed that row-write pulse into the row's STORE input.

At this point, you should be able to write to one row without changing the other.

#### Lab Part B: Build the read path

Now we solve the output problem.

For each row:

1.  Take the row's 4 output bits.
2.  Gate each bit with the row's active-high select line.

That means each bit of each row passes through an AND gate before it reaches the shared bus.

For each output bit position:

1.  combine the gated outputs from all rows with OR logic

Conceptually, this is a **gated OR** read bus.

In Minecraft, the large OR stage is often implemented physically as a **dust merge** with repeaters or other one-way elements preventing backflow. That is still the same logical idea: only the selected row is allowed to contribute `1`s to the shared output bus.

#### The experiment

Run this exact sequence on the tiny prototype:

1.  Select row 0
2.  Put `1100` on the Data In Bus
3.  Pulse WRITE
4.  Verify row 0 reads back `1100`
5.  Switch to row 1
6.  Verify row 1 still holds its old value
7.  Put `0011` on the Data In Bus
8.  Pulse WRITE
9.  Verify row 1 now reads `0011`
10. Switch back to row 0 and verify it still reads `1100`

If all of that works, the architecture is sound.

#### Why this small prototype matters

If something goes wrong here, the issue is still understandable.

If you jump straight to 16 rows, every mistake becomes harder to locate. Small prototypes are not busywork. They are how good engineers protect themselves from large, confusing failures later.

---

### Lesson 11.4: Scaling up to 16x4 RAM

> **Key Takeaway:** The full RAM module is not a new idea. It is the exact same idea repeated carefully and organized well.

Now we scale the prototype into the full memory module.

#### Lab Part A: Build the row array

1.  Duplicate your 4-bit register **16 times**.
2.  Arrange them in a clear grid or stacked structure.
3.  Label them by address from `0` through `F`.

#### Lab Part B: Reuse the decoder and add the inverter bank

1.  Build or reuse the 4-to-16 decoder from the display system.
2.  Feed it with a 4-bit address input.
3.  Add one torch inverter on each decoder output line.
4.  Label the resulting active-high lines `Select 0` through `Select F`.

#### Lab Part C: Wire the write path

1.  Run the shared 4-bit Data In Bus to all 16 rows.
2.  Create a shared WRITE signal.
3.  For each row, AND its select line with WRITE.
4.  Make sure WRITE is a **short pulse**, reusing the pulse-limiter idea from Module 10.
5.  Feed that pulse into the row's STORE input.

This guarantees that only the selected row captures new data.

#### Lab Part D: Wire the read bus

For each of the four output bits:

1.  gate that bit from each row with the row's select line
2.  merge the results into one shared output line

The result is a 4-bit **Memory Output Bus** that shows the contents of exactly one selected row.

<div align="center"><img src="./images/ram-minecraft.png" alt="16x4 RAM Minecraft Build" width="512px"/><br/><em>Figure: A 16x4-bit RAM build. The decoder and inverter bank create active-high row selects, the write gates control storage, and the gated read bus presents the selected row on the output.</em></div><br/>

#### A practical debugging strategy

Do not try to verify all 16 addresses at once.

Bring the system up in stages:

1.  test 2 rows
2.  expand to 4
3.  expand to 8
4.  then finish all 16

At each stage, prove both behaviors:

-   writing changes only the selected row
-   reading shows only the selected row

#### The final test

Run this exact sequence:

1.  **Write to address `6`**
    -   Address Bus = `0110`
    -   Data In Bus = `1100`
    -   Pulse WRITE
2.  **Verify readback at address `6`**
    -   keep Address Bus = `0110`
    -   change Data In Bus to `0000`
    -   Memory Output Bus should still read `1100`
3.  **Check another address**
    -   change Address Bus to `0111`
    -   Memory Output Bus should now show whatever is stored at address `7`
4.  **Return to address `6`**
    -   Memory Output Bus should return to `1100`

If this works, you have built real, addressable RAM.

#### Looking ahead: programming mode

For now, we are interacting with RAM directly through temporary address and data controls.

In the next module, we will wrap this memory in the full computer infrastructure. The same basic ideas become a real **programming mode**, where a front panel lets you enter addresses and data by hand before switching the machine back into Run mode.

---

### Module 11 Conclusion

You have now built one of the defining structures of a real computer: addressable memory.

This is more than "a lot of registers." It is an organized system in which a binary address selects a location, a write path stores new information, and a read path retrieves existing information. That is a foundational architectural pattern that appears everywhere in computing.

You also saw another example of modular engineering paying off. The decoder from the display system did not have to be thrown away. It just needed an inverter bank so it could serve a new role.

In the next module, we will build the computer's timing and routing infrastructure: the clock, the program counter, the phase sequencer, and the bus selectors that let all of these components work together.

---

### Module 11 Checkpoint

#### Practice Problem 11.5.1: Knowledge Check

1.  In a 16x4-bit RAM, what do the numbers `16` and `4` each mean?
2.  Why do we add an inverter bank after our existing decoder before using it for RAM?
3.  Why must register outputs be gated before joining the shared Memory Output Bus?

<details>
<summary><strong>Show Solution</strong></summary>

1.  `16` is the number of distinct memory locations. `4` is the number of bits stored at each location.
2.  Because the display decoder is active-low, but RAM row selection is much easier to build and reason about with active-high select lines.
3.  Without read gating, multiple rows would try to contribute to the output bus at the same time, causing incorrect combined outputs.

</details>

#### Practice Problem 11.5.2: The architecture question

Our RAM read bus is described as a gated OR. In Minecraft, why might the physical build not look like a giant textbook OR gate even though the logic is the same?

<details>
<summary><strong>Show Solution</strong></summary>

Because in Minecraft, large OR behavior is often implemented with merged dust lines and one-way components rather than a single neat symbolic gate. The logic is still OR: any selected row that contributes a `1` can power the shared line. The physical implementation is just adapted to the medium.

</details>

#### Practice Problem 11.5.3: Debug challenge

Your decoder appears to be selecting the right address, but pressing WRITE never changes the chosen row.

What is the most likely missing adaptation from the display decoder to the RAM system?

<details>
<summary><strong>Show Solution</strong></summary>

The most likely problem is that you forgot the **inverter bank**. Without it, the decoder is still active-low. The selected line is LOW, so the AND gate for the row write path never sees a HIGH select signal and the write pulse never reaches the row.

</details>

#### Real-world connection: Word lines and bit lines

Real RAM chips also rely on the same broad ideas you just built. Decoding logic activates one row, often called a **word line**, while carefully controlled read and write circuitry connects that row to shared vertical paths, often called **bit lines**. Silicon RAM is denser and faster, but the conceptual skeleton is the same.

#### Software connection: Arrays and indexing

When software accesses something like `memory[6]`, it is using the idea of addressing. The number `6` acts like an address or index that selects one location from a larger collection. Your RAM module is the hardware counterpart of that idea: one binary address chooses one stored word.

#### Key Terms
-   **Active-high select**: A selection signal convention where the chosen line is represented by `1` or HIGH.
-   **Address**: A binary identifier that specifies one memory location.
-   **Address bus**: The collection of wires that carries the current memory address.
-   **Data bus**: The collection of wires that carries data into or out of memory.
-   **Decoder**: A circuit that converts a binary code into one active output line.
-   **Gated OR**: A readout strategy in which each source is first enabled or disabled by a gate, and the allowed outputs are then combined with OR logic.
-   **Memory Output Bus**: The shared bus carrying the contents of the currently selected memory row.
-   **Random Access Memory (RAM)**: Memory in which any location can be accessed directly by address.
-   **Read path**: The circuitry that places the contents of the selected memory location onto the output bus.
-   **Row select**: The signal that identifies which memory row is currently active.
-   **Write Enable (`WE`)**: The control signal that permits new data to be stored.
-   **Write path**: The circuitry that stores the input data into the selected memory location.
