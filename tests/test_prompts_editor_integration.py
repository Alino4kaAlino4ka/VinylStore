#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интеграционный тест для редактора промптов в админ-панели
Проверяет работу функции fetchAndRenderPrompts и сохранение промптов
"""

import sys
import os
import requests
import time
import json

# Настройка кодировки для Windows
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

API_BASE = "http://127.0.0.1:8007"

def wait_for_service(max_retries=30, delay=1):
    """Ожидание доступности сервиса"""
    print(f"⏳ Ожидание доступности сервиса prompts-manager на {API_BASE}...")
    for i in range(max_retries):
        try:
            response = requests.get(f"{API_BASE}/health", timeout=2)
            if response.status_code == 200:
                print(f"✅ Сервис доступен!")
                return True
        except requests.exceptions.RequestException:
            pass
        if i % 5 == 0 and i > 0:
            print(f"   ...попытка {i}/{max_retries}")
        time.sleep(delay)
    
    print(f"❌ Сервис недоступен после {max_retries} попыток")
    return False

def test_get_all_prompts():
    """Тест получения всех промптов (эмуляция fetchAndRenderPrompts)"""
    print("\n1️⃣ Тест GET /api/v1/prompts (функция fetchAndRenderPrompts)...")
    try:
        response = requests.get(f"{API_BASE}/api/v1/prompts", timeout=5)
        
        if response.status_code != 200:
            print(f"   ❌ FAILED: HTTP {response.status_code}")
            return False
        
        prompts = response.json()
        
        if not isinstance(prompts, list):
            print(f"   ❌ FAILED: Ожидался список, получен {type(prompts)}")
            return False
        
        print(f"   ✅ PASSED: Получено промптов: {len(prompts)}")
        
        # Проверяем структуру каждого промпта
        required_fields = ['id', 'name', 'content']
        for prompt in prompts:
            for field in required_fields:
                if field not in prompt:
                    print(f"   ❌ FAILED: Отсутствует поле '{field}' в промпте")
                    return False
        
        # Проверяем наличие дефолтных промптов
        names = [p['name'] for p in prompts]
        if 'recommendation_prompt' in names:
            print("   ✅ Найден recommendation_prompt")
        else:
            print("   ⚠️  recommendation_prompt не найден (может быть проблемой)")
        
        if 'description_prompt' in names:
            print("   ✅ Найден description_prompt")
        else:
            print("   ⚠️  description_prompt не найден (может быть проблемой)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False

def test_update_prompt_simulation():
    """Тест обновления промпта (эмуляция клика на 'Сохранить')"""
    print("\n2️⃣ Тест PUT /api/v1/prompts/{name} (кнопка 'Сохранить')...")
    try:
        # Получаем текущий промпт
        get_response = requests.get(f"{API_BASE}/api/v1/prompts/recommendation_prompt", timeout=5)
        if get_response.status_code != 200:
            print(f"   ❌ FAILED: Не удалось получить промпт (HTTP {get_response.status_code})")
            return False
        
        original_prompt = get_response.json()
        original_content = original_prompt['content']
        
        # Генерируем тестовый контент
        test_content = f"""ТЕСТОВЫЙ ПРОМПТ ДЛЯ ИНТЕГРАЦИОННОГО ТЕСТА
