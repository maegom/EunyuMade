# 은유제작소 EUNYU MADE Website v2

정적 HTML/CSS/JavaScript 기반 사이트입니다.

## 1. `/happy` 주소 사용

루트의 `vercel.json`에 아래 설정이 포함되어 있습니다.

```json
{
  "cleanUrls": true,
  "trailingSlash": false
}
```

Vercel 배포 후:

- `https://www.eunyumade.com/happy.html`
- → `https://www.eunyumade.com/happy`

형태의 깨끗한 URL을 사용할 수 있습니다.

사이트 내부 링크도 `/happy`로 설정되어 있습니다.

## 2. PNG 이미지

SVG 이미지 자산을 제거했습니다.

- 로고: `assets/logo/eunyu-logo.png`
- HAPPY 이미지: `assets/images/happy-project-main.png`
- 프로젝트 자리: `assets/images/project-placeholder.png`
- 실험 이미지: `assets/images/experiment-01.png`
- 실험 이미지: `assets/images/experiment-02.png`

PNG 파일을 같은 파일명으로 덮어써도 되고,
`site-config.js`에서 경로를 변경해도 됩니다.

## 3. 이미지 / 외부 링크 수정

`site-config.js`:

```js
links: {
  happy: "/happy",
  blog: "#",
  instagram: "#",
  youtube: "#",
  github: "#"
}
```

예:

```js
instagram: "https://instagram.com/eunyumade",
youtube: "https://youtube.com/@eunyumade",
github: "https://github.com/계정명",
blog: "https://blog.naver.com/..."
```

## 4. 이메일

현재 이메일:

`eunyumade01@gmail.com`

Footer의 `Email 복사`를 누르면 클립보드에 복사됩니다.

브라우저에서 클립보드 권한을 사용할 수 없는 경우
복사할 수 있는 창이 대신 뜹니다.

## 5. "다음에는 무엇을 만들어볼까요?"

별도의 데이터베이스 서버를 사용하지 않습니다.

입력 후 버튼을 누르면:

1. 사용자의 기본 이메일 앱을 엽니다.
2. 받는 사람은 `eunyumade01@gmail.com`
3. 입력한 아이디어를 이메일 본문에 자동으로 채웁니다.
4. 사용자가 직접 `전송`해야 실제로 은유제작소에 전달됩니다.

사이트나 서버에는 입력 내용이 자동 저장되지 않습니다.

나중에 Google Forms / Formspree / Supabase / 자체 API를 연결하면
사이트에서 바로 수집하도록 변경할 수 있습니다.

## 6. HAPPY 웹 인터랙션

`/happy` 페이지에 세 개의 별도 체험이 있습니다.

### TOUCH — HELLO, HAPPY!
- 웹 로봇이 팔을 위로 회전해 손 내밀기
- 머리를 클릭하거나 쓰다듬기 버튼을 누르면 표정 변화

### PLAY — POCKET HAPPY
- 간식 받기 미니게임
- 화면/버튼 또는 키보드 ← → 조작
- 점수 표시

### FEEL — A DAY WITH HAPPY
- 선택적으로 웹캠 켜기
- 쓰다듬기 / 공 던지기 / 산책
- 모바일 기기에서 지원될 경우 Vibration API 진동
- 웹캠 영상은 브라우저 화면에만 표시하며 업로드하지 않음

## 7. 블로그

메인 페이지의 Making Log를 제거하고 Blog CTA로 변경했습니다.

`site-config.js`:

```js
blog: "블로그 주소"
```

## 8. Vercel 배포

1. 프로젝트 폴더를 GitHub 저장소에 업로드
2. Vercel → Add New Project
3. 저장소 선택
4. Framework Preset: Other
5. 별도 Build Command 없이 배포

`vercel.json`은 프로젝트 루트에 그대로 두세요.
