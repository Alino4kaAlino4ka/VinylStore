@echo off
echo Перезапуск всех сервисов...
echo.

echo Остановка всех процессов Python...
taskkill /f /im python.exe 2>nul
echo.

echo Ожидание 3 секунды...
ping 127.0.0.1 -n 4 >nul
echo.

echo Запуск Catalog Service (порт 8000)...
start "Catalog Service" cmd /k "cd /d %~dp0services\catalog && echo Starting Catalog Service... && python -c \"from main import app; import uvicorn; uvicorn.run(app, host='127.0.0.1', port=8000, reload=True)\""

echo Ожидание 2 секунды...
ping 127.0.0.1 -n 3 >nul

echo Запуск Cart Service (порт 8001)...
start "Cart Service" cmd /k "cd /d %~dp0services\cart && echo Starting Cart Service... && python -c \"from main import app; import uvicorn; uvicorn.run(app, host='127.0.0.1', port=8001, reload=True)\""

echo Ожидание 2 секунды...
ping 127.0.0.1 -n 3 >nul

echo Запуск Orders Service (порт 8002)...
start "Orders Service" cmd /k "cd /d %~dp0services\orders && echo Starting Orders Service... && python -c \"from main import app; import uvicorn; uvicorn.run(app, host='127.0.0.1', port=8002, reload=True)\""

echo Ожидание 2 секунды...
ping 127.0.0.1 -n 3 >nul

echo Запуск Users Service (порт 8003)...
start "Users Service" cmd /k "cd /d %~dp0services\users && echo Starting Users Service... && python -c \"from main import app; import uvicorn; uvicorn.run(app, host='127.0.0.1', port=8003, reload=True)\""

echo.
echo Все сервисы запущены!
echo.
echo Ожидание 5 секунд для полного запуска...
ping 127.0.0.1 -n 6 >nul

echo.
echo Проверка статуса сервисов:
echo.

echo Catalog Service (порт 8000):
powershell -Command "try { $response = Invoke-RestMethod -Uri 'http://localhost:8000/health' -Method Get; Write-Host 'OK -' $response.status } catch { Write-Host 'ERROR -' $_.Exception.Message }"

echo Cart Service (порт 8001):
powershell -Command "try { $response = Invoke-RestMethod -Uri 'http://localhost:8001/health' -Method Get; Write-Host 'OK -' $response.status } catch { Write-Host 'ERROR -' $_.Exception.Message }"

echo Orders Service (порт 8002):
powershell -Command "try { $response = Invoke-RestMethod -Uri 'http://localhost:8002/health' -Method Get; Write-Host 'OK -' $response.status } catch { Write-Host 'ERROR -' $_.Exception.Message }"

echo Users Service (порт 8003):
powershell -Command "try { $response = Invoke-RestMethod -Uri 'http://localhost:8003/health' -Method Get; Write-Host 'OK -' $response.status } catch { Write-Host 'ERROR -' $_.Exception.Message }"

echo.
echo Перезапуск завершен!
echo Для полного тестирования откройте check_services.html в браузере
echo.
pause


