## Appendix B: Glossary

This glossary compiles key terms from the Redstone University curriculum, organized alphabetically. Each term’s definition is followed by a footnote indicating the module where it is introduced.

**7-segment display**
: An arrangement of seven light segments that can be combined to display numbers and some letters. [4]

**Active-high select**
: A selection signal convention where the chosen line is represented by `1` or HIGH. [11]

**Active-Low Logic**
: A design principle where the "active" or "on" state is represented by a LOW (unpowered) signal. [4]

**Adder**
: A digital circuit that performs binary addition. [5]

**Address**
: A binary identifier that specifies one memory location. [11]

**Address bus**
: The collection of wires that carries the current memory address. [11]

**ALU (Arithmetic Logic Unit)**
: The processor subsystem that performs arithmetic and logical operations on binary data. [9]

**Argument Register (AR)**
: The register that stores the second nibble of the current instruction. [12a]

**Arithmetic lane**
: The ALU subcircuit that performs addition and subtraction in this design. [9]

**BCD (Binary-Coded Decimal)**
: A method of representing the decimal digits `0`–`9` using a 4-bit binary code. [4]

**Binary**
: A base-2 number system that uses only two symbols, `0` and `1`, to represent information. It is the fundamental language of all digital computers. [1]

**Binary Coded Decimal (BCD)**
: A representation in which each decimal digit is stored as its own 4-bit binary value. [13]

**Binary-Coded Decimal (BCD)**
: A representation in which each decimal digit `0` through `9` is stored as its own 4-bit binary pattern. [5]

**Binary-to-BCD conversion**
: The process of translating a binary number into separate decimal digits encoded in BCD. [13]

**Bit**
: A single "binary digit," which can be either a `0` or a `1`. It is the smallest possible unit of data in computing. [1]

**Bitwise Operation**
: An operation in software that manipulates numbers at the level of their individual bits, rather than their decimal value. [1]

**Boolean Algebra**
: A branch of mathematics for working with true/false values ($1$/$0$), using operators like AND, OR, and NOT. [2]

**Bus (Input Bus)**
: A collection of parallel wires that carry a complete piece of binary information. Our 4-bit input interface creates a 4-bit bus. [1]

**Capture on release**
: The timing behavior of a level-sensitive latch: transparent while its strobe is high, it keeps whatever value is present at the instant the strobe falls. [10]

**Carry bit**
: A bit that is generated when a column of addition exceeds what can be represented in that column and must spill into the next one. [5]

**Clock**
: The timing signal that coordinates state changes across the machine. [12a]

**Combinational logic**
: Logic whose outputs depend only on present inputs. [10]

**Comparator**
: A circuit that answers a relationship question about two values, such as whether they are equal. [7]

**Composite Gate**
: A logic gate that is constructed by combining primitive gates (e.g., an AND gate built from NOT and OR gates). [2]

**Condition code**
: Another common name for a status flag bit used by control flow instructions. [7]

**Control decoder**
: The logic that translates an opcode and timing phase into control signals. [12b]

**Control rail**
: A one-hot control line that gates one source onto a shared destination. [12a]

**Control signal**
: A signal that configures or steers a digital system rather than carrying ordinary data. [9]

**D-latch**
: A memory element that stores one bit and can be opened or closed by a control signal. [10]

**Data bus**
: The collection of wires that carries data into or out of memory. [11]

**Data path**
: The route along which actual data values travel through a digital system. [8]

**Decimal**
: The base-10 number system that humans commonly use, with ten unique symbols (`0`-`9`). [1]

**Decoder**
: A circuit that takes a multi-bit binary input and activates a single, corresponding output line. Our decoder acts as an **Identifier**. [4]

**Demultiplexer (DEMUX)**
: A circuit that routes one input to one of several possible outputs. [8]

**Diode**
: A component that allows a signal to flow in only one direction, preventing back-powering. The Redstone Repeater is our primary diode. [0]

**Diode Matrix**
: A grid of input and output lines where components (like our taps) are placed at intersections to create a programmable logic device, often used as a ROM. [4]

**Display driver**
: Hardware or software that converts internal values into signals suitable for a visual display. [13]

**Double Dabble**
: A classic shift-and-add-3 algorithm for converting binary numbers into BCD. [13]

**Encoder**
: A circuit that takes a single active input line and translates it into a multi-bit coded output. Our encoder acts as a **Mapper**. [4]

**Equality comparator**
: A comparator whose output is `1` only when two inputs are identical. [7]

**Execute phase**
: The phase in which the current instruction actually changes machine state. [12b]

**Feedback loop**
: A connection in which part of a circuit’s output influences its future behavior. [10]

