@echo off
REM Interactive chat with venv
cd /d "%~dp0"
call crew_venv\Scripts\activate.bat
python main.py chat
pause
