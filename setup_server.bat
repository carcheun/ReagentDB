@echo off 

Rem Server setup batch scrip, commands are 'start', 'stop', 'clean' and a hidden
Rem option 'clean_all'. clean_all will clean containers, images, AND volumes 

if "%~1"=="start" (echo Starting the server...
    GOTO docker_stop) 
if "%~1"=="stop" (echo Stopping the server... 
    GOTO docker_stop)
if "%~1"=="clean" (echo Cleaning containers and images 
    GOTO docker_clean)
if "%~1"=="clean_all" (GOTO docker_clean_all)

echo Commands: [start] [stop] [clean]
echo start - starts the server
echo stop - stops the server
echo clean - clean up containers and images
goto:eof

:docker_clean
    docker-compose -f .\local.docker-compose.prod.yml down
    FOR /f "tokens=*" %%i IN ('docker ps -aq') DO docker rm %%i -f
    FOR /f "tokens=*" %%i IN ('docker images --format "{{.ID}}"') DO docker rmi %%i -f
    goto:eof

:docker_clean_all
    Rem Clean all, including volumes
    echo [101m[WARNING]: ALL ENTRIES IN THE DATABASE WILL BE PERMENANTLY DELETED[0m
    set /p confirm_clean_all="Continue? (Y/N)"

    if "%confirm_clean_all%"=="Y" (GOTO docker_clean_all_confirm)
    if "%confirm_clean_all%"=="y" goto docker_clean_all_confirm

    echo Aborting clean process...
    goto:eof

:docker_clean_all_confirm
    echo [101m[WARNING]: STARTING DATABASE VOLUME REMOVAL PROCESS...[0m
    docker-compose -f .\local.docker-compose.prod.yml down
    FOR /f "tokens=*" %%i IN ('docker ps -aq') DO docker rm %%i
    FOR /f "tokens=*" %%i IN ('docker images --format "{{.ID}}"') DO docker rmi %%i -f
    docker volume prune
    goto:eof

:docker_stop
    docker-compose -f .\local.docker-compose.prod.yml down
    if "%~1"=="start" (GOTO docker_start)
    goto:eof

:docker_start
    Rem Build images from .tar files and then build containers
    docker load -i nginx.tar
    docker load -i postgres.tar
	docker load -i redis.tar
    docker load -i rdb.tar
    docker-compose -f .\local.docker-compose.prod.yml up --build -d