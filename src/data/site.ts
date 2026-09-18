// 사이트 공통 정보. 주소나 연락처가 바뀌면 이 파일만 고치면 됩니다.
export const site = {
  name: '은유제작소',
  nameEn: 'EUNYU MADE',
  url: 'https://www.eunyumade.com',
  tagline: '상상과 생각, 감정을 실제 경험으로 만듭니다.',
  description:
    '은유제작소 EUNYU MADE. 장난감, 로봇, 게임, 웹, 3D 프린팅으로 생각과 감정을 실제로 만지고 보고 들을 수 있는 경험으로 만드는 제작소.',
  email: 'hoho7013@gmail.com',
  logo: '/assets/logo/eunyu-logo.png', // 449×244, 투명 배경
  mark: '/assets/logo/eunyu-mark.png', // 픽토그램 512×512, 투명 배경
  ogImage: '/assets/images/happy/main.webp',
  // 비어 있는 링크는 사이트 어디에도 표시되지 않습니다. 생기는 날 채우면 버튼이 나타납니다.
  links: {
    instagram: 'https://www.instagram.com/eunyumade',
    youtube: '',
    blog: '',
    github: '',
    store: '',
    support: '',
  },
};

export type Status = 'idea' | 'experiment' | 'prototype' | 'making' | 'made' | 'exhibited';
export type Kind = 'web' | 'object' | 'installation' | 'experiment';

// 상태는 살짝만 드러냅니다. 프로토타입과 제작 중은 같은 말로.
export const statusLabel: Record<Status, string> = {
  idea: '아이디어',
  experiment: '실험',
  prototype: '만드는 중',
  making: '만드는 중',
  made: '완성',
  exhibited: '전시',
};

export const kindLabel: Record<Kind, string> = {
  web: '웹',
  object: '실물',
  installation: '전시',
  experiment: '실험',
};

/** 독립 프로젝트의 카테고리 이름 */
export const soloLabel = '독립 프로젝트';

/** 체험(실행) 링크 하나 */
export interface Play { label: string; url: string; note?: string }

/** play_url과 plays를 합쳐 체험 목록으로. play_url이 앞에 옵니다. */
export function getPlays(data: { play_url?: string; plays?: Play[] }): Play[] {
  const list = [...(data.plays ?? [])];
  if (data.play_url && !list.some((p) => p.url === data.play_url)) list.unshift({ label: '실행하기', url: data.play_url });
  return list;
}

/** 다른 도메인(별도 배포 앱)이면 새 탭으로 엽니다. */
export const isExternal = (url: string) => /^https?:\/\//.test(url);

/** 프로젝트 주소: 시리즈가 있으면 /<series>/<slug>, 없으면 /works/<slug> */
export function projectHref(series: string | undefined, id: string): string {
  return series ? `/${series}/${id}` : `/works/${id}`;
}

/** 외부 링크에 QR·명함 유입 표시를 붙입니다. */
export function withSource(url: string, source: string): string {
  try {
    const u = new URL(url);
    u.searchParams.set('utm_source', source);
    return u.toString();
  } catch {
    return url;
  }
}
