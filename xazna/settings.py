import os
from dotenv import load_dotenv
from datetime import timedelta
from pathlib import Path
from kombu import Queue
from celery.schedules import crontab

load_dotenv()

CELERY_TASK_QUEUES = (
    Queue("email", routing_key="email.#"),
    Queue("clean", routing_key="clean.#"),
    Queue("check", routing_key="check.#"),
)


CELERY_TASK_ROUTES = {
    "tasks.convert_file": {"queue": "conversion", "routing_key": "conversion.file"},
    "tasks.send_email_confirmation": {
        "queue": "email",
        "routing_key": "email.confirmation"
    },
    "tasks.send_email_reset_password": {
        "queue": "email",
        "routing_key": "email.reset"
    }
}


CELERY_BEAT_SCHEDULE = {
    "clean-tokens-daily": {
        "task": "accounts.tasks.clean_password_reset_tokens",
        "schedule": crontab(hour=3, minute=0),  # every day at 03:00 server time
        "options": {
            "queue": "clean",
            "routing_key": "clean.tokens"
        }
    },
    "check-subscriptions-daily": {
        "task": "finance.tasks.check_subscriptions",
        "schedule":crontab(hour=0, minute=0),  # every day at 00:00 server time
        "options": {
            "queue": "check",
            "routing_key": "check.subscriptions"
        }
    }
}

TTS_SERVER = os.getenv("TTS_SERVER")
STT_SERVER = os.getenv("STT_SERVER")


CELERY_BROKER_URL = f"redis://{os.getenv("REDIS_HOST")}:6379/0"
CELERY_RESULT_BACKEND = f"redis://{os.getenv("REDIS_HOST")}:6379/0"
CELERY_RESULT_EXTENDED = True
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 10800
CELERY_TASK_SOFT_TIME_LIMIT = 10700
CELERY_WORKER_MAX_MEMORY = 1024 * 1024 * 4  # 4 GB

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv("SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
DEBUG = True
BASE_URL = os.getenv("BASE_URL")
AUTH_USER_MODEL = "accounts.CustomUserModel"
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")


ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "172.28.23.100"
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "drf_yasg",
    "django_celery_beat",
    "shared",
    "accounts",
    "tts",
    "stt",
    "finance"
]


CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:3000",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "xazna.middleware.CoreMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

]

ROOT_URLCONF = "xazna.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
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

WSGI_APPLICATION = "xazna.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DATABASE_NAME"),
        "HOST": os.getenv("DATABASE_HOST"),
        "PORT": os.getenv("DATABASE_PORT"),
        "USER": os.getenv("DATABASE_USER"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD"),
    }
}

AUTHENTICATION_BACKENDS = [
    "accounts.backends.AuthenticationBackend",
]

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

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    )
}
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("ACCESS_TOKEN_LIFETIME", 10))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.getenv("REFRESH_TOKEN_LIFETIME", 7))),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,

    "ALGORITHM": JWT_ALGORITHM,
    "SIGNING_KEY": SECRET_KEY,
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

    "JTI_CLAIM": "jti",

    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",

    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
}

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Tashkent"
USE_TZ = True

USE_I18N = True

USE_TZ = True

MEDIA_ROOT = BASE_DIR / "media-files"
MEDIA_URL = "/media/"

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = os.getenv("SMTP_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_MAX_ATTEMPTS = 3
EMAIL_MAX_RESENDS = 5
EMAIL_ATTEMPT_BLOCK_TIME = 10
EMAIL_RESEND_BLOCK_TIME = 5
EMAIL_EXPIRE_TIME = 3
RESET_PASSWORD_EXPIRE_TIME = 3
RESET_PASSWORD_LINK = os.getenv("RESET_PASSWORD_LINK")
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
