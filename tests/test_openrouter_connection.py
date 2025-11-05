#!/usr/bin/env python3
"""
Тест подключения к OpenRouter API
"""
import os
import sys
from pathlib import Path
from openai import OpenAI

def load_config():
    """Загружает конфигурацию из файла config.env"""
    config = {}
    config_path = Path(__file__).parent.parent / 'config.env'
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key] = value
    except FileNotFoundError:
        print("❌ Файл config.env не найден!")
        return None
    return config

def test_openrouter_connection():
    """Тестирует подключение к OpenRouter API"""
    print("🔑 Тестирование подключения к OpenRouter API...")
    
    # Загружаем конфигурацию
    config = load_config()
    if not config:
        return False
    
    api_key = config.get('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ OPENROUTER_API_KEY не найден в конфигурации!")
        return False
    
    print(f"✅ API ключ загружен: {api_key[:20]}...")
    
    try:
        # Создаем клиент OpenAI
        client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        print("🤖 Отправляем тестовый запрос к OpenRouter...")
        
        # Отправляем простой тестовый запрос
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты - помощник для тестирования API. Отвечай кратко."},
                {"role": "user", "content": "Привет! Это тест подключения. Ответь 'Подключение успешно!'"}
            ],
            max_tokens=50,
            temperature=0.1
        )
        
        # Получаем ответ
        reply = response.choices[0].message.content
        print(f"✅ Ответ от OpenRouter: {reply}")
        
        # Проверяем, что ответ содержит ожидаемый текст
        if "подключение" in reply.lower() or "успешно" in reply.lower():
            print("🎉 Подключение к OpenRouter API работает корректно!")
            return True
        else:
            print("⚠️ Получен ответ, но он неожиданный")
            return True  # API работает, просто ответ неожиданный
            
    except Exception as e:
        print(f"❌ Ошибка при подключении к OpenRouter: {str(e)}")
        return False

def test_recommender_service():
    """Тестирует работу сервиса рекомендаций"""
    print("\n🔧 Тестирование сервиса рекомендаций...")
    
    try:
        import httpx
        
        # Проверяем, что сервис запущен
        response = httpx.get("http://localhost:8005/health", timeout=5)
        if response.status_code == 200:
            print("✅ Сервис рекомендаций запущен и отвечает")
            health_data = response.json()
            print(f"   Статус: {health_data.get('status')}")
            print(f"   Версия: {health_data.get('version')}")
            print(f"   AI модель: {health_data.get('ai_model')}")
            return True
        else:
            print(f"❌ Сервис рекомендаций отвечает с кодом {response.status_code}")
            return False
            
    except httpx.ConnectError:
        print("❌ Сервис рекомендаций не запущен на порту 8005")
        print("   Запустите: start_recommender.bat")
        return False
    except Exception as e:
        print(f"❌ Ошибка при тестировании сервиса: {str(e)}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов подключения к OpenRouter API\n")
    
    # Тест 1: Подключение к OpenRouter
    openrouter_ok = test_openrouter_connection()
    
    # Тест 2: Сервис рекомендаций
    service_ok = test_recommender_service()
    
    print("\n" + "="*50)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"   OpenRouter API: {'✅ РАБОТАЕТ' if openrouter_ok else '❌ НЕ РАБОТАЕТ'}")
    print(f"   Сервис рекомендаций: {'✅ РАБОТАЕТ' if service_ok else '❌ НЕ РАБОТАЕТ'}")
    
    if openrouter_ok and service_ok:
        print("\n🎉 Все тесты пройдены успешно!")
        print("   Сервис рекомендаций готов к работе!")
        return 0
    else:
        print("\n⚠️ Некоторые тесты не пройдены")
        print("   Проверьте настройки и попробуйте снова")
        return 1

if __name__ == "__main__":
    sys.exit(main())
