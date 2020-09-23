# ReagentDB :custard:

Database for shared access of PA and Reagents. Created with [Django](https://www.djangoproject.com/). Additional documentation can be found [here](https://docs.google.com/document/d/1FQorW-QdDwtvsyt8JGdymdz8dF_mChPYoJoDqpSbcSg/edit?usp=sharing)

Installation
------------
### Using Docker App
Requirements:
-  [Docker Desktop (Windows)](https://docs.docker.com/docker-for-windows/install/)

### Without Docker
Requirements:
-  [Python 3.7.X](https://www.python.org/downloads/)  
-  [postgresql](https://www.postgresql.org/download/)
  
  OPTIONAL:
    setup a postgresql [container](https://hub.docker.com/_/postgres) via [Docker Desktop](https://docs.docker.com/docker-for-windows/install/) instead of installing postgresql
    
Python Virtual Enviornment Setup
```
pip install virtualenv
```
Change to the project directory and create the virtual enviornment
```
python -m virtualenv .
```
Use activate.bat in the newly generated 'Scripts' directory to access your virtual enviornment. Once within the enviornment, install the python requirements.
```
python pip install requirements.txt
```

Usage
------------
```
python manage.py runserver
python manage.py testserver mydata.json
python manage.py test
```

Docker
------------
```
docker-compose -f docker-compose.yml up --build -d
```
