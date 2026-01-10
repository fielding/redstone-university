## Module 1: Speaking in 1s and 0s – The Input Interface

### Module 1 Summary

- **Narrative Beat:** Before we can build a computer, we need a way to talk to it. Our language will be binary, and our input interface will be a set of simple levers.
- **Learning Goals:**
  - Understand binary as a system of on/off switches.
  - Build a physical interface to input binary numbers.
  - Strengthen binary intuition through practice.
- **Lesson Overview:**
    - Lesson 1.1: The Theory – Why Computers Use Binary
    - Lesson 1.2: The Lab – Building Our 4-Bit Input Interface
    - Lesson 1.3: Drills & Games – Strengthening Your Binary Intuition
- **Minecraft Artifact:** A working 4-bit input interface for binary numbers.

---

### Module 1 Introduction

Welcome to your first day at Redstone University!

Our grand adventure is to build a complete, working computer from scratch. But like any great journey, we need to start with the basics. The very first thing we need is a way to talk to our machine. We need a way to give it information.

In this module, we’re going to build a **4-bit input interface**, a simple set of switches that lets us speak the computer’s native language: **binary**. In Minecraft, levers hold their state, making them perfect for this job. By flipping them, we can set a 4-bit binary number (any value from `0` to `15`) and see it in action. This isn’t a true register (a storage device we’ll build later), but it’s a hands-on way to input binary data and understand how computers start processing information. As we move forward, you’ll see how this simple setup connects to the bigger picture.

Let’s get started!

---

### Lesson 1.1: The Theory – Why Computers Use Binary

Think about how you count. You probably use ten symbols: `0`, `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`. This is the **decimal** (base-10) system. It feels natural to us, likely because humans evolved with ten fingers. When we get past `9`, we don't invent a new symbol; we just add a new column to the left, the "tens" column, and start over. The number `12` is really just our way of saying "one ten, plus two ones."

Computers are different. They don't have fingers. Deep down, they are made of billions of microscopic electronic switches called transistors. A switch is a very simple device. It can only ever be in one of two states: **ON** or **OFF**. There is no "halfway on."

This simple, two-state system is the foundation of all modern computing. We call it **binary** (base-2). To represent any piece of information, we just assign a meaning to these two states:

- `OFF` = `0`
- `ON` = `1`

That's it! Every single thing your computer does, from displaying this text, to playing a song, to running a complex game, is ultimately just a massive, coordinated manipulation of these simple `1`s and `0`s. Each individual `1` or `0` is called a **bit** (short for "binary digit").

So, how can we possibly represent a big number like `13` with just `1`s and `0`s? We use the same trick as our decimal system: we use columns with different values. But instead of ones, tens, and hundreds, our binary columns simply double each time.

| Bit Position | `3`   | `2`   | `1`   | `0`   |
|--------------|-----|-----|-----|-----|
| Power of 2   | `2³`  | `2²`  | `2¹`  | `2⁰`  |
| Place Value  | `8`   | `4`   | `2`   | `1`   |
| Binary       | `1`   | `1`   | `0`   | `1`   |

- **Bit Position:** The rightmost bit is position `0`, then `1`, `2`, and so on to the left.
- **Power of 2:** Each position represents a power of `2`.
- **Place Value:** The actual value for each bit.
- **Binary:** The value of each bit for the number `1101`.


To figure out the value of a binary number, you just add up the values of the columns where there is a `1` (or an "ON" switch).

For example, the binary number `1101`:
- Is there a `1` in the `8`s place? **Yes.**
- Is there a `1` in the `4`s place? **Yes.**
- Is there a `1` in the `2`s place? **No.**
- Is there a `1` in the `1`s place? **Yes.**

So, the value is $8 + 4 + 1 = 13$. We've just translated from the computer's language back to ours!

---

### Lesson 1.2: The Lab – Building and Using Our 4-Bit Input Interface

It’s time to stop talking and start building! Our **4-bit input interface** will act as a simple “keyboard,” letting us manually input any number from `0` to `15` in binary. Using levers, we will set the bits by flipping them up for `1` and down for `0`. A simple setup that will enable us to create binary numbers we can see and use.

#### Materials Needed

- 4 standard building blocks<sup>*</sup>
- 4 Levers
- 4 Signs
- 8 Pieces of Redstone Dust

