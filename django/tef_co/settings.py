from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-dev-key-tef-co-practice-2024'

DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'co_practice',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'tef_co.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.template.context_processors.static',
            ],
        },
    },
]

WSGI_APPLICATION = 'tef_co.wsgi.application'

DATABASES = {}

STATIC_URL = '/static/'

# Auto-register static dirs for every co_web_content/practice_*/ folder.
# Audio segments → co_practice/<slug>/audio/
# Image folder(s) → co_practice/<slug>/images/
_CO_WEB_CONTENT = BASE_DIR.parent / 'co_web_content'
STATICFILES_DIRS = []
for _practice_dir in sorted(_CO_WEB_CONTENT.glob('practice_*')):
    _slug = _practice_dir.name[len('practice_'):]
    _audio = _practice_dir / 'audio'
    if _audio.is_dir():
        STATICFILES_DIRS.append((f'co_practice/{_slug}/audio', _audio))
    for _d in sorted(_practice_dir.iterdir()):
        if _d.is_dir() and _d.name != 'audio':
            STATICFILES_DIRS.append((f'co_practice/{_slug}/images', _d))
