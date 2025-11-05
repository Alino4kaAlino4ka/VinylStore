#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для создания заказа и проверки отправки в Telegram
"""

import requests
import json
import time

print("🧪 Тестирование создания заказа с отправкой в Telegram...\n")

# Данные тестового заказа
order_data = {
    "product_ids": ["1", "2"],
    "quantities": {
        "1": 2,
        "2": 1
    }
}

print("📦 Создание тестового заказа...")
print(f"   Товары: {order_data['product_ids']}")
print(f"   Количество: {order_data['quantities']}\n")

try:
    response = requests.post(
        "http://127.0.0.1:8002/api/v1/orders",
        json=order_data,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    if response.status_code == 200:
        order_result = response.json()
        print("✅ Заказ создан успешно!")
        print(f"   Номер заказа: {order_result.get('order_id')}")
        print(f"   Всего товаров: {order_result.get('total_items')}")
        print("\n📱 Проверьте Telegram у @Alino4kaGribavova")
        print("   Должно прийти сообщение с деталями заказа")
    else:
        print(f"❌ Ошибка при создании заказа: {response.status_code}")
        print(f"   Ответ: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ Не удалось подключиться к сервису orders")
    print("   Убедитесь, что сервис запущен на порту 8002")
except Exception as e:
    print(f"❌ Ошибка: {e}")

