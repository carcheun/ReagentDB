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

daphne ReagentDB.asgi:application --bind 0.0.0.0 --port 9000