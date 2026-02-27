import json
import re
from .practices import get_json_file

_CACHE = {}  # slug → list of question dicts


def _load(slug):
    if slug in _CACHE:
        return _CACHE[slug]

    json_path = get_json_file(slug)
    if json_path is None:
        raise FileNotFoundError(f'No questions JSON found for practice "{slug}"')

    with open(json_path, encoding='utf-8') as f:
        raw = json.load(f)

    questions = []
    for q in raw:
        text = q['question']
        image_filename = None

        # Extract image filename from any [image] marker, regardless of path prefix
        match = re.search(r'\n\[image\]\s+\S+/(\S+)', text)
        if match:
            image_filename = match.group(1)
            text = text[:match.start()].strip()

        letters = ['A', 'B', 'C', 'D']
        options_with_letters = [
            {'letter': letters[i], 'text': opt}
            for i, opt in enumerate(q['options'])
        ]

        questions.append({
            **q,
            'text': text,
            'image_filename': image_filename,
            'options_with_letters': options_with_letters,
        })

    _CACHE[slug] = questions
    return questions


def get_all(slug):
    return _load(slug)


def get_by_id(slug, question_no):
    for q in _load(slug):
        if q['question_no'] == question_no:
            return q
    return None
