@echo off
setlocal
cd /d "%~dp0"

echo [1/3] Removing .python-version locally...
if exist ".python-version" del /f /q ".python-version"

echo [2/3] Erasing cached GitHub credentials...
(
echo protocol=https
echo host=github.com
) | git credential reject

echo [3/3] Setting remote to https://shahbaz147@github.com/shahbaz147/awaaz-tts.git...
git remote set-url origin https://shahbaz147@github.com/shahbaz147/awaaz-tts.git

git rm --cached .python-version >nul 2>&1
git add -A
git commit -m "Remove .python-version" >nul 2>&1

echo.
echo Pushing as shahbaz147...
git push -u origin main

pause
