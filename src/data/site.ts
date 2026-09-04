// 사이트 공통 정보. 주소나 연락처가 바뀌면 이 파일만 고치면 됩니다.
export const site = {
  name: '은유제작소',
  nameEn: 'EUNYU MADE',
  url: 'https://www.eunyumade.com',
  tagline: '상상과 생각, 감정을 실제 경험으로 만듭니다.',
  description:
    '은유제작소 EUNYU MADE. 장난감, 로봇, 게임, 웹, 3D 프린팅으로 생각과 감정을 실제로 만지고 보고 들을 수 있는 경험으로 만드는 제작소.',
  email: 'hoho7013@gmail.com',
  logo: '/assets/logo/eunyu-logo-hand.png',
  ogImage: '/assets/images/happy-project-main.png',
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

export const statusLabel: Record<Status, string> = {
  idea: '아이디어',
  experiment: '실험',
  prototype: '프로토타입',
  making: '제작 중',
  made: '완성',
  exhibited: '전시',
};

export const kindLabel: Record<Kind, string> = {
  web: '웹',
  object: '실물',
  installation: '전시',
  experiment: '실험',
};

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
