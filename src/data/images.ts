// 프로젝트 이미지: src/assets/projects/<slug>/cover.* (정방형 썸네일), main.* (상세 페이지 메인 이미지)
// 파일을 넣기만 하면 빌드할 때 자동으로 찾아서 웹용 크기의 WebP로 변환합니다. 설정 줄은 필요 없습니다.
import type { ImageMetadata } from 'astro';
import { getImage } from 'astro:assets';

const files = import.meta.glob<{ default: ImageMetadata }>(
  '/src/assets/projects/*/*.{png,jpg,jpeg,webp,avif,PNG,JPG,JPEG,WEBP}',
  { eager: true }
);

type Slot = 'cover' | 'main';

function find(slug: string, slot: Slot): ImageMetadata | undefined {
  for (const [path, mod] of Object.entries(files)) {
    const m = path.match(/\/src\/assets\/projects\/([^/]+)\/([^/.]+)\.[a-z]+$/i);
    if (m && m[1] === slug && m[2].toLowerCase() === slot) return mod.default;
  }
  return undefined;
}

export interface BuiltImage { src: string; width: number; height: number }

/** 변환된 이미지 주소와 크기. 파일이 없으면 undefined. */
export async function projectImage(
  slug: string,
  slot: Slot,
  width: number,
  format: 'webp' | 'jpg' = 'webp'
): Promise<BuiltImage | undefined> {
  const raw = find(slug, slot);
  if (!raw) return undefined;
  // 크기는 복제본에서 읽습니다. 원본 객체의 속성을 직접 읽으면 Astro가 원본 파일을
  // "쓰이는 파일"로 보고 몇 MB짜리 원본까지 배포 폴더에 남깁니다.
  const meta: ImageMetadata = (raw as ImageMetadata & { clone?: ImageMetadata }).clone ?? raw;
  const w = Math.min(width, meta.width);
  const img = await getImage({ src: raw, width: w, format, quality: 82 });
  return { src: img.src, width: w, height: Math.round((meta.height / meta.width) * w) };
}