<sup>*You can use any solid block, but for the input interface, I recommend a redstone lamp. It doubles as a visual indicator of the current state of each bit.</sup>

---

This input bus will serve as the starting point for our future circuits. In later modules, we’ll process these binary inputs and display the results on a 7-segment display. This device lights up segments to show numbers, like on a digital clock.

#### The Build Guide

![Minecraft Input Interface](./images/input_minecraft.png)
*Figure: The input interface in Minecraft, set to `0110` (binary for `6`). The levers are flipped to represent the bits, and the dust is connected to the back. Using redstone lamps makes it easy to see the current state of each bit.*

1. I recommend creating a new world and under the advanced options, set the world type to "Flat". They even have a flat preset called "Redstone Ready" that is perfect for our needs.
2. Place **four Redstone Lamps** or **four solid blocks** in a horizontal line with one space between to prevent their redstone dust from merging.
3. On the front face of each block, place one **Lever**. A lever is the perfect physical bit! When it's flipped down, it's `0`. When it's flipped up, it's `1`.
4. Now, let's label our work so we don't get confused. Place a **Sign** on the very top of the block. From **right to left**, label them `1`, `2`, `4`, and `8`. We go right-to-left because, just like in the number `12`, the least valuable digit (the `2`) is on the right. See the schematic, screenshot, or diagram for clarity if needed.
5. Finally, let's wire it up. Go around to the back of your four blocks to the opposite side that you placed the lever. Place a piece or two of **Redstone Dust** on the ground directly behind each one. When you flip a lever, its block becomes powered, which sends a signal to the dust. These four parallel lines of dust are now your official **
4-bit input bus**. A "bus" is just the fancy engineering term for a bundle of wires that carry a complete piece of information.
6. Double-check that your build looks similar to the one in the figure above.


---

Before we test our new input interface, I want to introduce you to the same input interface represented in CircuitVerse, a free online digital logic circuit simulator. Moving forward, every circuit we build will be introduced in theory with the CircuitVerse version first, and then we will build it in Minecraft. This is primarily due to being able to easily represent the circuit in a clear and concise way, something that isn't always possible with Minecraft screenshots. Everything you build is included in the [CircuitVerse project for this course](https://circuitverse.org/users/323134/projects/redstone-university-cafe6ad2-2c4f-41b6-8a91-51fd8fa24698)



#### CircuitVerse Version

![CircuitVerse Input Interface](./images/input_circuitverse.png)
*Figure: The same 4-bit input interface, built in CircuitVerse. It is also set to `0110` (`6` in decimal).*

While it has a few stylistic differences, the concept is exactly the same as our Minecraft build. It's an input interface that allows for input of a 4-bit binary number.

Don't worry, we will be building more interesting circuits very soon.

---

### Lesson 1.3: Drills & Games – Strengthening Your Binary Intuition

Let's get a feel for our new device. Binary feels weird at first, but it will become second nature with just a little practice.

#### Takeaway

Practicing will make binary numbers feel as natural as decimal. The more you practice, the faster you'll get!

#### Drill 1: Binary to Decimal

- **Goal:** What decimal number is `1011`?
- **Action:** Go to your input interface and set the levers: ON, OFF, ON, ON.
- **Calculation:** $8 + 0 + 2 + 1 = 11$. So, `1011` is `11`.

#### Drill 2: Decimal to Binary (The "Greedy" Method)

- **Goal:** Let's represent the number `6`.
- **Thought Process:** Always start with your biggest bit and work your way down.
    1. Is `6` greater than or equal to `8`? **No.** Leave the `8` lever OFF.
    2. Is `6` greater than or equal to `4`? **Yes.** Flip the `4` lever ON. We have $6 - 4 = 2$ left to account for.
    3. Is `2` greater than or equal to `2`? **Yes.** Flip the `2` lever ON. We have $2 - 2 = 0$ left.
    4. Is `0` greater than or equal to `1`? **No.** Leave the `1` lever OFF.
- **Result:** The levers are OFF, ON, ON, OFF, which is the binary number `0110`.

#### The Binary "Game"

While not the ideal version of a game, this is a great way to build speed. Pick a random number between `0` and `15` and see how quickly you can represent it on your input interface. This will burn the powers of two (`1`, `2`, `4`, `8`) into your memory.

