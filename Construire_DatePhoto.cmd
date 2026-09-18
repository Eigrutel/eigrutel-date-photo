@echo off
setlocal
cd /d "%~dp0"
echo Date Photo - Construction Windows / Windows build
py -3 -m venv .venv
if errorlevel 1 goto error
".venv\Scripts\python.exe" -m pip install -r requirements-build.txt
if errorlevel 1 goto error
".venv\Scripts\python.exe" -m unittest discover -v
if errorlevel 1 goto error
".venv\Scripts\python.exe" build_windows.py
if errorlevel 1 goto error
echo Termine / Done: dist\DatePhoto-1.0.0.exe
pause
exit /b 0
:error
echo ECHEC / FAILED - Consultez le message ci-dessus / See error above.
pause
exit /b 1
