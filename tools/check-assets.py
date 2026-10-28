"""assets/assets.json 점검: 이미지 파일이 있는지, 좌표가 비어 있지 않은지 확인한다.

사용법: python tools/check-assets.py
Pillow가 있으면 덮개 유리창 투명 여부도 함께 본다(pip install pillow).
"""
import json
import sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
HUB_TOLERANCE = 3  # 허브와 스핀들 중심 차이 허용값(데크 픽셀)

errors, warnings = [], []


def get(obj, path):
    for key in path.split("."):
        if not isinstance(obj, dict) or key not in obj:
            return None
        obj = obj[key]
    return obj


def check_file(path_str, label, required=True):
    if not path_str:
        (errors if required else warnings).append(f"{label}: 경로가 없습니다")
        return None
    path = ASSETS / path_str
    if not path.is_file():
        (errors if required else warnings).append(f"{label}: 파일이 없습니다 ({path_str})")
        return None
    return path


def check_coord(data, path, length=None):
    value = get(data, path)
    if value is None:
        errors.append(f"{path}: 값이 없습니다")
    elif isinstance(value, list):
        if length and len(value) != length:
            errors.append(f"{path}: 숫자 {length}개가 필요합니다 ({value})")
        elif all(v == 0 for v in value):
            errors.append(f"{path}: 좌표가 0으로 비어 있습니다")
        elif any(v <= 0 for v in value[2:]):
            errors.append(f"{path}: 너비·높이·반지름은 0보다 커야 합니다 ({value})")
    elif value == 0:
        errors.append(f"{path}: 값이 0으로 비어 있습니다")


def main():
    json_path = ASSETS / "assets.json"
    if not json_path.is_file():
        print("오류: assets/assets.json이 없습니다. tools/calibrate.html로 만들어 주세요.")
        return 1
    data = json.loads(json_path.read_text(encoding="utf-8"))

    # 이미지 파일
    check_file(get(data, "deck.image"), "deck.image")
    lid = check_file(get(data, "deck.lid.image"), "deck.lid.image")
    for key in ("rew", "play", "stop", "ff"):
        check_file(get(data, f"keys.files.{key}"), f"keys.files.{key}")
    check_file(get(data, "cassette.image"), "cassette.image")
    check_file(get(data, "cassette.label"), "cassette.label")
    check_file(get(data, "headphones.image"), "headphones.image")
    for key, value in (get(data, "optional") or {}).items():
        check_file(value, f"optional.{key}", required=False)

    # 좌표
    for path in ("deck.size", "cassette.size", "headphones.size"):
        check_coord(data, path, 2)
    for path in ("deck.bay", "deck.lcd", "deck.keyChannel", "cassette.labelArea",
                 "cassette.window", "cassette.seatInBay"):
        check_coord(data, path, 4)
    for path in ("deck.spindles.left", "deck.spindles.right",
                 "cassette.hubs.left", "cassette.hubs.right"):
        check_coord(data, path, 3)
    for path in ("deck.lid.hingeY", "cassette.packMaxRadius"):
        check_coord(data, path)
    place = get(data, "headphones.place")  # 음수 허용
    if not place or len(place) != 4 or place[2] <= 0 or place[3] <= 0:
        errors.append(f"headphones.place: 너비·높이가 필요합니다 ({place})")

    # 허브가 스핀들 위에 놓이는지
    seat, shell_size = get(data, "cassette.seatInBay"), get(data, "cassette.size")
    if not errors and seat and shell_size:
        scale = seat[2] / shell_size[0]
        for side in ("left", "right"):
            hx, hy, _ = get(data, f"cassette.hubs.{side}")
            sx, sy, _ = get(data, f"deck.spindles.{side}")
            dx, dy = seat[0] + hx * scale - sx, seat[1] + hy * scale - sy
            if max(abs(dx), abs(dy)) > HUB_TOLERANCE:
                warnings.append(f"{side} 허브가 스핀들에서 ({dx:+.0f}, {dy:+.0f})px 어긋납니다. calibrate의 '허브에 맞추기'를 눌러 주세요")

    # 덮개 유리창 투명 여부(카세트 칸 가운데를 본다)
    bay = get(data, "deck.bay")
    if lid and bay:
        try:
            from PIL import Image
            alpha = Image.open(lid).convert("RGBA").getchannel("A")
            cx, cy = bay[0] + bay[2] // 2, bay[1] + bay[3] // 2
            if alpha.getpixel((cx, cy)) >= 250:
                warnings.append("deck-lid 유리창이 불투명합니다. 덮개를 닫으면 카세트가 보이지 않습니다")
        except ImportError:
            warnings.append("Pillow가 없어 덮개 유리창 검사를 건너뜁니다")

    for msg in errors:
        print("오류:", msg)
    for msg in warnings:
        print("경고:", msg)
    if not errors and not warnings:
        print("assets.json 점검 통과")
    elif not errors:
        print(f"오류 없음, 경고 {len(warnings)}개")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
