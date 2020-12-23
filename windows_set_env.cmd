@ECHO OFF
if "%~1"=="dev_env" (echo setup dev enviornment...
    GOTO dev_env) 
if "%~1"=="production" (echo setup production enviornment... 
    GOTO prod_env)

echo Commands: [dev_env] [production]
echo dev_env - set developer enviornmental variables
echo production - set production enviornmental variables
goto:eof

:prod_env
    if exist .env.nodocker (
        echo Loading .env.nodocker variables
        FOR /F %%A IN (%~dp0\.env.nodocker) DO SET %%A
        FOR /F %%A IN (%~dp0\.env.nodocker) DO echo %%A
    ) else (
        echo ERROR: .env.nodocker is missing!
    )
    goto:eof

:dev_env
    if exist .env.dev (
        echo Loading .env.dev variables
        FOR /F %%A IN (%~dp0\.env.dev) DO SET %%A
        FOR /F %%A IN (%~dp0\.env.dev) DO echo %%A
    ) else (
        echo ERROR: .env.dev is missing!
    )
    goto:eof