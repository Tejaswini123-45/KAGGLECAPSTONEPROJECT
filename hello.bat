@echo off
REM Run main crew with venv
cd /d "%~dp0"
call crew_venv\Scripts\activate.bat
python main.py run
pause
