import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const status = z.enum(['idea', 'experiment', 'prototype', 'making', 'made', 'exhibited']);
const kind = z.enum(['web', 'object', 'installation', 'experiment']);

// 프로젝트 하나 = src/content/projects/<slug>.md 파일 하나.
// series가 있으면 /<series>/<slug>, 없으면 독립 프로젝트로 /works/<slug>.
const projects = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/projects' }),
  schema: z.object({
    title: z.string(),
    series: z.string().optional(), // 시리즈 slug (예: happy). 없으면 독립 프로젝트
    verb: z.string().optional(), // 시리즈 허브에서 쓰는 한 단어 (예: 만지기)
    kind,
    status,
    year: z.number().optional(),
    one_line: z.string(),
    inputs: z.string().optional(),
    outputs: z.string().optional(),
    tech: z.array(z.string()).default([]),
    materials: z.array(z.string()).default([]),
    cover: z.string().optional(), // /assets/... 타일과 히어로에 쓰는 이미지
    loop: z.string().optional(), // /assets/... 3~6초 루프 영상 (호버 시 재생)
    hero: z.string().optional(), // /assets/... 상세 페이지 히어로 영상
    play_url: z.string().optional(), // 실행 페이지 하나. 있으면 "실행하기" 버튼
    // 체험이 여러 개면 여기에. 첫 항목이 목록 타일의 "실행하기" 버튼이 됩니다.
    plays: z.array(z.object({ label: z.string(), url: z.string(), note: z.string().optional() })).default([]),
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
    cover: z.string().optional(), // 허브 대표 이미지
    common: z.array(z.string()).default([]),
    order: z.number().default(99),
  }),
});

export const collections = { projects, series };
