"""
Add AI-generated highlights to CO (Compréhension Orale) questions.

Usage:
    python api/src/add_highlights.py \
        --input co_web_content/co_18.json \
        --output co_web_content/co_18_highlighted.json \
        [--model claude-haiku-4-5-20251001]
"""

import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv
import anthropic

# Load .env from project root (two levels up from api/src/)
load_dotenv(Path(__file__).parent.parent.parent / ".env")

SYSTEM_PROMPT = (
    "You are helping French language learners identify the key evidence in a listening "
    "transcript that leads to the correct answer. Always quote text EXACTLY as it appears."
)

IMAGE_QUESTION_PROMPT = """\
This question asks the student to match the audio to one of four images (A/B/C/D). \
The correct image is {right_option}. Identify the key noun or descriptive phrase(s) in \
the transcript that visually identify the scene. Return ONLY a JSON array of exact verbatim \
quoted strings (1–2 items), no explanation.

Transcript: {transcript}\
"""

TEXT_OPTION_PROMPT = """\
Given this French audio transcript and multiple choice question, identify the EXACT verbatim \
phrase(s) from the transcript that most directly support the correct answer. Return ONLY a \
JSON array of quoted strings (1–3 items), no explanation.

Transcript: {transcript}
Question: {question}
Options:
{options_block}
Correct answer: {right_option}. {correct_option_text}\
"""


def is_image_question(options: list[str]) -> bool:
    """Return True if all options are single letters (image-type question)."""
    return all(len(o.strip()) == 1 and o.strip().isalpha() for o in options)


def build_prompt(question: dict) -> str:
    options = question["options"]
    transcript = question["audio_transcript"]
    right_option = question["right_option"]

    if is_image_question(options):
        return IMAGE_QUESTION_PROMPT.format(
            right_option=right_option,
            transcript=transcript,
        )

    # Map letter -> option text
    letter_map = {chr(ord("A") + i): opt for i, opt in enumerate(options)}
    options_block = "\n".join(
        f"  {chr(ord('A') + i)}. {opt}" for i, opt in enumerate(options)
    )
    correct_option_text = letter_map.get(right_option, "")

    return TEXT_OPTION_PROMPT.format(
        transcript=transcript,
        question=question.get("question", ""),
        options_block=options_block,
        right_option=right_option,
        correct_option_text=correct_option_text,
    )


def extract_highlights(
    client: anthropic.Anthropic, question: dict, model: str
) -> list[str]:
    prompt = build_prompt(question)
    response = client.messages.create(
        model=model,
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip()

    # Find JSON array in the response
    start = raw.find("[")
    end = raw.rfind("]")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON array found in response: {raw!r}")

    highlights = json.loads(raw[start: end + 1])
    if not isinstance(highlights, list) or not all(
        isinstance(h, str) for h in highlights
    ):
        raise ValueError(f"Expected list of strings, got: {highlights!r}")

    return highlights


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Add LLM-generated highlights to CO questions."
    )
    parser.add_argument("--input", required=True, help="Path to input JSON file")
    parser.add_argument("--output", required=True, help="Path to output JSON file")
    parser.add_argument(
        "--model",
        default="claude-haiku-4-5-20251001",
        help="Claude model ID to use (default: claude-haiku-4-5-20251001)",
    )
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as f:
        questions = json.load(f)

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    enriched = []
    for q in questions:
        qno = q.get("question_no", "?")
        print(f"Processing Q{qno}...", end=" ", flush=True)
        try:
            highlights = extract_highlights(client, q, args.model)
            print(f"OK ({len(highlights)} highlight(s))")
        except Exception as exc:
            print(f"WARNING: could not parse highlights — {exc}")
            highlights = []

        enriched.append({**q, "highlights": highlights})

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)

    print(f"\nWrote {len(enriched)} questions to {args.output}")


if __name__ == "__main__":
    main()
