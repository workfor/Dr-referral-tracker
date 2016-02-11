from Practice_Referral.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'test',
        'TEST_NAME': 'travis_ci_test',
    }
}
