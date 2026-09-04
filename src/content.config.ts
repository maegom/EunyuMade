import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const status = z.enum(['idea', 'experiment', 'prototype', 'making', 'made', 'exhibited']);
const kind = z.enum(['web', 'object', 'installation', 'experiment']);

// 프로젝트 하나 = src/content/projects/<slug>.md 파일 하나.
const projects = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/projects' }),
  schema: z.object({
    title: z.string(),
    series: z.string(), // 시리즈 slug (예: happy)
    verb: z.string().optional(), // 시리즈 허브에서 쓰는 상호작용 동사 (예: 만지기)
    kind,
    status,
    year: z.number().optional(),
    one_line: z.string(),
    inputs: z.string().optional(),
    outputs: z.string().optional(),
    tech: z.array(z.string()).default([]),
    materials: z.array(z.string()).default([]),
    cover: z.string().optional(), // /assets/... 정사각형 이미지
    loop: z.string().optional(), // /assets/... 3~6초 루프 영상
    hero: z.string().optional(), // /assets/... 히어로 영상
    play_url: z.string().optional(), // 실행 페이지. 있으면 "실행하기" 버튼
    companion: z.object({ url: z.string(), label: z.string().default('웹에서 흉내낸 것') }).optional(),
    relations: z.array(z.object({ slug: z.string(), note: z.string() })).default([]),
    traces: z.array(z.object({ src: z.string(), caption: z.string().optional() })).default([]),
    featured: z.boolean().default(false),
    order: z.number().default(99),
  }),
});

// 시리즈 하나 = src/content/series/<slug>.md
const series = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/series' }),
  schema: z.object({
    title: z.string(),
    tagline: z.string(),
    description: z.string(),
    cover: z.string().optional(),
    toy_url: z.string().optional(), // 허브의 "만나보기"
    toy_label: z.string().optional(),
    common: z.array(z.string()).default([]),
  }),
});

// 실험 하나 = src/content/lab/<slug>.md
const lab = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/lab' }),
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    kind,
    tags: z.array(z.string()).default([]),
    summary: z.string(),
    cover: z.string().optional(),
    loop: z.string().optional(),
    play_url: z.string().optional(),
    became: z.string().optional(), // 이 실험이 이어진 프로젝트 경로 (예: /happy/malangmung)
  }),
});

export const collections = { projects, series, lab };
