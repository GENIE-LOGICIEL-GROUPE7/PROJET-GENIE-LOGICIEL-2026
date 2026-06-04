"""
settings.py — Configuration Django complète pour RMS
Groupe 7 — GTEL 3046 — ENSPY 2025-2026

IMPORTANT : Ce fichier remplace/complète le settings.py généré par django-admin.
Placer ce fichier dans : resto_groupe7/settings.py
"""
import pymysql
pymysql.install_as_MySQLdb()   # ← OBLIGATOIRE : Ligne 1 avant tout import Django

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-gtel3046-groupe7-enspy-2025-2026-CHANGEZ-EN-PRODUCTION'
DEBUG = True   # Mettre False en production
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '*']

# Application personnalisée
AUTH_USER_MODEL = 'restaurant.User'   # ← AVANT toute migration !

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Applications tierces
    'crispy_forms',
    'crispy_bootstrap5',
    # Notre application
    'restaurant',
]

CRISPY_TEMPLATE_PACK = 'bootstrap5'
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'resto_groupe7.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

# ── Base de Données MySQL ────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.mysql',
        'NAME':     'Restaurant',
        'USER':     'root',
        'PASSWORD': 'votre_mot_de_passe_mysql',
        'HOST':     '127.0.0.1',
        'PORT':     '3306',
        'OPTIONS':  {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# ── Cache (locmem en dev, Redis en prod) ──────────────────────────
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        # En production avec Redis :
        # 'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        # 'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# ── Fichiers statiques et médias ──────────────────────────────────
STATIC_URL  = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
    BASE_DIR / 'restaurant' / 'static',
    BASE_DIR / 'resto_groupe7' / 'static',
                    ]
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ── Internationalisation ──────────────────────────────────────────
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE     = 'Africa/Douala'
USE_I18N = USE_TZ = True

# ── Authentification ──────────────────────────────────────────────
LOGIN_URL          = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL= '/login/'

# ── Email (configuration SMTP) ────────────────────────────────────
EMAIL_BACKEND  = 'django.core.mail.backends.console.EmailBackend'  # Dev
# En production :
# EMAIL_BACKEND  = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST     = 'smtp.gmail.com'
# EMAIL_PORT     = 587
# EMAIL_USE_TLS  = True
# EMAIL_HOST_USER     = 'votre@email.com'
# EMAIL_HOST_PASSWORD = 'votre_mot_de_passe'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
