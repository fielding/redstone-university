// @ts-check
import { defineConfig, passthroughImageService } from 'astro/config';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

// Serve images un-optimized in dev so replaced figures show immediately
// (Astro's image optimizer caches aggressively and made updated renders/
// diagrams appear stale). Production builds still optimize.
const dev = process.argv.includes('dev');

// https://astro.build/config
export default defineConfig({
  prefetch: {
    prefetchAll: true,
    defaultStrategy: 'hover',
  },
  ...(dev ? { image: { service: passthroughImageService() } } : {}),
  // dev only: tell the browser never to cache responses, so replaced figures
  // always refetch (the optimized image URL is unchanged when dimensions match,
  // which otherwise serves a stale cached copy).
  ...(dev ? { vite: { server: { headers: { 'Cache-Control': 'no-store' } } } } : {}),
  markdown: {
    remarkPlugins: [remarkMath],
    rehypePlugins: [rehypeKatex],
    // Light Shiki theme: the default (github-dark) writes per-token inline colors
    // tuned for a dark background, which are near-invisible on our light code bg.
    shikiConfig: { theme: 'github-light' },
  },
});
