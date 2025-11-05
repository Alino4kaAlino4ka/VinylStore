@echo off
echo Starting Auth Service...
cd /d "%~dp0services\auth"
echo Current directory: %CD%
echo Starting Python service...
python main.py
pause
