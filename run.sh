#!/bin/sh
if [[ -n "$UPDATE_DB" ]]; then
  echo "Updating POI database"
  python manage.py import-data
elif [[ -n "$INIT_DB" ]]; then
    echo "Initializing POI database"
    python manage.py drop-db
    python manage.py create-db
    python manage.py import-data
elif [[ -n "$TESTING" ]]; then
  echo "Running tests"
  export TESTING="True"
  python manage.py test
else
  gunicorn --config gunicorn_config.py manage:app
fi
