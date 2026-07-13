## Part III: The Processor Core – Memory and Control

Incredible work completing Part II. Take a moment to step back and appreciate what you have built. You have forged the complete brain of our computer: a powerful and versatile Arithmetic Logic Unit that can perform arithmetic, execute logic, and report on the status of its own calculations. You have built a genuine, manually operated processor core.

But a computer is more than a processor. It does not wait for a human to flip levers for every single step. A true computer can follow a list of instructions, a program, all on its own.

In this final core Part of the course, we give our machine its memory, its rhythm, and its language. The theme is **Automation**. We are going to build the architectural pieces that separate a static calculator from a dynamic, self-running computer.

### Our Mission for Part III

This Part now unfolds across four closely linked modules.

-   **In Module 10 (The Processor's Scratchpad),** we will tackle the concept of state by building a register that can remember a value, giving the ALU a place to store its work.

-   **In Module 11 (Addressable Storage),** we will scale that single scratchpad into a full notebook by constructing a 16x4-bit Random Access Memory (RAM) module.

-   **In Module 12a (The Infrastructure),** we will build the machine's timing and routing backbone: the system clock, the Program Counter, the phase sequencer, the front panel, and the selector networks that let all the buses cooperate.

-   **In Module 12b (The Language of the Machine),** we will define the instruction set, build the control decoder, and run the first real program, complete with a conditional branch based on a latched status flag.

By the end of this Part, you will have achieved the central goal of the course. You will have orchestrated simple components into a machine that can execute a stored program without your direct intervention.

Let's begin by giving our computer a memory.
