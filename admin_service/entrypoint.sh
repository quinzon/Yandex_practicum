#!/bin/sh

python manage.py migrate --fake --fake movies 0001
python manage.py migrate --no-input

exec "$@"