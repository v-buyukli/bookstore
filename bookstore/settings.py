import os
from pathlib import Path

import dj_database_url
import environ
from decouple import config, Csv


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY")

IS_HEROKU_APP = "DYNO" in os.environ and not "CI" in os.environ
IS_LOCAL = config("IS_LOCAL", default=False, cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="127.0.0.1,0.0.0.0", cast=Csv())

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "api.apps.ApiConfig",
    "corsheaders",
    "rest_framework",
    "django_filters",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.auth.middleware.RemoteUserMiddleware",
]

ROOT_URLCONF = "bookstore.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "bookstore.wsgi.application"

if IS_HEROKU_APP:
    DATABASES = {"default": dj_database_url.config(conn_max_age=600, ssl_require=True)}
elif IS_LOCAL:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config("POSTGRES_NAME"),
            "USER": config("POSTGRES_USER"),
            "PASSWORD": config("POSTGRES_PASSWORD"),
            "HOST": config("POSTGRES_HOST", default="localhost"),
            "PORT": config("POSTGRES_PORT", default="5432"),
        }
    }

CACHES = {
    "default": {
        "BACKEND": "django_bmemcached.memcached.BMemcached",
        "TIMEOUT": None,
        "LOCATION": config("MEMCACHIER_SERVERS", cast=Csv()),
        "OPTIONS": {
            "username": config("MEMCACHIER_USERNAME"),
            "password": config("MEMCACHIER_PASSWORD"),
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ORIGIN_ALLOW_ALL = True

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "django.contrib.auth.backends.RemoteUserBackend",
]

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_jwt.authentication.JSONWebTokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 15,
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}

AUTH0_DOMAIN = config("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = config("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = config("AUTH0_CLIENT_SECRET")
AUTHORIZATION_HEADER = config("AUTHORIZATION_HEADER")

JWT_AUTH = {
    "JWT_PAYLOAD_GET_USERNAME_HANDLER": "api.utils.jwt_get_username_from_payload_handler",
    "JWT_DECODE_HANDLER": "api.utils.jwt_decode_token",
    "JWT_ALGORITHM": "RS256",
    "JWT_AUDIENCE": "https://bookstore/api",
    "JWT_ISSUER": f"https://{AUTH0_DOMAIN}/",
    "JWT_AUTH_HEADER_PREFIX": "Bearer",
}

API_URL = config("API_URL", default="http://127.0.0.1:3000/api")
MONOBANK_API_KEY = config("MONOBANK_API_KEY")
