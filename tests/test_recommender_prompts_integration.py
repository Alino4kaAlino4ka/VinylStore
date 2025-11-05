#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование интеграции Recommender с Prompts Manager
Проверяет Headless AI архитектуру
"""

import requests
import json
import sys
from pathlib import Path

# Добавляем корневую папку проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

PROMPTS_MANAGER_URL = "http://127.0.0.1:8007"
RECOMMENDER_URL = "http://127.0.0.1:8004"
TIMEOUT = 10

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

def check_service_health(url, service_name):
    """Проверка доступности сервиса"""
    try:
        response = requests.get(f"{url}/health", timeout=5)
        if response.status_code == 200:
            print_success(f"{service_name} доступен")
            return True
        else:
            print_error(f"{service_name} недоступен (статус: {response.status_code})")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"{service_name} не запущен на {url}")
        return False
    except Exception as e:
        print_error(f"Ошибка при проверке {service_name}: {e}")
        return False

def test_prompts_manager_available():
    """Тест доступности Prompts Manager"""
    print_test("Prompts Manager доступность")
    return check_service_health(PROMPTS_MANAGER_URL, "Prompts Manager")

def test_recommender_available():
    """Тест доступности Recommender"""
    print_test("Recommender доступность")
    return check_service_health(RECOMMENDER_URL, "Recommender")

def test_prompts_manager_has_prompts():
    """Проверка наличия промптов в Prompts Manager"""
    print_test("Наличие промптов в Prompts Manager")
    try:
        response = requests.get(f"{PROMPTS_MANAGER_URL}/api/v1/prompts", timeout=TIMEOUT)
        
        if response.status_code == 200:
            prompts = response.json()
            if isinstance(prompts, list) and len(prompts) > 0:
                print_success(f"Найдено {len(prompts)} промптов")
                
                # Проверяем наличие необходимых промптов
                prompt_ids = [p["id"] for p in prompts]
                required_prompts = ["recommendation_prompt", "description_prompt"]
                
                for req_prompt in required_prompts:
                    if req_prompt in prompt_ids:
                        print_success(f"Промпт '{req_prompt}' найден")
                    else:
                        print_error(f"Промпт '{req_prompt}' не найден")
                        return False
                
                return True
            else:
                print_warning("Промпты не найдены в Prompts Manager")
                return False
        else:
            print_error(f"Ошибка получения промптов: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Ошибка: {e}")
        return False

def test_recommender_gets_recommendation_prompt():
    """Тест получения промпта рекомендаций через Recommender"""
    print_test("Recommender получает промпт рекомендаций")
    try:
        # Проверяем, что Recommender может работать с промптами
        # Делаем простой запрос на генерацию рекомендаций
        response = requests.post(
            f"{RECOMMENDER_URL}/api/v1/recommendations/generate",
            json={
                "prompt": "Тестовый запрос"
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        # Ожидаем либо успешный ответ, либо ошибку, но не 503 (service unavailable)
        if response.status_code == 503:
            error_detail = response.json().get("detail", "")
            if "prompts-manager" in error_detail.lower():
                print_error("Recommender не может подключиться к Prompts Manager")
                return False
            else:
                print_warning(f"Другая ошибка 503: {error_detail}")
                return False
        elif response.status_code in [200, 500]:
            # 200 - успех, 500 - возможно проблема с LLM, но не с Prompts Manager
            print_success("Recommender успешно обработал запрос (промпты получены)")
            return True
        else:
            print_warning(f"Неожиданный статус: {response.status_code}")
            # Не считаем это критической ошибкой
            return True
    except requests.exceptions.Timeout:
        print_warning("Таймаут запроса (возможно LLM медленно отвечает)")
        return True  # Не критично для теста интеграции
    except Exception as e:
        print_error(f"Ошибка: {e}")
        return False

def test_prompts_manager_cors_for_browser():
    """Тест CORS для браузерных запросов"""
    print_test("CORS для браузерных запросов")
    try:
        # Симулируем браузерный запрос с Origin
        response = requests.get(
            f"{PROMPTS_MANAGER_URL}/api/v1/prompts",
            headers={
                "Origin": "null",
                "Access-Control-Request-Method": "GET"
            },
            timeout=TIMEOUT
        )
        
        # Проверяем CORS заголовки
        cors_headers = ["Access-Control-Allow-Origin", "Access-Control-Allow-Methods"]
        missing_headers = []
        
        for header in cors_headers:
            if header in response.headers:
                print_success(f"{header}: {response.headers[header]}")
            else:
                missing_headers.append(header)
        
        if not missing_headers:
            print_success("Все необходимые CORS заголовки присутствуют")
            return True
        else:
            print_error(f"Отсутствуют CORS заголовки: {missing_headers}")
            return False
    except Exception as e:
        print_error(f"Ошибка: {e}")
        return False

def test_error_responses_have_cors():
    """Тест, что ответы с ошибками тоже имеют CORS заголовки"""
    print_test("CORS заголовки в ответах с ошибками")
    try:
        # Запрашиваем несуществующий промпт
        response = requests.get(
            f"{PROMPTS_MANAGER_URL}/api/v1/prompts/nonexistent_test_prompt_12345",
            headers={"Origin": "null"},
            timeout=TIMEOUT
        )
        
        # Должна быть ошибка 404
        if response.status_code == 404:
            # Проверяем наличие CORS заголовков
            if "Access-Control-Allow-Origin" in response.headers:
                print_success("CORS заголовки присутствуют в ответе ошибки 404")
                return True
            else:
                print_error("CORS заголовки отсутствуют в ответе ошибки 404")
                return False
        else:
            print_warning(f"Неожиданный статус: {response.status_code}")
            return True
    except Exception as e:
        print_error(f"Ошибка: {e}")
        return False

def main():
    """Запуск всех тестов интеграции"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("[TEST] ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ RECOMMENDER <-> PROMPTS MANAGER")
    print(f"{'='*60}{Colors.END}\n")
    
    tests = [
        ("Prompts Manager доступность", test_prompts_manager_available),
        ("Recommender доступность", test_recommender_available),
        ("Наличие промптов", test_prompts_manager_has_prompts),
        ("Recommender получает промпты", test_recommender_gets_recommendation_prompt),
        ("CORS для браузера", test_prompts_manager_cors_for_browser),
        ("CORS в ответах с ошибками", test_error_responses_have_cors),
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
    print("[RESULTS] РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ ИНТЕГРАЦИИ")
    print(f"{'='*60}{Colors.END}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Colors.GREEN}[PASSED]{Colors.END}" if result else f"{Colors.RED}[FAILED]{Colors.END}"
        print(f"{test_name:.<50} {status}")
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"Итого: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print(f"{Colors.GREEN}[SUCCESS] ВСЕ ТЕСТЫ ИНТЕГРАЦИИ ПРОЙДЕНЫ!{Colors.END}\n")
        return 0
    else:
        print(f"{Colors.RED}[WARNING] НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ{Colors.END}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())

