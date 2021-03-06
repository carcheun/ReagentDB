#!/bin/sh
if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."
    echo $SQL_HOST $SQL_PORT

    while ! nc -zv $SQL_HOST $SQL_PORT; do
        sleep 0.1
    done

    echo "PostgreSQL started"
fi

if [ -z "$RDB_ONLY" ] && RDB_ONLY=1
then
    echo "Running manage.py setup commands"
    # flush will clear your database
    #python manage.py flush --no-input
    python manage.py makemigrations
    python manage.py migrate
    python manage.py initadmin
    python manage.py collectstatic --noinput
fi
# TODO: cronjob not working
#python manage.py crontab add

exec "$@"

#gunicorn ReagentDB.wsgi:application --bind 0.0.0.0:8000
#daphne ReagentDB.asgi:application --bind 0.0.0.0 --port 8000