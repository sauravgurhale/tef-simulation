"""
Add AI-generated highlights to CO (Compréhension Orale) questions.

Reads the JSON file, updates the `highlights` field on each question in-place,
and writes the result back to the same file.

Usage:
    python api/src/add_highlights.py \
        --input co_web_content/practice_18/co_18.json \
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
    "You are helping French language learners study for the TEF oral comprehension exam. "
    "Your task is to identify ALL key evidence in the audio transcript that a student must "
    "notice to select the correct answer and confidently reject the incorrect ones. "
    "Every string you return must be an EXACT verbatim substring of the transcript — "
    "do not paraphrase, translate, or alter any text."
)

IMAGE_QUESTION_PROMPT = """\
This is a TEF oral comprehension question where the student must match the audio to one \
of four images (A, B, C, D). The correct image is {right_option}.

Identify ALL words and phrases in the transcript that visually describe the scene — \
including objects, people, locations, and actions — that help identify this specific image \
and distinguish it from the other three options.

Rules:
- Return ONLY a JSON array of exact verbatim strings from the transcript
- Cover every descriptive element relevant to the visual scene
- Prefer short, specific phrases; avoid quoting unnecessary surrounding words
- No explanation, no commentary

Transcript: {transcript}\
"""

TEXT_OPTION_PROMPT = """\
This is a TEF oral comprehension multiple-choice question. Identify ALL key phrases in \
the transcript that a student must notice to answer correctly.

Include phrases that:
1. Directly state or imply the correct answer
2. Contain negations, conditionals, or qualifiers that rule out wrong options \
   (e.g. "ne … pas", "seulement", "avant de", "à condition que", "jamais")
3. Contain key quantities, frequencies, or time markers that differentiate the correct \
   answer from distractors
4. Express intent, obligation, opinion, or certainty relevant to the correct answer

Rules:
- Return ONLY a JSON array of exact verbatim strings from the transcript
- Include ALL relevant phrases — err on the side of completeness
- Each string must be an exact substring of the transcript
- No explanation, no commentary

Transcript: {transcript}
Question: {question}
Options:
{options_block}
Correct answer: {right_option}. {correct_option_text}\
"""


def normalize_quotes(s: str) -> str:
    """Replace curly apostrophes/quotes with straight ones for matching."""
    return s.replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')


def fix_highlight(transcript: str, highlight: str) -> str | None:
    """Return the verbatim transcript span that matches highlight, or None."""
    if highlight in transcript:
        return highlight
    norm_t = normalize_quotes(transcript)
    norm_h = normalize_quotes(highlight)
    idx = norm_t.find(norm_h)
    if idx != -1:
        return transcript[idx: idx + len(norm_h)]
    idx = norm_t.lower().find(norm_h.lower())
    if idx != -1:
        return transcript[idx: idx + len(norm_h)]
    return None


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
        max_tokens=1024,
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

    # Ensure every highlight is a verbatim substring; fix quote mismatches, drop hallucinations.
    transcript = question["audio_transcript"]
    verified = []
    for h in highlights:
        fixed = fix_highlight(transcript, h)
        if fixed:
            verified.append(fixed)
        else:
            print(f"  (dropped non-verbatim: {h!r})", flush=True)
    return verified


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Update highlights in a CO questions JSON file (in-place)."
    )
    parser.add_argument("--input", required=True, help="Path to JSON file (updated in-place)")
    parser.add_argument(
        "--model",
        default="claude-haiku-4-5-20251001",
        help="Claude model ID to use (default: claude-haiku-4-5-20251001)",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    with open(input_path, encoding="utf-8") as f:
        questions = json.load(f)

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    for q in questions:
        qno = q.get("question_no", "?")
        print(f"Processing Q{qno}...", end=" ", flush=True)
        try:
            highlights = extract_highlights(client, q, args.model)
            print(f"OK ({len(highlights)} highlight(s))")
        except Exception as exc:
            print(f"WARNING: could not parse highlights — {exc}")
            highlights = []

        q["highlights"] = highlights

    with open(input_path, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

    print(f"\nUpdated {len(questions)} questions in {input_path}")


if __name__ == "__main__":
    main()
