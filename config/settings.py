"""
Django Settings — SocioEcoData
Ponto de integração #1: Define o banco de dados PostgreSQL + pgvector.
Todas as credenciais são lidas do arquivo .env via django-environ.
"""
import environ
from pathlib import Path

# --- Caminhos Base ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Leitura do .env ---
env = environ.Env(
    DEBUG=(bool, False)
)
environ.Env.read_env(BASE_DIR / '.env')

# --- Segurança ---
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

# --- Aplicações Instaladas ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # App principal do projeto
    'core',
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

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Diretório global de templates (para o dashboard.html)
        'DIRS': [BASE_DIR / 'presentation' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ============================================================
# PONTO DE INTEGRAÇÃO #1: BANCO DE DADOS PostgreSQL + pgvector
# ============================================================
# A URL completa é lida do .env (DATABASE_URL).
# Exemplo: postgres://socio_user:socio_password@localhost:5432/socio_db
# O Django conecta via psycopg2 (psycopg2-binary no requirements.txt).
# A extensão pgvector é habilitada pelo script scripts/init_pgvector.sql
# e usada pelo modelo DocumentoMetodologico via VectorField (pgvector-python).
DATABASES = {
    'default': env.db('DATABASE_URL')
}

# --- Internacionalização ---
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# --- Arquivos Estáticos ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'presentation' / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================
# PONTO DE INTEGRAÇÃO #3: OpenAI API Key
# ============================================================
# Lida do .env e disponibilizada como variável de ambiente do processo.
# O SDK da OpenAI (openai.Client()) lê automaticamente a variável
# de ambiente OPENAI_API_KEY — não é necessário passá-la explicitamente.
# Usada em: core/services/agent_orchestrator.py
import os
os.environ.setdefault('OPENAI_API_KEY', env('OPENAI_API_KEY', default=''))

# --- Groq API ---
GROQ_API_KEY = env('GROQ_API_KEY', default='')
GROQ_MODEL = env('GROQ_MODEL', default='llama-3.3-70b-versatile')
