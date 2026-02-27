import json
import re
from pathlib import Path

_QUESTIONS = None

def _load():
    global _QUESTIONS
    if _QUESTIONS is not None:
        return _QUESTIONS

    json_path = Path(__file__).parent.parent.parent.parent / 'co_web_content' / 'co_18.json'
    with open(json_path, encoding='utf-8') as f:
        raw = json.load(f)

    questions = []
    for q in raw:
        text = q['question']
        image_filename = None

        match = re.search(r'\n\[image\]\s+co_web_content/co_18_images/(\S+)', text)
        if match:
            image_filename = match.group(1)
            text = text[:match.start()].strip()

        options = q['options']
        letters = ['A', 'B', 'C', 'D']
        options_with_letters = [
            {'letter': letters[i], 'text': opt}
            for i, opt in enumerate(options)
        ]

        questions.append({
            **q,
            'text': text,
            'image_filename': image_filename,
            'options_with_letters': options_with_letters,
        })

    _QUESTIONS = questions
    return _QUESTIONS


def get_all():
    return _load()


def get_by_id(question_no):
    questions = _load()
    for q in questions:
        if q['question_no'] == question_no:
            return q
    return None
