# 은유제작소 EUNYU MADE 웹사이트 v3

Astro로 정적 생성하고 Vercel에 배포합니다. GitHub `main`에 푸시하면 자동 배포됩니다.

## 구조

```
src/
  content/
    projects/   프로젝트 하나 = 파일 하나 (예: malangmung.md)
    series/     시리즈 하나 = 파일 하나 (예: happy.md)
  data/site.ts  이름, 메일, 로고 경로, 소셜 링크 (비어 있으면 사이트에 표시되지 않음)
  pages/        / (전체 목록), /[series] (시리즈 허브), /[series]/[slug], /works/[slug], /about, /card, 404
  components/ProjectPage.astro   프로젝트 상세 페이지 템플릿
public/
  assets/logo/    eunyu-logo.png (로고), eunyu-mark.png (픽토그램)
  assets/images/  프로젝트 이미지 (<slug>/cover.webp ...)
  favicon.png, apple-touch-icon.png
  play/           실행형 페이지 (예: /play/happy-toy, 지금은 링크되지 않음)
  eunyumade.vcf   명함의 "연락처 저장"
apps/
  true-size/      별도 Vercel 프로젝트로 배포하는 실물 크기 스튜디오 (truesize.eunyumade.com)
design/logo-src/  로고 원본 보관 (서빙되지 않음)
```

## 새 프로젝트 추가

`src/content/projects/<slug>.md`를 만듭니다. `title`, `kind`, `status`, `one_line`은 필수입니다.
`series`를 쓰면 그 시리즈에 묶이고 주소는 `/<series>/<slug>`, 쓰지 않으면 독립 프로젝트로 `/works/<slug>`가 됩니다.

```md
---
title: 말랑멍
series: happy            # 생략하면 독립 프로젝트
verb: 만지기             # 시리즈 허브에서 이름 위에 붙는 한 단어 (선택)
kind: web                # web | object | installation | experiment
status: prototype        # idea | experiment | prototype | making | made | exhibited
year: 2026
one_line: 손으로 잡고 늘리는 HAPPY
inputs: 카메라 손 추적
outputs: 캐릭터 변형과 표정
tech: [MediaPipe Hand Landmarker, Canvas]
materials: []            # 실물이면 재료
cover: /assets/images/malangmung/cover.webp   # 타일과 히어로 이미지
loop: /assets/images/malangmung/loop.mp4      # 3~6초, 소리 없음 (선택)
hero: /assets/images/malangmung/hero.mp4      # 상세 페이지 히어로 영상 (선택)
plays:                                        # 체험(실행) 링크. 1개면 "실행하기", 2~3개면 이름별 버튼, 4개 이상이면 상세 페이지로
  - label: 다마고치
    url: https://pocketmung.eunyumade.com/play/   # 다른 도메인이면 새 탭으로 열림
    note: 포켓멍 디바이스를 웹에서 그대로.
  - label: 2인 게임
    url: https://pocketmung.eunyumade.com/co-op/
play_url: /play/malangmung                    # 링크가 하나뿐일 때 쓰는 짧은 형태 (plays와 같이 써도 됨)
featured: true           # 목록 맨 앞의 두 칸짜리 타일
order: 2                 # 묶음 안 순서
relations:
  - slug: pocketmung
    note: 손 추적이 터치와 자이로로 이어집니다
traces:
  - src: /assets/images/malangmung/trace-01.jpg
    caption: 첫 손 추적 테스트
---
본문은 마크다운으로. 세 문장 이내를 권합니다.
```

- 이미지는 `public/assets/images/<slug>/`에 넣습니다. 커버는 세로가 긴 이미지도 괜찮습니다. 타일이 알아서 가운데를 보여줍니다.
- `status`가 `idea`면 목록에는 오르지 않고 시리즈 허브의 "다음 구성원"에만 표시됩니다.
- 상태는 목록에서 작은 칩으로만 드러납니다. 만드는 중과 완성을 따로 나누지 않습니다.
- 목록의 분류 탭은 시리즈 파일에서 자동으로 만들어집니다. 새 시리즈는 `src/content/series/<slug>.md` 하나면 됩니다.

## 실행형 페이지

브라우저에서 실행되는 것은 `public/play/<slug>/index.html`로 두고, 프로젝트의 `play_url`에 그 주소를 씁니다. 나중에 별도 저장소로 분리해도 `vercel.json`의 rewrite로 같은 주소를 유지할 수 있습니다.

`apps/true-size`는 같은 GitHub 저장소를 사용하는 별도 Vercel 프로젝트입니다. Vercel의 Root Directory를 `apps/true-size`로 지정하고 `truesize.eunyumade.com`을 연결합니다.

## 로컬에서 보기

```bash
npm install
npm run dev
```

## 다른 PC에서 이어서 작업

작업 전 `git pull`, 작업 후 `git add -A && git commit -m "..." && git push`.
