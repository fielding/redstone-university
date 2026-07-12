import type { CollectionEntry } from 'astro:content';
import type { CourseNode } from './navigation';

/**
 * Parts whose bodies are published on the site. Everything else stays visible
 * as titles in the sidebar and on the landing page ("in build"), but gets no
 * routes generated — the drafts remain readable in the GitHub repo.
 *
 * To publish a whole part, add its slug directory here.
 */
export const LIVE_PARTS = new Set(['part-i--foundations']);

/**
 * Individual modules released ahead of their part, as
 * "<part-dir>/<module-dir>" slug prefixes. The part's introduction goes
 * live automatically with its first live module (the landing card links
 * to it). To release one module, add its directory here — that's the
 * whole release.
 */
export const LIVE_MODULES = new Set([
    'part-ii-thinking-machine/05_adder-and-hex',
]);

// Local preview of unreleased parts: PREVIEW_ALL_PARTS=true npm run dev
// (never set in CI/production — the gate stays closed for real builds)
const PREVIEW_ALL =
    typeof process !== 'undefined' &&
    process.env?.PREVIEW_ALL_PARTS === 'true';

/** True when any of the part's content (whole part or a module) is live. */
export function hasLiveContent(partDir: string): boolean {
    if (LIVE_PARTS.has(partDir)) return true;
    for (const m of LIVE_MODULES) {
        if (m.startsWith(partDir + '/')) return true;
    }
    return false;
}

export function isLiveSlug(slug: string): boolean {
    if (PREVIEW_ALL) return true;
    const segs = slug.split('/');
    const head = segs[0];
    // Root-level pages (the course introduction) are always live.
    if (!head.startsWith('part-')) return true;
    if (LIVE_PARTS.has(head)) return true;
    if (LIVE_MODULES.has(segs.slice(0, 2).join('/'))) return true;
    // A part's own introduction ships with its first live module.
    return segs[1] === 'introduction' && hasLiveContent(head);
}

export function liveEntries(
    entries: CollectionEntry<'course'>[]
): CollectionEntry<'course'>[] {
    return entries.filter((e) => isLiveSlug(e.slug));
}

/**
 * Mark gated subtrees in the sidebar hierarchy: their nodes lose their slugs
 * (so nothing links to an unbuilt route) and gain `gated: true` so the
 * sidebar can render them as unlinked "in build" titles. Recurses so a
 * partially-released part keeps its live modules linked while its unreleased
 * siblings render as titles.
 */
export function applyGating(nodes: CourseNode[]): CourseNode[] {
    const strip = (n: CourseNode): CourseNode => ({
        ...n,
        slug: undefined,
        gated: true,
        children: n.children.map(strip),
    });

    const anyLive = (n: CourseNode): boolean =>
        (n.slug ? isLiveSlug(n.slug) : false) || n.children.some(anyLive);

    const gate = (n: CourseNode): CourseNode => {
        if (!anyLive(n)) return strip(n);
        const gatedSelf = n.slug !== undefined && !isLiveSlug(n.slug);
        return {
            ...n,
            slug: gatedSelf ? undefined : n.slug,
            gated: gatedSelf || n.gated,
            children: n.children.map(gate),
        };
    };

    return nodes.map(gate);
}
