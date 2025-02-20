#!/bin/sh

cd /app
# Collect static files
echo "Collecting static files"
python manage.py collectstatic --noinput

# Creating database migrations
echo "Applying database migrations"
python manage.py makemigrations --noinput

# Apply database migrations
echo "Applying database migrations"
python manage.py migrate

# Start the server
echo "Starting gunicorn"
gunicorn --chdir=/app/src \
    --workers=4 \
    --threads=6 \
    --worker-class=gthread \
    --preload \
    --bind :8000 \
    --log-level=info \
    --error-logfile - \
    --access-logfile - \
    --capture-output \
    tecgen.wsgi:application

cd -
