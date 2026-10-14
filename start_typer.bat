@echo off
cd /d "%~dp0"
py -3 typer.py
if not errorlevel 1 exit /b 0
python typer.py
if not errorlevel 1 exit /b 0
echo.
echo Не удалось запустить приложение. Установите Python 3 с сайта python.org.
pause
