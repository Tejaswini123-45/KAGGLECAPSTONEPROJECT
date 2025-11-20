@echo off
REM Web Server Launcher
REM Serves index.html on http://localhost:5000

cd /d "%~dp0"

echo.
echo ====================================
echo   Starting Web Server (port 5000)
echo ====================================
echo.
echo Open this in your browser:
echo   http://localhost:5000
echo.
echo In another terminal, run:
echo   python main.py server
echo.
echo Press Ctrl+C to stop this server
echo.

crew_venv\Scripts\python.exe web_server.py

pause
