import importlib
from ..practices import GROUPS, get_practice_folder


def _build_audio_map(slug):
    """
    Auto-generate the AUDIO_MAP for any standard TEF CO practice.

    The segment layout is always the same:
      - Each group gets one intro segment, then one segment per question.
      - Exception: Groupe 7 (Dialogues, labelled 'audio partagé') — question
        pairs share a single segment.

    Segment filename format is detected automatically (zero-padded or not).
    """
    audio_dir = get_practice_folder(slug) / 'audio'
    zero_pad = (audio_dir / 'segment_01.mp3').exists()

    def seg(n):
        return f'segment_{n:02d}.mp3' if zero_pad else f'segment_{n}.mp3'

    audio_map = {}
    counter = 1

    for group in GROUPS:
        intro = counter
        counter += 1
        questions = group['questions']
        # Short label like "Groupe 7 (Q23–Q30)" for the intro card
        short = group['label'].split(' — ')[0]
        intro_label = f"{short} (Q{questions[0]}–Q{questions[-1]})"

        if 'partagé' in group['label']:
            # Paired questions share one segment each
            for i in range(0, len(questions), 2):
                q1, q2 = questions[i], questions[i + 1]
                main = counter
                counter += 1
                audio_map[q1] = {'intro': seg(intro), 'main': seg(main),
                                  'intro_label': intro_label, 'shared_with': [q2]}
                audio_map[q2] = {'intro': seg(intro), 'main': seg(main),
                                  'intro_label': intro_label, 'shared_with': [q1]}
        else:
            for q in questions:
                main = counter
                counter += 1
                audio_map[q] = {'intro': seg(intro), 'main': seg(main),
                                 'intro_label': intro_label, 'shared_with': None}

    return audio_map


def get_audio_map(slug):
    """
    Return the AUDIO_MAP for the given practice slug.

    Looks for a hand-written override at audio_maps/p{slug}.py first.
    Falls back to auto-generating from the standard TEF CO segment layout.
    """
    try:
        mod = importlib.import_module(f'.p{slug}', package=__name__)
        return mod.AUDIO_MAP
    except ImportError:
        return _build_audio_map(slug)