**Fetch phase**
: The phase in which the machine reads the opcode or argument nibble from RAM. [12b]

**Fixed-width arithmetic**
: Arithmetic performed in a container with a limited number of bits. [6]

**Flag**
: A single-bit signal that summarizes some property of an ALU result. [7]

**Flag Register**
: A small register that stores status bits such as Zero and Negative for later control decisions. [10]

**Front panel**
: The human interface used to program, reset, halt, and step the computer. [12a]

**Full adder**
: A 1-bit arithmetic circuit that adds $A$, $B$, and `CarryIn`, producing `Sum` and `CarryOut`. [5]

**Functionally Complete**
: A property of a set of logic gates (or a single gate like NAND/NOR) from which any possible Boolean function can be constructed. [3]

**Gated OR**
: A readout strategy in which each source is first enabled or disabled by a gate, and the allowed outputs are then combined with OR logic. [11]

**Gated-OR merge**
: A routing idiom in which each source is ANDed with its own select rail and the results merge onto a shared line; the RAM read bus and the register input networks both use it. [12a]

**Hexadecimal**
: A base-16 number system that maps perfectly onto 4-bit binary values. [5]

**HLT**
: The halt instruction that stops the machine's clock. [12b]

**Input**
: A component, like a Lever, that allows a user to manually control a circuit. [0]

**Instruction Register (IR)**
: The register that stores the current opcode nibble. [12a]

**Instruction set architecture (ISA)**
: The defined collection of instructions the machine understands. [12b]

**Interface (Input Interface)**
: A device that allows a user or system to provide information to a machine. Our 4-lever setup is a manual input interface. [1]

**Inverter (NOT Gate)**
: A circuit or component that flips a signal from ON to OFF, or OFF to ON. The Redstone Torch is our primitive inverter. [0]

**Jump target**
: The address loaded into the Program Counter by a jump instruction. [12b]

**Lane**
: One parallel operation path inside the ALU. [9]

**Logic Gate**
: A physical device that performs a Boolean logic operation on one or more inputs to produce a single output. [2]

**Lookup table**
: A structure that maps each possible input directly to its desired output. [13]

**Memory Output Bus**
: The shared bus carrying the contents of the currently selected memory row. [11]

**Modularity**
: The engineering practice of designing a system in independent, interchangeable components. This makes the system easier to design, test, and upgrade. [4]

**Most significant bit (MSB)**
: The leftmost bit of a binary value, which carries the largest place value. [7]

**Multiplexer (MUX)**
: A circuit that selects one of several inputs and forwards it to a single output. [8]

**Negative Flag (`N`)**
: A flag that copies the most-significant bit of the result in a Two's Complement interpretation. [7]

**Nibble**
: A group of 4 bits. [5]

**One-hot**
: A signal convention in which exactly one line in a group is active at a time. [12a]

**Opcode**
: A code that specifies which operation a processor should perform. [9]

**Output**
: A component, like a Redstone Lamp, that displays the result or state of a circuit. [0]

**Overflow**
: The condition where the true result of a calculation needs more bits than are available in the destination width. [6]

**Phase sequencer**
: The control structure that cycles through `T0`, `T1`, and `T2`. [12a]

**Power Source**
: A component, like a Redstone Torch or Lever, that outputs a full-strength (`15`) signal. [0]

**Primitive Gate**
: A basic, indivisible logic gate from which more complex gates are built. In our course, these are NOT and OR. [2]

**Program Counter (PC)**
: The register that stores the address of the next memory nibble to fetch. [12a]

**Program mode**
: The operating mode in which the human manually writes values into RAM. [12a]

**Pulse limiter**
: A circuit that converts a long signal into a short, controlled pulse. [10]

**Random Access Memory (RAM)**
: Memory in which any location can be accessed directly by address. [11]

**Read path**
: The circuitry that places the contents of the selected memory location onto the output bus. [11]

**Register**
: A small, extremely fast storage location inside a computer's central processing unit (CPU) that holds data for immediate use.


### Module 1 Conclusion

Fantastic work! You've now mastered the most fundamental concept in all of computing: how information is physically represented in a binary system. You have a working input device, and you've seen how this physical concept directly connects to both real-world hardware and clever software algorithms.

Your input bus is ready to carry these binary signals to the next stage where logic gates will turn them into calculations and decisions. Now that you’ve built your input interface and practiced working with binary, you’re ready to learn how to manipulate these binary signals in Module 2: The Grammar of Circuits. There, we will build our first logic gates, which will process the inputs you’ve set here into meaningful outputs.

