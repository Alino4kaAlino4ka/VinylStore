#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Запуск всех тестов системы промптов
"""

import subprocess
import sys
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def run_test(test_file, test_name):
    """Запуск отдельного теста"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"🧪 {test_name}")
    print(f"{'='*60}{Colors.END}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            cwd=Path(__file__).parent,
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"{Colors.RED}❌ Ошибка запуска теста: {e}{Colors.END}")
        return False

def main():
    """Запуск всех тестов"""
    print(f"\n{Colors.BLUE}{'='*70}")
    print("[RUN] ПОЛНОЕ ТЕСТИРОВАНИЕ СИСТЕМЫ ПРОМПТОВ")
    print(f"{'='*70}{Colors.END}\n")
    
    # Теперь скрипт находится в tests/, поэтому пути относительные от tests/
    tests = [
        ("test_prompts_manager_full.py", "Тестирование Prompts Manager API"),
        ("test_recommender_prompts_integration.py", "Тестирование интеграции Recommender ↔ Prompts Manager"),
        ("test_admin_prompts_frontend.py", "Тестирование фронтенд функционала"),
        ("test_chat_api.py", "Тестирование AI-виртуального консультанта (API)"),
    ]
    
    results = []
    for test_file, test_name in tests:
        test_path = Path(__file__).parent / test_file
        if test_path.exists():
            success = run_test(test_path, test_name)
            results.append((test_name, success))
        else:
            print(f"{Colors.YELLOW}[SKIP] Файл {test_file} не найден, пропуск{Colors.END}")
            results.append((test_name, None))
    
    # Итоговая статистика
    print(f"\n{Colors.BLUE}{'='*70}")
    print("📊 ИТОГОВАЯ СТАТИСТИКА")
    print(f"{'='*70}{Colors.END}\n")
    
    passed = sum(1 for _, result in results if result is True)
    failed = sum(1 for _, result in results if result is False)
    skipped = sum(1 for _, result in results if result is None)
    total = len(results)
    
    for test_name, result in results:
        if result is True:
            status = f"{Colors.GREEN}[PASSED]{Colors.END}"
        elif result is False:
            status = f"{Colors.RED}[FAILED]{Colors.END}"
        else:
            status = f"{Colors.YELLOW}[SKIPPED]{Colors.END}"
        
        print(f"{test_name:.<50} {status}")
    
    print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"[OK] Пройдено: {passed}")
    print(f"[FAIL] Провалено: {failed}")
    if skipped > 0:
        print(f"[SKIP] Пропущено: {skipped}")
    print(f"[TOTAL] Всего: {total}")
    print(f"{Colors.BLUE}{'='*70}{Colors.END}\n")
    
    if failed == 0 and skipped == 0:
        print(f"{Colors.GREEN}[SUCCESS] ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!{Colors.END}\n")
        return 0
    elif failed > 0:
        print(f"{Colors.RED}[WARNING] НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ{Colors.END}\n")
        return 1
    else:
        print(f"{Colors.YELLOW}[WARNING] НЕКОТОРЫЕ ТЕСТЫ ПРОПУЩЕНЫ{Colors.END}\n")
        return 0

if __name__ == "__main__":
    sys.exit(main())

