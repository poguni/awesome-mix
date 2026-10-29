# Awesome Mix 실사 이미지 제작 명세 (시안 A · Nano Banana)

작성일: 2026-10-28

## 1. 개요

시안 A(Midnight Deck)를 실사풍으로 바꾸려면 AI 이미지 6장(선택 3장 추가)이 필요합니다. 릴 회전, 감긴 테이프, LCD, 유리 반사광, 그림자, 키가 눌리는 모습은 코드로 그립니다.

| 항목 | 내용 |
| --- | --- |
| 기준 디자인 | 시안 A · Midnight Deck(무광 그래파이트 본체, 호박색 LCD, 주황 PLAY 키, 주황 폼 헤드폰) |
| 생성 도구 | OpenRouter API(gen.py, 기본 2K) 또는 Gemini 앱 무료 등급(최대 약 1K) |
| 작업 흐름 | 1024px로 생성 → Upscayl로 2배 확대 → 배경 제거 → 창 부분 오려내기 → WebP 내보내기 |
| 예상 생성 수 | 필수 6장 × 재시도 3~4회 = 약 20장 |
| 표시 크기 | 데크 본체는 화면에서 최대 가로 1024px, 이미지는 그 2배(2048px)로 준비 |

### 전제

- 프롬프트는 영어로 씁니다. 제품 사진 용어는 영어일 때 결과가 더 안정적입니다.
- 비율은 프롬프트 문장("4:3 aspect ratio")으로 지정합니다.
- 무료 등급 이미지에는 오른쪽 아래에 보이는 워터마크가 붙을 수 있습니다. 모든 프롬프트에 넓은 여백을 요청해, 워터마크가 지울 배경 위에 떨어지게 합니다.
- 소니·워크맨의 이름, 로고, 대표 모델 외형은 쓰지 않고 "1980년대 휴대용 카세트 플레이어"라는 일반 표현만 씁니다.

## 2. 레이어 구조

플레이어는 "빈 카세트 칸 → 카세트 → 덮개" 순서로 쌓습니다. 덮개를 CSS 3D로 열고 닫아서 실제로 카세트를 꽂는 장면을 만듭니다. 표는 아래(뒷면)부터 위(앞면) 순서입니다.

| 순서 | 레이어 | 만드는 방법 | 움직임 |
| --- | --- | --- | --- |
| 1 | 데크 본체 + 빈 카세트 칸(`deck-bay`) | AI 이미지 | 고정 |
| 2 | 감긴 테이프 덩어리 2개 | 코드(CSS 동심원 질감), 선택적으로 `tape-pack-texture` | 남은 시간에 따라 크기 변화 |
| 3 | 릴 허브 2개 | 코드(SVG), 선택적으로 `cassette-hub` | 재생 중 회전 |
| 4 | 카세트 셸(`cassette-shell`, 창·허브 구멍 투명) | AI 이미지 | 넣기·꺼내기 때 아래로 미끄러짐 |
| 5 | 라벨 종이(`cassette-label`) | AI 이미지 + 색 띠·손글씨는 코드 | 테이프마다 제목·색 변경 |
| 6 | 카세트 창 유리 | 코드(반투명 레이어) | 고정 |
| 7 | 덮개 테두리(`deck-lid`, 창 부분 투명) | AI 이미지에서 오려냄 | `rotateX`로 열림·닫힘 |
| 8 | 덮개 유리 반사광 | 코드(`mix-blend-mode: screen`) | 덮개와 함께 회전 |
| 9 | LCD 창 내용 | 코드(텍스트) | 곡 정보 표시 |
| 10 | 키 4개(`keys-up`에서 `prep.py`로 자동 자름) | AI 이미지 1장 | 누르면 코드로 아래로 1.5% 이동하고 조금 어두워짐 |
| 11 | 헤드폰(`headphones`) | AI 이미지 | 고정(재생 중 아주 약하게 흔들림) |
| 12 | 바닥 그림자 | 코드(`filter: drop-shadow`) | 카세트를 넣으면 진해짐 |

### 키가 눌리는 모습(코드)

눌린 상태 이미지를 따로 만들지 않고, 올라온 상태 이미지 하나를 코드로 바꿉니다. 같은 이미지를 쓰므로 위치가 어긋날 일이 없습니다.

- 아래로 이동: `transform: translateY(1.5%)`(키 높이의 1.5%)
- 어둡게: `filter: brightness(0.88)`
- 그림자 줄이기: 키 아래 `drop-shadow`를 올라온 상태의 절반으로
- 전환 시간: 누를 때 0.06초, 튀어오를 때 0.12초

### 카세트 넣기 연출

1. EJECT를 누르면 덮개가 아래쪽 경첩을 축으로 35도 앞으로 열린다(0.35초, "철컥" 소리).
2. 선반의 테이프를 고르면 카세트가 위에서 내려와 칸에 자리 잡는다(0.4초).
3. 덮개가 닫히고 "딱" 소리가 난 뒤 PLAY를 누를 수 있다.

덮개가 열린 모습을 따로 생성하지 않고 CSS 3D 회전으로 처리하므로, 이미지 수가 줄고 레이어끼리 어긋날 일이 없습니다.

## 3. 공통 규칙

모든 이미지는 같은 카메라, 같은 조명, 같은 배경으로 만듭니다. 하나라도 다르면 겹쳤을 때 합성한 티가 납니다.

