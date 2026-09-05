"""Development settings for the Open FMEA Django PoC."""
from __future__ import annotations

import os
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DOMAIN_DIR = BASE_DIR / "domain"
DJANGO_APP_DIR = BASE_DIR / "django_app"

for package_root in (DOMAIN_DIR, DJANGO_APP_DIR):
    package_root_str = str(package_root)
    if package_root_str not in sys.path:
        sys.path.insert(0, package_root_str)

SECRET_KEY = os.environ.get("OPEN_FMEA_SECRET_KEY", "open-fmea-dev-only")
DEBUG = os.environ.get("OPEN_FMEA_DEBUG", "1") == "1"
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "testserver"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "fmea_app",
    "fmea_review",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "open_fmea_project.urls"

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

WSGI_APPLICATION = "open_fmea_project.wsgi.application"
ASGI_APPLICATION = "open_fmea_project.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ.get("OPEN_FMEA_DB_PATH", BASE_DIR / "db.sqlite3"),
    }
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

OPEN_FMEA_IMPORT_MAX_UPLOAD_BYTES = int(
    os.environ.get("OPEN_FMEA_IMPORT_MAX_UPLOAD_BYTES", str(10 * 1024 * 1024))
)
OPEN_FMEA_AI_ENABLED = os.environ.get("OPEN_FMEA_AI_ENABLED", "0") == "1"
OPEN_FMEA_OLLAMA_ENDPOINT = os.environ.get("OPEN_FMEA_OLLAMA_ENDPOINT", "http://127.0.0.1:11434")
OPEN_FMEA_OLLAMA_MODEL = os.environ.get("OPEN_FMEA_OLLAMA_MODEL") or None
OPEN_FMEA_OLLAMA_TIMEOUT_SECONDS = float(os.environ.get("OPEN_FMEA_OLLAMA_TIMEOUT_SECONDS", "30"))
