@echo off
setlocal
cd /d "%~dp0"

set "PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if not exist "%PY%" set "PY=python"

echo ========================================================
echo Checking exact Edge-TTS voices...
echo ========================================================
"%PY%" check_edge_voices.py
echo.
echo ========================================================
echo Running Awaaz TTS Synthesis Test...
echo ========================================================
"%PY%" test_tts.py
echo.
pause
