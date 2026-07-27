/**
 * Human titles for the course pages, keyed by content-collection slug.
 *
 * The markdown under `src/` deliberately carries no frontmatter: the PDF
 * pipeline concatenates raw file bodies, so a YAML block would render into the
 * book. Without it the site has only directory names to work from, and those
 * slugify down to fragments like "input register". This map is the site-side
 * substitute, and it lives here rather than in the content so the PDF build
 * stays untouched.
 *
 * `title` mirrors the file's own first `## ` heading, verbatim. It is what the
 * document title, the link-preview card, and the in-page heading agree on.
 * `navLabel` is the short form for the 280px sidebar column and the pager.
 */
export type CourseTitle = {
    /** Short form for the sidebar and the prev/next pager. */
    navLabel: string;
    /** Full heading, verbatim from the file's first `## `. */
    title: string;
};

export const COURSE_TITLES: Record<string, CourseTitle> = {
    'introduction': {
        navLabel: 'Welcome',
        title: 'Welcome to Redstone University!',
    },

    // ── Part I: The Foundations ──
    'part-i--foundations/introduction': {
        navLabel: 'Part I: The Foundations',
        title: 'Part I: The Foundations – Laying the Groundwork',
    },
    'part-i--foundations/00_prelude-the-redstone-toolkit/draft': {
        navLabel: 'Module 0: The Redstone Toolkit',
        title: 'Module 0: The Redstone Toolkit – Orientation Day (Optional)',
    },
    'part-i--foundations/01_input-register/draft': {
        navLabel: 'Module 1: The Input Interface',
        title: 'Module 1: Speaking in 1s and 0s – The Input Interface',
    },
    'part-i--foundations/02_the-grammar-of-circuits/draft': {
        navLabel: 'Module 2: The Grammar of Circuits',
        title: 'Module 2: The Grammar of Circuits – Foundational Logic Gates',
    },
    'part-i--foundations/03_the-art-of-logic/draft': {
        navLabel: 'Module 3: The Art of Logic',
        title: 'Module 3: The Art of Logic – Simplification and Special Gates',
    },
    'part-i--foundations/03b_interlude-compact-design-final/draft': {
        navLabel: 'Interlude I: Compact Design',
        title: 'Interlude I: The Art of Compact Design (Optional)',
    },
    'part-i--foundations/04_decoders-and-displays/draft': {
        navLabel: 'Module 4: Decoders and Displays',
        title: 'Module 4: From Binary to Pictures: Building a Digital Display',
    },
    'part-i--foundations/04b_interlude-power-of_abstraction/draft': {
        navLabel: 'Interlude II: The Power of Abstraction',
        title: 'Interlude II: The Power of Abstraction in Practice – Engineering with Black Boxes (Optional)',
    },

    // ── Part II: The Thinking Machine ──
    'part-ii-thinking-machine/introduction': {
        navLabel: 'Part II: The Thinking Machine',
        title: 'Part II: The Thinking Machine – Building the Processor',
    },
    'part-ii-thinking-machine/05_adder-and-hex/draft': {
        navLabel: 'Module 5: The 4-Bit Adder',
        title: 'Module 5: The 4-Bit Adder & the Hexadecimal Upgrade',
    },
    'part-ii-thinking-machine/06_advanced-arithmetic/draft': {
        navLabel: 'Module 6: Advanced Arithmetic',
        title: 'Module 6: Advanced Arithmetic – Overflow and Subtraction',
    },
    'part-ii-thinking-machine/07_comparators-and-flags/draft': {
        navLabel: 'Module 7: Comparators and Flags',
        title: 'Module 7: Comparators and Status Flags – The Dawn of Decision-Making',
    },
    'part-ii-thinking-machine/08_the-multiplexer/draft': {
        navLabel: 'Module 8: The Multiplexer',
        title: 'Module 8: The Multiplexer – The Digital Switch',
    },
    'part-ii-thinking-machine/09_the-alu/draft': {
        navLabel: 'Module 9: The ALU',
        title: 'Module 9: The ALU – The Grand Assembly',
    },

    // ── Part III: The Processor Core ──
    'part-iii--processor-core/introduction': {
        navLabel: 'Part III: The Processor Core',
        title: 'Part III: The Processor Core – Memory and Control',
    },
    'part-iii--processor-core/10_processor-scratchpad/draft': {
        navLabel: 'Module 10: Building a Register',
        title: "Module 10: The Processor's Scratchpad – Building a Register",
    },
    'part-iii--processor-core/11_addressable-storage/draft': {
        navLabel: 'Module 11: Addressable Storage',
        title: 'Module 11: Addressable Storage – Building RAM',
    },
    'part-iii--processor-core/12a_infrastructure-clock-counter-and-control-paths/draft': {
        navLabel: 'Module 12a: The Infrastructure',
        title: 'Module 12a: The Infrastructure – Clock, Counter, and Control Paths',
    },
    'part-iii--processor-core/12b_the-language-of-the-machine-and-the-first-program/draft': {
        navLabel: 'Module 12b: The Language of the Machine',
        title: 'Module 12b: The Language of the Machine – Instructions and the First Program',
    },

    // ── Part IV: Post-Graduate Studies ──
    'part-iv--post-graduate/introduction': {
        navLabel: 'Part IV: Post-Graduate Studies',
        title: 'Part IV: Post-Graduate Studies – Advanced Engineering',
    },
    'part-iv--post-graduate/13_double-dabble/draft': {
        navLabel: 'Module 13: Double Dabble',
        title: 'Module 13: The "Real World" Display – The Double Dabble Algorithm',
    },
    'part-iv--post-graduate/99_graduation/draft': {
        navLabel: 'Graduation',
        title: 'Graduation: Beyond Redstone University',
    },
};
