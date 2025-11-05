import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH для импорта модулей
# Корень проекта - на 4 уровня выше от scripts/utils/admin/add_test_user.py
# (admin -> utils -> scripts -> корень)
# Используем resolve() для получения абсолютного пути
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from database.connection import SessionLocal
from database.models import User
from services.catalog.security import get_password_hash

def add_test_user():
    """
    Добавляет тестового пользователя Uzer@gmail.com с паролем Uzer.
    """
    db = SessionLocal()
    
    try:
        # Проверяем, существует ли уже пользователь Uzer@gmail.com
        existing_user = db.query(User).filter(User.email == "Uzer@gmail.com").first()
        if existing_user:
            print("Пользователь Uzer@gmail.com уже существует в базе данных.")
            return
        
        # Создаем нового пользователя
        hashed_password = get_password_hash("Uzer")
        new_user = User(
            email="Uzer@gmail.com",
            hashed_password=hashed_password
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print("Пользователь Uzer@gmail.com успешно добавлен в базу данных!")
        print(f"Email: Uzer@gmail.com")
        print(f"Пароль: Uzer")
        
    except Exception as e:
        print(f"Произошла ошибка при добавлении пользователя: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_test_user()
