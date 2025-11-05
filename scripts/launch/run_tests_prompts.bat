@echo off
chcp 65001 >nul
echo Запуск всех тестов системы промптов...
echo.

cd /d %~dp0

echo [1/3] Тестирование Prompts Manager API...
python tests/test_prompts_manager_full.py
echo.

echo [2/3] Тестирование интеграции Recommender ^<^-> Prompts Manager...
python tests/test_recommender_prompts_integration.py
echo.

echo [3/3] Тестирование фронтенд функционала...
python tests/test_admin_prompts_frontend.py
echo.

echo.
echo Все тесты завершены!
pause

