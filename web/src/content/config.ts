import { defineCollection, z } from 'astro:content';

const courseCollection = defineCollection({
    type: 'content', // v2.5.0+
    // The course markdown has no frontmatter: the PDF build concatenates raw
    // file bodies, so a YAML block would render into the book. Page titles come
    // from utils/titles.ts instead.
    schema: z.object({
        title: z.string().optional(),
    }),
});

export const collections = {
    'course': courseCollection,
};
