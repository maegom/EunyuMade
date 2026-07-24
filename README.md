# 은유제작소 EUNYU MADE Website

정적 HTML/CSS/JavaScript로 만든 웹사이트입니다.  
Vercel, GitHub Pages, Netlify 등에 그대로 배포할 수 있습니다.

## 파일 구조

- `index.html` : 메인 홈페이지
- `happy.html` : HAPPY 프로젝트 상세 + 웹 미니 인터랙션
- `image-guide.html` : 이미지/링크 교체 가이드
- `site-config.js` : **이미지 경로, SNS 링크, 로고 경로를 한 곳에서 관리**
- `styles.css` : 전체 디자인
- `script.js` : 공통 메뉴/설정 적용
- `happy.js` : HAPPY 웹 인터랙션
- `assets/logo/eunyu-logo.svg` : 임시 로고
- `assets/images/happy-project-main.png` : 현재 첨부한 HAPPY 이미지

## 가장 먼저 수정할 곳

### 1. 로고 교체
원하는 로고 파일을 `assets/logo/` 폴더에 넣고  
`site-config.js`의 아래 경로를 변경합니다.

```js
logo: "assets/logo/내로고.png"
```

또는 기존 `eunyu-logo.svg` 파일을 같은 이름으로 덮어써도 됩니다.

### 2. HAPPY 대표 이미지
현재 첨부 이미지를 기본값으로 넣어두었습니다.

```js
happyMain: "assets/images/happy-project-main.png"
```

다른 이미지를 넣고 경로만 바꾸면 메인과 HAPPY 상세 페이지에 동시에 반영됩니다.

외부 이미지 주소도 가능합니다.

```js
happyMain: "https://example.com/happy.jpg"
```

### 3. Instagram / YouTube / GitHub
`site-config.js`의 `links`를 수정하세요.

```js
instagram: "https://instagram.com/...",
youtube: "https://youtube.com/...",
github: "https://github.com/...",
email: "mailto:..."
```

## HAPPY 웹 인터랙션

`happy.html`의 "웹에서도 해피와 잠깐 놀아보세요" 영역에 간단한 인터랙션이 있습니다.

- 마우스를 해피에게 가까이 이동 → 해피가 반응
- 공 드래그 → 공놀이
- 쓰다듬기 / 간식 / 산책 버튼

현재는 외부 라이브러리 없이 CSS + JS로 만든 가벼운 프로토타입입니다.
나중에 실제 캐릭터 이미지, Canvas, Phaser, Three.js 등으로 교체할 수 있습니다.

## Vercel 배포

1. 이 폴더 전체를 GitHub 저장소에 업로드
2. Vercel → Add New Project
3. 해당 GitHub 저장소 선택
4. Framework Preset: `Other`
5. Build Command: 비워두기
6. Output Directory: 비워두기
7. Deploy

## 로컬 실행

파일을 더블클릭해도 기본 화면은 열리지만, 브라우저 보안정책 때문에 로컬 서버 사용을 권장합니다.

Python:
```bash
python -m http.server 8000
```

브라우저에서:
`http://localhost:8000`

## 디자인 컨셉

- 베이지 / 크림 기반
- 브라운 텍스트
- 따뜻한 오렌지 포인트
- HAPPY 프로젝트는 밝은 자연색과 섞어 사용
- 메인 Hero는 정적이며, 인터랙션은 프로젝트 안에서만 사용
