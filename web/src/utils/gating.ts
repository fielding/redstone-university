import type { CollectionEntry } from 'astro:content';
import type { CourseNode } from './navigation';

/**
 * Parts whose bodies are published on the site. Everything else stays visible
 * as titles in the sidebar and on the landing page ("in build"), but gets no
 * routes generated — the drafts remain readable in the GitHub repo.
 *
 * To publish a part, add its slug directory here. That's the whole release.
 */
export const LIVE_PARTS = new Set(['part-i--foundations']);

// Local preview of unreleased parts: PREVIEW_ALL_PARTS=true npm run dev
// (never set in CI/production — the gate stays closed for real builds)
const PREVIEW_ALL =
    typeof process !== 'undefined' &&
    process.env?.PREVIEW_ALL_PARTS === 'true';

export function isLiveSlug(slug: string): boolean {
    if (PREVIEW_ALL) return true;
    const head = slug.split('/')[0];
    // Root-level pages (the course introduction) are always live.
    if (!head.startsWith('part-')) return true;
    return LIVE_PARTS.has(head);
}

export function liveEntries(
    entries: CollectionEntry<'course'>[]
): CollectionEntry<'course'>[] {
    return entries.filter((e) => isLiveSlug(e.slug));
}

function firstSlug(node: CourseNode): string | undefined {
    if (node.slug) return node.slug;
    for (const child of node.children) {
        const s = firstSlug(child);
        if (s) return s;
    }
    return undefined;
}

/**
 * Mark gated subtrees in the sidebar hierarchy: their nodes lose their slugs
 * (so nothing links to an unbuilt route) and gain `gated: true` so the
 * sidebar can render them as unlinked "in build" titles.
 */
export function applyGating(nodes: CourseNode[]): CourseNode[] {
    const strip = (n: CourseNode): CourseNode => ({
        ...n,
        slug: undefined,
        gated: true,
        children: n.children.map(strip),
    });

    return nodes.map((node) => {
        const probe = firstSlug(node);
        return probe && !isLiveSlug(probe) ? strip(node) : node;
    });
}
