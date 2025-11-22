"""
Django settings for PuntoVenta project.
"""
from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar el .env que está dentro de PuntoVenta/
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_PATH, override=True)

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-ru2b9_m4llnw(2bkhsiht(slvkl!s=k=imp_i_41*q9fsnwd$m"
)

DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "ventas",
    "widget_tweaks",
    "django.contrib.humanize",
    "rest_framework",
]


from datetime import timedelta

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "PuntoVenta.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "PuntoVenta.wsgi.application"


# ---------------------------------------------------------------------------
# DATABASES
#   - SQLite local por defecto
#   - Postgres remoto si USE_REMOTE_DB=1
# ---------------------------------------------------------------------------
USE_REMOTE_DB = os.getenv("USE_REMOTE_DB", "0") == "1"

if USE_REMOTE_DB:
    # Nombres de variables PROPIAS para no chocar con USER del sistema
    required = ["DBNAME", "DBUSER", "DBPASSWORD", "DBHOST", "DBPORT"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise RuntimeError(f"Faltan variables {missing} en {ENV_PATH}")

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DBNAME"),
            "USER": os.getenv("DBUSER"),
            "PASSWORD": os.getenv("DBPASSWORD"),
            "HOST": os.getenv("DBHOST"),  # SOLO host, sin 'postgresql://'
            "PORT": os.getenv("DBPORT", "5432"),
            "OPTIONS": {"sslmode": "require"},
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
# ---------------------------------------------------------------------------


LANGUAGE_CODE = "es-mx"
TIME_ZONE = "America/Mexico_City"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
