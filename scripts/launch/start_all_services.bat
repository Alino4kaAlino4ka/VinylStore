@echo off
chcp 65001 >nul
echo Starting All Microservices...
echo.

echo Starting Catalog Service on port 8000...
start "Catalog Service" cmd /k "cd /d %~dp0services\catalog && python -c \"from main import app; import uvicorn; uvicorn.run(app, host='127.0.0.1', port=8000, reload=True)\""

timeout /t 2 /nobreak >nul

echo Starting Auth Service on port 8001...
start "Auth Service" cmd /k "cd /d %~dp0services\auth && python -c \"from main import app; import uvicorn; uvicorn.run(app, host='127.0.0.1', port=8001, reload=True)\""

timeout /t 2 /nobreak >nul

echo Starting Orders Service on port 8002...
start "Orders Service" cmd /k "cd /d %~dp0services\orders && python -c \"from main import app; import uvicorn; uvicorn.run(app, host='127.0.0.1', port=8002, reload=True)\""

timeout /t 2 /nobreak >nul

echo Starting Users Service on port 8003...
start "Users Service" cmd /k "cd /d %~dp0services\users && python -c \"from main import app; import uvicorn; uvicorn.run(app, host='127.0.0.1', port=8003, reload=True)\""

timeout /t 2 /nobreak >nul

echo Starting Prompts Manager Service on port 8007...
start "Prompts Manager Service" cmd /k "cd /d %~dp0services\prompts-manager && python -c \"from main import app; import uvicorn; uvicorn.run(app, host='127.0.0.1', port=8007, reload=True)\""

timeout /t 2 /nobreak >nul

echo Starting Recommender Service on port 8004...
REM API ключ должен быть установлен в config.env или переменных окружения системы
REM НЕ храните API ключи в batch файлах!
start "Recommender Service" cmd /k "cd /d %~dp0services\recommender && python -c \"from main import app; import uvicorn; uvicorn.run(app, host='127.0.0.1', port=8004, reload=True)\""

timeout /t 2 /nobreak >nul

echo Starting Cart Service on port 8005...
start "Cart Service" cmd /k "cd /d %~dp0services\cart && python -c \"from main import app; import uvicorn; uvicorn.run(app, host='127.0.0.1', port=8005, reload=True)\""

echo.
echo All microservices started!
echo.
echo Service URLs:
echo - Catalog Service: http://127.0.0.1:8000
echo - Auth Service: http://127.0.0.1:8001
echo - Orders Service: http://127.0.0.1:8002
echo - Users Service: http://127.0.0.1:8003
echo - Prompts Manager Service: http://127.0.0.1:8007
echo - Recommender Service: http://127.0.0.1:8004
echo - Cart Service: http://127.0.0.1:8005
echo.
echo Press any key to exit...
pause >nul
