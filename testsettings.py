USE_TZ = True

SECRET_KEY = 'notSECRET'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache'
    }
}

INSTALLED_APPS = (
    'people',
    'metadata',
)
