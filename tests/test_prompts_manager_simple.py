#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой тест для prompts-manager
Можно запустить напрямую для проверки работы сервиса
"""

import sys
import os

# Настройка кодировки для Windows
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

import requests
import time

BASE_URL = "http://127.0.0.1:8007"

def wait_for_service(max_retries=30, delay=1):
    """Ожидание доступности сервиса"""
    print(f"⏳ Ожидание доступности сервиса prompts-manager на {BASE_URL}...")
    for i in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print(f"✅ Сервис доступен!")
                return True
        except requests.exceptions.RequestException:
            pass
        if i % 5 == 0 and i > 0:
            print(f"   ...попытка {i}/{max_retries}")
        time.sleep(delay)
    
    print(f"❌ Сервис недоступен после {max_retries} попыток")
    print(f"   Убедитесь, что сервис запущен: python -m uvicorn services.prompts-manager.main:app --port 8007")
    return False

def test_health():
    """Тест health check"""
    print("\n1️⃣ Тест health check...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "prompts-manager"
        print("   ✅ PASSED")
        return True
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False

def test_get_all_prompts():
    """Тест получения всех промптов"""
    print("\n2️⃣ Тест получения всех промптов...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/prompts", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"   ✅ PASSED (найдено промптов: {len(data)})")
        
        # Проверяем наличие дефолтных промптов
        names = [p["name"] for p in data]
        if "recommendation_prompt" in names:
            print("   ✅ Найден recommendation_prompt")
        else:
            print("   ⚠️  recommendation_prompt не найден")
            
        if "description_prompt" in names:
            print("   ✅ Найден description_prompt")
        else:
            print("   ⚠️  description_prompt не найден")
            
        return True
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False

def test_get_prompt():
    """Тест получения конкретного промпта"""
    print("\n3️⃣ Тест получения промпта recommendation_prompt...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/prompts/recommendation_prompt", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "recommendation_prompt"
        assert "content" in data
        assert len(data["content"]) > 0
        print(f"   ✅ PASSED (контент: {len(data['content'])} символов)")
        return True
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False

def test_update_prompt():
    """Тест обновления промпта"""
    print("\n4️⃣ Тест обновления промпта...")
    try:
        # Получаем оригинальный контент
        response = requests.get(f"{BASE_URL}/api/v1/prompts/recommendation_prompt", timeout=5)
        original_content = response.json()["content"]
        
        # Обновляем
        new_content = "Тестовый промпт для проверки обновления"
        update_response = requests.put(
            f"{BASE_URL}/api/v1/prompts/recommendation_prompt",
            json={"content": new_content},
            timeout=5
        )
        assert update_response.status_code == 200
        assert update_response.json()["content"] == new_content
        
        # Восстанавливаем оригинальный
        restore_response = requests.put(
            f"{BASE_URL}/api/v1/prompts/recommendation_prompt",
            json={"content": original_content},
            timeout=5
        )
        assert restore_response.status_code == 200
        print("   ✅ PASSED")
        return True
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False

def test_get_nonexistent():
    """Тест получения несуществующего промпта"""
    print("\n5️⃣ Тест получения несуществующего промпта...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/prompts/nonexistent_prompt", timeout=5)
        assert response.status_code == 404
        print("   ✅ PASSED")
        return True
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False

def main():
    """Главная функция"""
    print("=" * 60)
    print("🧪 ТЕСТИРОВАНИЕ ПРОМПТS-MANAGER")
    print("=" * 60)
    
    if not wait_for_service():
        sys.exit(1)
    
    results = []
    results.append(test_health())
    results.append(test_get_all_prompts())
    results.append(test_get_prompt())
    results.append(test_update_prompt())
    results.append(test_get_nonexistent())
    
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Пройдено: {passed}/{total}")
    print(f"Успешность: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        return 0
    else:
        print(f"\n❌ ПРОВАЛЕНО ТЕСТОВ: {total - passed}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

