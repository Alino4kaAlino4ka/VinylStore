#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Автоматическая настройка MySQL (требуется доступ root)
"""

import sys
import getpass
import pymysql

def setup_mysql():
    """Автоматическая настройка MySQL"""
    print("=" * 60)
    print("Автоматическая настройка MySQL")
    print("=" * 60)
    
    # Запрашиваем пароль root
    root_password = getpass.getpass("Введите пароль root MySQL: ")
    
    try:
        # Подключаемся как root
        print("\n[1] Подключение к MySQL как root...")
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password=root_password,
            connect_timeout=5
        )
        print("✅ Подключение успешно")
        
        with connection.cursor() as cursor:
            # Создаем базу данных
            print("\n[2] Создание базы данных 'audio_store'...")
            try:
                cursor.execute("CREATE DATABASE IF NOT EXISTS audio_store CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                print("✅ База данных создана или уже существует")
            except Exception as e:
                print(f"⚠️  Ошибка при создании базы данных: {e}")
            
            # Создаем пользователя
            print("\n[3] Создание пользователя 'user'@'localhost'...")
            try:
                cursor.execute("CREATE USER IF NOT EXISTS 'user'@'localhost' IDENTIFIED BY '1234'")
                print("✅ Пользователь создан или уже существует")
            except Exception as e:
                print(f"⚠️  Ошибка при создании пользователя: {e}")
            
            # Выдаем права
            print("\n[4] Выдача прав пользователю...")
            try:
                cursor.execute("GRANT ALL PRIVILEGES ON audio_store.* TO 'user'@'localhost'")
                print("✅ Права выданы")
            except Exception as e:
                print(f"⚠️  Ошибка при выдаче прав: {e}")
            
            # Обновляем привилегии
            print("\n[5] Обновление привилегий...")
            try:
                cursor.execute("FLUSH PRIVILEGES")
                print("✅ Привилегии обновлены")
            except Exception as e:
                print(f"⚠️  Ошибка при обновлении привилегий: {e}")
        
        connection.close()
        
        # Проверяем подключение с новыми учетными данными
        print("\n[6] Проверка подключения с новыми учетными данными...")
        try:
            test_connection = pymysql.connect(
                host='localhost',
                user='user',
                password='1234',
                database='audio_store',
                connect_timeout=5
            )
            print("✅ Подключение с учетными данными из config.env работает!")
            test_connection.close()
            
            print("\n" + "=" * 60)
            print("✅ MySQL настроен успешно!")
            print("   Теперь можно запустить: python init_db.py")
            return True
        except Exception as e:
            print(f"❌ Не удалось подключиться с новыми учетными данными: {e}")
            return False
            
    except pymysql.err.OperationalError as e:
        if e.args[0] == 1045:
            print(f"❌ Неверный пароль root или доступ запрещен: {e}")
        else:
            print(f"❌ Ошибка подключения: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = setup_mysql()
    sys.exit(0 if success else 1)