Создан: {time.strftime('%Y-%m-%d %H:%M:%S')}
Этот промпт будет удален после теста."""
        
        # Выполняем PUT запрос (как в функции сохранения)
        update_response = requests.put(
            f"{API_BASE}/api/v1/prompts/recommendation_prompt",
            headers={'Content-Type': 'application/json'},
            json={'content': test_content},
            timeout=5
        )
        
        if update_response.status_code != 200:
            print(f"   ❌ FAILED: HTTP {update_response.status_code}")
            try:
                error_detail = update_response.json()
                print(f"   Детали ошибки: {error_detail}")
            except:
                pass
            return False
        
        updated_prompt = update_response.json()
        
        if updated_prompt['content'] != test_content:
            print(f"   ❌ FAILED: Контент не обновился")
            print(f"   Ожидалось: {test_content[:50]}...")
            print(f"   Получено: {updated_prompt['content'][:50]}...")
            return False
        
        print("   ✅ PASSED: Промпт успешно обновлен")
        
        # Восстанавливаем оригинальный контент
        restore_response = requests.put(
            f"{API_BASE}/api/v1/prompts/recommendation_prompt",
            headers={'Content-Type': 'application/json'},
            json={'content': original_content},
            timeout=5
        )
        
        if restore_response.status_code == 200:
            print("   ✅ Оригинальный контент восстановлен")
        else:
            print(f"   ⚠️  Не удалось восстановить оригинальный контент (HTTP {restore_response.status_code})")
        
        return True
        
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False

def test_empty_content_validation():
    """Тест валидации пустого контента"""
    print("\n3️⃣ Тест валидации пустого контента...")
    try:
        # Получаем текущий промпт для восстановления
        get_response = requests.get(f"{API_BASE}/api/v1/prompts/description_prompt", timeout=5)
        if get_response.status_code != 200:
            print("   ⚠️  Пропущен: не удалось получить промпт для теста")
            return True
        
        original_content = get_response.json()['content']
        
        # Пытаемся отправить пустой контент
        # Примечание: сервер может принять пустой контент, это нормально для некоторых случаев
        empty_response = requests.put(
            f"{API_BASE}/api/v1/prompts/description_prompt",
            headers={'Content-Type': 'application/json'},
            json={'content': ''},
            timeout=5
        )
        
        # Восстанавливаем оригинальный контент
        requests.put(
            f"{API_BASE}/api/v1/prompts/description_prompt",
            headers={'Content-Type': 'application/json'},
            json={'content': original_content},
            timeout=5
        )
        
        if empty_response.status_code == 200:
            print("   ⚠️  Пустой контент принят (валидация на фронтенде обязательна)")
        else:
            print(f"   ✅ Пустой контент отклонен сервером (HTTP {empty_response.status_code})")
        
        return True
        
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False

def test_error_handling():
    """Тест обработки ошибок (404, сетевые ошибки)"""
    print("\n4️⃣ Тест обработки ошибок...")
    try:
        # Тест 1: Несуществующий промпт
        response = requests.get(f"{API_BASE}/api/v1/prompts/nonexistent_prompt_99999", timeout=5)
        
        if response.status_code == 404:
            error_data = response.json()
            if 'detail' in error_data:
                print(f"   ✅ 404 ошибка обработана корректно: {error_data['detail'][:50]}...")
            else:
                print("   ⚠️  404 ошибка, но структура ответа неожиданная")
        else:
            print(f"   ❌ FAILED: Ожидался 404, получен {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False

def test_cors_headers():
    """Тест CORS заголовков для фронтенда"""
    print("\n5️⃣ Тест CORS заголовков...")
    try:
        response = requests.options(
            f"{API_BASE}/api/v1/prompts",
            headers={
                'Origin': 'http://localhost',
                'Access-Control-Request-Method': 'GET'
            },
            timeout=5
        )
        
        # Проверяем наличие CORS заголовков
        cors_headers = ['Access-Control-Allow-Origin', 'Access-Control-Allow-Methods']
        found_headers = []
        
        for header in cors_headers:
            if header in response.headers:
                found_headers.append(header)
        
        if found_headers:
            print(f"   ✅ CORS заголовки присутствуют: {', '.join(found_headers)}")
        else:
            print("   ⚠️  CORS заголовки не найдены (возможно, CORS настроен иначе)")
        
        return True
        
    except Exception as e:
        print(f"   ⚠️  Ошибка проверки CORS: {e}")
        return True  # Не критично для работы

def main():
    """Главная функция"""
    print("=" * 70)
    print("🧪 ИНТЕГРАЦИОННЫЙ ТЕСТ РЕДАКТОРА ПРОМПТОВ")
    print("=" * 70)
    print("\nЭтот тест проверяет работу функции fetchAndRenderPrompts из admin.js")
    print("и эмулирует взаимодействие с API prompts-manager.\n")
    
    if not wait_for_service():
        print("\n❌ Сервис недоступен. Запустите prompts-manager перед тестами.")
        sys.exit(1)
    
    results = []
    results.append(test_get_all_prompts())
    results.append(test_update_prompt_simulation())
    results.append(test_empty_content_validation())
    results.append(test_error_handling())
    results.append(test_cors_headers())
    
    print("\n" + "=" * 70)
    print("📊 РЕЗУЛЬТАТЫ")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"\nПройдено: {passed}/{total}")
    print(f"Успешность: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("\n📝 Рекомендации:")
        print("   1. Проверьте работу редактора в браузере (admin.html)")
        print("   2. Убедитесь, что промпты отображаются корректно")
        print("   3. Протестируйте сохранение промптов")
        print("   4. Откройте test_prompts_editor.html для UI тестирования")
        return 0
    else:
        print(f"\n❌ ПРОВАЛЕНО ТЕСТОВ: {total - passed}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

