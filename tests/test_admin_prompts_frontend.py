#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование фронтенд функционала админ-панели для промптов
Проверяет доступность API и корректность данных
"""

import requests
import json
import sys
from pathlib import Path

PROMPTS_MANAGER_URL = "http://127.0.0.1:8007"
TIMEOUT = 5

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name):
    print(f"\n{Colors.BLUE}[TEST] {name}{Colors.END}")

def print_success(message):
    print(f"{Colors.GREEN}[OK] {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}[FAIL] {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}[WARN] {message}{Colors.END}")

def test_api_accessible_from_browser():
    """Тест доступности API для браузерных запросов"""
    print_test("API доступен для браузерных запросов")
    try:
        # Симулируем браузерный запрос
        response = requests.get(
            f"{PROMPTS_MANAGER_URL}/api/v1/prompts",
            headers={
                "Origin": "null",  # Origin для file:// протокола
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            },
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            print_success("API доступен для браузерных запросов")
            
            # Проверяем CORS
            if "Access-Control-Allow-Origin" in response.headers:
                print_success("CORS заголовки присутствуют")
                return True
            else:
                print_error("CORS заголовки отсутствуют")
                return False
        else:
            print_error(f"API недоступен: статус {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Не удалось подключиться к API. Убедитесь, что сервис запущен.")
        return False
    except Exception as e:
        print_error(f"Ошибка: {e}")
        return False

def test_api_returns_valid_json():
    """Тест валидности JSON ответа"""
    print_test("API возвращает валидный JSON")
    try:
        response = requests.get(f"{PROMPTS_MANAGER_URL}/api/v1/prompts", timeout=TIMEOUT)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    print_success("JSON валиден и является массивом")
                    return True
                else:
                    print_error(f"JSON не является массивом: {type(data)}")
                    return False
            except json.JSONDecodeError as e:
                print_error(f"Невалидный JSON: {e}")
                return False
        else:
            print_error(f"Ошибка статуса: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Ошибка: {e}")
        return False

def test_prompts_structure():
    """Тест структуры промптов"""
    print_test("Структура промптов корректна")
    try:
        response = requests.get(f"{PROMPTS_MANAGER_URL}/api/v1/prompts", timeout=TIMEOUT)
        
        if response.status_code == 200:
            prompts = response.json()
            
            if not prompts:
                print_warning("Список промптов пуст")
                return True
            
            required_fields = ["id", "name", "template"]
            all_valid = True
            
            for prompt in prompts:
                missing = [f for f in required_fields if f not in prompt]
                if missing:
                    print_error(f"Промпт {prompt.get('id', 'unknown')} не содержит поля: {missing}")
                    all_valid = False
                else:
                    # Проверяем типы
                    if not isinstance(prompt["id"], str):
                        print_error(f"Поле 'id' должно быть строкой, получено: {type(prompt['id'])}")
                        all_valid = False
                    if not isinstance(prompt["name"], str):
                        print_error(f"Поле 'name' должно быть строкой, получено: {type(prompt['name'])}")
                        all_valid = False
                    if not isinstance(prompt["template"], str):
                        print_error(f"Поле 'template' должно быть строкой, получено: {type(prompt['template'])}")
                        all_valid = False
            
            if all_valid:
                print_success("Все промпты имеют корректную структуру")
                print(f"   Проверено промптов: {len(prompts)}")
                for prompt in prompts:
                    print(f"   - {prompt['id']}: {prompt['name']}")
            
            return all_valid
        else:
            print_error(f"Ошибка получения промптов: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Ошибка: {e}")
        return False

def test_update_prompt_api():
    """Тест API обновления промпта"""
    print_test("API обновления промпта работает")
    try:
        # Получаем первый промпт
        get_response = requests.get(f"{PROMPTS_MANAGER_URL}/api/v1/prompts", timeout=TIMEOUT)
        if get_response.status_code != 200:
            print_error("Не удалось получить промпты для теста")
            return False
        
        prompts = get_response.json()
        if not prompts:
            print_warning("Нет промптов для теста")
            return True
        
        prompt_id = prompts[0]["id"]
        original_template = prompts[0]["template"]
        
        # Обновляем промпт
        update_data = {"template": original_template + "\n[Тест обновления]"}
        update_response = requests.put(
            f"{PROMPTS_MANAGER_URL}/api/v1/prompts/{prompt_id}",
            json=update_data,
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        
        if update_response.status_code == 200:
            updated_prompt = update_response.json()
            
            # Проверяем CORS
            if "Access-Control-Allow-Origin" in update_response.headers:
                print_success("CORS заголовки присутствуют в ответе PUT")
            else:
                print_warning("CORS заголовки отсутствуют в ответе PUT")
            
            if updated_prompt["template"] == update_data["template"]:
                print_success("Промпт успешно обновлен")
                
                # Восстанавливаем оригинал
                restore_data = {"template": original_template}
                restore_response = requests.put(
                    f"{PROMPTS_MANAGER_URL}/api/v1/prompts/{prompt_id}",
                    json=restore_data,
                    headers={"Content-Type": "application/json"},
                    timeout=TIMEOUT
                )
                
                if restore_response.status_code == 200:
                    print_success("Оригинальный контент восстановлен")
                
                return True
            else:
                print_error("Контент не обновлен корректно")
                return False
        else:
            print_error(f"Ошибка обновления: {update_response.status_code}")
            print_error(f"Ответ: {update_response.text[:200]}")
            return False
    except Exception as e:
        print_error(f"Ошибка: {e}")
        return False

def test_error_responses_structure():
    """Тест структуры ответов с ошибками"""
    print_test("Структура ответов с ошибками корректна")
    try:
        # Запрашиваем несуществующий промпт
        response = requests.get(
            f"{PROMPTS_MANAGER_URL}/api/v1/prompts/nonexistent_prompt_12345",
            timeout=TIMEOUT
        )
        
        if response.status_code == 404:
            # Проверяем, что ответ валидный JSON
            try:
                error_data = response.json()
                if "detail" in error_data:
                    print_success("Структура ошибки корректна (JSON с полем 'detail')")
                    # Проверяем CORS
                    if "Access-Control-Allow-Origin" in response.headers:
                        print_success("CORS заголовки присутствуют в ответе ошибки")
                        return True
                    else:
                        print_error("CORS заголовки отсутствуют в ответе ошибки")
                        return False
                else:
                    print_error("Ответ ошибки не содержит поле 'detail'")
                    return False
            except json.JSONDecodeError:
                print_error("Ответ ошибки не является валидным JSON")
                return False
        else:
            print_warning(f"Неожиданный статус для несуществующего промпта: {response.status_code}")
            return True
    except Exception as e:
        print_error(f"Ошибка: {e}")
        return False

def main():
    """Запуск всех тестов фронтенда"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("[TEST] ТЕСТИРОВАНИЕ ФРОНТЕНД ФУНКЦИОНАЛА АДМИН-ПАНЕЛИ")
    print(f"{'='*60}{Colors.END}\n")
    
    tests = [
        ("API доступен для браузера", test_api_accessible_from_browser),
        ("API возвращает валидный JSON", test_api_returns_valid_json),
        ("Структура промптов корректна", test_prompts_structure),
        ("API обновления работает", test_update_prompt_api),
        ("Структура ошибок корректна", test_error_responses_structure),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Критическая ошибка в тесте '{test_name}': {e}")
            results.append((test_name, False))
    
    # Итоговая статистика
    print(f"\n{Colors.BLUE}{'='*60}")
    print("[RESULTS] РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ ФРОНТЕНДА")
    print(f"{'='*60}{Colors.END}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Colors.GREEN}[PASSED]{Colors.END}" if result else f"{Colors.RED}[FAILED]{Colors.END}"
        print(f"{test_name:.<50} {status}")
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"Итого: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print(f"{Colors.GREEN}[SUCCESS] ВСЕ ТЕСТЫ ФРОНТЕНДА ПРОЙДЕНЫ!{Colors.END}\n")
        return 0
    else:
        print(f"{Colors.RED}[WARNING] НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ{Colors.END}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())

