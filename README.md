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
### Running Unit tests
First create a postgres database using docker. Close or stop other postgres containers first.
```
docker run --name postgres -e POSTGRES_USER=admin -e POSTGRES_PASSWORD=admin -p 5432:5432 -d postgres
```
Use activate.bat to enable python virtual environment in cmd.exe. Set the environmental variables using the following, with working directory as ReagentDB
```
windows_set_env.cmd dev_env
cd app
python manage.py makemigrations
python manage.py migrate
python manage.py test
```
### Running Dev Enviornment
Following above instructions, use the following instead of python manage.py test
```
python manage.py testserver mydata.json
```
or
```
python manage.py runserver
```

Docker
------------
### Running production server without local .tar files
```
docker-compose -f docker-compose.prod.yml up --build -d
```

### Running production server with local .tar files
```
setup_server.bat start
```

### Creating local image files from built images
Create local images from built images to ship to customers. First pull and build images from the hub/source code
```
docker-compose -f docker-compose.yml up --build -d
```
When images are built, carefully select the images used for ReagentDB and save them as .tar files
```
docker image ls
```
Copy the value under the column **IMAGE ID**. We will need to save images for nginx, postgres, reagentsdb, and redis.
```
docker save [imageID] -o [filename] [REPOSITORY]:[TAG]
...
docker save [imageID] -o nginx.tar nginx:1.19.2-alpine
docker save [imageID] -o postgres.tar postgres:latest
docker save [imageID] -o redis.tar redis:6.0-alpine
...
docker save e36f60b88522 -o rdb.tar reagentsdb:v0.1
```
we can manually load the images using the following
```
docker load nginx.tar
docker load rdb.tar
...
```
local.docker-compose.prod.yml is the docker yml file provided to customers that handles local images.