# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'km4eHMibwT6Axr'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'sample_db.sqlite3'),
    }
}

# SOCIAL_AUTH_TWITTER_KEY = 'update me'
# SOCIAL_AUTH_TWITTER_SECRET = 'update me'

SOCIAL_AUTH_GITHUB_KEY = 'km4eHMibwT6Axr'
SOCIAL_AUTH_GITHUB_SECRET = 'km4eHMibwT6Axr'

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = 'km4eHMibwT6Axr.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'km4eHMibwT6Axr'

dbuser = 'referrel'
dbpass = 'km4eHMibwT6Axr'
EMAIL_HOST_USER = 'km4eHMibwT6Axr'
EMAIL_HOST_PASSWORD = 'km4eHMibwT6Axr'

AWS_ACCESS_KEY_ID = 'km4eHMibwT6Axr'
AWS_SECRET_ACCESS_KEY = 'km4eHMibwT6Axr'