#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки отправки сообщений в Telegram
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
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TELEGRAM_BOT_TOKEN:
    print("❌ TELEGRAM_BOT_TOKEN не найден в config.env")
    exit(1)

if not TELEGRAM_CHAT_ID:
    print("❌ TELEGRAM_CHAT_ID не найден в config.env")
    exit(1)

print("🧪 Отправка тестового сообщения в Telegram...")
print(f"   Chat ID: {TELEGRAM_CHAT_ID}")
print(f"   Получатель: @Alino4kaGribavova\n")

try:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": "✅ Тестовое сообщение!\n\nTelegram-уведомления о заказах настроены и работают!\n\nТеперь при каждом оформлении заказа вы будете получать уведомление с полной информацией о заказе и товарах."
    }
    
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
    
    result = response.json()
    if result.get("ok"):
        print("✅ Тестовое сообщение успешно отправлено!")
        print("   Проверьте Telegram у пользователя @Alino4kaGribavova")
    else:
        print(f"❌ Ошибка: {result.get('description', 'Unknown error')}")
        
except requests.exceptions.RequestException as e:
    print(f"❌ Ошибка при отправке: {e}")
except Exception as e:
    print(f"❌ Неожиданная ошибка: {e}")

