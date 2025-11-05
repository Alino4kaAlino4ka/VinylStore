@echo off
echo Проверка работы сервисов...
echo.

echo Проверка портов:
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
echo Проверка завершена!
echo.
echo Для полного тестирования откройте check_services.html в браузере
echo.
pause
