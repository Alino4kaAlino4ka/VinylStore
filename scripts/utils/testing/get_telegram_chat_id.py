#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для получения chat_id в Telegram
"""

import requests
import os
from dotenv import load_dotenv
from pathlib import Path

# Загружаем переменные окружения
# Корень проекта - на 3 уровня выше от scripts/utils/testing/
project_root = Path(__file__).parent.parent.parent
config_paths = [
    project_root / 'config.env',
    Path.cwd() / 'config.env',
]
for config_path in config_paths:
    if config_path.exists():
        load_dotenv(config_path, override=False)
        break

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    print("❌ TELEGRAM_BOT_TOKEN не найден в config.env")
    exit(1)

print("🔍 Получение информации о боте и последних обновлениях...\n")

try:
    # Получаем информацию о боте
    bot_info_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
    response = requests.get(bot_info_url)
    response.raise_for_status()
    bot_info = response.json()
    
    if bot_info.get("ok"):
        bot_data = bot_info.get("result", {})
        print(f"✅ Бот подключен: @{bot_data.get('username', 'N/A')}")
        print(f"   Имя: {bot_data.get('first_name', 'N/A')}\n")
    
    # Получаем последние обновления (сообщения, которые бот получил)
    updates_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    response = requests.get(updates_url)
    response.raise_for_status()
    updates = response.json()
    
    if updates.get("ok"):
        results = updates.get("result", [])
        
        if not results:
            print("⚠️  Бот еще не получил ни одного сообщения.")
            print("\n📝 Инструкция:")
            print("   1. Найдите вашего бота в Telegram (по username из BotFather)")
            print("   2. Отправьте боту любое сообщение (например, /start)")
            print("   3. Запустите этот скрипт снова\n")
            
            print("💡 Альтернативный способ:")
            print("   Напишите боту @userinfobot или @getidsbot для получения вашего chat_id")
            print("   Затем добавьте его в config.env как TELEGRAM_CHAT_ID\n")
        else:
            print("📬 Найденные чаты:\n")
            
            chat_ids = set()
            for update in results:
                message = update.get("message", {})
                chat = message.get("chat", {})
                chat_id = chat.get("id")
                chat_type = chat.get("type", "unknown")
                
                if chat_id:
                    chat_ids.add((chat_id, chat_type, chat.get("first_name", ""), chat.get("username", "")))
            
            if chat_ids:
                print("   Chat ID можно использовать:")
                for chat_id, chat_type, first_name, username in sorted(chat_ids):
                    user_info = f"{first_name} (@{username})" if username else first_name or "Неизвестный пользователь"
                    print(f"   - {chat_id} ({chat_type}) - {user_info}")
                
                # Берем первый найденный chat_id
                first_chat_id = sorted(chat_ids)[0][0]
                print(f"\n✅ Рекомендуемый chat_id: {first_chat_id}")
                print(f"\n   Добавьте в config.env:")
                print(f"   TELEGRAM_CHAT_ID={first_chat_id}")
            else:
                print("   Не удалось извлечь chat_id из обновлений")
    else:
        print(f"❌ Ошибка при получении обновлений: {updates.get('description', 'Unknown error')}")
        
except requests.exceptions.RequestException as e:
    print(f"❌ Ошибка при подключении к Telegram API: {e}")
    print("   Проверьте интернет-соединение и правильность токена")
except Exception as e:
    print(f"❌ Неожиданная ошибка: {e}")

