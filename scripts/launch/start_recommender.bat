@echo off
echo Starting Recommender Service...
cd /d "%~dp0"

REM Загружаем переменные окружения из файла конфигурации
for /f "usebackq tokens=1,2 delims==" %%a in ("config.env") do (
    set %%a=%%b
)

echo API Key loaded: %OPENROUTER_API_KEY:~0,20%...
python -m uvicorn services.recommender.main:app --host 127.0.0.1 --port 8004 --reload
pause
