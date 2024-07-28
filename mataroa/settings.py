"""
Django settings for mataroa project.

Generated by 'django-admin startproject' using Django 3.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
from pathlib import Path
from urllib import parse

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY", "nonrandom_secret")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG") == "1"

LOCALDEV = os.getenv("LOCALDEV") == "1"

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    f".{os.getenv('DOMAIN', 'capivaras.dev')}",
    ".mataroalocal.blog",
    "*",
]

ADMINS = [("Theodore Keloglou", "zf@sirodoht.com")]

CANONICAL_HOST = os.getenv("DOMAIN", "capivaras.dev")
if LOCALDEV:
    CANONICAL_HOST = "mataroalocal.blog:8000"

INSTANCE_NAME = os.getenv("INSTANCE_NAME", "Mataroa")
INSTANCE_DESCRIPTION = os.getenv("INSTANCE_DESCRIPTION", "Naked blogging platform.")

# Application definition

INSTALLED_APPS = [
    "main.apps.MainConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
]

MIDDLEWARE = [
    "main.middleware.speed_middleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "main.middleware.host_middleware",
]

ROOT_URLCONF = "mataroa.urls"

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

WSGI_APPLICATION = "mataroa.wsgi.application"

AUTH_USER_MODEL = "main.User"

LOGIN_REDIRECT_URL = "index"
LOGOUT_REDIRECT_URL = "index"

SESSION_COOKIE_AGE = 31449600  # 60 * 60 * 24 * 7 * 52 = 1 year in seconds
SESSION_COOKIE_DOMAIN = CANONICAL_HOST.split(":")[0]  # session visible in subdomains

DATE_FORMAT = "F j, Y"
DATETIME_FORMAT = "F j, Y, P"


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

database_url = os.getenv("DATABASE_URL", "")
database_url = parse.urlparse(database_url)
# e.g. postgres://mataroa:password@127.0.0.1:5432/mataroa
database_name = database_url.path[1:]  # url.path is '/mataroa'
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": parse.unquote(database_name or ""),
        "USER": parse.unquote(database_url.username or ""),
        "PASSWORD": parse.unquote(database_url.password or ""),
        "HOST": database_url.hostname,
        "PORT": database_url.port or "",
        "CONN_MAX_AGE": 500,
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
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


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = False

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    },
}


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Default forms.URLField scheme
# https://docs.djangoproject.com/en/5.0/ref/settings/#forms-urlfield-assume-https

FORMS_URLFIELD_ASSUME_HTTPS = True


# Email

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
if LOCALDEV:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_USE_TLS = True
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.postmarkapp.com")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_PORT = "587"

EMAIL_FROM_HOST = CANONICAL_HOST
DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL", f"{INSTANCE_NAME} <{EMAIL_HOST_USER}>"
)
EMAIL_SUBJECT_PREFIX = f"[{INSTANCE_NAME}  notification] "

EMAIL_TEST_RECEIVE_LIST = os.environ.get("EMAIL_TEST_RECEIVE_LIST")


# Security middleware

if not DEBUG and not LOCALDEV:
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# Translate

TRANSLATE_API_URL = os.getenv(
    "TRANSLATE_API_URL", "https://translate.capivaras.dev/api/generate"
)
TRANSLATE_API_TOKEN = os.getenv("TRANSLATE_API_TOKEN", "")


# Logging
# https://docs.djangoproject.com/en/4.1/ref/logging/#default-logging-configuration

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "formatters": {
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[{server_time}] {message}",
            "style": "{",
        }
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
        },
        "django.server": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "django.server",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "mail_admins"],
            "level": "INFO",
        },
        "django.server": {
            "handlers": ["django.server"],
            "level": "INFO",
            "propagate": False,
        },
        "django.security.DisallowedHost": {
            "handlers": ["console"],
            "propagate": False,
        },
    },
}
