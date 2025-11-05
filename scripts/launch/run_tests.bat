@echo off
echo 🧪 Запуск тестов функционала корзины
echo =====================================
echo.

echo 📋 Доступные тесты:
echo 1. Простые тесты (tests/simple_tests.html)
echo 2. Интерактивные тесты (tests/test_cart_frontend.html)
echo 3. Unit-тесты в консоли (tests/test_cart_unit.html)
echo 4. Отладка (tests/debug_cart.html)
echo 5. Открыть папку с тестами
echo 6. Запустить все тесты
echo.

set /p choice="Выберите опцию (1-6): "

if "%choice%"=="1" (
    echo 🚀 Запуск простых тестов...
    start tests/simple_tests.html
    echo ✅ Простые тесты открыты в браузере
) else if "%choice%"=="2" (
    echo 🚀 Запуск интерактивных тестов...
    start tests/test_cart_frontend.html
    echo ✅ Интерактивные тесты открыты в браузере
) else if "%choice%"=="3" (
    echo 🚀 Запуск unit-тестов...
    start tests/test_cart_unit.html
    echo ✅ Unit-тесты открыты в браузере
) else if "%choice%"=="4" (
    echo 🔍 Запуск отладки...
    start tests/debug_cart.html
    echo ✅ Отладка открыта в браузере
) else if "%choice%"=="5" (
    echo 📁 Открытие папки с тестами...
    explorer tests
    echo ✅ Папка с тестами открыта
) else if "%choice%"=="6" (
    echo 🚀 Запуск всех тестов...
    start tests/simple_tests.html
    timeout /t 2 /nobreak >nul
    start tests/test_cart_frontend.html
    timeout /t 2 /nobreak >nul
    start tests/test_cart_unit.html
    timeout /t 2 /nobreak >nul
    start tests/debug_cart.html
    echo ✅ Все тесты открыты в браузере
) else (
    echo ❌ Неверный выбор. Попробуйте снова.
)

echo.
echo 📖 Для получения дополнительной информации см. tests/README.md
pause
