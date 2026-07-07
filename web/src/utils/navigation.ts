import type { CollectionEntry } from 'astro:content';

export type CourseNode = {
    title: string;
    slug?: string;
    children: CourseNode[];
    order: number;
    /** True when the node belongs to an unpublished part (see utils/gating). */
    gated?: boolean;
};

export function buildCourseHierarchy(entries: CollectionEntry<'course'>[]): CourseNode[] {
    const root: CourseNode = { title: 'Root', children: [], order: 0 };

    // Helper to find or create a node
    const findOrCreateNode = (parent: CourseNode, title: string, order: number = 999) => {
        let node = parent.children.find(n => n.title === title);
        if (!node) {
            node = { title, children: [], order };
            parent.children.push(node);
        }
        // Update order if we found a more specific one
        if (order < node.order) node.order = order;
        return node;
    };

    for (const entry of entries) {
        const parts = entry.slug.split('/');
        let currentNode = root;

        // Handle root-level files (like introduction.md)
        if (parts.length === 1) {
            const title = entry.data.title || formatTitle(parts[0]);
            currentNode.children.push({
                title,
                slug: entry.slug,
                children: [],
                order: getOrder(parts[0])
            });
            continue;
        }

        // Handle nested files
        for (let i = 0; i < parts.length; i++) {
            const part = parts[i];
            const isLast = i === parts.length - 1;

            if (isLast) {
                // It's a file (lesson or intro)
                // If it's "introduction" or "draft", it belongs to the parent folder
                if (part === 'introduction' || part === 'draft') {
                    currentNode.slug = entry.slug;
                    // If the parent didn't have a title from a folder name, use the entry title
                    if (entry.data.title) currentNode.title = entry.data.title;
                } else {
                    // It's a regular lesson file
                    currentNode.children.push({
                        title: entry.data.title || formatTitle(part),
                        slug: entry.slug,
                        children: [],
                        order: getOrder(part)
                    });
                }
            } else {
                // It's a folder (Part or Module)
                currentNode = findOrCreateNode(currentNode, formatTitle(part), getOrder(part));
            }
        }
    }

    // Recursive sort
    const sortNodes = (nodes: CourseNode[]) => {
        nodes.sort((a, b) => a.order - b.order);
        nodes.forEach(n => sortNodes(n.children));
    };
    sortNodes(root.children);

    return root.children;
}

export type CourseLink = { title: string; slug: string };

/**
 * Flatten the course hierarchy into the linear reading order shown in the
 * sidebar (depth-first, parents before their children), keeping only nodes
 * that point at a real page. Used to compute prev/next pager links.
 */
export function flattenCourse(nodes: CourseNode[]): CourseLink[] {
    const out: CourseLink[] = [];
    const walk = (ns: CourseNode[]) => {
        for (const n of ns) {
            if (n.slug) out.push({ title: n.title, slug: n.slug });
            if (n.children.length) walk(n.children);
        }
    };
    walk(nodes);
    return out;
}

function getOrder(segment: string): number {
    // Extract number + optional letter suffix from "01_Name" or "03b_Interlude-..."
    // So 3.0 < 3.1 (03a) < 3.2 (03b) < 4.0 etc.
    const match = segment.match(/^(\d+)([a-z]?)_/);
    if (match) {
        const num = parseInt(match[1], 10);
        const letter = match[2];
        const letterOffset = letter
            ? (letter.charCodeAt(0) - 'a'.charCodeAt(0) + 1) * 0.1
            : 0;
        return num + letterOffset;
    }

    // Slugs are lowercased by Astro (e.g. "part-iii--processor-core"), so match
    // case-insensitively. Order longest/most-specific first: "part-iii" must be
    // tested before "part-i" since the latter is a prefix of the former.
    const seg = segment.toLowerCase();
    if (seg.startsWith('part-iv-')) return 4;
    if (seg.startsWith('part-iii-')) return 3;
    if (seg.startsWith('part-ii-')) return 2;
    if (seg.startsWith('part-i-')) return 1;
    if (seg === 'introduction') return 0;

    return 999;
}

function formatTitle(segment: string): string {
    // Remove leading "01_" or "03b_" prefix, drop trailing "-final" / "-draft",
    // convert any remaining dashes or underscores to spaces.
    return segment
        .replace(/^\d+[a-z]?_/, '')
        .replace(/[-_](final|draft)$/i, '')
        .replace(/[-_]/g, ' ');
}
