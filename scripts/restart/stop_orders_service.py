#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для остановки сервиса orders
"""

import subprocess
import sys
import os

def stop_orders_on_port():
    """Останавливает процесс на порту 8002"""
    print("🛑 Остановка сервиса orders на порту 8002...")
    
    if sys.platform == "win32":
        try:
            # Находим PID процесса на порту 8002
            result = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True,
                text=True
            )
            
            lines = result.stdout.split('\n')
            for line in lines:
                if ':8002' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        print(f"   Найден процесс с PID: {pid}")
                        
                        # Останавливаем процесс
                        try:
                            subprocess.run(
                                ["taskkill", "/F", "/PID", pid],
                                capture_output=True,
                                text=True
                            )
                            print(f"✅ Процесс {pid} остановлен")
                            return True
                        except Exception as e:
                            print(f"❌ Ошибка при остановке процесса: {e}")
                            return False
            
            print("⚠️  Процесс на порту 8002 не найден (возможно, уже остановлен)")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False
    else:
        # Linux/Mac
        try:
            result = subprocess.run(
                ["lsof", "-ti:8002"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                pid = result.stdout.strip()
                subprocess.run(["kill", "-9", pid])
                print(f"✅ Процесс {pid} остановлен")
                return True
            else:
                print("⚠️  Процесс на порту 8002 не найден")
                return True
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False

if __name__ == "__main__":
    if stop_orders_on_port():
        print("\n✅ Готово! Теперь можно запустить сервис заново")
    else:
        print("\n❌ Не удалось остановить сервис")

