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
> The foundational section of the course, **Part I: The Foundations – The Human Interface**, is now complete and ready for you to explore. My goal is to make this the best possible resource it can be, and your feedback is a critical part of that process.
>
> Please feel free to dive in, try the builds, and read through the lessons. If you find a typo, have a suggestion, or think a concept is unclear, please **[open an issue on GitHub](https://github.com/fielding/redstone-university/issues)**. All feedback is extremely valuable.
>
> *The rest of the course (Parts II, III, and IV) is currently in active development.*

---

## About The Project

Have you ever used a computer and wondered what’s *really* happening inside? Not just the software, but the deep, physical magic behind it all?

**Redstone University** is a journey into the heart of the machine. This project provides a complete, university-level curriculum for learning computer architecture from first principles. But instead of abstract Hardware Description Languages and simulators, our campus is the world of Minecraft. We will make the abstract tangible, turning theory into a physical, working machine that you can walk around inside of.

As a self-taught computer engineer, I found myself wanting to explore the foundational principles of computer science. The initial spark for this project, however, came from wanting to build something that could share these incredible ideas with my daughter, Ada. Ada introduced me to Minecraft when she was not even 2 years old, and we've been building together ever since. I realized that the abstract concepts of binary, bitwise operations, logic gates, and computer architecture are sometimes introduced in ways that make them feel very intangible. At the same time, I saw the incredibly complex and logical machines being built in Minecraft with Redstone. The idea was born: **what if we could learn these concepts in a tangible way, by building a computer from scratch, using tools we already love?**

That is the mission of Redstone University.

### Who Is This For?

This course is for the curious. It's for:
-   **My daughter, Ada**, for whom this project was first imagined.
-   **Students and kids** who want a fun, hands-on introduction to STEM and computer science.
-   **University CS students** who want a physical way to visualize the concepts from their "Computer Architecture" class.
-   **Self-taught programmers and professionals** who want to solidify their understanding of what's happening at the hardware level.

---

## Course Structure & Curriculum

This course is structured as a complete curriculum, taking you from zero knowledge to a fully functional, programmable 4-bit computer. We will follow a clear, logical path, broken into four distinct parts:

-   **Part I: The Foundations – The Human Interface.** We will begin by building the essential input/output system. We'll learn the language of binary, master the grammar of Boolean logic, and construct a manual input panel and a 7-segment digital display.

-   **Part II: The Thinking Machine – Building the Processor.** Here, we will construct the entire mathematical and logical brain of our computer. We'll engineer an adder and subtractor, give it the ability to make decisions with comparators and status flags, and forge everything into a complete Arithmetic Logic Unit (ALU).

-   **Part III: The Automated Computer – Memory and Control.** In this final core part, we will achieve true automation across Modules 10–12b. We'll build registers and addressable RAM to give our processor a memory, then add the clocking, routing, and control logic that let it fetch, decode, and execute instructions from a stored program.

-   **Part IV: Post-Graduate Studies (Bonus Content).** For those who want to go even further, Module 13 explores advanced topics, including the hardware required to display multi-digit decimal numbers just like a real-world calculator.

The current outline includes 13 numbered modules, with Module 12 intentionally split into **12a** (clock, counter, and control paths) and **12b** (instructions and the first program). Please see `curriculum.md` for the full module-by-module outline and `structure.md` for details on how the course is organized.

---


## Contributing

Contributions are what make the open-source community such an amazing place to learn and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion to improve a lesson, fix a typo, or correct a circuit diagram, please feel free to fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

Please see [contributing.md](.github/CONTRIBUTING.md) for more details.

---

## License

This project is dual-licensed to ensure it remains a free educational resource while protecting the creator's rights.

#### Course Content
The educational content of this course, including all Markdown files (`.md`), images, diagrams, and assets, is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0)](http://creativecommons.org/licenses/by-nc-sa/4.0/).

<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a>

This means you are free to share and adapt the material for **non-commercial** purposes, as long as you give appropriate credit and distribute your contributions under the same license.

#### Software
All source code in this repository, such as the build script, is licensed under the [MIT License](LICENSE). You are free to use, modify, and distribute this code for any purpose.
