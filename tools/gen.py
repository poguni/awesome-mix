#!/usr/bin/env python3
"""OpenRouter API로 Awesome Mix 실사 이미지 레이어를 생성한다.

외부 패키지 없이 파이썬 3.9 이상에서 동작한다. API 키는 환경 변수로만 받는다.

    export OPENROUTER_API_KEY="sk-or-..."
    python3 gen.py --list
    python3 gen.py IMG-01 --count 2
    python3 gen.py IMG-02 --ref out/IMG-01_20261028-101500_1.png
    python3 gen.py FIX-text --ref out/IMG-01_20261028-101500_1.png
"""
import argparse
import base64
import datetime
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "google/gemini-3.1-flash-image"
ROOT = Path(__file__).resolve().parent


def load_prompts() -> dict:
    return json.loads((ROOT / "prompts.json").read_text(encoding="utf-8"))


def build_prompt(spec: dict, styles: dict, keep: str) -> str:
    parts = []
    if spec.get("edit"):
        parts.append(keep)
    parts.append(spec["prompt"].strip())
    if spec.get("aspect"):
        parts.append(f"{spec['aspect']} aspect ratio.")
    style = styles.get(spec.get("style", "product"), "")
    text = " ".join(parts)
    return f"{text}\n{style}" if style else text


def data_url(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


def build_payload(model: str, prompt: str, refs: list, aspect: str, size: str) -> dict:
    content = [{"type": "text", "text": prompt}]
    content += [{"type": "image_url", "image_url": {"url": data_url(p)}} for p in refs]
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": content}],
        "modalities": ["image", "text"],
    }
    image_config = {}
    if aspect:
        image_config["aspect_ratio"] = aspect
    if size:
        image_config["image_size"] = size
    if image_config:
        payload["image_config"] = image_config
    return payload


def call_api(payload: dict, key: str) -> dict:
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "X-Title": "Awesome Mix image layers",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as res:
            return json.loads(res.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"API 오류 {e.code}: {e.read().decode(errors='replace')[:800]}")


def extract_images(result: dict) -> list:
    """응답에서 data URL 이미지들을 꺼낸다."""
    message = (result.get("choices") or [{}])[0].get("message") or {}
    urls = [img.get("image_url", {}).get("url") for img in message.get("images") or []]
    content = message.get("content")
    if isinstance(content, list):
        urls += [part.get("image_url", {}).get("url") for part in content if part.get("type") == "image_url"]
    return [u for u in urls if u and u.startswith("data:")]


def save_image(url: str, stem: str) -> Path:
    header, b64 = url.split(",", 1)
    mime = header[5:].split(";")[0]
    ext = mimetypes.guess_extension(mime) or ".png"
    out = ROOT / "out" / f"{stem}{'.png' if ext == '.png' else ext}"
    out.parent.mkdir(exist_ok=True)
    out.write_bytes(base64.b64decode(b64))
    return out


def main() -> None:
    data = load_prompts()
    prompts, styles, keep = data["prompts"], data["styles"], data["keep"]

    ap = argparse.ArgumentParser(description="OpenRouter로 이미지 레이어 생성")
    ap.add_argument("id", nargs="?", help="prompts.json의 ID (예: IMG-01)")
    ap.add_argument("--ref", action="append", default=[], type=Path, help="참고 이미지 경로(여러 번 가능)")
    ap.add_argument("--count", type=int, default=1, help="생성 횟수(기본 1)")
    ap.add_argument("--model", default=os.environ.get("OPENROUTER_IMAGE_MODEL", DEFAULT_MODEL))
    ap.add_argument("--size", default="2K", help="image_size: 1K, 2K, 4K 등. 빈 값이면 보내지 않음")
    ap.add_argument("--extra", default="", help="프롬프트 끝에 덧붙일 문장")
    ap.add_argument("--list", action="store_true", help="프롬프트 ID 목록 보기")
    ap.add_argument("--dry-run", action="store_true", help="API를 부르지 않고 요청 내용만 출력")
    args = ap.parse_args()

    if args.list or not args.id:
        for pid, spec in prompts.items():
            print(f"{pid:12} {spec['title']}")
        return
    if args.id not in prompts:
        sys.exit(f"알 수 없는 ID: {args.id} (--list로 확인)")

    spec = prompts[args.id]
    if spec.get("needs_ref") and not args.ref:
        sys.exit(f"{args.id}는 참고 이미지가 필요합니다: --ref <{spec['needs_ref']} 결과 파일>")
    for p in args.ref:
        if not p.is_file():
            sys.exit(f"참고 이미지가 없습니다: {p}")

    prompt = build_prompt(spec, styles, keep)
    if args.extra:
        prompt = f"{prompt}\n{args.extra}"
    payload = build_payload(args.model, prompt, args.ref, spec.get("aspect", ""), args.size)

    if args.dry_run:
        shown = json.loads(json.dumps(payload))
        for part in shown["messages"][0]["content"]:
            if part["type"] == "image_url":
                part["image_url"]["url"] = part["image_url"]["url"][:40] + "…"
        print(json.dumps(shown, ensure_ascii=False, indent=2))
        return

    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        sys.exit("환경 변수 OPENROUTER_API_KEY를 먼저 설정하세요.")

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    total_cost = 0.0
    for i in range(1, args.count + 1):
        print(f"[{i}/{args.count}] {args.id} 생성 중… ({args.model})")
        result = call_api(payload, key)
        images = extract_images(result)
        cost = (result.get("usage") or {}).get("cost")
        if isinstance(cost, (int, float)):
            total_cost += cost
        if not images:
            text = ((result.get("choices") or [{}])[0].get("message") or {}).get("content")
            print(f"  이미지가 오지 않았습니다. 모델 응답: {str(text)[:400]}")
            continue
        for j, url in enumerate(images, 1):
            suffix = f"{i}" if len(images) == 1 else f"{i}-{j}"
            print(f"  저장: {save_image(url, f'{args.id}_{stamp}_{suffix}')}")
    if total_cost:
        print(f"청구 비용 합계: ${total_cost:.4f}")


if __name__ == "__main__":
    main()
