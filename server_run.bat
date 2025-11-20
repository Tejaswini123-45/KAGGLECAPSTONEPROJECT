@echo off
REM Start API server with venv
cd /d "%~dp0"
call crew_venv\Scripts\activate.bat
python main.py server
pause
