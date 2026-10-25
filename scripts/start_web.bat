@echo off
cd /d "%~dp0.."
for /f "delims=" %%i in ('powershell -NoProfile -Command "[Environment]::GetEnvironmentVariable('DEEPSEEK_API_KEY','User')"') do set "DEEPSEEK_API_KEY=%%i"
".venv\Scripts\python.exe" "web\app.py"
pause
