<p align="center"><picture><source media="(prefers-color-scheme: light)" srcset="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/logo.png"><img alt="Redstone University Logo" src="https://media.githubusercontent.com/media/fielding/redstone-university/main/assets/images/logo-dark.png"></picture></p>

## Welcome to Redstone University!

Have you ever used a computer or a smartphone and wondered what’s *really* happening inside? Not the software, but the physical machine underneath it, the part that somehow turns electricity into arithmetic?

This course is about answering that question by building the machine yourself, in Minecraft, one circuit at a time.

I'm a self-taught software engineer with a non-traditional path, and at some point I wanted to go back and fill in the foundations properly. Binary, logic gates, computer architecture: I tried books and theory first, and the concepts stayed abstract no matter how many diagrams I stared at. Meanwhile, people were building genuinely complex logical machines in Minecraft with Redstone. Eventually the two thoughts collided: **what if we learned how a computer works by building one from scratch, using tools we already love?**

That's the mission of Redstone University: take the theory and turn it into a physical, working machine you can walk around inside.

### Why I Built This

Redstone University is the course I wished existed while I was teaching myself digital logic and computer architecture. The curriculum follows the path that actually made things click for me: build the thing I wanted to see next, run into the problem that naturally comes with it, solve it, repeat. Every lesson, build, and design choice came out of that loop.

What sets it apart? You're retracing the route I actually took, so alongside the "what" you get the "why" and the "how" behind each step. Minecraft is the laboratory, which keeps the abstract parts tangible (and, frankly, fun). And when clarity and efficiency disagree, we side with clarity.

---

### Course Build Philosophy

> **Disclaimer:** The builds and circuits in this course are intentionally designed for clarity and educational value, not for performance or compactness. We lay out circuits horizontally and in a “paper-like” fashion to make the logic easy to follow, just as you would draw them on paper. Our goal is to illustrate the underlying principles of computer engineering, not to create the most efficient or smallest circuits.

---

### How the Course is Structured

This course is organized as a complete curriculum, taking you from zero knowledge to a fully functional, programmable 4-bit computer. It is divided into Parts (major phases), Modules (specific projects), and Lessons (step-by-step instructions).

Along the way you can expect:
-   **Personal motivation and narrative:** Each module is introduced with a story or challenge that mirrors my own learning process.
-   **Hands-on builds:** Every concept is brought to life with a Minecraft circuit and, where helpful, a CircuitVerse diagram.
-   **Theory and practice:** The modules balance foundational theory with immediate, practical application.
-   **Real-world and software connections:** Each idea gets tied back to real computers and, where it fits, to programming challenges.

---

### The Road Ahead

-   **Part I: The Foundations – Laying the Groundwork.** We start with the basics of Redstone and binary, then work through the grammar of Boolean logic and use it to build a complete input and output system: a manual input panel and a 7-segment digital display.
    -   **Module 0 (Optional):** The Redstone Toolkit
    -   **Module 1:** The 4-Bit Input Interface
    -   **Module 2:** The Grammar of Circuits – Foundational Logic Gates
    -   **Module 3:** The Art of Logic – Simplification and Special Gates
    -   **Module 4:** Decoders & Digital Displays
    -   *(Includes Interludes on Compact Design and Abstraction)*

-   **Part II: The Thinking Machine – Building the Processor.** Here we construct the mathematical and logical brain of our computer. We build an adder and subtractor, give it the ability to make decisions with status flags, and assemble it all into a complete Arithmetic Logic Unit (ALU).
    -   **Module 5:** The 4-Bit Adder & The Hexadecimal Upgrade
    -   **Module 6:** Advanced Arithmetic – Overflow and Subtraction
    -   **Module 7:** Comparators and Status Flags
    -   **Module 8:** The Multiplexer – The Digital Switch
    -   **Module 9:** The ALU – The Grand Assembly

-   **Part III: The Processor Core – Memory and Control.** This is where the computer starts running itself. We build registers and addressable RAM to give our processor a memory, then add the clocking, routing, and control logic that let it fetch, decode, and execute instructions from a stored program.
    -   **Module 10:** The Processor's Scratchpad – Building a Register
    -   **Module 11:** Addressable Storage – Building RAM
    -   **Module 12a:** The Infrastructure – Clock, Counter, and Control Paths
    -   **Module 12b:** The Language of the Machine – Instructions and the First Program

-   **Part IV: Post-Graduate Studies – Advanced Engineering.** For anyone who wants to keep going: advanced topics, like building the hardware required to display multi-digit decimal numbers, the way a real-world calculator does.
    -   **Module 13:** The "Real World" Display – The Double Dabble Algorithm

---

### Who Is This For?

This course is for the curious. It's for:
-   **My daughter, Ada**, for whom this project was first imagined.
-   **Students and kids** who want a fun, hands-on introduction to STEM and computer science.
-   **University CS students** who want a physical way to visualize the concepts from their "Computer Architecture" class.
-   **Self-taught programmers and professionals** who want to solidify their understanding of what's happening at the hardware level.

### How to Get Started & Accessibility

This course is designed to be followed along in **Minecraft**. However, Minecraft is not strictly required!

#### Supported Editions & Versions
This course is authored on **Minecraft Bedrock Edition** and designed so that all of **Part I** works on **both Bedrock and Java** as written (we use only dust, torches, repeaters, lamps, and solid blocks).

If any module introduces edition‑specific behavior (e.g., pistons, observers, sub‑tick timing), it will be flagged in a **Bedrock/Java Notes** box with a tested variant.

**Versions tested:**
Bedrock: **[1.21.101]** • Java: **[pending]**

World downloads are provided for both Java and Bedrock. You can use this to check your work, explore the final product, or use the pre-built components as "black boxes" if you want to focus more on the high-level concepts.

**The "No-Minecraft Track":** If you don't have Minecraft or prefer a more theoretical approach, you can still complete this entire course. Every lesson will include text descriptions, diagrams, and schematics. I will also provide links to free online digital logic simulators (like [CircuitVerse](https://circuitverse.org/simulator)) where you can build and test these circuits without the game. The learning is in the logic, and the logic works the same in a simulator.

I'm glad you're here. It's time to stop just *using* computers and start *understanding* them.

---

### How to Use This Course

-   **Follow the modules in order:** Each module builds on the last, so start at the beginning and work your way through.
-   **Try the builds yourself:** The hands-on experience is where the real learning happens. Use Minecraft or CircuitVerse as you prefer.
-   **Use the world download or diagrams:** If you get stuck or want to check your work, explore the provided world or reference the diagrams.
-   **Read the real-world and software connections:** These sections help you see why each concept matters beyond Minecraft.
-   **Go at your own pace:** Take your time with each lesson, and revisit earlier modules whenever you need a refresher.


### Notation & Conventions

- **Bit names & order:** `B3 B2 B1 B0` (left → right). In math, use subscripts for readability: $B_3, B_2, B_1, B_0$.
- **Binary/hex literals (concrete values):** `0b0011`, `0x0C` (uppercase A–F). Decimal is plain text unless in code.
- **Variables & expressions (abstract):** LaTeX, e.g., $A$, $A \land B$, $\neg A$.
- **Dual notation (first use):** $A \text{ AND } B : A \land B$. Subsequent mentions: $A \land B$.
- **Active‑low signals:** Diagrams use a **bubble**. In text use an **overbar** (e.g., $\overline{L_3}$); if LaTeX isn’t available in a label, use `L3_n`.
- **Diagram colors:** RU palette = **neon green** (powered), **gray** (unpowered). Gate families use consistent palette colors in figures.



Ready? Let’s get building!
