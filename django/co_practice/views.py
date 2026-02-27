import json
from django.shortcuts import render
from django.http import Http404
from django.utils.safestring import mark_safe
from .data.questions import get_by_id, get_all
from .data.audio_map import AUDIO_MAP

GROUPS = [
    {'label': 'Groupe 1 — Conversations courtes (images)', 'questions': list(range(1, 5))},
    {'label': 'Groupe 2 — Messages courts',                'questions': list(range(5, 9))},
    {'label': 'Groupe 3 — Messages téléphoniques',         'questions': list(range(9, 15))},
    {'label': 'Groupe 4 — Annonces radio',                 'questions': list(range(15, 18))},
    {'label': 'Groupe 5 — Conversations longues',          'questions': list(range(18, 21))},
    {'label': 'Groupe 6 — Bulletins d\'information',       'questions': list(range(21, 23))},
    {'label': 'Groupe 7 — Dialogues (audio partagé)',      'questions': list(range(23, 31))},
    {'label': 'Groupe 8 — Émissions',                      'questions': list(range(31, 41))},
]

AUDIO_BASE = 'co_practice/audio/co_18_com/'
IMAGE_BASE = 'co_practice/images/'


def index(request):
    return render(request, 'co_practice/index.html', {'groups': GROUPS})


def results(request):
    correct_answers = {q['question_no']: q['right_option'] for q in get_all()}
    return render(request, 'co_practice/results.html', {
        'groups': GROUPS,
        'correct_answers_json': mark_safe(json.dumps(correct_answers)),
    })


def question(request, question_id):
    if not 1 <= question_id <= 40:
        raise Http404

    q = get_by_id(question_id)
    if q is None:
        raise Http404

    audio_info = AUDIO_MAP[question_id]

    img_path = None
    if q['image_filename']:
        img_path = IMAGE_BASE + q['image_filename']

    audio_paths = {
        'intro': AUDIO_BASE + audio_info['intro'] if audio_info['intro'] else None,
        'intro_label': audio_info['intro_label'],
        'main': AUDIO_BASE + audio_info['main'],
        'shared_with': audio_info['shared_with'],
    }

    prev_id = question_id - 1 if question_id > 1 else None
    next_id = question_id + 1 if question_id < 40 else None

    return render(request, 'co_practice/question.html', {
        'question': q,
        'img_path': img_path,
        'audio_paths': audio_paths,
        'prev_id': prev_id,
        'next_id': next_id,
    })
