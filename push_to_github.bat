@echo off
setlocal
cd /d "%~dp0"

echo ========================================================
echo Pushing latest code to https://github.com/shahbaz147/awaaz-tts...
echo ========================================================

git init
git config user.email "shahbaz147@users.noreply.github.com"
git config user.name "shahbaz147"

git branch -M main
git remote remove origin >nul 2>&1
git remote add origin https://github.com/shahbaz147/awaaz-tts.git

git add .
git commit -m "Add Vercel serverless support and all Pakistani voices"
git push -u origin main --force

echo.
echo ========================================================
echo Code successfully pushed to GitHub!
echo ========================================================
pause
