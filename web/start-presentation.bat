@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "PORT=8000"
set "URL=http://localhost:%PORT%/"

cd /d "%SCRIPT_DIR%"

echo Uruchamianie serwera HTTP w katalogu: %SCRIPT_DIR%
echo Adres prezentacji: %URL%
start "" %URL%
python -m http.server %PORT%

endlocal
