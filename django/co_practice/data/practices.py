from pathlib import Path

CO_WEB_CONTENT = Path(__file__).resolve().parent.parent.parent.parent / 'co_web_content'

# TEF CO group structure is identical across all practice sets
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


def get_practice_folder(slug):
    return CO_WEB_CONTENT / f'practice_{slug}'


def get_json_file(slug):
    folder = get_practice_folder(slug)
    matches = list(folder.glob('*.json'))
    return matches[0] if matches else None


def discover_practices():
    """Return sorted list of available practice dicts (only folders with a JSON file)."""
    practices = []
    for folder in sorted(CO_WEB_CONTENT.glob('practice_*'), key=lambda p: int(p.name[len('practice_'):])):
        if not folder.is_dir():
            continue
        if not list(folder.glob('*.json')):
            continue
        slug = folder.name[len('practice_'):]
        practices.append({
            'slug': slug,
            'label': f'CO {slug}',
            'folder': folder,
        })
    return practices
