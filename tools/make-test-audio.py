"""ffmpeg로 테스트용 짧은 MP3를 test-audio/에 만든다(git에 올리지 않음).

사용법: python tools/make-test-audio.py
- 곡마다 길이·음 높이·ID3 태그가 다르다.
- 태그 없는 곡 1개(파일 이름으로 "가수 - 제목"을 읽는지 확인용)
- 하위 폴더 안의 곡 1개(재귀 검색 확인용)
- 앨범 아트가 든 곡 1개
- legacy/: 한국어·일본어를 CP949·Shift_JIS로 적은 옛 태그 곡 3개와 정상 서유럽어 곡 1개
- formats/: ALAC(.m4a)와 FLAC 무손실 곡
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
COVER = {"01-neon-harbor.mp3"}  # 앨범 아트(주황 단색 256px)를 넣을 곡

# 옛 태그 프로그램처럼 "ISO-8859-1"이라 적고 실제로는 다른 인코딩 바이트를 넣은 곡
# (파일 경로, 길이(초), 주파수(Hz), 실제 인코딩, 프레임)
LEGACY = [
    ("legacy/sakuranbo-cp949.mp3", 12, 523, "cp949", {"TIT2": "さくらんぼ", "TPE1": "大塚愛", "TALB": "愛 am BEST"}),
    ("legacy/spring-cp949.mp3", 11, 554, "cp949", {"TIT2": "봄날은 간다", "TPE1": "김윤아"}),
    ("legacy/yakusoku-sjis.mp3", 13, 587, "shift_jis", {"TIT2": "約束", "TPE1": "大塚ちひろ"}),
    ("legacy/cafe-latin1.mp3", 10, 659, "latin-1", {"TIT2": "Café del Mar", "TPE1": "Beyoncé"}),  # 바뀌면 안 되는 곡
]

# 코덱 확인용 무손실 곡: ALAC(크롬 재생 불가), FLAC(재생 가능)
# (파일 경로, 길이(초), 주파수(Hz), 코덱 옵션, 태그)
FORMATS = [
    ("formats/lossless-alac.m4a", 9, 698, ["-c:a", "alac", "-sample_fmt", "s16p"], {"title": "Lossless ALAC", "artist": "Codec Lab"}),
    ("formats/lossless.flac", 8, 740, ["-c:a", "flac", "-sample_fmt", "s16"], {"title": "Lossless FLAC", "artist": "Codec Lab"}),
]


def legacy_id3(frames, codec):
    """인코딩 바이트를 0(ISO-8859-1)으로 적은 ID3v2.3 태그를 만든다."""
    body = b""
    for frame_id, text in frames.items():
        data = b"\x00" + text.encode(codec)
        body += frame_id.encode() + len(data).to_bytes(4, "big") + b"\x00\x00" + data
    size = len(body)
    syncsafe = bytes([(size >> 21) & 0x7F, (size >> 14) & 0x7F, (size >> 7) & 0x7F, size & 0x7F])
    return b"ID3\x03\x00\x00" + syncsafe + body


def main():
    if not shutil.which("ffmpeg"):
        print("오류: ffmpeg를 찾을 수 없습니다.")
        return 1
    OUT.mkdir(exist_ok=True)
    cover = OUT / "_cover.jpg"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "color=c=0xF2772A:s=256x256",
                    "-frames:v", "1", str(cover)], check=True)
    for name, seconds, freq, tags in TRACKS:
        path = OUT / name
        path.parent.mkdir(parents=True, exist_ok=True)
        cmd = ["ffmpeg", "-y", "-loglevel", "error",
               "-f", "lavfi", "-i", f"sine=frequency={freq}:duration={seconds}"]
        if name in COVER:
            cmd += ["-i", str(cover), "-map", "0:a", "-map", "1:v", "-c:v", "copy",
                    "-disposition:v", "attached_pic"]
        cmd += ["-ac", "2", "-b:a", "128k"]
        if tags:
            cmd += ["-id3v2_version", "3"]
            for key, value in tags.items():
                cmd += ["-metadata", f"{key}={value}"]
        else:
            cmd += ["-map_metadata", "-1", "-write_id3v1", "0", "-id3v2_version", "0"]
        subprocess.run(cmd + [str(path)], check=True)
        print(f"{name}  {seconds}초  {'태그 있음' if tags else '태그 없음'}{'  앨범 아트' if name in COVER else ''}")
    cover.unlink()
    for name, seconds, freq, codec, frames in LEGACY:
        path = OUT / name
        path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"sine=frequency={freq}:duration={seconds}",
                        "-ac", "2", "-b:a", "128k", "-map_metadata", "-1", "-write_id3v1", "0", "-id3v2_version", "0",
                        str(path)], check=True)
        path.write_bytes(legacy_id3(frames, codec) + path.read_bytes())
        print(f"{name}  {seconds}초  옛 태그({codec})")
    for name, seconds, freq, codec_args, tags in FORMATS:
        path = OUT / name
        path.parent.mkdir(parents=True, exist_ok=True)
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"sine=frequency={freq}:duration={seconds}",
               "-ac", "2", "-ar", "44100", *codec_args]
        for key, value in tags.items():
            cmd += ["-metadata", f"{key}={value}"]
        subprocess.run(cmd + [str(path)], check=True)
        print(f"{name}  {seconds}초  {codec_args[1].upper()}")
    print(f"완료: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
