# Awesome Mix 카세트 플레이어

내 PC의 MP3 폴더를 실사풍 카세트 데크(시안 A · Midnight Deck)로 재생하는 브라우저 앱입니다. 크롬·엣지 전용입니다.

## 폴더 구조

```text
Awesome Mix/
├─ index.html                앱(HTML·CSS·JS 한 파일)
├─ CLAUDE.md                 Claude Code 작업 규칙(자동으로 읽힘)
├─ README.md                 이 파일
├─ .gitignore
├─ assets/                   앱이 쓰는 이미지와 좌표
│  ├─ assets.json            이미지 좌표(tools/calibrate.html로 만듦)
│  ├─ deck/  cassette/  shelf/
│  └─ _master/  _work/       이미지 작업 원본(앱에서 쓰지 않음, git 제외)
├─ docs/
│  ├─ Awesome_Mix_PRD_v2.md  개발 계획서(최신, .html은 같은 내용)
│  └─ Awesome_Mix_PRD.md     이전 판(참고용)
├─ design/
│  ├─ design-A-midnight-deck.html   확정 디자인 시안 A
│  ├─ image-spec.md          실사 이미지 제작 명세(최신)
│  └─ awesome-mix-*          이전 판·시안 B(참고용)
├─ tools/
│  ├─ calibrate.html         assets.json 좌표 측정기
│  ├─ check-assets.py        assets.json 점검
│  ├─ make-test-audio.py     테스트 음원 만들기
│  ├─ gen.py, prompts.json   OpenRouter 이미지 생성
│  ├─ prep.py                키 자동 자르기, WebP 변환
│  └─ README.md              도구 사용법
└─ test-audio/               테스트 음원(make-test-audio.py로 만듦, git 제외)
```

## 앱 실행

`file://`로 열면 assets.json을 읽지 못하므로, 프로젝트 폴더에서 로컬 서버를 띄웁니다.

```bash
python -m http.server 8000
```

macOS·Linux에서는 `python3 -m http.server 8000`을 씁니다. 그다음 크롬이나 엣지에서 `http://localhost:8000`을 엽니다.

## 이미지 점검

이미지나 좌표를 바꾼 뒤에는 아래 명령으로 점검합니다. 파일 누락, 빈 좌표, 허브와 스핀들 어긋남, 덮개 유리창이 불투명한지 알려 줍니다. 덮개 검사에는 Pillow(`pip install pillow`)가 필요합니다.

```bash
python tools/check-assets.py
```

## 테스트 음원

ffmpeg가 있어야 합니다. `test-audio/`에 태그와 길이가 서로 다른 짧은 MP3 6곡(태그 없는 곡 1개, 하위 폴더 곡 1개 포함)을 만듭니다.

```bash
python tools/make-test-audio.py
```
