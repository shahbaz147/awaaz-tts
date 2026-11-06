@echo off
setlocal
cd /d "%~dp0"

echo ========================================================
echo Awaaz Edge-TTS: Render Deployment Git Setup
echo ========================================================
echo.

where git >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Git is not installed or not in PATH.
    echo You can upload the files directly via GitHub.com in your browser!
    echo.
    pause
    exit /b 1
)

if not exist ".git" (
    echo [1/3] Initializing local git repository...
    git init
    git branch -M main
) else (
    echo [1/3] Git repository already initialized.
)

echo [2/3] Staging and committing files...
git add .
git commit -m "Deploy Awaaz Edge-TTS Server with Pakistani regional languages"

echo.
echo [3/3] Ready to push to GitHub!
echo.
set /p REPO_URL="Enter your GitHub Repository URL (e.g. https://github.com/username/awaaz-tts.git): "

if not "%REPO_URL%"=="" (
    git remote remove origin >nul 2>&1
    git remote add origin %REPO_URL%
    echo Pushing to GitHub...
    git push -u origin main
    echo.
    echo ========================================================
    echo SUCCESS! Code pushed to GitHub.
    echo Now connect this repo on https://dashboard.render.com!
    echo ========================================================
) else (
    echo No URL entered. You can push manually whenever you want.
)

echo.
pause

