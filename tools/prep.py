#!/usr/bin/env python3
"""생성한 이미지를 앱에서 쓸 수 있게 다듬는다. Pillow가 필요하다(pip install pillow).

    python3 prep.py keys out/IMG-06_….png              # 키 4개를 찾아 잘라 저장
    python3 prep.py keys keys-up.png --remove-bg        # 배경이 남아 있으면 함께 제거
    python3 prep.py webp _master/headphones.png --width 1200
"""
import argparse
import json
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFilter
except ImportError:
    sys.exit("Pillow가 필요합니다: pip install pillow")

ROOT = Path(__file__).resolve().parent
# tools/ 안에 있으면 프로젝트의 assets/ 폴더를, 아니면 같은 폴더의 assets/를 쓴다
ASSETS = (ROOT.parent if ROOT.name == "tools" else ROOT) / "assets"
KEY_NAMES = ["rew", "play", "stop", "ff"]


def key_mask(im: Image.Image, dark_max: int, sat_min: float) -> Image.Image:
    """키 색(어두운 그래파이트 또는 채도 높은 주황)인 픽셀만 255로 표시한 마스크를 만든다.

    밝기가 dark_max 이하이거나 채도가 sat_min 이상인 픽셀을 키로 본다. 회색 그림자는 밝고 채도가 낮아 빠진다.
    키 전용 방식이라, 은색 광택이 있는 본체에는 쓰지 않는다(본체는 포토샵에서 지운다).
    """
    rgb = im.convert("RGB")
    mask = Image.new("L", rgb.size, 0)
    mp, px = mask.load(), rgb.load()
    w, h = rgb.size
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            hi, lo = max(r, g, b), min(r, g, b)
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            if lum <= dark_max or (hi > 0 and (hi - lo) / hi >= sat_min):
                mp[x, y] = 255
    return mask


def fill_rows(mask: Image.Image, box: list) -> Image.Image:
    """키는 속이 꽉 찬 모양이므로, 줄마다 왼쪽 끝과 오른쪽 끝 사이를 모두 채운 이 키만의 마스크를 만든다."""
    x0, y0, x1, y1 = box
    src = mask.load()
    out = Image.new("L", mask.size, 0)
    op = out.load()
    for y in range(y0, y1 + 1):
        xs = [x for x in range(x0, x1 + 1) if src[x, y] > 128]
        for x in range(xs[0], xs[-1] + 1) if xs else ():
            op[x, y] = 255
    # 가장자리를 1px 정도 부드럽게 한다
    return out.filter(ImageFilter.GaussianBlur(0.8))


def find_objects(alpha: Image.Image, expected: int) -> list:
    """불투명한 픽셀이 모인 가로 구간을 찾아 물체별 [x0, y0, x1, y1]을 돌려준다."""
    w, h = alpha.size
    ap = alpha.load()
    col = [sum(1 for y in range(0, h, 2) if ap[x, y] > 128) for x in range(w)]
    runs, start = [], None
    for x in range(w + 1):
        filled = x < w and col[x] > 6
        if filled and start is None:
            start = x
        elif not filled and start is not None:
            if x - start > w * 0.03:
                runs.append((start, x - 1))
            start = None
    if len(runs) != expected:
        sys.exit(f"물체를 {expected}개 찾아야 하는데 {len(runs)}개를 찾았습니다. 배경이 깨끗이 지워졌는지 확인하세요.")
    boxes = []
    for x0, x1 in runs:
        rows = [y for y in range(h) if any(ap[x, y] > 128 for x in range(x0, x1 + 1, 3))]
        boxes.append([x0, rows[0], x1, rows[-1]])
    return boxes


def save_pair(im: Image.Image, path_png: Path, quality: int) -> None:
    path_png.parent.mkdir(parents=True, exist_ok=True)
    im.save(path_png)
    im.save(path_png.with_suffix(".webp"), "WEBP", quality=quality, method=6)


