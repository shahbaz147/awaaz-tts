@echo off
setlocal
cd /d "%~dp0"

echo [1/4] Removing .python-version locally...
if exist ".python-version" del /f /q ".python-version"

echo [2/4] Clearing old GitHub credentials from Windows...
cmdkey /delete:LegacyGeneric:target=git:https://github.com >nul 2>&1

echo [3/4] Staging changes...
git rm --cached .python-version >nul 2>&1
git add -A
git commit -m "Remove .python-version for Vercel Python 3.12" >nul 2>&1

echo [4/4] Pushing to https://github.com/shahbaz147/awaaz-tts...
echo.
echo * If a browser window pops up, click "Sign in with your browser" / "Authorize" *
echo.
git push -u origin main

echo.
echo Done! Check Vercel now.
pause

