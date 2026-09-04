import { defineConfig } from 'astro/config';

// 은유제작소 사이트. 정적 생성 → Vercel.
// URL은 경로 기본 (eunyumade.com/happy/malangmung). vercel.json의 cleanUrls와 짝을 이룹니다.
export default defineConfig({
  site: 'https://www.eunyumade.com',
  trailingSlash: 'never',
  build: { format: 'file' },
});
