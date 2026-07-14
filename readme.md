<p align="center">
    <picture>
      <source media="(prefers-color-scheme: light)" srcset="assets/images/logo.png">
      <img alt="Redstone University Logo" src="assets/images/logo-dark.png">
    </picture>
</p>

<h1 align="center">Redstone University</h1>

<p align="center">
  <strong>An interactive course on computer science and digital architecture, built from the ground up in Minecraft.</strong>
  <br />
  <br />
  <a href="#-course-structure--curriculum">Course Structure</a>
  ·
  <a href="https://github.com/fielding/redstone-university/issues">Report a Bug or Typo in the Course</a>
  ·
  <a href="https://github.com/fielding/redstone-university/issues">Request a Feature</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Course%20Status-In%20Development-yellow" alt="Course Status: In Development">
  <img src="https://img.shields.io/badge/Contributions-Welcome-brightgreen" alt="Contributions Welcome">
</p>

---

## 🚀 Early Preview: Part I is Ready for Feedback!

> **Welcome to the Redstone University early preview!**
>
> **Part I: The Foundations – Laying the Groundwork** is complete and ready to explore. I want this to be the best resource it can be, and that takes more eyes than mine.
>
> Try the builds, read the lessons, and if you find a typo, have a suggestion, or think a concept is unclear, **[open an issue on GitHub](https://github.com/fielding/redstone-university/issues)**.
>
> *The rest of the course (Parts II, III, and IV) is currently in active development.*

---

## About The Project

This project is a complete, university-level introductory curriculum in digital logic and computer architecture, starting from first principles. The campus is Minecraft. Instead of hardware description languages and simulators, every concept in the course becomes a physical, working machine you can walk around inside of.

I'm a self-taught computer engineer, and I'd been wanting to revisit the foundations properly for a while. The real push came from my daughter, Ada. She introduced me to Minecraft before she was even 2, and we've been building together ever since. Binary, bitwise operations, logic gates, computer architecture: these concepts are often introduced in ways that make them feel intangible, while over in Minecraft people are casually building machines out of Redstone that put my old homework to shame. So the question asked itself: what if we learned this stuff by building a computer from scratch, with tools we already love?

### Who Is This For?

This course is for the curious. It's for:
-   **My daughter, Ada**, who this project was first imagined for.
-   **Students and kids** who want a fun, hands-on introduction to STEM and computer science.
-   **University CS students** who could use a physical way to picture what their "Computer Architecture" class keeps describing.
-   **Self-taught programmers and professionals** filling in what's actually happening at the hardware level.

---

## Course Structure & Curriculum

This course is structured as a cumulative sequence, taking you from zero knowledge to a fully functional, programmable 4-bit computer. It's broken into four parts:

-   **Part I: The Foundations – Laying the Groundwork.** We start with the essential input/output system: the language of binary, the grammar of Boolean logic, a manual input panel, and a 7-segment digital display.

-   **Part II: The Thinking Machine – Building the Processor.** The mathematical and logical brain of the computer. We engineer an adder and subtractor, give it the ability to make decisions with comparators and status flags, and combine everything into a complete Arithmetic Logic Unit (ALU).

-   **Part III: The Processor Core – Memory and Control.** True automation, across Modules 10–12b. Registers and addressable RAM give our processor a memory, then clocking, routing, and control logic let it fetch, decode, and execute instructions from a stored program.

-   **Part IV: Post-Graduate Studies – Advanced Engineering.** For anyone who wants to keep going, Module 13 covers advanced topics, including the hardware it takes to display multi-digit decimal numbers just like a real-world calculator.

The current outline includes 13 numbered modules, with Module 12 intentionally split into **12a** (clock, counter, and control paths) and **12b** (instructions and the first program). See `curriculum.md` for the full module-by-module outline and `structure.md` for how the course is organized.

---


## Contributing

If you have a suggestion to improve a lesson, a typo to fix, or a circuit diagram to correct, fork the repo and open a pull request, or just open an issue with the "enhancement" tag. Either way, it's appreciated.

See [contributing.md](.github/CONTRIBUTING.md) for details.

---

## License

This project is dual-licensed so the course stays a free educational resource while the creator's rights stay protected.

#### Course Content
The educational content of this course, including all Markdown files (`.md`), images, diagrams, and assets, is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0)](http://creativecommons.org/licenses/by-nc-sa/4.0/).

<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a>

This means you are free to share and adapt the material for **non-commercial** purposes, as long as you give appropriate credit and distribute your contributions under the same license.

#### Software
All source code in this repository, such as the build script, is licensed under the [MIT License](LICENSE). You are free to use, modify, and distribute this code for any purpose.