| 항목 | 규칙 |
| --- | --- |
| 시점 | 정면 정투영(기울기 0도), 망원 렌즈 느낌으로 원근 왜곡 없음 |
| 조명 | 왼쪽 위 45도에서 부드러운 소프트박스, 오른쪽에 약한 보조광 |
| 배경 | 순수한 밝은 회색 단색(#E6E6E6). 바닥 그림자·반사 없음(그림자는 코드로 넣음) |
| 여백 | 물체가 화면의 70~75%만 차지하고 가운데 배치(워터마크가 배경에 떨어지게) |
| 재질 | 무광 그래파이트 플라스틱과 기계 가공한 알루미늄 모서리, 사용감은 아주 약간만 |
| 색상 | 본체 #1C1B1A, 모서리 알루미늄 #9A9EA4, PLAY 키·헤드폰 폼 주황 #F2772A, 카세트 셸 짙은 갈색빛 검정 #24221F, 라벨 아이보리 #EFE6D2 |
| 금지 | 로고, 글자, 상표, 모델명, 손, 사람, 주변 소품, 아웃포커스 흐림, 기울어진 각도 |

### 공통 스타일 문구

아래 문단이 모든 프롬프트의 끝에 들어가는 공통 문구입니다. 5장의 프롬프트에는 이미 들어 있으니, 새 이미지를 추가로 만들 때만 이 문단을 가져다 쓰면 됩니다.

```text
Studio product photograph, straight-on front orthographic view with zero tilt, long telephoto lens so there is no perspective distortion, everything in sharp focus. Soft softbox key light from the top-left at 45 degrees with a faint fill light from the right. Plain flat light-grey background (#E6E6E6) with no floor shadow and no reflection. The object is centered and fills only about 70 percent of the frame, leaving generous empty margin on every side. Photorealistic materials, subtle micro-scratches, no logos, no text, no letters, no numbers, no brand marks, no hands, no props.
```

기존 이미지를 참고 이미지로 올려 고칠 때는 아래 문장이 프롬프트 맨 앞에 들어갑니다. 5장의 편집·수정 프롬프트에는 이 문장과 공통 문구가 모두 들어 있습니다.

```text
Using the attached image as the exact reference, keep the same object, size, position in the frame, camera angle, lighting, colors and background. Change only the following:
```

## 4. 이미지 명세

AI로 생성할 이미지는 필수 6장(IMG-01·02·04·05·06·08)입니다. IMG-03은 IMG-02를 오려서, 키 4개 파일은 IMG-06을 `prep.py`로 자동으로 잘라서 만듭니다. 눌린 키 이미지(이전 IMG-07)는 만들지 않고 코드로 표현합니다. 최종 크기는 2048px 안팎의 생성본을 자른 크기입니다.

| ID | 최종 파일 | 내용 | 생성 비율 | 최종 크기(px) | 투명 영역 | 제작 방식 | 구분 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| IMG-01 | `deck/deck-bay@2x.webp` | 덮개가 없는 데크 본체 정면. 위쪽은 빈 카세트 칸(헤드·캐스턴·핀치롤러·릴 스핀들 2개), 아래쪽은 빈 LCD 창과 키가 들어갈 긴 홈 하나 | 4:3 | 2048×1536 | 본체 바깥 | 새로 생성 | 필수 |
| IMG-02 | `_work/deck-closed.png` | IMG-01과 같은 본체에 덮개(연기색 유리창 달린 테두리)를 닫은 모습. 앱에는 쓰지 않는 작업용 | 4:3 | — | — | IMG-01 편집 | 필수 |
| IMG-03 | `deck/deck-lid@2x.webp` | IMG-02에서 덮개 테두리만 오려낸 것. IMG-01과 같은 캔버스 크기·위치 | — | 2048×1536 | 덮개 바깥, 유리창 | IMG-02 오려내기 | 필수 |
| IMG-04 | `cassette/cassette-shell@2x.webp` | 카세트테이프 정면. 라벨 자리는 매끈한 빈 면, 가운데 투명창, 허브 구멍 2개, 나사 5개, 아래 사다리꼴 테이프 노출부. **몸체 비율은 데크 칸(`deck.bay`)과 같은 약 1.8:1**(아래 "IMG-04-wide" 참고) | 16:9 | 몸체 폭 약 1260 | 바깥, **창, 허브 구멍(반드시)** | 새로 생성(IMG-04-wide) | 필수 |
| IMG-05 | `cassette/cassette-label@2x.webp` | 아무것도 안 쓴 아이보리 라벨 종이, 연한 가로줄 3개, 종이 결 | 21:9 | 1110×240 | 바깥 | 새로 생성 | 필수 |
| IMG-06 | `deck/key-*@2x.webp`(4개로 자동 분할) | 기호가 없는 키 4개가 한 줄로 놓인 모습, 모두 올라온 상태. 두 번째만 주황(PLAY), 나머지는 그래파이트. 위·아래 여백이 넓어야 함 | 21:9 | 키마다 약 400×630 | 바깥, 그림자 | 새로 생성 → prep.py 자동 자르기 | 필수 |
| IMG-08 | `deck/headphones@2x.webp` | 은색 헤드밴드에 주황 폼 이어패드 2개가 달린 헤드폰 정면 | 3:2 | 1200×800 | 바깥 | 새로 생성 | 필수 |
| IMG-09 | `cassette/cassette-hub@2x.webp` | 카세트 릴 허브 1개(흰 플라스틱, 안쪽 톱니 6개) 정면 | 1:1 | 512×512 | 바깥, 가운데 구멍 | 새로 생성 | 선택 |
| IMG-10 | `cassette/tape-pack-texture@2x.webp` | 감긴 갈색 자기 테이프를 정면에서 본 동심원 질감 | 1:1 | 1024×1024 | 없음(코드로 원형 자름) | 새로 생성 | 선택 |
| IMG-11 | `shelf/case-spine@2x.webp` | 투명 카세트 케이스의 옆면(책등), 빈 종이 속지 | 9:16 | 160×960 | 바깥 | 새로 생성 | 선택 |

### 키 조각 파일

IMG-06 한 장을 `prep.py keys`가 키별로 자동으로 잘라 4개 파일을 만듭니다(6장 참고). 네 키는 위·아래 끝을 똑같이 맞춰 자릅니다.

- `deck/key-rew@2x.webp`
- `deck/key-play@2x.webp`
- `deck/key-stop@2x.webp`
- `deck/key-ff@2x.webp`

키 위의 기호(◀◀ ▶ ■ ▶▶)는 AI가 모양을 틀리게 그리기 쉽습니다. 그래서 빈 키로 만들고, 기호는 코드에서 음각처럼 보이도록 얹습니다.

### 폴더 구조

```text
assets/
├─ deck/       deck-bay, deck-lid, key-rew/play/stop/ff, headphones
├─ cassette/   cassette-shell, cassette-label, cassette-hub, tape-pack-texture
├─ shelf/      case-spine
├─ _master/    확대·배경 제거만 끝난 PNG 원본(앱에 포함하지 않음)
├─ _work/      생성 원본과 작업용 파일(앱에 포함하지 않음)
└─ assets.json 각 이미지의 좌표 기록(7절 참고)
```

## 5. 프롬프트 세트

아래 코드 블록은 모두 완성형입니다. 공통 스타일 문구와 편집 문구가 이미 들어 있어, 블록 하나를 통째로 복사해 붙여 넣으면 됩니다. 각 이미지에는 "새로 만들기" 프롬프트와, 앞서 만든 이미지를 참고로 올려 재질·조명을 맞추는 "참고 이미지 버전"이 있습니다. 둘 중 하나만 쓰면 됩니다. 순서는 IMG-01 → 02 → 04 → 05 → 06 → 08이 좋습니다. 편집 프롬프트(02)는 마음에 드는 원본을 채팅창에 첨부한 뒤 보냅니다.

### IMG-01 데크 본체(빈 카세트 칸)

```text
A premium 1980s-inspired portable stereo cassette player seen from the front, with its cassette door removed so the empty cassette compartment is fully visible. The body is a rounded rectangle of matte dark graphite plastic (#1C1B1A) framed by a thin machined aluminum bezel (#9A9EA4) with chamfered, lightly polished edges. The upper two-thirds of the front is the empty recessed cassette compartment: a dark matte interior, two white toothed reel spindles, and along the bottom edge of the compartment a chrome tape head, a black rubber pinch roller and a thin metal capstan. Two small hinge knuckles sit on the bottom edge of the compartment opening. Below the compartment is a horizontal control strip with only two elements: on top, a wide blank unlit display window of dark amber-tinted glass; underneath it, one single long empty horizontal recessed channel running almost the full width of the body, completely empty, with no buttons, no keys and no dividers inside it. A ridged volume wheel edge peeks out on the right side. There are no buttons anywhere on the front of the player. 4:3 aspect ratio.
Studio product photograph, straight-on front orthographic view with zero tilt, long telephoto lens so there is no perspective distortion, everything in sharp focus. Soft softbox key light from the top-left at 45 degrees with a faint fill light from the right. Plain flat light-grey background (#E6E6E6) with no floor shadow and no reflection. The object is centered and fills only about 70 percent of the frame, leaving generous empty margin on every side. Photorealistic materials, subtle micro-scratches, no logos, no text, no letters, no numbers, no brand marks, no hands, no props.
```

확인할 점: 칸 안에 카세트가 없어야 하고, 아래 긴 홈 안에 버튼이나 칸막이가 없어야 합니다. 키 4개는 이 홈을 4등분해 코드로 얹습니다. 버튼이 생기면 아래 FIX-keys 프롬프트로 고칩니다.

### IMG-02 덮개 닫힌 본체(IMG-01 편집)

```text
Using the attached image as the exact reference, keep the same object, size, position in the frame, camera angle, lighting, colors and background. Change only the following: add a closed cassette door over the cassette compartment. The door is a thin matte graphite frame matching the body, with a large rectangular window of smoked dark transparent glass through which the empty compartment is faintly visible. The door has two small hinges along its bottom edge, aligned with the existing hinge knuckles, and a small finger notch at the top center. Do not change anything outside the compartment opening. 4:3 aspect ratio.
Studio product photograph, straight-on front orthographic view with zero tilt, long telephoto lens so there is no perspective distortion, everything in sharp focus. Soft softbox key light from the top-left at 45 degrees with a faint fill light from the right. Plain flat light-grey background (#E6E6E6) with no floor shadow and no reflection. The object is centered and fills only about 70 percent of the frame, leaving generous empty margin on every side. Photorealistic materials, subtle micro-scratches, no logos, no text, no letters, no numbers, no brand marks, no hands, no props.
```

확인할 점: IMG-01과 겹쳐 보았을 때 본체 윤곽과 긴 홈 위치가 어긋나지 않아야 합니다. 어긋나면 다시 생성합니다.

### IMG-04 카세트 셸

```text
A standard compact audio cassette tape seen exactly from the front, lying perfectly flat. The shell is dark brownish-black matte plastic (#24221F) with five small recessed screws. The upper area has a smooth, flat, slightly recessed empty rectangle where a label would go, with no paper label on it. In the center there is a clear rectangular window, and two round hub holes show two white plastic reel hubs with only a very thin ring of brown tape on each, as if nearly empty. At the bottom center there is a trapezoid ridge with two small round holes and a strip of exposed brown tape. True cassette proportions of about 100 by 64 millimeters. 3:2 aspect ratio.
Studio product photograph, straight-on front orthographic view with zero tilt, long telephoto lens so there is no perspective distortion, everything in sharp focus. Soft softbox key light from the top-left at 45 degrees with a faint fill light from the right. Plain flat light-grey background (#E6E6E6) with no floor shadow and no reflection. The object is centered and fills only about 70 percent of the frame, leaving generous empty margin on every side. Photorealistic materials, subtle micro-scratches, no logos, no text, no letters, no numbers, no brand marks, no hands, no props.
```

확인할 점: 창과 허브 구멍의 가장자리가 뚜렷해야 오려내기 쉽습니다. 라벨 자리에 글자가 생기면 다시 생성합니다.

참고 이미지 버전(IMG-01을 첨부):

```text
Use the attached image only as a reference for materials, color palette, lighting direction and camera angle. Do not copy its shape and do not include the attached object in the result. Create a new, separate image of: a standard compact audio cassette tape seen exactly from the front, lying perfectly flat. The shell is dark brownish-black matte plastic (#24221F) with five small recessed screws. The upper area has a smooth, flat, slightly recessed empty rectangle where a label would go, with no paper label on it. In the center there is a clear rectangular window, and two round hub holes show two white plastic reel hubs with only a very thin ring of brown tape on each, as if nearly empty. At the bottom center there is a trapezoid ridge with two small round holes and a strip of exposed brown tape. True cassette proportions of about 100 by 64 millimeters. 3:2 aspect ratio.
Studio product photograph, straight-on front orthographic view with zero tilt, long telephoto lens so there is no perspective distortion, everything in sharp focus. Soft softbox key light from the top-left at 45 degrees with a faint fill light from the right. Plain flat light-grey background (#E6E6E6) with no floor shadow and no reflection. The object is centered and fills only about 70 percent of the frame, leaving generous empty margin on every side. Photorealistic materials, subtle micro-scratches, no logos, no text, no letters, no numbers, no brand marks, no hands, no props.
```

### IMG-04-wide 카세트 셸(데크 칸 비율에 맞춘 판, 권장)

처음 만든 셸은 실제 카세트 비율(약 1.57:1)이라, 그보다 납작한 데크 칸(약 1.8:1)에 맞추려고 세로로 누르면 허브 구멍이 타원이 됩니다. 그래서 **처음부터 칸 비율로 그리게** 하고, 창과 허브 구멍은 **비어서 배경이 비치게** 그리게 해 오려내기 쉽게 합니다. `tools/prompts.json`의 `IMG-04-wide`이며, 지난번 AI 셸을 참고 이미지로 붙여 재질과 색을 맞춥니다.

```bash
python3 tools/gen.py IMG-04-wide --ref assets/cassette/cassette-shell-backup1.webp --count 3
```

| 조건 | 값 | 이유 |
| --- | --- | --- |
| 몸체 비율 | 가로 1.8 : 세로 1 | 데크 칸 `deck.bay`(1112×617)와 같은 비율. 누르거나 늘이지 않아도 칸에 맞는다 |
| 허브 구멍 중심 | 몸체 폭의 28.5%·71.5%, 높이의 약 46% | 몸체가 칸 폭에 맞을 때 데크 스핀들 위에 온다(스핀들 간격 = 칸 폭의 43.1%) |
| 허브 구멍 모양 | 크기가 같은 정원 | 코드가 그리는 허브·감긴 테이프는 원이라, 구멍도 원이어야 테두리와 맞는다 |
| 창·허브 구멍 속 | 비어 있고 배경 회색이 비침 | 배경을 지울 때 함께 지워져 투명해진다 |

확인할 점:
- 허브 구멍이 타원이거나 안에 릴이 그려져 나오면 `FIX-holes`(편집)로 고칩니다. AI가 위치를 정확히 맞추지 못해도 calibrate의 "허브에 맞추기"가 크기와 위치를 맞춥니다.
- 오려낸 뒤 **창과 허브 구멍이 완전히 투명(알파 0)**해야 합니다. 불투명하면 그 아래에서 도는 허브와 감긴 테이프가 보이지 않습니다. `python tools/check-assets.py`가 이를 검사합니다.
- 새 셸을 넣은 뒤에는 calibrate의 카세트 탭에서 `labelArea`·`window`·`hubs`·`packMaxRadius`를 다시 표시하고, 합성 확인 탭에서 "허브에 맞추기"를 누릅니다. 코드는 고치지 않아도 됩니다.

### IMG-05 빈 라벨 종이

```text
A single blank paper cassette label lying perfectly flat: ivory colored (#EFE6D2) matte uncoated paper with fine visible fibers, a long rectangle with slightly rounded corners, and three faint thin horizontal ruled lines in pale grey. Completely blank, with no writing, no colored stripes, no printing. 21:9 aspect ratio.
Studio product photograph, straight-on front orthographic view with zero tilt, long telephoto lens so there is no perspective distortion, everything in sharp focus. Soft softbox key light from the top-left at 45 degrees with a faint fill light from the right. Plain flat light-grey background (#E6E6E6) with no floor shadow and no reflection. The object is centered and fills only about 70 percent of the frame, leaving generous empty margin on every side. Photorealistic materials, no logos, no text, no letters, no numbers, no brand marks, no hands, no props.
```

확인할 점: 종이가 휘거나 기울지 않아야 합니다. 주황·청록 색 띠와 손글씨는 코드로 얹습니다.

참고 이미지 버전(IMG-04를 첨부):

```text
Use the attached image only as a reference for lighting direction, color temperature and camera angle. Do not copy its shape and do not include the attached object in the result. Create a new, separate image of: a single blank paper cassette label lying perfectly flat, sized to fit the empty label area of the attached cassette. Ivory colored (#EFE6D2) matte uncoated paper with fine visible fibers, a long rectangle with slightly rounded corners, and three faint thin horizontal ruled lines in pale grey. Completely blank, with no writing, no colored stripes, no printing. 21:9 aspect ratio.
Studio product photograph, straight-on front orthographic view with zero tilt, long telephoto lens so there is no perspective distortion, everything in sharp focus. Soft softbox key light from the top-left at 45 degrees with a faint fill light from the right. Plain flat light-grey background (#E6E6E6) with no floor shadow and no reflection. The object is centered and fills only about 70 percent of the frame, leaving generous empty margin on every side. Photorealistic materials, no logos, no text, no letters, no numbers, no brand marks, no hands, no props.
```

### IMG-06 키 4개(올라온 상태)

```text
A row of exactly four separate chunky rectangular push keys from a 1980s cassette player, viewed straight from the front and evenly spaced in one horizontal line: a first key at the far left, a second key left of center, a third key right of center and a fourth key at the far right. Each key has a softly rounded top face and a visible front edge thickness. The second key from the left is satin orange plastic (#F2772A); the other three are matte dark graphite plastic (#232328). All four keys are in the raised, unpressed position. The key faces are completely blank with no symbols. The row of keys is centered vertically in the frame and fills only about 60 percent of the frame height, with generous empty space above and below the keys. 21:9 aspect ratio.
Studio product photograph, straight-on front orthographic view with zero tilt, long telephoto lens so there is no perspective distortion, everything in sharp focus. Soft softbox key light from the top-left at 45 degrees with a faint fill light from the right. Plain flat light-grey background (#E6E6E6) with no floor shadow and no reflection. The object is centered and fills only about 70 percent of the frame, leaving generous empty margin on every side. Photorealistic materials, subtle micro-scratches, no logos, no text, no letters, no numbers, no brand marks, no hands, no props.
```

확인할 점: 키가 정확히 4개이고, 너비와 간격이 같아야 합니다. 키 위·아래에 여백이 남아야 자동 자르기가 안정적입니다. 눌린 상태는 따로 만들지 않습니다.

참고 이미지 버전(IMG-01을 첨부, 긴 홈 길이에 맞추기):

```text
Use the attached image only as a reference for materials, color palette, lighting direction and camera angle, and size the keys so that the four of them side by side would exactly fill the long empty key channel of the attached player. Do not include the player itself in the result. Create a new, separate image of: a row of exactly four separate chunky rectangular push keys from a 1980s cassette player, viewed straight from the front and evenly spaced in one horizontal line: a first key at the far left, a second key left of center, a third key right of center and a fourth key at the far right. Each key has a softly rounded top face and a visible front edge thickness. The second key from the left is satin orange plastic (#F2772A); the other three are matte dark graphite plastic (#232328). All four keys are in the raised, unpressed position. The key faces are completely blank with no symbols. The row of keys is centered vertically in the frame and fills only about 60 percent of the frame height, with generous empty space above and below the keys. 21:9 aspect ratio.
Studio product photograph, straight-on front orthographic view with zero tilt, long telephoto lens so there is no perspective distortion, everything in sharp focus. Soft softbox key light from the top-left at 45 degrees with a faint fill light from the right. Plain flat light-grey background (#E6E6E6) with no floor shadow and no reflection. The object is centered and fills only about 70 percent of the frame, leaving generous empty margin on every side. Photorealistic materials, subtle micro-scratches, no logos, no text, no letters, no numbers, no brand marks, no hands, no props.
```

### IMG-08 헤드폰

```text
A pair of lightweight 1980s-style on-ear headphones seen straight from the front: a thin brushed-steel headband (#8E9298) forming a smooth arch, two round ear pads of soft open-cell foam in bright orange (#F2772A) with clearly visible foam pores, small black plastic ear cups behind the foam, and a thin black cable leaving the left ear cup and hanging down in a gentle curve. The headphones are symmetric. 3:2 aspect ratio.
Studio product photograph, straight-on front orthographic view with zero tilt, long telephoto lens so there is no perspective distortion, everything in sharp focus. Soft softbox key light from the top-left at 45 degrees with a faint fill light from the right. Plain flat light-grey background (#E6E6E6) with no floor shadow and no reflection. The object is centered and fills only about 70 percent of the frame, leaving generous empty margin on every side. Photorealistic materials, no logos, no text, no letters, no numbers, no brand marks, no hands, no props.
```

확인할 점: 폼 주황색이 PLAY 키와 비슷해야 하고, 케이블이 화면 밖으로 잘리지 않아야 합니다.

참고 이미지 버전(IMG-06을 첨부, 주황색 맞추기):

```text
Use the attached image only as a reference for materials, lighting direction and camera angle, and match the orange of the foam exactly to the orange key in the attached image. Do not include the keys in the result. Create a new, separate image of: a pair of lightweight 1980s-style on-ear headphones seen straight from the front: a thin brushed-steel headband (#8E9298) forming a smooth arch, two round ear pads of soft open-cell foam in bright orange (#F2772A) with clearly visible foam pores, small black plastic ear cups behind the foam, and a thin black cable leaving the left ear cup and hanging down in a gentle curve. The headphones are symmetric. 3:2 aspect ratio.
Studio product photograph, straight-on front orthographic view with zero tilt, long telephoto lens so there is no perspective distortion, everything in sharp focus. Soft softbox key light from the top-left at 45 degrees with a faint fill light from the right. Plain flat light-grey background (#E6E6E6) with no floor shadow and no reflection. The object is centered and fills only about 70 percent of the frame, leaving generous empty margin on every side. Photorealistic materials, no logos, no text, no letters, no numbers, no brand marks, no hands, no props.
```

### IMG-09 릴 허브(선택)

```text
A single white plastic cassette reel hub seen straight from the front: a white ring with six small inward-pointing teeth around a round center hole, slightly glossy injection-molded plastic with a thin mold seam. 1:1 aspect ratio.
Studio product photograph, straight-on front orthographic view with zero tilt, long telephoto lens so there is no perspective distortion, everything in sharp focus. Soft softbox key light from the top-left at 45 degrees with a faint fill light from the right. Plain flat light-grey background (#E6E6E6) with no floor shadow and no reflection. The object is centered and fills only about 70 percent of the frame, leaving generous empty margin on every side. Photorealistic materials, no logos, no text, no letters, no numbers, no brand marks, no hands, no props.
```

### IMG-10 감긴 테이프 질감(선택)

질감 이미지는 화면을 꽉 채워야 하므로 공통 문구를 쓰지 않습니다.

```text
A macro photograph looking straight at the flat face of a tightly wound pack of brown magnetic audio tape, filling the entire frame edge to edge with fine concentric rings centered in the frame and a soft satin sheen. Even, uniform lighting, sharp focus everywhere, no hub, no background, no text. 1:1 aspect ratio.
```

### IMG-11 케이스 책등(선택)

```text
The narrow spine edge of a clear plastic cassette tape case standing upright, seen straight from the side: transparent hard plastic with soft vertical reflections, and a blank ivory paper insert visible inside along the spine. Completely blank, no writing. 9:16 aspect ratio.
Studio product photograph, straight-on orthographic view with zero tilt, long telephoto lens so there is no perspective distortion, everything in sharp focus. Soft softbox key light from the top-left at 45 degrees with a faint fill light from the right. Plain flat light-grey background (#E6E6E6) with no floor shadow and no reflection. The object is centered with generous empty margin above and below. Photorealistic materials, no logos, no text, no letters, no numbers, no brand marks, no hands, no props.
```

### 결과가 어긋날 때 쓰는 수정 프롬프트

어긋난 결과 이미지를 첨부하고 아래 블록 중 하나를 통째로 보냅니다. 문제마다 바꿀 내용만 다르고, 나머지 문구는 모두 같습니다.

**비스듬히 내려다본 각도로 나옴**

```text
Using the attached image as the exact reference, keep the same object, its design, materials, colors, lighting and background. Change only the following: turn the camera so it faces the front surface exactly head-on, like a flat scan, with no top or side surfaces visible and no perspective distortion.
Studio product photograph, straight-on front orthographic view with zero tilt, long telephoto lens so there is no perspective distortion, everything in sharp focus. Soft softbox key light from the top-left at 45 degrees with a faint fill light from the right. Plain flat light-grey background (#E6E6E6) with no floor shadow and no reflection. The object is centered and fills only about 70 percent of the frame, leaving generous empty margin on every side. Photorealistic materials, subtle micro-scratches, no logos, no text, no letters, no numbers, no brand marks, no hands, no props.
```

**글자나 로고가 생김**

```text
Using the attached image as the exact reference, keep the same object, size, position in the frame, camera angle, lighting, colors and background. Change only the following: remove every letter, number, logo, symbol and printed marking so that all surfaces are plain, filling those areas with the surrounding material.
Studio product photograph, straight-on front orthographic view with zero tilt, long telephoto lens so there is no perspective distortion, everything in sharp focus. Soft softbox key light from the top-left at 45 degrees with a faint fill light from the right. Plain flat light-grey background (#E6E6E6) with no floor shadow and no reflection. The object is centered and fills only about 70 percent of the frame, leaving generous empty margin on every side. Photorealistic materials, subtle micro-scratches, no logos, no text, no letters, no numbers, no brand marks, no hands, no props.
```

**물체가 화면을 너무 크게 채움**

```text
Using the attached image as the exact reference, keep the same object, camera angle, lighting, colors and background. Change only the following: zoom out so the object is smaller and fills only about 70 percent of the frame, centered, with generous empty background margin on every side.
Studio product photograph, straight-on front orthographic view with zero tilt, long telephoto lens so there is no perspective distortion, everything in sharp focus. Soft softbox key light from the top-left at 45 degrees with a faint fill light from the right. Plain flat light-grey background (#E6E6E6) with no floor shadow and no reflection. The object is centered and fills only about 70 percent of the frame, leaving generous empty margin on every side. Photorealistic materials, subtle micro-scratches, no logos, no text, no letters, no numbers, no brand marks, no hands, no props.
```

**바닥 그림자나 반사가 생김**

```text
Using the attached image as the exact reference, keep the same object, size, position in the frame, camera angle, lighting and colors. Change only the following: make the background perfectly flat light grey (#E6E6E6) with no shadow, no reflection and no gradient under or around the object.
Studio product photograph, straight-on front orthographic view with zero tilt, long telephoto lens so there is no perspective distortion, everything in sharp focus. Soft softbox key light from the top-left at 45 degrees with a faint fill light from the right. Plain flat light-grey background (#E6E6E6) with no floor shadow and no reflection. The object is centered and fills only about 70 percent of the frame, leaving generous empty margin on every side. Photorealistic materials, subtle micro-scratches, no logos, no text, no letters, no numbers, no brand marks, no hands, no props.
```

**색이 다름**

```text
Using the attached image as the exact reference, keep the same object, size, position in the frame, camera angle, lighting and background. Change only the following: match the colors exactly to these values: graphite body #1C1B1A, aluminum bezel #9A9EA4, dark keys #232328, all orange parts #F2772A, cassette shell #24221F, label paper #EFE6D2, headband steel #8E9298. Keep the material finishes the same.
Studio product photograph, straight-on front orthographic view with zero tilt, long telephoto lens so there is no perspective distortion, everything in sharp focus. Soft softbox key light from the top-left at 45 degrees with a faint fill light from the right. Plain flat light-grey background (#E6E6E6) with no floor shadow and no reflection. The object is centered and fills only about 70 percent of the frame, leaving generous empty margin on every side. Photorealistic materials, subtle micro-scratches, no logos, no text, no letters, no numbers, no brand marks, no hands, no props.
```

**본체 아래에 버튼이 생김(IMG-01, FIX-keys)**

```text
Using the attached image as the exact reference, keep the same object, size, position in the frame, camera angle, lighting, colors and background. Change only the following: replace all the buttons and key recesses in the lower control strip with one single long empty horizontal recessed channel running almost the full width of the body, with no buttons, no keys and no dividers inside it. Keep the display window above it unchanged.
Studio product photograph, straight-on front orthographic view with zero tilt, long telephoto lens so there is no perspective distortion, everything in sharp focus. Soft softbox key light from the top-left at 45 degrees with a faint fill light from the right. Plain flat light-grey background (#E6E6E6) with no floor shadow and no reflection. The object is centered and fills only about 70 percent of the frame, leaving generous empty margin on every side. Photorealistic materials, subtle micro-scratches, no logos, no text, no letters, no numbers, no brand marks, no hands, no props.
```

## 6. 후처리 절차

도구는 아래와 같이 씁니다. 확대는 Upscayl(데스크톱 앱), 배경 제거와 오려내기는 Photoshop(무료 대안은 Photopea), 키 자르기는 prep.py, WebP 변환은 Squoosh(웹)를 씁니다. 배경 제거는 rembg나 remove.bg로 대신해도 됩니다.

| 도구 | 용도 |
| --- | --- |
| Gemini 앱 | 생성·편집, 원본 PNG 내려받기 |
| Upscayl | 2배 확대(사진용 기본 모델) |
| Photoshop(또는 Photopea) | 배경 제거, 창·구멍 오려내기, 자르기, 색 보정, 좌표 재기 |
| Squoosh | WebP 변환과 용량 확인 |

### 순서

1. **원본 보관**: 생성본을 `_work/IMG-01_v1.png`처럼 버전을 붙여 저장합니다. 편집용으로 채택한 원본은 따로 표시해 둡니다.
2. **2배 확대**: Upscayl에서 배율 2배, 출력 PNG로 확대합니다. IMG-01과 IMG-02는 같은 모델·같은 설정으로 확대해야 픽셀 위치가 맞습니다.
3. **배경 제거**: 자동 배경 제거는 은색 테두리의 광택을 배경으로 착각해 지워 버립니다. 데크 본체·카세트·라벨처럼 모양이 둥근 사각형인 물체는 Photoshop의 펜 도구나 모서리가 둥근 사각형 도구로 윤곽을 따고, 선택 영역으로 바꿔 레이어 마스크를 만듭니다(삭제 대신 마스크). 가장자리는 마스크 속성에서 페더 0.5~1px로 다듬습니다. 헤드폰처럼 곡선이 많은 물체는 ‘피사체 선택’ 후 ‘선택 및 마스크’로 손봐도 됩니다. 지운 뒤에는 어두운 색(#0D0D0E) 레이어를 밑에 깔아 테두리 광택이 남아 있는지 확인합니다. 키(IMG-06)는 배경을 지우지 않아도 prep.py가 배경과 그림자까지 함께 처리합니다. 워터마크는 배경 위에 있으므로 이때 함께 사라집니다.
4. **덮개 오려내기(IMG-03)**: IMG-02를 열고, 덮개 테두리 바깥을 모두 지웁니다. 이어서 유리창 안쪽을 사각형 선택으로 지워 투명하게 만듭니다. **캔버스는 자르지 않고** IMG-01과 같은 2048×1536으로 둡니다.
5. **카세트 오려내기(IMG-04)**: 가운데 창은 사각형 선택, 허브 구멍 2개는 원형 선택(Shift를 누른 채 끌어 정원)으로 지웁니다. IMG-04-wide처럼 창·구멍 속이 배경 회색이면 배경을 지울 때 함께 지워지므로, 남은 부분만 다듬습니다. 두 구멍의 중심 좌표를 기록합니다(7장). **셸을 세로나 가로로 늘이거나 누르지 않습니다.** 비율이 칸과 다르면 다시 생성합니다(누르면 허브 구멍이 타원이 됩니다).
6. **정렬 검사**: IMG-01 위에 IMG-03을 올리고 혼합 모드를 "차이"로 바꿉니다. 덮개 경첩과 본체 가장자리가 거의 검게 보여야 합니다. 어긋나면 이동 도구로 맞추거나 IMG-02를 다시 생성합니다.
7. **자르기**: 데크 레이어(IMG-01·03)를 빼고, 4장 표의 최종 크기로 자릅니다. 키는 직접 자르지 않고 아래 ‘키 자동 자르기’로 처리합니다.
8. **색 보정**: 스포이드로 PLAY 키와 헤드폰 폼을 찍어 보고, 서로 다르면 색조·채도로 #F2772A 근처에 맞춥니다.
9. **내보내기**: 마스터는 `_master/`에 PNG로, 앱용은 Squoosh에서 WebP(품질 85~90, 투명 유지)로 내보냅니다.

### 키 자동 자르기

`prep.py`가 IMG-06에서 키 4개를 찾아, 그림자와 옆 키를 뺀 뒤 같은 높이로 잘라 줍니다. Pillow(`pip install pillow`)가 필요합니다.

```bash
python3 tools/prep.py keys tools/out/IMG-06_생성파일.png
```

- 결과: `assets/deck/key-rew·play·stop·ff@2x`의 PNG와 WebP, `assets/assets.json`의 `keys` 항목
- 확인: `tools/_preview/keys-preview.png`에서 어두운 배경 위의 키 4개와 자른 범위(주황 선)를 봅니다.
- 키가 4개로 나뉘지 않으면 오류를 내고 멈춥니다. 키 사이 틈이 그림자로 막혔거나 키가 붙어 있는 경우이므로 IMG-06을 다시 생성합니다.
- 더 어두운 키를 쓰면 `--dark-max`(기본 112)를, 주황이 연하면 `--sat-min`(기본 0.3)을 조정합니다.

### 용량 목표

| 파일 | 목표 용량 |
| --- | --- |
| `deck-bay@2x.webp` | 400KB 이하 |
| `deck-lid@2x.webp` | 150KB 이하 |
| `cassette-shell@2x.webp` | 200KB 이하 |
| 키 4개 | 각 30KB 이하 |
| `headphones@2x.webp` | 150KB 이하 |
| 전체 | 1.5MB 이하 |

## 7. 좌표 기록(assets.json)과 앱 연결

AI 이미지는 부품 위치가 매번 달라서, 완성된 이미지에서 좌표를 재서 `assets/assets.json`에 적습니다. 앱은 이 값을 %로 바꿔 릴·키·LCD·카세트·헤드폰을 제자리에 놓습니다. 이 파일은 내려받는 것이 아니라, 내 이미지로 `tools/calibrate.html`에서 만듭니다.

1. `tools/calibrate.html`을 크롬에서 열고 "assets 폴더 열기"로 프로젝트의 `assets` 폴더를 고릅니다. 파일 이름으로 이미지가 자동 연결됩니다.
2. **데크** 탭에서 `bay`·`spindles`·`lcd`·`keyChannel`·`lid.hingeY`를, **카세트** 탭에서 `labelArea`·`window`·`hubs`·`packMaxRadius`를 이미지 위에 끌어서 표시합니다. 돋보기와 방향키(1px, Shift는 10px)로 정확히 맞춥니다.
3. **합성 확인** 탭에서 "허브에 맞추기"를 누르면 카세트 허브가 데크 스핀들에 맞도록 `seatInBay`가 자동 계산됩니다. 헤드폰 위치를 끌어서 정하고 점검 목록을 확인합니다.
4. "assets.json 내려받기" 후 파일을 `assets/` 폴더 바로 아래에 둡니다.

단위는 각 이미지(@2x) 기준 픽셀입니다. `[x, y, 너비, 높이]`는 왼쪽 위 기준 사각형, `[cx, cy, r]`은 원의 중심과 반지름입니다. `seatInBay`와 `headphones.place`는 데크 이미지 좌표입니다. 아래 숫자는 형식을 보여 주는 자리 표시입니다.

```json
{
  "version": 1,
  "deck": {
    "image": "deck/deck-bay@2x.webp",
    "size": [2048, 1536],
    "bay": [0, 0, 0, 0],
    "spindles": { "left": [0, 0, 0], "right": [0, 0, 0] },
    "lcd": [0, 0, 0, 0],
    "keyChannel": [0, 0, 0, 0],
    "lid": { "image": "deck/deck-lid@2x.webp", "hingeY": 0 }
  },
  "keys": {
    "files": { "rew": "deck/key-rew@2x.webp", "play": "deck/key-play@2x.webp", "stop": "deck/key-stop@2x.webp", "ff": "deck/key-ff@2x.webp" },
    "sizes": { "rew": [0, 0], "play": [0, 0], "stop": [0, 0], "ff": [0, 0] },
    "pressed": { "translateY": "1.5%", "brightness": 0.88 }
  },
  "cassette": {
    "image": "cassette/cassette-shell@2x.webp",
    "label": "cassette/cassette-label@2x.webp",
    "size": [1260, 800],
    "labelArea": [0, 0, 0, 0],
    "window": [0, 0, 0, 0],
    "hubs": { "left": [0, 0, 0], "right": [0, 0, 0] },
    "packMaxRadius": 0,
    "seatInBay": [0, 0, 0, 0]
  },
  "headphones": {
    "image": "deck/headphones@2x.webp",
    "size": [1200, 800],
    "place": [0, 0, 0, 0]
  }
}
```

| 키 | 재는 법 | 앱에서 쓰는 곳 |
| --- | --- | --- |
| `deck.bay` | 빈 카세트 칸의 안쪽 사각형 | 카세트가 내려오는 범위, 덮개 영역 |
| `deck.spindles` | 칸 안 흰 스핀들의 중심과 반지름 | 카세트 허브를 맞추는 기준점 |
| `deck.lcd` | 빈 LCD 창의 안쪽 사각형 | LCD 글자 위치 |
| `deck.keyChannel` | 키가 들어갈 긴 홈의 안쪽 사각형 | 4등분해 키 배치, 클릭 영역 |
| `deck.lid.hingeY` | 덮개 경첩이 있는 가로선의 y | `rotateX` 회전축 |
| `keys` | 재지 않음(측정기나 `prep.py keys`가 기록) | 키 파일·크기, 눌림 표현값 |
| `cassette.labelArea` | 셸의 빈 라벨 자리 | 라벨 종이·색 띠·손글씨 제목 |
| `cassette.window` | 가운데 투명창 | 창 유리 레이어 |
| `cassette.hubs` | 허브 구멍 2개의 중심과 반지름 | 릴 회전 중심, 감긴 테이프의 최소 반지름 |
| `cassette.packMaxRadius` | 감긴 테이프가 가득 찼을 때의 반지름 | 릴 반지름 공식의 r_max |
| `cassette.seatInBay` | "허브에 맞추기"로 자동 계산(데크 좌표) | 넣기 애니메이션의 도착 위치 |
| `headphones.place` | 합성 화면에서 끌어서 지정(데크 좌표) | 헤드폰 위치 |

덮개 유리·카세트 창 유리·그림자는 좌표만 있으면 코드로 그릴 수 있어 별도 이미지가 필요 없습니다.

## 8. 검수 체크리스트

### 이미지마다

- [ ] 정면 시점이고 기울어짐이 없다.
- [ ] 로고, 글자, 숫자, 상표가 하나도 없다.
- [ ] 조명이 왼쪽 위에서 들어온다(하이라이트는 왼쪽 위, 어두운 면은 오른쪽 아래).
- [ ] 배경이 완전히 지워졌고, 가장자리에 회색 테두리가 남지 않았다.
- [ ] 확대 후에도 가장자리에 번짐이나 계단 현상이 없다.
- [ ] 파일 이름과 최종 크기가 4장 표와 같다.

### 합성했을 때

- [ ] IMG-01과 IMG-03을 겹치면 덮개가 본체에 정확히 맞는다.
- [ ] 카세트를 칸에 넣었을 때 카세트 허브 중심이 스핀들 중심과 맞는다.
- [ ] 키를 눌렀을 때 좌우로 움직이지 않고 아래로만 내려간다.
- [ ] PLAY 키, 헤드폰 폼, 라벨 색 띠의 주황색이 같은 색으로 보인다.
- [ ] 어두운 화면 배경(#0D0D0E) 위에서 본체 윤곽이 구분된다. 구분이 안 되면 테두리 알루미늄을 조금 밝힌다.
- [ ] 전체 용량이 1.5MB 이하다.

이미지가 준비되면 시안 A의 Claude Design 캔버스에 올리고, 이 레이어 구조와 assets.json 좌표로 실사 버전 시안을 만듭니다.
