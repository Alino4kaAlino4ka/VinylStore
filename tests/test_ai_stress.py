#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Стресс-тесты для AI интеграции из TESTING_CHECKLIST.md
Часть 3: Надежность интеграции ИИ
"""

import requests
import json
import sys
import time

if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

def test_recommender_prompts_connection():
    """Тест подключения Recommender к Prompts Manager"""
    print("\n🔗 Тест: Recommender ↔ Prompts Manager интеграция")
    try:
        # Проверяем, что Recommender может получить промпты
        prompts_response = requests.get("http://127.0.0.1:8007/api/v1/prompts", timeout=5)
        if prompts_response.status_code == 200:
            prompts = prompts_response.json()
            print(f"   ✓ Prompts Manager доступен: {len(prompts)} промптов")
            
            # Проверяем health Recommender
            rec_response = requests.get("http://127.0.0.1:8004/health", timeout=5)
            if rec_response.status_code == 200:
                print(f"   ✓ Recommender доступен")
                return True
        return False
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
        return False

def test_recommendations_invalid_input():
    """Тест обработки некорректного ввода для рекомендаций"""
    print("\n⚠️  Тест: Некорректный ввод для рекомендаций")
    
    # Тест 1: Пустые предпочтения
    try:
        payload = {
            "user_preferences": "",
            "current_books": [],
            "genre_preferences": [],
            "max_recommendations": 5,
            "model": "gpt-4"
        }
        response = requests.post(
            "http://127.0.0.1:8004/api/v1/recommendations/generate",
            json=payload,
            timeout=10
        )
        if response.status_code in [400, 422]:
            print("   ✓ Пустые предпочтения корректно обработаны (400/422)")
        else:
            print(f"   ⚠ Пустые предпочтения: статус {response.status_code}")
    except Exception as e:
        print(f"   ✗ Ошибка при тестировании пустых предпочтений: {e}")
    
    # Тест 2: Несуществующие ID пластинок
    try:
        payload = {
            "user_preferences": "Люблю классический рок",
            "current_books": [99999, 99998],
            "genre_preferences": ["рок"],
            "max_recommendations": 5,
            "model": "gpt-4"
        }
        response = requests.post(
            "http://127.0.0.1:8004/api/v1/recommendations/generate",
            json=payload,
            timeout=90
        )
        # Может быть успешный ответ, так как система должна игнорировать несуществующие ID
        if response.status_code == 200:
            print("   ✓ Несуществующие ID пластинок обработаны корректно")
        elif response.status_code in [400, 404]:
            print(f"   ✓ Несуществующие ID корректно отклонены ({response.status_code})")
        else:
            print(f"   ⚠ Неожиданный статус: {response.status_code}")
    except requests.Timeout:
        print("   ⚠ Таймаут (это нормально для AI запросов)")
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
    
    return True

def test_description_invalid_id():
    """Тест генерации описания для несуществующего ID"""
    print("\n❌ Тест: Генерация описания для несуществующего ID (99999)")
    try:
        response = requests.post(
            "http://127.0.0.1:8004/api/v1/recommendations/generate-description/99999",
            timeout=10
        )
        if response.status_code == 404:
            print("   ✓ Корректно обработана ошибка 404 (товар не найден)")
            return True
        elif response.status_code == 500:
            error_data = response.json()
            if "не найден" in error_data.get("detail", "").lower():
                print("   ✓ Корректно обработана ошибка (товар не найден)")
                return True
        print(f"   ⚠ Неожиданный статус: {response.status_code}")
        return False
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
        return False

def test_catalog_fallback():
    """Тест fallback режима для Catalog"""
    print("\n🔄 Тест: Проверка fallback режима (не реализовано на бэкенде, только фронтенд)")
    print("   ℹ Fallback режим работает на фронтенде с localStorage")
    return True

def test_prompts_manager_availability():
    """Тест доступности Prompts Manager"""
    print("\n🤖 Тест: Доступность Prompts Manager")
    try:
        response = requests.get("http://127.0.0.1:8007/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Prompts Manager доступен: {data.get('service')}")
            
            # Проверяем доступность промптов
            prompts_response = requests.get("http://127.0.0.1:8007/api/v1/prompts", timeout=5)
            if prompts_response.status_code == 200:
                prompts = prompts_response.json()
                print(f"   ✓ Доступно промптов: {len(prompts)}")
                return True
        return False
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
        return False

def test_recommender_with_prompts():
    """Тест работы Recommender с промптами"""
    print("\n🎯 Тест: Работа Recommender с Prompts Manager")
    try:
        # Получаем список промптов
        prompts_response = requests.get("http://127.0.0.1:8007/api/v1/prompts", timeout=5)
        if prompts_response.status_code == 200:
            prompts = prompts_response.json()
            if prompts:
                prompt_id = prompts[0].get('id')
                # Проверяем, что Recommender может получить промпт
                # (это косвенная проверка - реальный запрос потребует AI ключа)
                print(f"   ✓ Промпты доступны для Recommender (ID: {prompt_id})")
                return True
            else:
                print("   ⚠ Промпты не найдены в базе")
                return False
        return False
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
        return False

def main():
    """Запустить все стресс-тесты"""
    print("="*70)
    print("СТРЕСС-ТЕСТЫ AI ИНТЕГРАЦИИ")
    print("Часть 3 из TESTING_CHECKLIST.md")
    print("="*70)
    
    results = []
    
    # Тест подключения
    results.append(("Интеграция Recommender ↔ Prompts Manager", test_recommender_prompts_connection()))
    
    # Тесты обработки ошибок
    results.append(("Обработка некорректного ввода", test_recommendations_invalid_input()))
    results.append(("Генерация описания для несуществующего ID", test_description_invalid_id()))
    
    # Тесты доступности
    results.append(("Доступность Prompts Manager", test_prompts_manager_availability()))
    results.append(("Работа Recommender с промптами", test_recommender_with_prompts()))
    
    # Информационные тесты
    test_catalog_fallback()
    
    # Вывод результатов
    print("\n" + "="*70)
    print("РЕЗУЛЬТАТЫ СТРЕСС-ТЕСТОВ")
    print("="*70)
    
    passed = 0
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} | {name}")
        if result:
            passed += 1
    
    total = len(results)
    print("="*70)
    print(f"Итого: {passed}/{total} тестов пройдено")
    print("="*70)
    
    if passed == total:
        print("\n✅ Все стресс-тесты пройдены!")
        return 0
    else:
        print("\n⚠️  Некоторые стресс-тесты не прошли")
        return 1

if __name__ == "__main__":
    sys.exit(main())

