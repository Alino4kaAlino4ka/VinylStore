@echo off
echo Starting Fixed Services...
echo.

echo Starting Catalog Service on port 8000...
start "Catalog Service" cmd /k "cd /d %~dp0services\catalog && python main.py"

timeout /t 3 /nobreak >nul

echo Starting Recommender Service on port 8004...
REM API ключ должен быть установлен в config.env или переменных окружения системы
REM НЕ храните API ключи в batch файлах!
start "Recommender Service" cmd /k "cd /d %~dp0services\recommender && python main.py"

echo.
echo Services started!
echo.
echo Service URLs:
echo - Catalog Service: http://127.0.0.1:8000
echo - Recommender Service: http://127.0.0.1:8004
echo.
echo Press any key to exit...
pause >nul
