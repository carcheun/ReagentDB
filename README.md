# ReagentDB :custard:

Database for storing PA and Reagents. Created with [Django](https://www.djangoproject.com/)

## As Docker App
### Installation
------------
Requirements:
-  [Docker Desktop (Windows)](https://docs.docker.com/docker-for-windows/install/)

## As Python App
### Installation
------------
Requirements:
-  [Python 3.7.X](https://www.python.org/downloads/)  
-  [postgresql](https://www.postgresql.org/download/)
  
  OPTIONAL:
    setup a postgresql [container](https://hub.docker.com/_/postgres) via [Docker Desktop](https://docs.docker.com/docker-for-windows/install/) instead of installing postgresql
    
python pip install requirements.txt
  
Usage
------------
python manage.py runserver

python manage.py testserver mydata.json

python manage.py test


Docker
------------
docker-compose -f docker-compose.yml up --build -d