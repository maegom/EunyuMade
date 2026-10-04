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
  assets/images/  시리즈 대표 이미지 등 (프로젝트 이미지는 src/assets/projects/)
  favicon.png, apple-touch-icon.png
  play/           실행형 페이지 (예: /play/happy-toy, 지금은 링크되지 않음)
  eunyumade.vcf   명함의 "연락처 저장"
apps/
  true-size/      별도 Vercel 프로젝트로 배포하는 실물 크기 스튜디오 (truesize.eunyumade.com)
design/logo-src/  로고 원본 보관 (서빙되지 않음)
```

## 새 프로젝트 추가

`src/content/projects/<slug>.md`를 만듭니다. `title`, `kind`, `one_line`은 필수입니다.
`series`를 쓰면 그 시리즈에 묶이고 주소는 `/<series>/<slug>`, 쓰지 않으면 "그 외"로 분류되어 `/works/<slug>`가 됩니다.

```md
---
title: 말랑멍
series: happy            # 생략하면 "그 외"로 분류
verb: 만지기             # 시리즈 허브에서 이름 위에 붙는 한 단어 (선택)
kind: web                # web | object | installation | experiment
status: idea             # 아직 아이디어뿐이라 목록에서 감추고 싶을 때만 씁니다. 평소에는 이 줄을 빼세요
year: 2026
one_line: 손으로 잡고 늘리는 HAPPY
inputs: 카메라 손 추적
outputs: 캐릭터 변형과 표정
tech: [MediaPipe Hand Landmarker, Canvas]
materials: []            # 실물이면 재료
# 이미지는 여기에 적지 않습니다. 아래 "프로젝트 이미지" 참고.
hero: /assets/images/malangmung/hero.mp4      # 상세 페이지 맨 위를 영상으로 바꾸고 싶을 때만 (선택)
plays:                                        # 체험(실행) 링크. 1개면 "실행하기", 2~3개면 이름별 버튼, 4개 이상이면 상세 페이지로
  - label: 다마고치
    url: https://pocketmung.eunyumade.com/play/   # 다른 도메인이면 새 탭으로 열림
    note: 포켓멍 디바이스를 웹에서 그대로.
  - label: 2인 게임
    url: https://pocketmung.eunyumade.com/co-op/
play_url: /play/malangmung                    # 링크가 하나뿐일 때 쓰는 짧은 형태 (plays와 같이 써도 됨)
featured: true           # 목록 맨 앞의 두 칸짜리 타일. 그 뒤는 시리즈 순서(series 파일의 order) → 프로젝트 order
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

- 이미지는 아래 "프로젝트 이미지" 규칙대로 폴더에 넣기만 하면 됩니다.
- `status: idea`인 프로젝트는 목록에 오르지 않고 시리즈 허브의 "다음 구성원"에만 표시됩니다. 그 밖의 상태는 화면에 표시하지 않습니다.
- 목록의 분류 탭은 시리즈 파일에서 자동으로 만들어집니다. 새 시리즈는 `src/content/series/<slug>.md` 하나면 됩니다.

## 프로젝트 이미지

프로젝트마다 폴더 하나에 두 장을 넣습니다. 폴더 이름은 프로젝트 파일 이름과 같게.

```
src/assets/projects/<slug>/cover.png   정방형 썸네일 (목록 타일, 시리즈 카드)
src/assets/projects/<slug>/main.png    전체 화면 캡처 (상세 페이지 맨 위, 자르지 않고 표시)
```

- PNG, JPG, WebP 모두 됩니다. 원본 그대로 넣어도 빌드할 때 웹용 크기의 WebP로 자동 변환됩니다.
- 설정 줄은 필요 없습니다. 파일을 넣거나 같은 이름으로 덮어쓰고 푸시하면 반영됩니다.
- `cover`가 없으면 이름이 들어간 타일로, `main`이 없으면 `cover`로 대신 보여 줍니다.
- 상세 페이지의 메인 이미지를 누르면 첫 번째 체험 주소가 열립니다.

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
