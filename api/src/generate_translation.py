"""Translate audio_transcript fields in a CO JSON file from French to English.

Usage:
    python generate_translation.py --json co_web_content/practice_1/co_1.json

The script reads the JSON, translates each question's audio_transcript to English
using the Claude API, adds an english_translation key, and writes the file in-place.
"""

import argparse
import json
import os
from typing import Any

import anthropic
from dotenv import load_dotenv

load_dotenv()


def translate_transcript(client: anthropic.Anthropic, transcript: str) -> str:
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": (
                    "Translate the following French audio transcript to English. "
                    "Return only the translated text, no extra commentary.\n\n"
                    f"{transcript}"
                ),
            }
        ],
    )
    return message.content[0].text.strip()


def _extract_json_array(raw_text: str) -> list[str]:
    text = raw_text.strip()

    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            text = "\n".join(lines[1:-1]).strip()

    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1 or end < start:
        raise ValueError("Model response did not contain a JSON array.")

    parsed = json.loads(text[start : end + 1])
    if not isinstance(parsed, list):
        raise ValueError("Model response is not a JSON array.")
    return [str(item).strip() for item in parsed]


def translate_highlights(
    client: anthropic.Anthropic,
    transcript: str,
    english_translation: str,
    highlights: list[Any],
) -> list[str]:
    if not highlights:
        return []

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": (
                    "You are given:\n"
                    "1) A French transcript.\n"
                    "2) Its English translation.\n"
                    "3) French highlight phrases.\n\n"
                    "Task:\n"
                    "- For each French highlight, return the matching English phrase.\n"
                    "- Prefer exact wording from the provided English translation.\n"
                    "- Keep output concise.\n"
                    "- Return JSON only: an array of strings in the same order and same length.\n\n"
                    f"French transcript:\n{transcript}\n\n"
                    f"English translation:\n{english_translation}\n\n"
                    f"French highlights:\n{json.dumps(highlights, ensure_ascii=False)}"
                ),
            }
        ],
    )

    model_output = message.content[0].text.strip()
    translated_highlights = _extract_json_array(model_output)

    if len(translated_highlights) != len(highlights):
        raise ValueError(
            "Model returned a different number of translated highlights than input."
        )
    return translated_highlights


def generate_translations(json_path: str) -> None:
    with open(json_path, "r", encoding="utf-8") as f:
        questions = json.load(f)

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    for i, question in enumerate(questions, start=1):
        transcript = question.get("audio_transcript", "")
        highlights = question.get("highlights", [])
        if not transcript:
            question["english_translation"] = ""
            question["english_translation_highlights"] = []
            continue

        print(f"Translating question {i}/{len(questions)}...")
        english_translation = translate_transcript(client, transcript)
        question["english_translation"] = english_translation
        question["english_translation_highlights"] = translate_highlights(
            client=client,
            transcript=transcript,
            english_translation=english_translation,
            highlights=highlights,
        )

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

    print(f"Done. Updated {json_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Add English translations to a CO JSON file"
    )
    parser.add_argument(
        "--json",
        required=True,
        help="Path to the JSON file to update (e.g. co_web_content/practice_1/co_1.json)",
    )
    args = parser.parse_args()
    generate_translations(args.json)


if __name__ == "__main__":
    main()
