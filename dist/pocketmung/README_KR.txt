POCKETMUNG / HAPPY PLAY 상세 Blender 모델

파일 구성
- PocketMung_HappyPlay_Detailed.blend : 기본 레퍼런스 외관 + 숨김 생산형/내부 구조
- PocketMung_reference_assembly.glb : 첨부 이미지에 가까운 깨끗한 외관
- PocketMung_production_assembly.glb : 디스플레이/USB-C/전원 버튼/스피커 홀 버전
- stl/*.stl : 파트별 3D 프린팅 파일
- preview_*.png : 정면/후면/측면/상단/아이소메트릭 렌더

주요 치수
- 본체: 78.0 x 42.0 x 96.0 mm
- 귀 포함 높이: 약 122.5 mm
- 기본 벽 두께: 2.4 mm
- 전후면 분할 간격: 0.55 mm

Blender에서
1. 01_REFERENCE_ASSEMBLY가 기본으로 보입니다.
2. Outliner에서 01을 끄고 02_PRODUCTION_VARIANT를 켜면 실제 디바이스용 버전이 보입니다.
3. 03_INTERNALS에서 PCB/LCD/배터리 자리와 나사 보스를 확인할 수 있습니다.
4. Text Editor의 SOURCE_build_pocketmung.py에서 파라미터를 바꿔 다시 생성할 수 있습니다.

주의
첨부 이미지에서 외형 비율을 추정해 만든 콘셉트 모델입니다. 실제 출력 전에 Waveshare 보드, 배터리, USB-C 및 체결 부품을 캘리퍼스로 실측해 최종 치수를 조정해야 합니다.
