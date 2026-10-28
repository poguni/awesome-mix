# Awesome Mix 카세트 플레이어

내 PC의 MP3 폴더를 실사풍 카세트 데크(시안 A · Midnight Deck)로 재생하는 브라우저 앱입니다. 요구사항 원본은 `docs/Awesome_Mix_PRD_v2.md`이고, 이 파일은 작업 규칙만 담습니다. 내용이 부딪히면 PRD가 우선합니다.

## 문서 위치

| 파일 | 내용 |
| --- | --- |
| `docs/Awesome_Mix_PRD_v2.md` | 기능·디자인·기술 설계·개발 단계(M0~M6)·수용 기준. 작업 전에 해당 장을 먼저 읽는다 |
| `design/design-A-midnight-deck.html` | 확정 디자인 시안 A. 배치·색·서체·상호작용의 기준(데크·카세트는 CSS로 그린 자리 표시이며, 실제로는 assets 이미지로 바뀐다) |
| `design/image-spec.md` | 실사 이미지 레이어의 제작 규칙과 assets.json 설명 |
| `assets/assets.json` | 이미지 좌표. 사용자가 `tools/calibrate.html`로 만든다 |

## 반드시 지킬 규칙

- 앱 코드는 `index.html` 한 파일(HTML·CSS·JS)에 둔다. 빌드 도구·npm 패키지·프레임워크를 쓰지 않는다.
- 외부 스크립트는 jsmediatags 하나만, cdnjs에서 버전을 고정해 불러온다. 서체는 PRD 5-3의 Google Fonts만 쓴다.
- 색은 PRD 5-2의 CSS 변수 이름(`--bg`, `--panel`, `--accent` …)을 그대로 쓴다.
- 이미지 위치·크기를 코드에 숫자로 적지 않는다. 모두 `assets/assets.json`에서 읽고, 이미지 크기에 대한 %로 바꿔 쓴다(PRD 6-6).
- `assets/` 안의 이미지는 사용자가 직접 다듬은 원본이다. 이름을 바꾸거나 덮어쓰거나 재압축하지 않는다. 이미지 경로는 assets.json에 적힌 값을 그대로 쓴다(PNG일 수도 WebP일 수도 있다).
- 이미지나 assets.json을 불러오지 못하면 시안 A의 CSS 데크로 대체해, 앱이 멈추지 않게 한다.
- 키가 눌린 모습은 이미지를 바꾸지 않고 `keys.pressed` 값(아래로 1.5%, 밝기 0.88)으로 표현한다.
- OpenRouter API 키를 코드·저장소·로그에 넣지 않는다. 사용자가 설정에서 입력한 값을 브라우저(IndexedDB 또는 localStorage)에만 저장한다.
- 영화·제조사의 로고와 상표 이름(예: 소니, 워크맨)을 화면과 코드에 쓰지 않는다.
- 크롬·엣지 전용 API(File System Access)를 쓴다. 다른 브라우저에서는 안내 화면을 보여 준다.
- 모든 조작은 실제 `<button>`·`<input>`으로 만들고, 아이콘 버튼에는 `aria-label`, 토글에는 `aria-pressed`를 붙인다. `prefers-reduced-motion`을 지킨다.

## 실행과 확인

- 실행: 프로젝트 폴더에서 `python3 -m http.server 8000`(Windows는 `python -m http.server 8000`) → `http://localhost:8000`. `file://`로 열면 assets.json을 읽지 못한다.
- 화면 확인: Playwright로 1440×900과 1024×768 화면을 찍어 `design/design-A-midnight-deck.html`과 비교한다. 콘솔 오류가 없어야 한다.
- 테스트 음원: `test-audio/`에 ffmpeg로 만든 짧은 MP3(서로 다른 ID3 태그와 길이)를 둔다. 이 폴더는 git에 올리지 않는다. 실제 음원 파일은 저장소에 넣지 않는다.
- File System Access의 폴더 선택 창은 자동 테스트로 누를 수 없다. 끌어다 놓기와 `<input type="file" multiple>` 경로를 함께 만들어 자동 테스트는 그쪽으로 한다.
- assets.json 점검: 적힌 이미지 파일이 모두 있는지, 좌표가 0으로 비어 있지 않은지 확인하는 스크립트를 M0에서 만든다.

## 작업 방식

- PRD 8장의 단계(M0~M6) 하나씩 진행한다. 시작할 때 무엇을 바꿀지 짧은 계획을 먼저 보여 주고, 끝나면 해당 단계의 "완료 확인"과 9-1 수용 기준 중 관련 항목을 점검해 결과를 알린다.
- 단계가 끝나면 git 커밋을 제안한다(커밋 메시지는 한국어로).
- `index.html` 안의 코드는 PRD 6-1의 구성(Assets, Store, Library, Engine, Deck, Reels, Shelf, Curator)으로 나눠 주석 머리말을 붙인다.
- 사용자와는 한국어 존댓말로 대화하고, 코드 주석도 한국어로 짧게 쓴다.
- PRD와 다르게 구현해야 할 이유가 생기면 먼저 묻고, 합의한 내용은 `docs/Awesome_Mix_PRD_v2.md`에도 반영한다.

## 하지 말 것

- `tools/`의 파일과 `docs/`의 디자인 시안을 앱이 불러오게 만들지 않는다(참고 자료일 뿐이다).
- `assets/_work/`, `assets/_master/`, `tools/out/`, `tools/_preview/`의 파일을 앱에서 쓰지 않는다.
- 음원이나 앨범 아트를 외부 서버로 보내지 않는다. AI 호출에는 곡 메타데이터(텍스트)만 보낸다(PRD 4-1).
