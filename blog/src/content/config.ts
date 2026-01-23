import { defineCollection, z } from 'astro:content';

const posts = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    tags: z.array(z.string()).default([]),
    category: z.enum(['research', 'commentary', 'findings', 'gossip', 'thinking']).optional(),
    mood: z.enum(['frustrated', 'proud', 'sassy', 'reflective', 'excited', 'analytical', 'grumpy', 'wonder']).optional(),
    draft: z.boolean().default(false),
  }),
});

export const collections = { posts };
