# Contributing to Redstone University

First off, thank you for considering contributing! This project is a labor of love, and every contribution, no matter how small, helps make it a better resource for everyone.

## How Can I Contribute?

There are many ways you can help!

### 🐛 Reporting Bugs & Typos
If you find a mistake in the lesson text, a typo, or a circuit that doesn't work as described, please [open an issue](https://github.com/fielding/redstone-university/issues)!
*   Please provide a clear title and a detailed description of the problem.
*   If it's a circuit bug, include a screenshot or a description of the expected vs. actual behavior.

### ✨ Suggesting Enhancements
Have an idea for a new challenge, a clearer explanation, or a better circuit design? I'd love to hear it! Please [open an issue](https://github.com/fielding/redstone-university/issues) to start a discussion.

### 📥 Submitting Changes (Pull Requests)
If you'd like to directly fix a typo or make an improvement yourself, that's fantastic! Please follow these steps:
1.  **Fork the repository** to your own GitHub account.
2.  **Create a new branch** for your changes (`git checkout -b feature/MyAmazingIdea` or `fix/CorrectTypo`).
3.  **Make your changes** in your branch.
4.  **Commit your changes** with a clear commit message (`git commit -m 'Fix: Corrected typo in Module 2'`).
5.  **Push to your branch** (`git push origin feature/MyAmazingIdea`).
6.  **Open a Pull Request** back to this repository.

### Local Development Dependencies
Most contributors only need a text editor: the course content lives in Markdown under `src/`, and the Python scripts in `scripts/` use only the Python standard library. A `requirements.txt` file is included for tooling compatibility, but installing it is intentionally a no-op.

If you want to run the optional local build pipeline yourself:
1. Use Python 3.10 or newer.
2. Run `python -m pip install -r requirements.txt` (there are no external Python packages to install).
3. Run the content build scripts from the repository root, for example `python scripts/publish.py`.

The Astro web preview under `web/` has its own Node dependencies. Run `npm install` from `web/` before using `npm run dev` or `npm run build`.

### Style Guide
To ensure all course content is consistent, professional, and easy to follow, we have a detailed style guide. It covers everything from heading levels and formatting to the tone of the course.

**➡️ Please read the full [Style Guide](STYLE_GUIDE.md) before making any content changes.**

## Code of Conduct
To ensure this is a welcoming and inclusive space for everyone, this project adheres to a Code of Conduct. Please read it [here](CODE_OF_CONDUCT.md).

Thank you again for your help!
