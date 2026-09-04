# 은유제작소 EUNYU MADE 웹사이트 v3

Astro로 정적 생성하고 Vercel에 배포합니다. GitHub `main`에 푸시하면 자동 배포됩니다.

## 구조

```
src/
  content/
    projects/   프로젝트 하나 = 파일 하나 (예: malangmung.md)
    series/     시리즈 하나 = 파일 하나 (예: happy.md)
    lab/        실험 하나 = 파일 하나
  data/site.ts  이름, 메일, 소셜 링크 (비어 있으면 사이트에 표시되지 않음)
  pages/        / (선반), /[series], /[series]/[slug], /lab, /about, /card, 404
public/
  assets/       이미지, 로고
  play/         실행형 페이지 (예: /play/happy-toy)
  eunyumade.vcf 명함의 "연락처 저장"
```

## 새 프로젝트 추가

1. `src/content/projects/<slug>.md`를 만듭니다. 아래 항목 중 `title`, `series`, `kind`, `status`, `one_line`은 필수입니다.

```md
---
title: 말랑멍
series: happy            # src/content/series/<slug>.md 의 파일명
verb: 만지기             # 시리즈 허브에서 쓰는 동사
kind: web                # web | object | installation | experiment
status: prototype        # idea | experiment | prototype | making | made | exhibited
year: 2026
one_line: 손으로 잡고 늘리는 HAPPY
inputs: 카메라 손 추적
outputs: 캐릭터 변형과 표정
tech: [MediaPipe Hand Landmarker, Canvas]
materials: []            # 실물이면 재료
cover: /assets/images/malangmung/cover.jpg   # 정사각형
loop: /assets/images/malangmung/loop.mp4     # 3~6초, 소리 없음 (선택)
hero: /assets/images/malangmung/hero.mp4     # 히어로 영상 (선택)
play_url: /play/malangmung                   # 실행 페이지가 있으면 "실행하기" 버튼
featured: true           # 선반에서 두 칸짜리 특집
order: 2                 # 시리즈 안 순서
relations:
  - slug: pocketmung
    note: 손 추적이 터치와 자이로로 이어집니다
traces:
  - src: /assets/images/malangmung/trace-01.jpg
    caption: 첫 손 추적 테스트
---
본문은 마크다운으로. 세 문장 이내를 권합니다.
```

2. 이미지는 `public/assets/images/<slug>/`에 넣습니다.
3. 커밋하고 푸시하면 선반, 시리즈 허브, 프로젝트 페이지가 자동으로 생깁니다.

상태의 뜻: 아이디어(허브에만 표시) → 실험 → 프로토타입 → 제작 중 → 완성 → 전시. 선반의 줄은 상태로 정해집니다.

## 실행형 페이지

브라우저에서 실행되는 것은 `public/play/<slug>/index.html`로 두고, 프로젝트의 `play_url`에 그 주소를 씁니다. 나중에 별도 저장소로 분리해도 `vercel.json`의 rewrite로 같은 주소를 유지할 수 있습니다.

## 로컬에서 보기

```bash
npm install
npm run dev
```

## 다른 PC에서 이어서 작업

작업 전 `git pull`, 작업 후 `git add -A && git commit -m "..." && git push`.
