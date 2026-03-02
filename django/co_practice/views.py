from django.shortcuts import render
from django.http import Http404
from django.utils.html import escape
from django.utils.safestring import mark_safe

from .data.questions import get_by_id, get_all
from .data.audio_maps import get_audio_map
from .data.practices import discover_practices, get_practice_folder, GROUPS, get_audio_mode


def _highlighted_transcript(transcript, highlights):
    """Return transcript as safe HTML with highlight phrases wrapped in <mark>."""
    if not highlights:
        return escape(transcript)

    ranges = []
    for phrase in highlights:
        pos = transcript.find(phrase)
        if pos != -1:
            ranges.append((pos, pos + len(phrase)))

    if not ranges:
        return escape(transcript)

    ranges.sort()
    merged = [list(ranges[0])]
    for start, end in ranges[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])

    parts = []
    cursor = 0
    for start, end in merged:
        parts.append(escape(transcript[cursor:start]))
        parts.append(
            '<mark class="bg-yellow-200 rounded px-0.5 not-italic">'
            + escape(transcript[start:end])
            + '</mark>'
        )
        cursor = end
    parts.append(escape(transcript[cursor:]))

    return mark_safe(''.join(parts))


def main_home(request):
    return render(request, 'co_practice/main_home.html')


def home(request):
    practices = discover_practices()
    return render(request, 'co_practice/home.html', {'practices': practices})


def practice_index(request, practice_slug):
    if not get_practice_folder(practice_slug).exists():
        raise Http404
    return render(request, 'co_practice/index.html', {
        'groups': GROUPS,
        'practice_slug': practice_slug,
    })


def results(request, practice_slug):
    if not get_practice_folder(practice_slug).exists():
        raise Http404
    correct_answers = {q['question_no']: q['right_option'] for q in get_all(practice_slug)}
    return render(request, 'co_practice/results.html', {
        'groups': GROUPS,
        'correct_answers': correct_answers,
        'practice_slug': practice_slug,
    })


def question(request, practice_slug, question_id):
    if not get_practice_folder(practice_slug).exists():
        raise Http404
    if not 1 <= question_id <= 40:
        raise Http404

    q = get_by_id(practice_slug, question_id)
    if q is None:
        raise Http404

    audio_mode, full_audio_rel = get_audio_mode(practice_slug)
    audio_base = f'co_practice/{practice_slug}/audio/'
    image_base = f'co_practice/{practice_slug}/images/'

    img_path = image_base + q['image_filename'] if q['image_filename'] else None

    if audio_mode == 'full':
        full_audio_path = audio_base + full_audio_rel
        audio_paths = None
    else:
        audio_map = get_audio_map(practice_slug)
        audio_info = audio_map[question_id]
        full_audio_path = None
        audio_paths = {
            'intro': audio_base + audio_info['intro'] if audio_info['intro'] else None,
            'intro_label': audio_info['intro_label'],
            'main': audio_base + audio_info['main'],
            'shared_with': audio_info['shared_with'],
        }

    prev_id = question_id - 1 if question_id > 1 else None
    next_id = question_id + 1 if question_id < 40 else None

    highlighted = _highlighted_transcript(
        q['audio_transcript'], q.get('highlights', [])
    )
    highlighted_english = _highlighted_transcript(
        q.get('english_translation', ''), q.get('english_translation_highlights', [])
    )

    return render(request, 'co_practice/question.html', {
        'question': q,
        'img_path': img_path,
        'audio_mode': audio_mode,
        'audio_paths': audio_paths,
        'full_audio_path': full_audio_path,
        'prev_id': prev_id,
        'next_id': next_id,
        'highlighted_transcript': highlighted,
        'highlighted_english': highlighted_english,
        'practice_slug': practice_slug,
    })