---

### Module 1 Checkpoint

#### Practice Problem 1.4.1: Knowledge Check

1. What is the largest number a 5-bit input interface could input? (Hint: The next bit would be the `16`s place).
2. What is the decimal value of the binary number `1100`?
3. How would you represent the number `10` in binary?

<details>
<summary><strong>Show Solution</strong></summary>

1. The largest number a `5`-bit input interface could input is **`31`**. (In binary: `11111`, which is $16 + 8 + 4 + 2 + 1 = 31$.)
2. The decimal value of the binary number `1100` is **`12`**. ($8 + 4 + 0 + 0 = 12$.)
3. The number `10` in binary is **`1010`**. ($8 + 0 + 2 + 0 = 10$.)

</details>

#### Real-World Connection: CPU Registers

Your **4-bit input interface** is a simplified version of how real computers get information from the world. In everyday life, devices like keyboards, mice, and sensors act as input interfaces, turning your actions (like typing or clicking) into binary signals the computer understands. Our Minecraft build uses four levers to input a 4-bit number (`0` to `15`), but imagine scaling that up. Modern computers often handle **64-bit data**, meaning their circuits can process 64 bits at once, enough to represent numbers bigger than `18` quintillion!

Here’s how it connects: once an input device sends binary data, the computer stores it in **registers**, tiny, super-fast storage units inside the CPU. A “64-bit processor” has registers that hold 64 bits, letting it crunch huge numbers or instructions in a single step. Your 4-bit interface is just the beginning, it’s how we “talk” to the machine. Later, we’ll build a register and see how they use that input to make the computer think!

#### Software Connection (LeetCode): Counting Bits

How does a programmer "look at" the individual bits you just set with your levers? They use bitwise operations! This is a sneak peek of what we'll learn in the next modules, but it's too cool not to share.

A classic LeetCode problem is **"Number of 1 Bits"**: count how many `1`s are in a number's binary representation. Programmers solve this by checking each bit of the number one by one. It also gives a sneak peek at the concept of bitwise operations, which are essential for low-level programming and optimization.

```python
def countSetBits(n):
    count = 0
    while n > 0:
        # The '& 1' checks if the last bit is a 1
        if (n & 1) == 1:
            count += 1
        # The '>>= 1' shifts all bits one place to the right
        n >>= 1
    return count

# The binary for 13 is 1101
print(countSetBits(13)) # Output: 3
```

**Software Analogy:** In most programming languages, you can use bitwise operators to manipulate numbers at the binary level. For example, in Python, `n & 1` checks the lowest bit, and `n >>= 1` shifts all bits to the right. This is just like flipping levers and reading wires from your input interface!

#### Key Terms
-   **Binary**: A base-2 number system that uses only two symbols, `0` and `1`, to represent information. It is the fundamental language of all digital computers.
-   **Bit**: A single "binary digit," which can be either a `0` or a `1`. It is the smallest possible unit of data in computing.
-   **Bitwise Operation**: An operation in software that manipulates numbers at the level of their individual bits, rather than their decimal value.
-   **Bus (Input Bus)**: A collection of parallel wires that carry a complete piece of binary information. Our 4-bit input interface creates a 4-bit bus.
-   **Decimal**: The base-10 number system that humans commonly use, with ten unique symbols (`0`-`9`).
-   **Interface (Input Interface)**: A device that allows a user or system to provide information to a machine. Our 4-lever setup is a manual input interface.
-   **Register**: A small, extremely fast storage location inside a computer's central processing unit (CPU) that holds data for immediate use.


### Module 1 Conclusion

Fantastic work! You've now mastered the most fundamental concept in all of computing: how information is physically represented in a binary system. You have a working input device, and you've seen how this physical concept directly connects to both real-world hardware and clever software algorithms.

Your input bus is ready to carry these binary signals to the next stage where logic gates will turn them into calculations and decisions. Now that you’ve built your input interface and practiced working with binary, you’re ready to learn how to manipulate these binary signals in Module 2: The Grammar of Circuits. There, we will build our first logic gates, which will process the inputs you’ve set here into meaningful outputs.

The basic building blocks of our computer are about to take shape. Get ready for the world of logic gates and circuits!
