import type { CollectionEntry } from 'astro:content';

export type CourseNode = {
    title: string;
    slug?: string;
    children: CourseNode[];
    order: number;
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

function getOrder(segment: string): number {
    // Extract number from "01_Name" or "Part-I"
    const match = segment.match(/^(\d+)_/);
    if (match) return parseInt(match[1], 10);

    if (segment.startsWith('Part-I-')) return 1;
    if (segment.startsWith('Part-II-')) return 2;
    if (segment.startsWith('Part-III-')) return 3;
    if (segment.startsWith('Part-IV-')) return 4;
    if (segment === 'introduction') return 0;

    return 999;
}

function formatTitle(segment: string): string {
    // Remove "01_" prefix and replace dashes with spaces
    return segment.replace(/^\d+_/, '').replace(/-/g, ' ');
}
