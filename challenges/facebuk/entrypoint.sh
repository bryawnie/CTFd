#!/bin/sh
set -e

# Sin volumen: la base se regenera en cada arranque. seed.py es determinista
# (random.Random(1337)) y app.py nunca escribe en la base.
if [ ! -f social.db ]; then
    python seed.py
fi

exec gunicorn --bind "0.0.0.0:${PORT:-8080}" app:app
