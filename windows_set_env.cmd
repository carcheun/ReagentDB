@ECHO OFF
if exist .env.dev.nodocker (
    echo Loading .env.dev.nodocker variables
    FOR /F %%A IN (%~dp0\.env.dev.nodocker) DO SET %%A
    FOR /F %%A IN (%~dp0\.env.dev.nodocker) DO echo %%A
) else (
    echo ERROR: .env.dev.nodocker is missing!
)