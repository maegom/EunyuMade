---
title: BOARDROOM
series: studio-tools
verb: 입체로 보기
kind: web
status: made
year: 2026
one_line: KiCad 기판을 3D로 살펴보고 GLB · STEP으로 내보내는 스튜디오
inputs: KiCad PCB 파일 · 부품 STEP 모델(ZIP)
outputs: 3D 미리보기 · GLB · STEP
tech: [KiCad, Three.js, 미니 PC 변환 서버]
order: 3
plays:
  - label: 기판 스튜디오
    url: https://pcb.eunyumade.com/
    note: 샘플 기판(LED와 IC, 64 × 44 mm)으로 먼저 살펴볼 수 있습니다. 변환은 연결된 미니 PC에서 처리됩니다.
---
회로를 물건으로 옮기는 과정의 도구입니다. KiCad 기판 파일을 넣으면 연결된 미니 PC가 3D로 변환하고, 브라우저에서 돌려 보고 확대해 본 뒤 GLB나 STEP으로 내려받아 케이스 설계와 렌더링에 바로 씁니다.

부품의 3D 모델은 파일 지정, 자동 추정, 대체 선택 중에서 고를 수 있고, 별도 모델이 있으면 기판과 함께 ZIP으로 묶어 넣습니다. 기판의 3D 변환과 내보내기까지가 범위이며, 회로 검토나 설계 규칙 검사는 하지 않습니다.
