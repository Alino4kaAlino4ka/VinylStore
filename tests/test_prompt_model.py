"""
Тестовый скрипт для проверки модели Prompt и сервиса prompts-manager.
"""
import sys
import os
from pathlib import Path

# Добавляем корневую папку проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database import models, connection
from sqlalchemy.orm import Session

def test_prompt_model():
    """Тестирует создание модели Prompt"""
    print("=" * 60)
    print("ТЕСТ 1: Проверка модели Prompt")
    print("=" * 60)
    
    try:
        # Инициализируем базу данных
        connection.init_db()
        print("✓ База данных инициализирована")
        
        # Создаем тестовую сессию
        db: Session = connection.SessionLocal()
        
        try:
            # Проверяем, что таблица создана
            from sqlalchemy import inspect
            inspector = inspect(connection.engine)
            tables = inspector.get_table_names()
            
            if 'prompts' in tables:
                print("✓ Таблица 'prompts' существует")
            else:
                print("✗ Таблица 'prompts' не найдена!")
                return False
            
            # Проверяем структуру таблицы
            columns = inspector.get_columns('prompts')
            column_names = [col['name'] for col in columns]
            
            required_columns = ['id', 'name', 'template']
            for col in required_columns:
                if col in column_names:
                    print(f"✓ Колонка '{col}' существует")
                else:
                    print(f"✗ Колонка '{col}' не найдена!")
                    return False
            
            # Проверяем тип данных id
            id_column = next((col for col in columns if col['name'] == 'id'), None)
            if id_column:
                id_type = str(id_column['type'])
                if 'VARCHAR' in id_type or 'STRING' in id_type or 'TEXT' in id_type:
                    print(f"✓ Поле 'id' имеет строковый тип: {id_type}")
                else:
                    print(f"⚠ Поле 'id' имеет тип: {id_type} (ожидается строковый)")
            
            # Тест 1: Создание промпта с строковым id
            print("\n--- Тест создания промпта ---")
            test_prompt = models.Prompt(
                id="test_prompt_001",
                name="Тестовый промпт",
                template="Это тестовый шаблон промпта для проверки модели."
            )
            db.add(test_prompt)
            db.commit()
            print("✓ Промпт успешно создан с id='test_prompt_001'")
            
            # Тест 2: Получение промпта по id
            retrieved = db.query(models.Prompt).filter(models.Prompt.id == "test_prompt_001").first()
            if retrieved:
                print(f"✓ Промпт успешно получен: id={retrieved.id}, name={retrieved.name}")
                print(f"  template (первые 50 символов): {retrieved.template[:50]}...")
            else:
                print("✗ Не удалось получить созданный промпт!")
                return False
            
            # Тест 3: Получение промпта по name
            retrieved_by_name = db.query(models.Prompt).filter(models.Prompt.name == "Тестовый промпт").first()
            if retrieved_by_name and retrieved_by_name.id == "test_prompt_001":
                print("✓ Промпт успешно найден по name")
            else:
                print("✗ Не удалось найти промпт по name!")
                return False
            
            # Тест 4: Обновление template
            retrieved.template = "Обновленный шаблон промпта"
            db.commit()
            updated = db.query(models.Prompt).filter(models.Prompt.id == "test_prompt_001").first()
            if updated.template == "Обновленный шаблон промпта":
                print("✓ Шаблон промпта успешно обновлен")
            else:
                print("✗ Не удалось обновить шаблон!")
                return False
            
            # Удаляем тестовый промпт
            db.delete(retrieved)
            db.commit()
            print("✓ Тестовый промпт удален")
            
            return True
            
        except Exception as e:
            print(f"✗ Ошибка при тестировании модели: {e}")
            import traceback
            traceback.print_exc()
            db.rollback()
            return False
        finally:
            db.close()
            
    except Exception as e:
        print(f"✗ Ошибка инициализации: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_default_prompts():
    """Тестирует создание дефолтных промптов"""
    print("\n" + "=" * 60)
    print("ТЕСТ 2: Проверка дефолтных промптов")
    print("=" * 60)
    
    try:
        db: Session = connection.SessionLocal()
        
        try:
            # Проверяем наличие дефолтных промптов (они должны создаваться при старте сервиса)
            recommendation_prompt = db.query(models.Prompt).filter(
                models.Prompt.name == "recommendation_prompt"
            ).first()
            
            description_prompt = db.query(models.Prompt).filter(
                models.Prompt.name == "description_prompt"
            ).first()
            
            if recommendation_prompt:
                print(f"✓ Промпт 'recommendation_prompt' найден (id={recommendation_prompt.id})")
                print(f"  Длина шаблона: {len(recommendation_prompt.template)} символов")
            else:
                print("⚠ Промпт 'recommendation_prompt' не найден (будет создан при старте сервиса)")
            
            if description_prompt:
                print(f"✓ Промпт 'description_prompt' найден (id={description_prompt.id})")
                print(f"  Длина шаблона: {len(description_prompt.template)} символов")
            else:
                print("⚠ Промпт 'description_prompt' не найден (будет создан при старте сервиса)")
            
            return True
            
        except Exception as e:
            print(f"✗ Ошибка: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            db.close()
            
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n🚀 Запуск тестов модели Prompt\n")
    
    result1 = test_prompt_model()
    result2 = test_default_prompts()
    
    print("\n" + "=" * 60)
    if result1 and result2:
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
    print("=" * 60)

