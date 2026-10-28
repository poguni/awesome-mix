"""ffmpeg로 테스트용 짧은 MP3 6곡을 test-audio/에 만든다(git에 올리지 않음).

사용법: python tools/make-test-audio.py
- 곡마다 길이·음 높이·ID3 태그가 다르다.
- 태그 없는 곡 1개(파일 이름으로 "가수 - 제목"을 읽는지 확인용)
- 하위 폴더 안의 곡 1개(재귀 검색 확인용)
"""
import shutil
import subprocess
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "test-audio"

# (파일 경로, 길이(초), 주파수(Hz), 태그) — 태그가 None이면 태그를 넣지 않는다
TRACKS = [
    ("01-neon-harbor.mp3", 20, 220, {"title": "Neon Harbor", "artist": "The Velvet Static", "album": "Night Signals", "date": "1984", "genre": "Synthpop", "track": "1"}),
    ("02-paper-planets.mp3", 34, 277, {"title": "Paper Planets", "artist": "Juno & The Tides", "album": "Night Signals", "date": "1984", "genre": "Synthpop", "track": "2"}),
    ("03-slow-summer.mp3", 47, 330, {"title": "느린 여름", "artist": "해안선 라디오", "album": "여름 테이프", "date": "1987", "genre": "Ballad", "track": "1"}),
    ("04-magnetic-heart.mp3", 15, 392, {"title": "Magnetic Heart", "artist": "Lila Mercer", "album": "Pulse", "date": "1981", "genre": "Soul"}),
    ("Mono Bloom - Afterglow Avenue.mp3", 28, 440, None),
    ("sub/Rewind to You.mp3", 61, 494, {"title": "Rewind to You", "artist": "The Cassette Club", "album": "B-Sides", "date": "1989", "genre": "Rock"}),
]


def main():
    if not shutil.which("ffmpeg"):
        print("오류: ffmpeg를 찾을 수 없습니다.")
        return 1
    for name, seconds, freq, tags in TRACKS:
        path = OUT / name
        path.parent.mkdir(parents=True, exist_ok=True)
        cmd = ["ffmpeg", "-y", "-loglevel", "error",
               "-f", "lavfi", "-i", f"sine=frequency={freq}:duration={seconds}",
               "-ac", "2", "-b:a", "128k"]
        if tags:
            cmd += ["-id3v2_version", "3"]
            for key, value in tags.items():
                cmd += ["-metadata", f"{key}={value}"]
        else:
            cmd += ["-map_metadata", "-1", "-write_id3v1", "0", "-id3v2_version", "0"]
        subprocess.run(cmd + [str(path)], check=True)
        print(f"{name}  {seconds}초  {'태그 있음' if tags else '태그 없음'}")
    print(f"완료: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
