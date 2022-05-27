import os


def createDir(dirname):
    try:
        os.mkdir(dirname)
    except FileExistsError:
        pass


###### Site security
site_dns_url = 'quality.bluewaves.ovh'
site_data_path = 'uKKU2_data_TNM'
site_SECRET_KEY = 'django-insecure-+yym644td@cz*-+c*&@5&@)xvx%54(m3mu7l*6n#1@k0c_t+5s'
site_DEBUG_MODE = True
site_SESSION_COOKIE_SECURE = False
site_CSRF_COOKIE_SECURE = False
site_SECURE_SSL_REDIRECT = False

###### Site DB
site_DB_ENGINE = 'django.db.backends.postgresql_psycopg2'
site_DB_NAME = 'quality2'
site_DB_USER = 'quality2'
site_BD_PASSWORD = 'quality2'
site_BD_HOST = 'localhost'
site_BD_PORT = '5432'

###### Site Session Conf
site_SESSION_COOKIE_AGE = 3600  # (1 hour, in seconds)
site_DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 100  # 100M

###### Site Email Conf

site_EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
site_EMAIL_HOST = 'smtp-relay.sendinblue.com'  # smtp.gmail.com'
site_EMAIL_PORT = 587
site_EMAIL_USE_TLS = True
site_EMAIL_HOST_USER = 'medzarka@gmail.com'  # 'tanomah.quality@gmail.com'
site_EMAIL_HOST_PASSWORD = '8KgMfTzb3kCZNWxs'  # 'pmtwazazxtusgvhr'

##### Site Admin Title

MYSITE_ADMIN_TEMPLATE = 'ADMIN_INTERFACE' # choose between GRAPPELLI or ADMIN_INTERFACE
MYSITE_ADMIN_SITE_HEADER = "uKKU (ver.2) Admin"
MYSITE_ADMIN_SITE_INDEX_TITLE = "Welcome to uKKU2 Admin"
MYSITE_ADMIN_SITE_TITLE = "uKKU2 Quality Document Manager"


