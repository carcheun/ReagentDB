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

# flush will clear your database
#python manage.py flush --no-input
python manage.py makemigrations
python manage.py migrate
python manage.py initadmin
python manage.py collectstatic --noinput
# Is this cronjob even working? I dont know
# python manage.py crontab add

exec "$@"