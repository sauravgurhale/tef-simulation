"""Parse a CE HTML page where questions are embedded in the lp_quiz_js_data JS variable.

This covers pages saved before LearnPress renders the quiz client-side — the questions
live in a <script> block rather than as rendered HTML divs.

Usage:
    python api/src/generate_ce_json_lp.py ce_web_content/ce_2/ce_2.html
    python api/src/generate_ce_json_lp.py ce_web_content/ce_2/ce_2.html --output ce_web_content/ce_2/ce_2.json
"""

import argparse
import json
import re
import struct
import urllib.request
import zlib
from pathlib import Path

from bs4 import BeautifulSoup

LETTERS = ["A", "B", "C", "D"]


def extract_lp_quiz_data(html: str) -> list[dict]:
    """Extract and return the questions array from the lp_quiz_js_data JS variable."""
    m = re.search(r"var lp_quiz_js_data\s*=\s*(\{.*?\});\s*\n", html, re.DOTALL)
    if not m:
        raise ValueError("Could not find lp_quiz_js_data variable in HTML.")
    data = json.loads(m.group(1))
    return data["data"]["questions"]


def extract_passage(content_html: str) -> str:
    """Convert passage HTML to plain text.

    <p> blocks joined with double newlines; <br> becomes single newline;
    HTML entities decoded; indentation whitespace collapsed.
    """
    soup = BeautifulSoup(content_html, "html.parser")
    paragraphs = []
    for p in soup.find_all("p"):
        for br in p.find_all("br"):
            br.replace_with("|||BR|||")
        text = " ".join(p.get_text(separator=" ").split())
        text = text.replace("|||BR|||", "\n")
        lines = [line.strip() for line in text.split("\n")]
        text = "\n".join(lines).strip()
        if text:
            paragraphs.append(text)
    return "\n\n".join(paragraphs)


def _make_dummy_png(path: Path) -> None:
    """Create a 1×1 grey PNG using stdlib only (no Pillow)."""

    def png_chunk(name: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(name + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + name + data + struct.pack(">I", crc)

    signature = b"\x89PNG\r\n\x1a\n"
    ihdr = png_chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
    raw = b"\x00\x80\x80\x80"
    idat = png_chunk(b"IDAT", zlib.compress(raw))
    iend = png_chunk(b"IEND", b"")
    path.write_bytes(signature + ihdr + idat + iend)


def download_image(src: str, assets_dir: Path) -> str:
    """Download image to assets_dir; return relative path like 'assets/filename.png'.

    On failure, creates a 1×1 grey dummy PNG and returns 'assets/dummy_image.png'.
    """
    assets_dir.mkdir(parents=True, exist_ok=True)
    filename = src.split("/")[-1].split("?")[0]
    dest = assets_dir / filename
    try:
        urllib.request.urlretrieve(src, dest)
        print(f"  Downloaded image: {filename}")
        return f"assets/{filename}"
    except Exception as e:
        print(f"  WARNING: failed to download {src}: {e}. Using dummy image.")
        dummy = assets_dir / "dummy_image.png"
        _make_dummy_png(dummy)
        return "assets/dummy_image.png"


def parse_question(q: dict, question_no: int, assets_dir: Path) -> dict:
    """Convert one lp_quiz_js_data question dict into the CE JSON schema dict."""
    # --- passage ---
    passage = extract_passage(q.get("content", ""))

    # --- question text + image ---
    title_html = q.get("title", "")
    image_path = None

    title_soup = BeautifulSoup(title_html, "html.parser")
    img_tag = title_soup.find("img")
    if img_tag:
        src = img_tag.get("src", "")
        if src:
            image_path = download_image(src, assets_dir)
        img_tag.decompose()

    # Strip leftover <br> tags and normalize whitespace
    for br in title_soup.find_all("br"):
        br.replace_with(" ")
    question_text = " ".join(title_soup.get_text(separator=" ").split())

    # --- options (already plain text) ---
    options = [o["title"] for o in q.get("options", [])]

    # --- right_option ---
    right_option = None
    for i, o in enumerate(q.get("options", [])):
        if o.get("is_true") == "yes":
            right_option = LETTERS[i]
            break

    # --- explanation (already plain text) ---
    explanation = " ".join(q.get("explanation", "").split())

    return {
        "question_no": question_no,
        "passage": passage,
        "question": question_text,
        "options": options,
        "right_option": right_option,
        "image_path": image_path,
        "explanation": explanation,
    }


def assign_groups(questions: list[dict]) -> None:
    """Add 'group' field in-place based on consecutive identical passage text."""
    group = 1
    prev_passage = None
    for q in questions:
        if q["passage"] != prev_passage:
            if prev_passage is not None:
                group += 1
            prev_passage = q["passage"]
        q["group"] = group


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Parse a CE HTML page (lp_quiz_js_data format) and produce a CE JSON file"
    )
    parser.add_argument(
        "html",
        help="Path to the CE HTML file (e.g. ce_web_content/ce_2/ce_2.html)",
    )
    parser.add_argument(
        "--output",
        help="Output JSON path (default: same directory as HTML, .html → .json)",
    )
    args = parser.parse_args()

    html_path = Path(args.html)
    output_path = Path(args.output) if args.output else html_path.with_suffix(".json")
    assets_dir = html_path.parent / "assets"

    print(f"Parsing {html_path}...")
    html = html_path.read_text(encoding="utf-8")
    raw_questions = extract_lp_quiz_data(html)

    questions = [
        parse_question(q, i + 1, assets_dir) for i, q in enumerate(raw_questions)
    ]
    assign_groups(questions)

    # Reorder fields for readability
    ordered = [
        {
            "question_no": q["question_no"],
            "group": q["group"],
            "passage": q["passage"],
            "question": q["question"],
            "options": q["options"],
            "right_option": q["right_option"],
            "image_path": q["image_path"],
            "explanation": q["explanation"],
        }
        for q in questions
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(ordered, f, ensure_ascii=False, indent=2)

    print(f"Done. {len(ordered)} questions written to {output_path}")

    missing_right = [q["question_no"] for q in ordered if q["right_option"] is None]
    if missing_right:
        print(f"WARNING: missing right_option for questions: {missing_right}")

    images = [q["question_no"] for q in ordered if q["image_path"]]
    if images:
        print(f"Questions with images: {images}")


if __name__ == "__main__":
    main()
