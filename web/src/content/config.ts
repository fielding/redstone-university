import { defineCollection, z } from 'astro:content';

const courseCollection = defineCollection({
    type: 'content', // v2.5.0+
    schema: z.object({
        title: z.string().optional(),
        // Add other frontmatter properties if they exist in your markdown
    }),
});

export const collections = {
    'course': courseCollection,
};
