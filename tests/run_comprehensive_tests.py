#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Запуск комплексного тестирования Vinyl Shop
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Запуск комплексных тестов"""
    print("\n" + "="*70)
    print("🚀 ЗАПУСК КОМПЛЕКСНОГО ТЕСТИРОВАНИЯ")
    print("="*70 + "\n")
    
    # Теперь скрипт находится в tests/, поэтому ищем test_comprehensive.py в той же директории
    test_file = Path(__file__).parent / "test_comprehensive.py"
    
    if not test_file.exists():
        print(f"❌ Файл {test_file} не найден!")
        return 1
    
    result = subprocess.run(
        [sys.executable, str(test_file)],
        cwd=Path(__file__).parent  # tests/ директория
    )
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())