def update_assets_json(section: str, value: dict) -> Path:
    path = ASSETS / "assets.json"
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"version": 1}
    data[section] = value
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def cmd_keys(args) -> None:
    im = Image.open(args.image)
    if args.remove_bg or im.mode != "RGBA" or im.getextrema()[3][0] == 255:
        if not args.remove_bg:
            print("투명 배경이 없어 --remove-bg 방식으로 배경을 지웁니다.")
        raw = key_mask(im, args.dark_max, args.sat_min)
        boxes = find_objects(raw, len(KEY_NAMES))
        masks = [fill_rows(raw, b) for b in boxes]
    else:
        alpha = im.getchannel("A")
        boxes = find_objects(alpha, len(KEY_NAMES))
        masks = []
        for x0, y0, x1, y1 in boxes:
            own = Image.new("L", im.size, 0)
            own.paste(alpha.crop((x0, y0, x1 + 1, y1 + 1)), (x0, y0))
            masks.append(own)
    rgb = im.convert("RGB")

    # 올라온 키와 눌린 표현을 코드로 처리하므로, 네 키의 위·아래 끝을 똑같이 맞춰 자른다
    top = min(b[1] for b in boxes) - args.pad
    bottom = max(b[3] for b in boxes) + args.pad
    top, bottom = max(0, top), min(im.height - 1, bottom)
    rects = {}
    crops = []
    for name, (x0, _, x1, _), own in zip(KEY_NAMES, boxes, masks):
        box = (max(0, x0 - args.pad), top, min(im.width, x1 + 1 + args.pad), bottom + 1)
        layer = rgb.copy()
        layer.putalpha(own)  # 이 키만 남기고 옆 키·그림자는 투명하게
        crop = layer.crop(box)
        if args.height:
            crop = crop.resize((round(crop.width * args.height / crop.height), args.height), Image.LANCZOS)
        out = ASSETS / "deck" / f"key-{name}@2x.png"
        save_pair(crop, out, args.quality)
        rects[name] = {"file": f"deck/key-{name}@2x.webp", "size": list(crop.size)}
        crops.append(crop)
        print(f"  {name:5} {crop.size[0]}×{crop.size[1]}  → {out.with_suffix('.webp')}")

    widths = [c.width for c in crops]
    print(f"키 너비 차이: {max(widths) - min(widths)}px (작을수록 좋음)")
    # calibrate.html과 같은 형식으로 keys 항목만 고친다(다른 항목은 그대로 둔다)
    path = update_assets_json("keys", {
        "files": {n: r["file"] for n, r in rects.items()},
        "sizes": {n: r["size"] for n, r in rects.items()},
        "pressed": {"translateY": "1.5%", "brightness": 0.88},
    })
    print(f"좌표 기록: {path}")

    # 어두운 앱 배경 위에서 확인하는 미리 보기
    gap, pad = 24, 40
    sheet = Image.new("RGBA", (sum(widths) + gap * 3 + pad * 2, crops[0].height + pad * 2), (13, 13, 14, 255))
    x = pad
    for c in crops:
        sheet.alpha_composite(c, (x, pad))
        ImageDraw.Draw(sheet).rectangle([x, pad, x + c.width - 1, pad + c.height - 1], outline=(242, 119, 42, 255))
        x += c.width + gap
    preview = ROOT / "_preview" / "keys-preview.png"
    preview.parent.mkdir(parents=True, exist_ok=True)
    sheet.convert("RGB").save(preview)
    print(f"미리 보기: {preview} (주황 선이 자른 범위)")


def cmd_webp(args) -> None:
    im = Image.open(args.image)
    if args.width and im.width != args.width:
        im = im.resize((args.width, round(im.height * args.width / im.width)), Image.LANCZOS)
    out = Path(args.out) if args.out else Path(args.image).with_suffix(".webp")
    im.save(out, "WEBP", quality=args.quality, method=6)
    print(f"{out} {im.size[0]}×{im.size[1]} {out.stat().st_size // 1024}KB")


def main() -> None:
    ap = argparse.ArgumentParser(description="생성 이미지 후처리")
    sub = ap.add_subparsers(dest="cmd", required=True)

    k = sub.add_parser("keys", help="키 4개 이미지를 키별로 잘라 저장")
    k.add_argument("image")
    k.add_argument("--remove-bg", action="store_true", help="배경·그림자를 코드로 지움(투명 배경이 없으면 자동)")
    k.add_argument("--dark-max", type=int, default=112, help="키로 볼 최대 밝기(기본 112)")
    k.add_argument("--sat-min", type=float, default=0.3, help="키로 볼 최소 채도(기본 0.3, 주황 키용)")
    k.add_argument("--pad", type=int, default=12, help="자를 때 둘레 여백 px(기본 12)")
    k.add_argument("--height", type=int, default=0, help="잘라낸 키를 이 높이로 맞춤(0이면 그대로)")
    k.add_argument("--quality", type=int, default=90)
    k.set_defaults(func=cmd_keys)

    w = sub.add_parser("webp", help="PNG를 WebP로 변환")
    w.add_argument("image")
    w.add_argument("--width", type=int, default=0)
    w.add_argument("--out")
    w.add_argument("--quality", type=int, default=90)
    w.set_defaults(func=cmd_webp)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
