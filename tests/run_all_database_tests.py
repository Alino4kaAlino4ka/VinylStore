#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для запуска всех тестов базы данных MySQL
"""

import sys
import unittest
from pathlib import Path

# Добавляем корневую папку проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_all_tests():
    """Запуск всех тестов базы данных"""
    print("=" * 60)
    print("ЗАПУСК ВСЕХ ТЕСТОВ БАЗЫ ДАННЫХ MySQL")
    print("=" * 60)
    
    # Создаем тестовый набор
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Загружаем тесты подключения
    print("\n[1] Загрузка тестов подключения к MySQL...")
    try:
        import importlib.util
        tests_dir = Path(__file__).parent
        spec = importlib.util.spec_from_file_location("test_mysql_connection", tests_dir / "test_mysql_connection.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        connection_tests = loader.loadTestsFromModule(module)
        suite.addTests(connection_tests)
        print(f"   ✅ Загружено тестов подключения: {connection_tests.countTestCases()}")
    except Exception as e:
        print(f"   ❌ Ошибка загрузки тестов подключения: {e}")
        import traceback
        traceback.print_exc()
    
    # Загружаем тесты операций
    print("\n[2] Загрузка тестов операций с БД...")
    try:
        import importlib.util
        tests_dir = Path(__file__).parent
        spec = importlib.util.spec_from_file_location("test_database_operations", tests_dir / "test_database_operations.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        operations_tests = loader.loadTestsFromModule(module)
        suite.addTests(operations_tests)
        print(f"   ✅ Загружено тестов операций: {operations_tests.countTestCases()}")
    except Exception as e:
        print(f"   ❌ Ошибка загрузки тестов операций: {e}")
        import traceback
        traceback.print_exc()
    
    # Запускаем тесты
    print("\n" + "=" * 60)
    print("ЗАПУСК ТЕСТОВ")
    print("=" * 60)
    
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Выводим итоги
    print("\n" + "=" * 60)
    print("ИТОГИ ТЕСТИРОВАНИЯ")
    print("=" * 60)
    print(f"Всего тестов: {result.testsRun}")
    print(f"Успешно: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Провалено: {len(result.failures)}")
    print(f"Ошибок: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ ПРОВАЛЕННЫЕ ТЕСТЫ:")
        for test, traceback in result.failures:
            print(f"   - {test}")
    
    if result.errors:
        print("\n❌ ТЕСТЫ С ОШИБКАМИ:")
        for test, traceback in result.errors:
            print(f"   - {test}")
    
    if result.wasSuccessful():
        print("\n✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        return 0
    else:
        print("\n❌ НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)