The basic building blocks of our computer are about to take shape. Get ready for the world of logic gates and circuits! [1]

**Register B**
: The register that holds the ALU's second operand and drives Bus B. [12a]

**Repeater**
: A component that acts as a signal booster (refreshing signal strength to `15`) and a diode. [0]

**Repeater locking**
: A Redstone behavior in which a repeater powered from the side freezes the state of another repeater. [10]

**Result bus**
: The final output bus carrying the ALU’s selected result. [9]

**Ripple-carry adder**
: A multi-bit adder made by chaining full adders so the carry propagates from stage to stage. [5]

**ROM**
: Read-only memory; in this module, a fixed hardware lookup table implementing the conversion. [13]

**ROM (Read-Only Memory)**
: A type of storage where data is permanently programmed into the hardware's structure. [4]

**Row select**
: The signal that identifies which memory row is currently active. [11]

**RU-v1**
: The instruction set used by the first complete Redstone University computer. [12b]

**Run mode**
: The operating mode in which the machine uses its own control logic and clock to execute instructions. [12a]

**Select line**
: The control signal that tells a multiplexer which input to choose. [8]

**Selector network**
: The routing logic, gated-OR merges or 2:1 selectors, that chooses which data path is active. [12a]

**Sequential logic**
: Logic whose behavior depends on both present inputs and stored state. [10]

**Sign bit**
: In a signed binary representation, the most significant bit that indicates the sign of the value. [6]

**Signal Strength**
: The power level of a Redstone signal, ranging from `15` (full) down to `0` (off). A signal loses `1` strength for every block of dust it travels. [0]

**Simplification**
: The process of using the laws of Boolean algebra to reduce a complex logic expression to a simpler, equivalent one, resulting in a more efficient circuit. [3]

**State**
: The information currently remembered by a sequential circuit. [10]

**Status register**
: The conceptual collection of flag bits describing the outcome of the latest operation. [7]

**Step**
: A manually triggered single clock pulse used for debugging. [12a]

**Stored-program computer**
: A computer that keeps its instructions in memory and fetches them automatically during execution. [12b]

**Strong Power**
: A type of power provided by components like Repeaters or Torches directly to a block. It can activate all adjacent Redstone components, including dust. [0]

**Tap (Repeater/Torch)**
: Our term for a connection that reads a signal from a bus line to control another wire. [4]

**Transparent**
: The state of a latch when its output follows its input directly. [10]

**Truth Table**
: A chart showing every possible input combination for a logic circuit and its corresponding output. [2]

**Two's Complement**
: The standard binary representation for signed integers in which negation is performed by inverting the bits and adding `1`. [6]

**Universal Gate**
: A logic gate, such as NAND or NOR, that is functionally complete by itself. [3]

**Weak Power**
: A type of power provided by Redstone Dust to a block. It can activate components like lamps and repeaters, but not adjacent Redstone dust. [0]

**Wire**
: Our term for any component, usually Redstone Dust, that transmits a signal from one point to another. [0]

**Word size**
: The natural width, in bits, of the values a machine processes at once. [6]

**Write Enable (`WE`)**
: The control signal that permits new data to be stored. [11]

**Write path**
: The circuitry that stores the input data into the selected memory location. [11]

**Write strobe**
: A short pulse used to capture data into a memory element. [10]

**XOR (Exclusive OR)**
: A logic gate that outputs `1` only if its inputs are different. It is fundamental to binary arithmetic and many software algorithms. [3]

**Zero Flag (`Z`)**
: A flag that is `1` exactly when the result bus is all zeros. [7]


---

[0]: Module 0: The Redstone Toolkit – Orientation Day (Optional)

[1]: Module 1: Speaking in 1s and 0s – The Input Interface

[2]: Module 2: The Grammar of Circuits – Foundational Logic Gates

[3]: Module 3: The Art of Logic – Simplification and Special Gates

[4]: Module 4: From Binary to Pictures: Building a Digital Display

[5]: Module 5: The 4-Bit Adder & the Hexadecimal Upgrade

[6]: Module 6: Advanced Arithmetic – Overflow and Subtraction

[7]: Module 7: Comparators and Status Flags – The Dawn of Decision-Making

[8]: Module 8: The Multiplexer – The Digital Switch

[9]: Module 9: The ALU – The Grand Assembly

[10]: Module 10: The Processor's Scratchpad – Building a Register

[11]: Module 11: Addressable Storage – Building RAM

[12a]: Module 12a: The Infrastructure – Clock, Counter, and Control Paths

[12b]: Module 12b: The Language of the Machine – Instructions and the First Program

[13]: Module 13: The "Real World" Display – The Double Dabble Algorithm
