@echo off
REM Activate venv and run test
cd /d "%~dp0"
call crew_venv\Scripts\activate.bat
python test_live.py
pause
