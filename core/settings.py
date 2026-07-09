'''
Configurações do projeto PCP Komotors.

Um único settings.py. Variáveis via .env + django-environ.
- Código-fonte/identificadores em inglês; UI em pt-BR.
- Timezone America/Sao_Paulo.
- Login por email.
'''

from pathlib import Path

import environ

# --------------------------------------------------------------------- #
# Base paths
# --------------------------------------------------------------------- #
BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------- #
# Env (django-environ) — lê .env na raiz do projeto
# --------------------------------------------------------------------- #
env = environ.Env(
    DEBUG=(bool, True),
    SECRET_KEY=(str, 'django-insecure-troque-por-uma-chave-secreta-real-em-producao-pcp-komotors'),
    ALLOWED_HOSTS=(list, ['localhost', '127.0.0.1']),
    CSRF_TRUSTED_ORIGINS=(list, ['http://localhost:8000']),
    DATABASE_URL=(str, 'sqlite:///%s' % (BASE_DIR / 'db.sqlite3')),
    AUTH_EMAIL_LOGIN=(bool, False),
)

env_file = BASE_DIR / '.env'
if env_file.exists():
    environ.Env.read_env(env_file)


# --------------------------------------------------------------------- #
# Segurança
# --------------------------------------------------------------------- #
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env('ALLOWED_HOSTS')
CSRF_TRUSTED_ORIGINS = env('CSRF_TRUSTED_ORIGINS')

# Atrás do Traefik (somente em produção — sem efeito em dev).
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_REDIRECT_EXEMPT = ['/health/']

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


# --------------------------------------------------------------------- #
# Apps
# --------------------------------------------------------------------- #
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps do projeto
    'base',
    'operators',
    'catalogs',
    'production',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'base.context_processors.base_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = 'core.asgi'


# --------------------------------------------------------------------- #
# Database
# --------------------------------------------------------------------- #
# DATABASE_URL pode ser:
#   sqlite://BASE_DIR/db.sqlite3  (dev — placeholder interpolado abaixo)
#   postgres://user:pass@host:5432/pcp  (prod)
_db_url = env('DATABASE_URL')
if '%(BASE_DIR)s' in _db_url:
    _db_url = _db_url % {'BASE_DIR': str(BASE_DIR)}
DATABASES = {
    'default': env.db_url_config(_db_url),
}


# --------------------------------------------------------------------- #
# Autenticação — login por email
# --------------------------------------------------------------------- #
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTH_USER_MODEL = 'auth.User'  # auth nativa do Django

# Backend custom que autentica por email.
AUTHENTICATION_BACKENDS = [
    'base.backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Tela de login/logout do Django auth usa email.
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = 'login'


# --------------------------------------------------------------------- #
# Internacionalização e timezone
# --------------------------------------------------------------------- #
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True


# --------------------------------------------------------------------- #
# Static / media
# --------------------------------------------------------------------- #
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'