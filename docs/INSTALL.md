# KKU Measurement and Quality Documents Management

## uKKU2 Install steps (ver. 1)

Requirements:
```
Python 3.8.10
Django 3.2.10
Postgres 12
```

### Step 1 : Prepare the uKKU2 site directory

The uKKU3 works with two directories: The first directory is used for django 
code sources, and the second directory is used to store python env, 
static, media and log files.

In this section, we will detail how to prepare the first directory for site information:

1. create a directory named **web**. Then we create inside a sub-folder **sites**. 
The **~/web/sites** directory will contain all django projects.
```
mkdir ~/web
mkdir ~/web/sites
```
2. clone the uKKU2 project from **github** into the created **web/sites** folder:
```
cd ~/web/sites
git clone https://github.com/medzarka/uKKU2.git
```
3. You can also rename your project if you will use many copy of it. For instance, we will copy it to **uKKU2_TNM**:
```
mv uKKU2 uKKU2_TNM    
```
The django project code is installed into the **~/web/sites** folder and ready now.

### Step 2 : Prepare the uKKU2 data directory

The second folder is used to create the Python env, and to store static, media, and log files.
1. create a directory named uKKU2_data_{###} in the **web/data** folder. 
This directory will contain all django projects. 
It will contains also a tool to make periodic database backup.
For instance, we will create the folder **uKKU2_data_TNM**:
```
mkdir ~/web/data
mkdir ~/web/data/uKKU2_data_TNM
mkdir ~/web/data/uKKU2_data_TNM/env
mkdir ~/web/data/uKKU2_data_TNM/log
mkdir ~/web/data/uKKU2_data_TNM/media
mkdir ~/web/data/uKKU2_data_TNM/static
mkdir ~/web/data/uKKU2_data_TNM/run
mkdir ~/web/data/uKKU2_data_TNM/backups
```
So far, we configured the two folders for the django project code, and for data.

### Step 4 : Create and prepare a Python virtual environment
We will create a Python virtual environment for the django project.

1. install Python Virtual Environment on Ubuntu:
```
sudo apt-get update && sudo apt-get upgrade -y
sudo apt install python3-venv
```
2. Go to the **env** directory in the data folder:
```
cd ~/web/data/uKKU2_data_TNM/env
```
3. Create a Python virtual environment with the correct name. For instance, the environment will be named **uKKU2**:
```
python3 -m venv uKKU2
```
4. Install the required packages. This list is in the docs sjango code folder. The, we go the that folder, 
and we install these packages.
```
cd ~/web/sites/uKKU2_TNM/docs/
source ~/web/data/uKKU2_data_TNM/env/uKKU2/bin/activate
pip install -r requirements.txt
```

### Step 5 : Database

The software requires a database to store data. By default, we use PostgreSQL.
We start by installing postgres in Ubuntu:

```
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install postgresql postgresql-contrib libpq-dev python3-dev
```

Next step is to configure postgres database, user and permissions. As a sample, we will use 
'ukku2tnm' as a database name, a username and a password. You can use your own information.

```
sudo -u postgres psql
CREATE DATABASE ukku2tnm;
CREATE USER ukku2tnm WITH ENCRYPTED PASSWORD '{password here}';
ALTER ROLE ukku2tnm SET client_encoding TO 'utf8';
ALTER ROLE ukku2tnm SET default_transaction_isolation TO 'read committed';
ALTER ROLE ukku2tnm SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE ukku2tnm TO ukku2tnm;
\q
```

Finally, open the file ~/.pgpass in the home directory, and put information for each postgres 
user following the following template this form:
```
nano ~/.pgpass
localhost:5432:*:postgres:{postgres user password}
localhost:5432:ukku2tnm:ukku2tnm:{ password here}
```
And do not forget to secure access to the .pgpass file :
```
chmod 0600 ~/.pgpass
```
Then, the database is ready.

### Step 6 : Configure the Django Project and populate the database
In this step, we will detail how to configure the uKKU2 django site. Thus, the configuration should be provided as follows:
1. go to the **uKKU2_TNM/uKKU2** site folder:
```
cd ~/web/sites/uKKU2_TNM/uKKU2
```
2. create a file named **site_conf.py**:
```
touch site_conf.py
nano site_conf.py
```
3. Open the file and put the following content. You can update the content with your information:
```
import os

def createDir(dirname):
    try:
        os.mkdir(dirname)
    except FileExistsError:
        pass

###### Site security
site_dns_url = '{put here the DNS name for the uKKU2 site}'
site_data_path = '{put here the data folder. In our example, it is ~/web/data/uKKU2_data_TNM/}'
site_SECRET_KEY = '{ put here the django secret key. It is generated automatically by django-admin}'
site_DEBUG_MODE = True # True or False
site_SESSION_COOKIE_SECURE = True
site_CSRF_COOKIE_SECURE = True
site_SECURE_SSL_REDIRECT = True

###### Site DB
site_DB_ENGINE = 'django.db.backends.postgresql_psycopg2'
site_DB_NAME = '{ put here the name of the created postgres database}'
site_DB_USER = '{ put here the creteated postgres user that has access to the created database.}'
site_BD_PASSWORD = '{ put here the postgres user password.}'
site_BD_HOST = 'localhost'
site_BD_PORT = '5432'

###### Site Session Conf
site_SESSION_COOKIE_AGE = 3600  # (1 hour, in seconds). you can update it.
site_DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 100  # 100M, and you can update it.

###### Site Email Conf

site_EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
site_EMAIL_HOST = '{ put here the SMTP server}' 
site_EMAIL_PORT = 587
site_EMAIL_USE_TLS = True
site_EMAIL_HOST_USER = '{ put here the SMTP user}'  
site_EMAIL_HOST_PASSWORD = '{ put here the smptp user password}'  

##### Site Admin Title

MYSITE_ADMIN_TEMPLATE = 'ADMIN_INTERFACE' # choose between GRAPPELLI or ADMIN_INTERFACE
MYSITE_ADMIN_SITE_HEADER = "uKKU (ver.2) Admin"
MYSITE_ADMIN_SITE_INDEX_TITLE = "Welcome to uKKU2 Admin"
MYSITE_ADMIN_SITE_TITLE = "uKKU2 Quality Document Manager"
```
4. go to the uKKU2_TNM site and populate the database:
```
source ~/web/data/uKKU2_data_TNM/env/uKKU2/bin/activate
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
```

### Step 4 : Start the site as a ubuntu service

This step aims to create a gunicorn service for the uKKU2 site.

1. create the file **/etc/systemd/system/ukku2tnm.gunicorn.service**:
```
sudo nano /etc/systemd/system/ukku2tnm.gunicorn.service
```
2. put the following content into it:
```
[Unit]
Description=ukku2tnm.gunicorn daemon
After=network.target

[Service]
User=mzarka
Group=www-data
WorkingDirectory=/home/mzarka/web/sites/uKKU2_TNM
ExecStart=/home/mzarka/web/data/uKKU2_data_TNM/env/uKKU2/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/home/mzarka/web/data/uKKU2_data_TNM/run/ukku2tnm.gunicorn.sock \
          uKKU2.wsgi:application

[Install]
WantedBy=multi-user.target
```

3. start the service and enable it:
```
sudo systemctl start ukku2tnm.gunicorn.service
sudo systemctl enable ukku2tnm.gunicorn.service
sudo systemctl status ukku2tnm.gunicorn.service
```
The last instruction should show that the service is active.


in order to restart the uKKU2 site, type the following command:

```
sudo systemctl restart ukku2tnm.gunicorn.service
```

### Step 5 : Configure NGINX
**TODO**
### Step 6 : Site, database and media backups
In order to make backups for the database and the media files of the uKKU2 site, we use the 
**django-dbbackup** package.

#### Backups
* In order to make backups for the database and the media files, we type the following command:
```
python manage.py dbbackup --compress
python manage.py mediabackup --compress
```
* Then, and if we want to restore the database and the media files, we type the following command:
```
python manage.py dbrestore --uncompress
python manage.py mediarestore --uncompress 
```

The backup files (database and media) are stored in the **~/web/data/uKKU2_data_TNM/backups** folder.

In order to not lose backups after a server problem, save these backups in another support (local hard disk, Google Drive, ...).