"""Parse a CE (Compréhension Écrite) HTML quiz page and produce a CE JSON file.

Usage:
    python api/src/generate_ce_json.py ce_web_content/ce_1/ce_1.html
    python api/src/generate_ce_json.py ce_web_content/ce_1/ce_1.html --output ce_web_content/ce_1/ce_1.json
"""

import argparse
import json
import struct
import zlib
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup

LETTERS = ["A", "B", "C", "D"]


def extract_text(el) -> str:
    """Return whitespace-normalized text from a BeautifulSoup element."""
    return " ".join(el.get_text(separator=" ").split())


def extract_passage(content_div) -> str:
    """Extract passage text from question-content div.

    Joins <p> elements with double newlines; <br> tags become single newlines.
    HTML indentation whitespace is collapsed within each line.
    """
    paragraphs = []
    for p in content_div.find_all("p"):
        # Replace <br> with a sentinel to preserve intended line breaks
        for br in p.find_all("br"):
            br.replace_with("|||BR|||")
        # Collapse HTML whitespace using separator=" "
        text = " ".join(p.get_text(separator=" ").split())
        # Restore intended newlines
        text = text.replace("|||BR|||", "\n")
        # Strip each line
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
    raw = b"\x00\x80\x80\x80"  # filter byte + RGB grey pixel
    idat = png_chunk(b"IDAT", zlib.compress(raw))
    iend = png_chunk(b"IEND", b"")
    path.write_bytes(signature + ihdr + idat + iend)


def download_image(src: str, assets_dir: Path) -> str:
    """Download image to assets_dir; return relative path like 'assets/filename.png'.

    On any failure, creates a 1×1 grey dummy PNG and returns 'assets/dummy_image.png'.
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


def parse_ce_html(html_path: Path, assets_dir: Path) -> list[dict]:
    """Parse all questions from the CE HTML file; return list of question dicts."""
    html = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    question_divs = soup.find_all(
        "div", class_="question-single_choice"
    )

    questions = []
    for q_div in question_divs:
        # --- question_no ---
        index_span = q_div.find("span", class_="question-index")
        if not index_span:
            continue
        question_no = int(index_span.get_text(strip=True).rstrip("."))

        # --- image: find before decomposing anything ---
        img_tag = q_div.find("img")
        image_path = None
        if img_tag:
            src = img_tag.get("src", "")
            if src:
                image_path = download_image(src, assets_dir)
            img_tag.decompose()

        # --- question text (second span in h4.question-title, text only) ---
        title_h4 = q_div.find("h4", class_="question-title")
        spans = title_h4.find_all("span", recursive=False)
        # spans[0] = question-index span, spans[1] = question text span
        question_text = extract_text(spans[1])

        # --- passage ---
        content_div = q_div.find("div", class_="question-content")
        passage = extract_passage(content_div) if content_div else ""

        # --- options ---
        option_labels = q_div.find_all("label", class_="option-title")
        options = [extract_text(lbl) for lbl in option_labels]

        # --- right_option ---
        answer_lis = q_div.find_all("li", class_="answer-option")
        right_option = None
        for i, li in enumerate(answer_lis):
            if "answer-correct" in (li.get("class") or []):
                right_option = LETTERS[i]
                break

        # --- explanation ---
        explanation_div = q_div.find("div", class_="question-explanation-content")
        explanation = ""
        if explanation_div:
            inner_div = explanation_div.find("div")
            if inner_div:
                explanation = " ".join(inner_div.get_text(separator=" ").split())

        questions.append({
            "question_no": question_no,
            "passage": passage,
            "question": question_text,
            "options": options,
            "right_option": right_option,
            "image_path": image_path,
            "explanation": explanation,
        })

    return questions


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
        description="Parse a CE HTML quiz page and produce a CE JSON file"
    )
    parser.add_argument(
        "html",
        help="Path to the CE HTML file (e.g. ce_web_content/ce_1/ce_1.html)",
    )
    parser.add_argument(
        "--output",
        help="Output JSON path (default: same directory as HTML, replacing .html with .json)",
    )
    args = parser.parse_args()

    html_path = Path(args.html)
    output_path = Path(args.output) if args.output else html_path.with_suffix(".json")
    assets_dir = html_path.parent / "assets"

    print(f"Parsing {html_path}...")
    questions = parse_ce_html(html_path, assets_dir)
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
