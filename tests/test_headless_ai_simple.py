#!/usr/bin/env python3
"""
Простой тест Headless AI - проверка получения промпта
Запускается только если prompts-manager доступен
"""

import requests
import json

def test_prompt_retrieval():
    """Простая проверка получения промпта"""
    print("🧪 Тест Headless AI: Получение промпта из prompts-manager")
    print("=" * 60)
    
    # Проверка доступности prompts-manager
    try:
        health_response = requests.get("http://localhost:8007/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ prompts-manager недоступен")
            return False
        print("✅ prompts-manager доступен")
    except:
        print("❌ prompts-manager не запущен на порту 8007")
        print("💡 Запустите prompts-manager:")
        print("   python start_services_final.py")
        print("   или")
        print("   start_prompts_manager.bat")
        return False
    
    # Тест получения recommendation_prompt
    print("\n📋 Тест 1: Получение recommendation_prompt")
    try:
        response = requests.get("http://localhost:8007/api/v1/prompts/recommendation_prompt", timeout=10)
        if response.status_code == 200:
            data = response.json()
            content = data.get("content", "")
            print(f"✅ Промпт получен (длина: {len(content)} символов)")
            print(f"📄 Первые 150 символов:")
            print(f"   {content[:150]}...")
            return True
        else:
            print(f"❌ Ошибка: статус {response.status_code}")
            print(f"   {response.text}")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    
    # Тест получения description_prompt
    print("\n📋 Тест 2: Получение description_prompt")
    try:
        response = requests.get("http://localhost:8007/api/v1/prompts/description_prompt", timeout=10)
        if response.status_code == 200:
            data = response.json()
            content = data.get("content", "")
            print(f"✅ Промпт получен (длина: {len(content)} символов)")
            print(f"📄 Первые 150 символов:")
            print(f"   {content[:150]}...")
            return True
        else:
            print(f"❌ Ошибка: статус {response.status_code}")
            print(f"   {response.text}")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    success = test_prompt_retrieval()
    if success:
        print("\n✅ Все тесты пройдены!")
        print("💡 Теперь можно протестировать полную интеграцию с recommender")
    else:
        print("\n❌ Тесты не пройдены")
        exit(1)

