import type { CollectionEntry } from 'astro:content';
import type { CourseNode } from './navigation';

/**
 * Parts whose bodies are published on the site. Everything else stays visible
 * as titles in the sidebar and on the landing page (with a status badge), but gets no
 * routes generated; the drafts remain readable in the GitHub repo.
 *
 * To publish a whole part, add its slug directory here.
 */
export const LIVE_PARTS = new Set(['part-i--foundations']);

/**
 * Individual modules released ahead of their part, as
 * "<part-dir>/<module-dir>" slug prefixes. The part's introduction goes
 * live automatically with its first live module (the landing card links
 * to it). To release one module, add its directory here, and that's the
 * whole release.
 */
export const LIVE_MODULES = new Set([
    'part-ii-thinking-machine/05_adder-and-hex',
]);

/**
 * Roadmap badge shown on a part, on the landing page and in the sidebar,
 * keyed by part directory slug. A part with no entry here (e.g. a finished,
 * fully live part) shows no badge.
 */
export const PART_STATUS: Record<string, string> = {
    'part-ii-thinking-machine': 'In progress',
    'part-iii--processor-core': 'Coming soon',
    'part-iv--post-graduate': 'Planned',
};

// Local preview of unreleased parts: PREVIEW_ALL_PARTS=true npm run dev
// (never set in CI/production, where the gate stays closed for real builds)
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
 * sidebar can render them as unlinked titles with a status badge. Recurses so a
 * partially-released part keeps its live modules linked while its unreleased
 * siblings render as titles.
 */
export function applyGating(nodes: CourseNode[]): CourseNode[] {
    const statusFor = (slug?: string): string | undefined => {
        const head = slug?.split('/')[0];
        return head ? PART_STATUS[head] : undefined;
    };

    const strip = (n: CourseNode, inherited?: string): CourseNode => {
        const status = statusFor(n.slug) ?? inherited;
        return {
            ...n,
            slug: undefined,
            gated: true,
            status,
            children: n.children.map((c) => strip(c, status)),
        };
    };

    const anyLive = (n: CourseNode): boolean =>
        (n.slug ? isLiveSlug(n.slug) : false) || n.children.some(anyLive);

    const gate = (n: CourseNode): CourseNode => {
        if (!anyLive(n)) return strip(n);
        const gatedSelf = n.slug !== undefined && !isLiveSlug(n.slug);
        return {
            ...n,
            slug: gatedSelf ? undefined : n.slug,
            gated: gatedSelf || n.gated,
            status: gatedSelf ? statusFor(n.slug) : n.status,
            children: n.children.map(gate),
        };
    };

    return nodes.map(gate);
}
