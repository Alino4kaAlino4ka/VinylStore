@echo off
echo ========================================
echo    🧪 ЗАПУСК ВСЕХ ТЕСТОВ АУДИТЕРИЯ
echo ========================================
echo.

echo 📁 Переходим в папку tests...
cd /d "%~dp0"

echo.
echo 🚀 Запускаем Python тесты...
echo.

echo 1️⃣ Тесты авторизации администратора...
python test_admin_auth.py
echo.

echo 2️⃣ Тесты сервиса корзины...
python test_cart_service.py
echo.

echo 3️⃣ Тесты сервиса каталога...
python test_catalog_service.py
echo.

echo 4️⃣ Тесты сервиса заказов...
python test_orders_service.py
echo.

echo 5️⃣ Тесты базы данных...
python test_database.py
echo.

echo 6️⃣ Тесты подключения к OpenRouter...
python test_openrouter_connection.py
echo.

echo 7️⃣ Тесты рекомендательной системы...
python test_recommender_full.py
echo.

echo ========================================
echo    ✅ ВСЕ PYTHON ТЕСТЫ ЗАВЕРШЕНЫ
echo ========================================
echo.
echo 🌐 Для запуска HTML тестов откройте в браузере:
echo    - test_hub.html (центральный хаб)
echo    - test_recommendations_ui.html (рекомендации)
echo    - test_cart_frontend.html (корзина)
echo    - test_admin_auth.html (авторизация)
echo.
echo Нажмите любую клавишу для выхода...
pause >nul
