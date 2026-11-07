@echo off
setlocal
cd /d "%~dp0"

echo [1/3] Removing .python-version locally...
if exist ".python-version" del /f /q ".python-version"

echo [2/3] Preparing clean Vercel deployment...
git rm --cached .python-version >nul 2>&1
git add -A
git commit -m "Enhance voice resolution and resilience for English and Urdu fallback" >nul 2>&1

echo [3/3] Pushing to https://github.com/shahbaz147/awaaz-tts with force...
git push -u origin main --force

echo.
echo ========================================================
echo Code successfully pushed to GitHub!
echo Vercel will now automatically rebuild.
echo ========================================================
pause
