import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import List

import httpx
"""
Usage examples:
1) Minimal:
   python meme_post_template.py --meme-key zengxiaoxian --text-file text1.txt --output-base D:/tmp/out

2) With images + args JSON:
   python meme_post_template.py --meme-key zengxiaoxian --image D:/tmp/a.jpg --text "平时你打电子游戏吗" --args-json "{\"user_infos\":[]}" --output-base D:/tmp/out

3) Multiple texts + multiple images:
   python meme_post_template.py --meme-key zengxiaoxian --text-file text1.txt --text-file text2.txt --text "第三段文字" --image D:/tmp/a.jpg --image D:/tmp/b.png --output-base D:/tmp/out

4) Read args from UTF-8 file:
   python meme_post_template.py --meme-key zengxiaoxian --text-file text1.txt --args-file args.json --output-base D:/tmp/out


实用举例
python meme_post_template.py --image=d:/Claude/meme/marisa.jpg --meme-key wechat_pay --text v我50 --output-base D:/Claude/meme/
python meme_post_template.py --meme-key zengxiaoxian --text "平时你打电子游戏吗" --text "偶尔" --text "农药还是原神" --text "魔物娘" --output-base D:/Claude/meme/
"""

DEFAULT_BASE_URL = "http://127.0.0.1:2233"
DEFAULT_OUTPUT_BASE = "out"
DEFAULT_TIMEOUT = 60.0
DEFAULT_ENCODING = "utf-8"
DEFAULT_IMAGE_CONTENT_TYPE = "application/octet-stream"
TEXT_CONTENT_TYPE = "text/plain; charset=utf-8"
ARGS_CONTENT_TYPE = "application/json; charset=utf-8"

CONTENT_TYPE_TO_EXT = {
    "image/gif": "gif",
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/webp": "webp",
}


def detect_ext(content_type: str) -> str:
    ct = (content_type or "").lower()
    for mime, ext in CONTENT_TYPE_TO_EXT.items():
        if mime in ct:
            return ext
    return "bin"


def read_texts(direct_texts: List[str], text_files: List[Path]) -> List[str]:
    texts = list(direct_texts)
    for path in text_files:
        texts.append(path.read_text(encoding=DEFAULT_ENCODING).strip())
    return [t for t in texts if t]


def resolve_output_path(output_base: str, ext: str, meme_key: str) -> Path:
    raw = (output_base or "").strip()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    default_name = f"{meme_key}_{timestamp}.{ext}"

    if not raw:
        return Path(default_name)

    # Treat explicit directory-style values as output directory.
    if raw.endswith("/") or raw.endswith("\\"):
        output_dir = Path(raw)
        return output_dir / default_name

    base_path = Path(raw)
    if base_path.exists() and base_path.is_dir():
        return base_path / default_name

    # `Path("D:/tmp/.")` also means a directory.
    if base_path.name in {"", "."}:
        return base_path / default_name

    # Keep user-provided base file name and append detected extension.
    return Path(f"{raw}.{ext}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="POST meme-generator API with UTF-8 texts and auto output extension."
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--meme-key", required=True)
    parser.add_argument("--text", action="append", default=[])
    parser.add_argument("--text-file", action="append", default=[])
    parser.add_argument("--image", action="append", default=[])
    parser.add_argument("--args-json", default="")
    parser.add_argument("--args-file", default="")
    parser.add_argument("--output-base", default=DEFAULT_OUTPUT_BASE)
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    args = parser.parse_args()

    # Collect texts from direct CLI values and UTF-8 files.
    text_files = [Path(p) for p in args.text_file]
    texts = read_texts(args.text, text_files)

    if args.args_file and args.args_json:
        raise ValueError("Use only one of --args-file or --args-json.")

    args_payload = ""
    if args.args_file:
        args_payload = Path(args.args_file).read_text(encoding=DEFAULT_ENCODING).strip()
    elif args.args_json:
        args_payload = args.args_json.strip()

    url = f"{args.base_url.rstrip('/')}/memes/{args.meme_key}/"

    # Build multipart form fields for images/texts/args.
    files = []
    opened_files = []
    try:
        for image_path in args.image:
            p = Path(image_path)
            f = p.open("rb")
            opened_files.append(f)
            files.append(
                (
                    "images",
                    (p.name, f, DEFAULT_IMAGE_CONTENT_TYPE),
                )
            )

        for text in texts:
            files.append(("texts", (None, text.encode(DEFAULT_ENCODING), TEXT_CONTENT_TYPE)))

        if args_payload:
            # Validate that args payload is valid JSON before sending.
            json.loads(args_payload)
            files.append(("args", (None, args_payload.encode(DEFAULT_ENCODING), ARGS_CONTENT_TYPE)))

        # Send request and let server decide output media type.
        with httpx.Client(timeout=args.timeout) as client:
            resp = client.post(url, files=files)

        content_type = resp.headers.get("content-type", "")
        ext = detect_ext(content_type)
        output_path = resolve_output_path(args.output_base, ext, args.meme_key)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(resp.content)

        print(f"status: {resp.status_code}")
        print(f"content-type: {content_type or 'unknown'}")
        print(f"saved: {output_path.resolve()}")

        if resp.status_code >= 400:
            print("response preview:")
            try:
                print(resp.text[:500])
            except UnicodeDecodeError:
                print(resp.content[:200])
    finally:
        for f in opened_files:
            f.close()


if __name__ == "__main__":
    main()
