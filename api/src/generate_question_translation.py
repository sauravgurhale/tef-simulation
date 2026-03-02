"""Translate question and options fields in a CO JSON file from French to English.

Usage:
    python generate_question_translation.py --json co_web_content/practice_1/co_1.json

The script reads the JSON, translates each question's `question` and `options` fields
to English using the Claude API, adds `english_question` and `english_options` keys,
and writes the file in-place.
"""

import argparse
import json
import os
from typing import Any

import anthropic
from dotenv import load_dotenv

load_dotenv()


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


def _is_letter_option(option: str) -> bool:
    """Return True if the option is a single letter like A, B, C, D."""
    return option.strip() in {"A", "B", "C", "D", "E", "F"}


def _has_image_path(option: str) -> bool:
    """Return True if the option contains an image reference."""
    return "[image]" in option or option.strip().startswith("@")


def translate_question(client: anthropic.Anthropic, question: str) -> str:
    # Strip image references for translation but preserve them in output
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": (
                    "Translate the following French question to English. "
                    "Preserve any image references like '[image] @filename' exactly as-is. "
                    "Return only the translated text, no extra commentary.\n\n"
                    f"{question}"
                ),
            }
        ],
    )
    return message.content[0].text.strip()


def translate_options(
    client: anthropic.Anthropic,
    options: list[str],
) -> list[str]:
    # Build a list of only the options that need translation
    indices_to_translate = [
        i for i, o in enumerate(options)
        if not _is_letter_option(o) and not _has_image_path(o)
    ]

    if not indices_to_translate:
        return options

    subset = [options[i] for i in indices_to_translate]

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": (
                    "Translate the following French answer options to English. "
                    "Return JSON only: an array of strings in the same order and same length.\n\n"
                    f"Options:\n{json.dumps(subset, ensure_ascii=False)}"
                ),
            }
        ],
    )

    model_output = message.content[0].text.strip()
    translated_subset = _extract_json_array(model_output)

    if len(translated_subset) != len(subset):
        raise ValueError(
            "Model returned a different number of translated options than input."
        )

    result = list(options)
    for idx, translated_text in zip(indices_to_translate, translated_subset):
        result[idx] = translated_text
    return result


def generate_question_translations(json_path: str) -> None:
    with open(json_path, "r", encoding="utf-8") as f:
        questions = json.load(f)

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    for i, question in enumerate(questions, start=1):
        french_question = question.get("question", "")
        options = question.get("options", [])

        if not french_question:
            question["english_question"] = ""
            question["english_options"] = options
            continue

        print(f"Translating question {i}/{len(questions)}...")
        question["english_question"] = translate_question(client, french_question)
        question["english_options"] = translate_options(client, options)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

    print(f"Done. Updated {json_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Add English question/options translations to a CO JSON file"
    )
    parser.add_argument(
        "--json",
        required=True,
        help="Path to the JSON file to update (e.g. co_web_content/practice_1/co_1.json)",
    )
    args = parser.parse_args()
    generate_question_translations(args.json)


if __name__ == "__main__":
    main()
