#!/bin/sh
set -eu

mkdir -p "$(dirname "$OPEN_FMEA_DB_PATH")"

python manage.py migrate --noinput
python manage.py seed_demo

exec python manage.py runserver "0.0.0.0:${PORT:-8000}"

