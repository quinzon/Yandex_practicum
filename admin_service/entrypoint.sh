#!/bin/sh

python manage.py migrate --fake --fake movies 0001
python manage.py migrate --no-input

gunicorn config.wsgi:application --bind 0.0.0.0:8002 --reload

exec "$@"