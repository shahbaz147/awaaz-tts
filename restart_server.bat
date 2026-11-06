@echo off
setlocal
cd /d "%~dp0"

echo [1/2] Stopping existing TTS server...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo [2/2] Starting fresh Awaaz Edge-TTS Server...
start "" "%~dp0start.bat"
echo Done! Server restarted in separate window.
timeout /t 3 /nobreak >nul

