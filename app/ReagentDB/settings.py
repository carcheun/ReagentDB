"""
Django settings for ReagentDB project.

Generated by 'django-admin startproject' using Django 3.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import os
from pathlib import Path

from celery.schedules import crontab

# Build paths inside the project like this: BASE_DIR / 'subdir'.
#BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')
#SECRET_KEY = '_1fl$e!6#+&(brk8&qsi8&9itgglq=ti7*yhswk0od^zmg(sc9'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(os.environ.get('DEBUG', default=0))

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS').split(' ')

# TODO: Remove and change this to env files
# copied from https://github.com/dkarchmer/aws-eb-docker-django
# used for creating superuser as a manage.py command
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', default='admin')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', default='admin@email.com')
ADMIN_INITIAL_PASSWORD = os.environ.get('ADMIN_INITIAL_PASSWORD', default='admin')
ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
    (ADMIN_USERNAME, ADMIN_EMAIL),
)

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'reagents',                         # our reagents app we created
    'rest_framework',                   # needed for our rest_framework
    'rest_framework.authtoken',         # for authentication tokens
    'django_extensions',                # extra manange.py goodies
    'channels',                         # django channels for websocket
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

ROOT_URLCONF = 'ReagentDB.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'ReagentDB.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.postgresql_psycopg2',
#        'NAME': 'reagentsdb',
#        'USER' : 'admin',
#        'PASSWORD' : 'admin',
#        'HOST': 'localhost',
#        'PORT' : 5432,
#    }
#}

DATABASES = {
    'default': {
        'ENGINE': os.environ.get("SQL_ENGINE", "django.db.backends.sqlite3"),
        'NAME': os.environ.get("SQL_DATABASE", os.path.join(BASE_DIR, "db.sqlite3")),
        'USER': os.environ.get("SQL_USER", "user"),
        'PASSWORD': os.environ.get("SQL_PASSWORD", "password"),
        'HOST': os.environ.get("SQL_HOST", "localhost"),
        'PORT': os.environ.get("SQL_PORT", "5432"),
    }
}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(REDIS_HOST, REDIS_PORT)],
        }
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# django rest framework authentication
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',  # <-- And here
    ],
}

# channels setting
ASGI_APPLICATION = 'ReagentDB.asgi.application'

# Customer user model
AUTH_USER_MODEL = 'reagents.User'

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# Logger settings
LOGGING = {
    'version': 1,
    'disable_existing_loggers': 1,
    'formatters': {
        'info_log': {
            'format': '[{asctime}] [{levelname}] [{filename}.{funcName}:{lineno}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'info_log'
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    }
}

# Celery settings
# Celery and Celery-Beat depend on REDIS
CELERY_BROKER_URL = "redis://redis:6379"
CELERY_RESULT_BACKEND = "redis://redis:6379"
CELERY_BEAT_SCHEDULE = {
    # everyday at midnight, clear deltas that are no longer needed
    "check_and_remove_PADeltas": {
        "task": "reagents.tasks.check_and_remove_PADeltas",
        "schedule": crontab(minute=0, hour=0),
    },
    "check_and_remove_ReagentDeltas": {
        "task": "reagents.tasks.check_and_remove_ReagentDeltas",
        "schedule": crontab(minute=0, hour=0),
    },
    # archive or delete expired/empty reagents every
    # january 4th, or whatever
    "delete_old_reagents": {
        "task": "reagents.tasks.delete_old_reagents",
        "schedule": crontab(0, 0, day_of_month='1',
            month_of_year='4'),
    },
}