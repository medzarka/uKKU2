"""
Django settings for uKKU2 project.

Generated by 'django-admin startproject' using Django 4.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
from pathlib import Path
import os

import uKKU2.site_conf as site_conf

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = os.path.join(os.environ['HOME'], site_conf.site_data_path)
site_conf.createDir(DATA_DIR)
print(f'[DIR] the base dir is {BASE_DIR}')
print(f'[DIR] the data dir is {DATA_DIR}')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = site_conf.site_SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = site_conf.site_DEBUG_MODE

ALLOWED_HOSTS = ['localhost', '127.0.0.1', site_conf.site_dns_url]

# Application definition
INSTALLED_APPS = [ ]
if site_conf.MYSITE_ADMIN_TEMPLATE == 'GRAPPELLI':
    INSTALLED_APPS = ['grappelli', ]
if site_conf.MYSITE_ADMIN_TEMPLATE == 'ADMIN_INTERFACE':
    INSTALLED_APPS = ['admin_interface',
                      'colorfield', ]

INSTALLED_APPS += [

    'import_export',
    'dbbackup',  # django-dbbackup

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    '_data.apps.DataConfig',
    '_web.apps.WebConfig',
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

ROOT_URLCONF = 'uKKU2.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
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

WSGI_APPLICATION = 'uKKU2.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

# DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': BASE_DIR / 'db.sqlite3',
#    }
# }

DATABASES = {
    'default': {
        'ENGINE': site_conf.site_DB_ENGINE,
        'NAME': site_conf.site_DB_NAME,
        'USER': site_conf.site_DB_USER,
        'PASSWORD': site_conf.site_BD_PASSWORD,
        'HOST': site_conf.site_BD_HOST,
        'PORT': site_conf.site_BD_PORT,
        #'OPTIONS': {
        #    'init_command': "SET sql_mode='STRICT_TRANS_TABLES', innodb_strict_mode=1",
        #    'charset': 'utf8mb4',
        #    "autocommit": True,
        #}

    }
}

# CACHES = {
#    'default': {
#        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
#        'LOCATION': 'my_cache_table',
#    }
# }


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/
####### Translation config
# createDir(os.path.join(DATA_DIR, 'locale'))
# LOCALE_PATHS = [os.path.join(DATA_DIR, 'locale')]
# LANGUAGE_CODE = 'en'
# LANGUAGES = [
#    ('en', 'English'),
#    ('ar', 'Arabic'),
# ]
# print(f'[DIR] the localisation file is in {os.path.join(DATA_DIR, "locale")}')

TIME_ZONE = 'Asia/Riyadh'
USE_I18N = True
USE_L10N = True
USE_TZ = True

####### Media and Static files


site_conf.createDir(os.path.join(DATA_DIR, 'static'))
site_conf.createDir(os.path.join(DATA_DIR, 'media'))
STATIC_ROOT = os.path.join(os.path.join(DATA_DIR, 'static'))
STATIC_URL = '/static/'
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)
MEDIA_ROOT = os.path.join(os.path.join(DATA_DIR, 'media'))
MEDIA_URL = '/media/'
print(f'[DIR] the static files are in {os.path.join(DATA_DIR, "static")}')
print(f'[DIR] the media files are in {os.path.join(DATA_DIR, "media")}')

###### Login & Session Age
# LOGIN_URL = '/web/login/'
# LOGIN_REDIRECT_URL = '/web/dashboard'
# AUTH_USER_MODEL = '_data.User'
# AUTH_LOGIN_URL = 'web_auth_login'
# AUTH_LOGOUT_URL = 'web_auth_logout'
# AUTH_DASHBOARD_URL = 'web_dashboard'
LOGIN_URL = '/web/login/'
LOGIN_REDIRECT_URL = '/web/dashboard'
# print(f'[AUTH] the class {AUTH_USER_MODEL} is used as users backend.')

###### Session management. The session will close after
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = site_conf.site_SESSION_COOKIE_AGE
print(f'[Sessions] the maximum time to keep the session cookie is {SESSION_COOKIE_AGE / 60} minute(s).')

###### allow upload big file
DATA_UPLOAD_MAX_MEMORY_SIZE = site_conf.site_DATA_UPLOAD_MAX_MEMORY_SIZE
FILE_UPLOAD_MAX_MEMORY_SIZE = DATA_UPLOAD_MAX_MEMORY_SIZE
print(f'[FILES] the maximum size for file upload is  {DATA_UPLOAD_MAX_MEMORY_SIZE} bytes.')

###### SSL Session
SESSION_COOKIE_SECURE = site_conf.site_SESSION_COOKIE_SECURE
CSRF_COOKIE_SECURE = site_conf.site_CSRF_COOKIE_SECURE
SECURE_SSL_REDIRECT = site_conf.site_SECURE_SSL_REDIRECT

###### Loggin
site_conf.createDir(os.path.join(DATA_DIR, 'log'))
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(DATA_DIR, 'log', 'trace.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
print(f'[DIR] the log file is in {os.path.join(DATA_DIR, "log")}')

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#######  Sending emails: tanomah.quality@gmail.com
EMAIL_MODE = site_conf.site_email_mode

SITE_SOCKETLABS_API_SERVER_ID = site_conf.site_email_serverId
SITE_SOCKETLABS_INJECTION_API_KEY = site_conf.site_email_injectionApiKey
SITE_SOCKETLABS_SENDER = site_conf.site_email_sender

EMAIL_BACKEND = site_conf.site_EMAIL_BACKEND
EMAIL_HOST = site_conf.site_EMAIL_HOST
EMAIL_PORT = site_conf.site_EMAIL_PORT
EMAIL_USE_TLS = site_conf.site_EMAIL_USE_TLS
EMAIL_HOST_USER = site_conf.site_EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = site_conf.site_EMAIL_HOST_PASSWORD

# only if django version >= 3.0
X_FRAME_OPTIONS = "SAMEORIGIN"
SILENCED_SYSTEM_CHECKS = ["security.W019"]

from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}

##### Admin Title configuration
MYSITE_ADMIN_TEMPLATE = site_conf.MYSITE_ADMIN_TEMPLATE
GRAPPELLI_ADMIN_TITLE = site_conf.MYSITE_ADMIN_SITE_TITLE
ADMIN_SITE_SITE_HEADER = site_conf.MYSITE_ADMIN_SITE_HEADER
ADMIN_SITE_INDEX_TITLE = site_conf.MYSITE_ADMIN_SITE_INDEX_TITLE
ADMIN_SITE_SITE_TITLE = site_conf.MYSITE_ADMIN_SITE_TITLE


##### database and media backup
BACKUP_DIR = os.path.join(os.path.join(DATA_DIR, 'backup'))
site_conf.createDir(BACKUP_DIR)
DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': BACKUP_DIR}
print(f'[DIR] the backup dir is {os.path.join(DATA_DIR, "backup")}')

