import os


def get_database_config():
    return {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
        'PORT': os.getenv('POSTGRES_PORT', 5432),
        'OPTIONS': {
            'options': os.getenv('POSTGRES_OPTIONS'),
        },
    }


DATABASES = {
    'default': get_database_config(),
}
