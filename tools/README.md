# tools 폴더 안내

| 파일 | 용도 |
| --- | --- |
| `calibrate.html` | 브라우저에서 assets 폴더를 열어 이미지 좌표를 표시하고 `assets.json`을 내려받는 측정기(인터넷 불필요) |
| `gen.py` + `prompts.json` | OpenRouter API로 실사 이미지 레이어 생성(결과는 `tools/out/`) |
| `prep.py` | 키 이미지 자동 자르기(결과는 프로젝트의 `assets/deck/`, 미리 보기는 `tools/_preview/`), PNG→WebP 변환 |

## assets.json 만들기(calibrate.html)

1. `calibrate.html`을 크롬에서 더블클릭해 엽니다(서버 필요 없음).
2. "assets 폴더 열기"로 프로젝트의 `assets` 폴더를 고릅니다. 파일 이름(deck-bay, deck-lid, key-rew…, cassette-shell…)으로 이미지를 자동 연결합니다.
3. **데크** 탭: 항목마다 "표시"를 누르고 이미지 위에서 끕니다. 사각형은 모서리에서 모서리로, 원은 중심에서 테두리로 끌고, 경첩선은 클릭합니다. 오른쪽 위 돋보기로 위치를 맞추고, 방향키로 1px(Shift+방향키 10px)씩 옮길 수 있습니다.
4. **카세트** 탭: 라벨 자리, 창, 허브 구멍 2개, 감긴 테이프 최대 반지름을 표시합니다.
5. **합성 확인** 탭: "허브에 맞추기"를 누르면 카세트 허브가 데크 스핀들에 맞도록 `seatInBay`가 자동 계산됩니다. 헤드폰 위치를 끌어서 정하고, 점검 목록이 모두 초록색인지 봅니다.
6. "assets.json 내려받기" → 내려받은 파일을 **`assets/` 폴더 바로 아래**에 넣습니다.

표시한 값은 브라우저에 저장되어, 다시 열어도 남아 있습니다. 폴더에 `assets.json`이 이미 있으면 그 값을 불러와 이어서 고칠 수 있습니다.

# OpenRouter 이미지 생성 도구

`gen.py`는 Awesome Mix 실사 이미지 레이어(시안 A)를 OpenRouter API로 생성하는 스크립트입니다. 프롬프트는 `prompts.json`에 있고, 결과는 `tools/out/` 폴더에 저장됩니다. 파이썬 3.9 이상만 있으면 되고, 따로 설치할 패키지는 없습니다.

## 준비

1. https://openrouter.ai 에 가입하고 크레딧을 충전합니다. 이미지 모델에는 무료 버전이 없으며, 처음에는 5달러 정도면 충분합니다.
2. Keys 메뉴에서 이 작업 전용 API 키를 만들고, 사용 한도(credit limit)를 걸어 둡니다.
3. 터미널에서 키를 환경 변수로 등록합니다. 키를 파일이나 코드에 적지 마세요.

macOS·Linux:

```bash
export OPENROUTER_API_KEY="sk-or-여기에-키"
```

Windows PowerShell:

```powershell
$env:OPENROUTER_API_KEY = "sk-or-여기에-키"
```

## 사용법

```bash
python3 gen.py --list                         # 프롬프트 ID 목록
python3 gen.py IMG-01 --count 3               # 새로 만들기, 3장
python3 gen.py IMG-02 --ref out/IMG-01_….png  # 편집: 참고 이미지 첨부
python3 gen.py IMG-04-ref --ref out/IMG-01_….png
python3 gen.py FIX-keys --ref out/IMG-01_….png  # 어긋난 결과 고치기
python3 gen.py IMG-01 --dry-run               # 돈 쓰지 않고 요청 내용만 확인
```

| 옵션 | 설명 | 기본값 |
| --- | --- | --- |
| `--ref 파일` | 참고 이미지. 여러 번 쓰면 여러 장 첨부 | 없음 |
| `--count N` | 같은 프롬프트로 N번 생성 | 1 |
| `--size 값` | 해상도(`1K`, `2K`, `4K`). 모델이 거부하면 `--size ""` | `2K` |
| `--model ID` | 다른 이미지 모델로 바꾸기. 환경 변수 `OPENROUTER_IMAGE_MODEL`로도 지정 가능 | `google/gemini-3.1-flash-image` |
| `--extra "문장"` | 프롬프트 끝에 한 문장 덧붙이기 | 없음 |

`--size 2K`로 만들면 Upscayl로 확대하는 단계를 건너뛸 수 있습니다. 대신 1K보다 비용이 더 들 수 있습니다.

## 추천 순서

1. `IMG-01`을 2~3장 만들어 가장 좋은 것을 고릅니다.
2. 고른 IMG-01로 `IMG-02`(편집), `IMG-04-ref`, `IMG-06-ref`를 만듭니다.
3. 고른 IMG-06으로 `IMG-07`(편집)과 `IMG-08-ref`를, 고른 IMG-04로 `IMG-05-ref`를 만듭니다.
4. 결과가 어긋나면 `FIX-*` 프롬프트에 그 이미지를 `--ref`로 붙여 고칩니다.

## 키 자동 자르기(prep.py)

IMG-06(키 4개 이미지)을 키별로 잘라 줍니다. Pillow가 필요합니다(`pip install pillow`).

```bash
python3 prep.py keys out/IMG-06_….png
```

- 배경이 남아 있어도 됩니다. 키 색(어두운 그래파이트, 주황)만 남기고 배경과 그림자는 지웁니다.
- 결과는 프로젝트의 `assets/deck/key-rew·play·stop·ff@2x.png`/`.webp`로 저장되고, 파일 경로와 크기는 `assets/assets.json`의 `keys`에 기록됩니다(다른 항목은 건드리지 않음).
- `tools/_preview/keys-preview.png`에서 어두운 배경 위의 결과를 확인하세요.
- 눌린 상태 이미지는 만들지 않습니다. 앱에서 아래로 1.5% 옮기고 밝기를 0.88로 낮춰 표현합니다.

PNG를 WebP로만 바꿀 때는 아래처럼 씁니다.

```bash
python3 prep.py webp _master/headphones.png --width 1200
```

## 모델 ID와 가격 확인

모델 ID와 가격은 자주 바뀝니다. 쓰기 전에 OpenRouter의 이미지 모델 목록(https://openrouter.ai/collections/image-models)에서 확인하세요. 스크립트는 응답에 비용 정보가 있으면 끝에 합계를 보여 줍니다.

다른 모델로 바꿀 때는 그 모델이 이미지 출력(`modalities: ["image","text"]`)과 참고 이미지 입력을 지원하는지 모델 페이지에서 확인해야 합니다. 이미지만 출력하는 모델은 이 형식을 거부할 수 있습니다.
