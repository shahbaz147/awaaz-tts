@echo off
title Awaaz Edge-TTS Server
cd /d "%~dp0"

set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
set "PIP_EXE=%LOCALAPPDATA%\Programs\Python\Python312\Scripts\pip.exe"

if not exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=python"
    set "PIP_EXE=pip"
)

echo [1/2] Installing / verifying dependencies...
"%PIP_EXE%" install -r requirements.txt

echo.
echo [2/2] Starting Awaaz Edge-TTS Server on http://127.0.0.1:5000...
echo.
"%PYTHON_EXE%" app.py

pause

