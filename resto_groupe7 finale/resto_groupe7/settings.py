import pymysql
pymysql.install_as_MySQLdb()
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'gtel3046-groupe7-enspy-2025-changez-en-production'
DEBUG = True
ALLOWED_HOSTS = ['*']
AUTH_USER_MODEL = 'restaurant.User'
INSTALLED_APPS = [
    'django.contrib.admin','django.contrib.auth','django.contrib.contenttypes',
    'django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles',
    'crispy_forms','crispy_bootstrap5','restaurant',
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
TEMPLATES = [{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[],
    'APP_DIRS':True,'OPTIONS':{'context_processors':[
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},}]
WSGI_APPLICATION = 'resto_groupe7.wsgi.application'
# ══ CHANGEZ LE MOT DE PASSE MYSQL ICI ══
DATABASES = {'default': {
    'ENGINE':'django.db.backends.mysql','NAME':'Restaurant',
    'USER':'root','PASSWORD':'Ramsino3@',
    'HOST':'127.0.0.1','PORT':'3306',
    'OPTIONS':{'charset':'utf8mb4','init_command':"SET sql_mode='STRICT_TRANS_TABLES'"},
}}
LANGUAGE_CODE='fr-fr'; TIME_ZONE='Africa/Douala'; USE_I18N=True; USE_TZ=True
STATIC_URL='/static/'; MEDIA_URL='/media/'; MEDIA_ROOT=BASE_DIR/'media'
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
LOGIN_URL='/login/'; LOGIN_REDIRECT_URL='/dashboard/'; LOGOUT_REDIRECT_URL='/login/'
CACHES={'default':{'BACKEND':'django.core.cache.backends.locmem.LocMemCache'}}
EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend'
