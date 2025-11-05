@echo off
echo Stopping all microservices...
taskkill /f /im python.exe 2>nul
echo All microservices stopped.
pause




