#!/bin/bash

poetry run python manage.py collectstatic --noinput
poetry run python manage.py migrate

mkdir -p /home/app/data/logs/gunicorn
touch /home/app/data/logs/gunicorn/gunicorn.log
touch /home/app/data/logs/gunicorn/access.log

poetry run gunicorn django_rest.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 1 \
  --log-level info \
  --log-file /home/app/data/logs/gunicorn/gunicorn.log \
  --access-logfile /home/app/data/logs/gunicorn/access.log \
  --pid /home/app/data/gunicorn.pid
