import os
from pathlib import Path

import dj_database_url
import environ


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-6dhzial(1f6ed794%&%y)hxr7s(@3#q93bfby1os02yncx&%i%"

IS_HEROKU_APP = "DYNO" in os.environ and not "CI" in os.environ

if not IS_HEROKU_APP:
    DEBUG = True

if IS_HEROKU_APP:
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = []
    ALLOWED_HOSTS.append("0.0.0.0")
    ALLOWED_HOSTS.append("127.0.0.1")

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

    servers = os.environ["MEMCACHIER_SERVERS"]
    username = os.environ["MEMCACHIER_USERNAME"]
    password = os.environ["MEMCACHIER_PASSWORD"]

    AUTH0_DOMAIN = os.environ["AUTH0_DOMAIN"]
    AUTH0_CLIENT_ID = os.environ["AUTH0_CLIENT_ID"]
    AUTH0_CLIENT_SECRET = os.environ["AUTH0_CLIENT_SECRET"]

    AUTHORIZATION_HEADER = os.environ["AUTHORIZATION_HEADER"]
elif "vktr" in os.environ["PATH"]:
    env = environ.Env()
    environ.Env.read_env(".env")

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("POSTGRES_NAME"),
            "USER": env("POSTGRES_USER"),
            "PASSWORD": env("POSTGRES_PASSWORD"),
            "HOST": env("POSTGRES_HOST"),
            "PORT": env("POSTGRES_PORT"),
        }
    }

    servers = env("MEMCACHIER_SERVERS")
    username = env("MEMCACHIER_USERNAME")
    password = env("MEMCACHIER_PASSWORD")

    AUTH0_DOMAIN = env("AUTH0_DOMAIN")
    AUTH0_CLIENT_ID = env("AUTH0_CLIENT_ID")
    AUTH0_CLIENT_SECRET = env("AUTH0_CLIENT_SECRET")

    AUTHORIZATION_HEADER = env("AUTHORIZATION_HEADER")
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ["POSTGRES_NAME"],
            "USER": os.environ["POSTGRES_USER"],
            "PASSWORD": os.environ["POSTGRES_PASSWORD"],
            "HOST": os.environ["POSTGRES_HOST"],
            "PORT": os.environ["POSTGRES_PORT"],
        }
    }

    servers = os.environ["MEMCACHIER_SERVERS"]
    username = os.environ["MEMCACHIER_USERNAME"]
    password = os.environ["MEMCACHIER_PASSWORD"]

    AUTH0_DOMAIN = os.environ["AUTH0_DOMAIN"]
    AUTH0_CLIENT_ID = os.environ["AUTH0_CLIENT_ID"]
    AUTH0_CLIENT_SECRET = os.environ["AUTH0_CLIENT_SECRET"]

    AUTHORIZATION_HEADER = os.environ["AUTHORIZATION_HEADER"]


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

CACHES = {
    "default": {
        "BACKEND": "django_bmemcached.memcached.BMemcached",
        "TIMEOUT": None,
        "LOCATION": servers,
        "OPTIONS": {
            "username": username,
            "password": password,
        },
    }
}

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
}

JWT_AUTH = {
    "JWT_PAYLOAD_GET_USERNAME_HANDLER": "api.utils.jwt_get_username_from_payload_handler",
    "JWT_DECODE_HANDLER": "api.utils.jwt_decode_token",
    "JWT_ALGORITHM": "RS256",
    "JWT_AUDIENCE": "https://bookstore/api",
    "JWT_ISSUER": f"https://{AUTH0_DOMAIN}/",
    "JWT_AUTH_HEADER_PREFIX": "Bearer",
}
