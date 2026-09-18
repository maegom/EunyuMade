---
title: 실물 크기 스튜디오
series: studio-tools
verb: 맞추기
kind: web
status: made
year: 2026
one_line: 모니터를 실제 자로 보정해 이미지를 정확한 실물 크기로 보여주는 웹 도구
inputs: 실제 자, 모니터 보정값, 이미지
outputs: mm 단위 실물 크기 미리보기
tech: [HTML, CSS, JavaScript, File API, Fullscreen API]
materials: []
play_url: https://truesize.eunyumade.com
featured: false
order: 1
---
화면의 픽셀과 물리적인 길이가 어긋나는 문제에서 시작했습니다. 실제 자로 50·100·150 mm 기준선을 보정하면, 불러온 이미지를 원하는 mm 크기로 놓고 움직이며 확인할 수 있습니다.

이미지 파일과 보정값은 사용자의 브라우저 안에서만 다룹니다.
