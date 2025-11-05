"""
Скрипт для сброса пароля пользователя или обновления хеша на новый формат.
Использует прямое хеширование bcrypt для совместимости.
"""
import sys
import os
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH для импорта модулей
# Корень проекта - на 4 уровня выше от scripts/utils/admin/reset_user_password.py
# (admin -> utils -> scripts -> корень)
# Используем resolve() для получения абсолютного пути
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from database.connection import SessionLocal
from database.models import User
from passlib.context import CryptContext

# Используем ту же конфигурацию, что и в auth сервисе
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash_direct(password: str) -> str:
    """Хеширует пароль используя passlib (bcrypt), как в auth сервисе."""
    try:
        return pwd_context.hash(password)
    except Exception as e:
        # Если passlib не работает, используем прямой bcrypt
        import bcrypt
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

def reset_user_password(email: str, new_password: str):
    """
    Обновляет пароль пользователя с новым хешем.
    Если пользователь не существует, создает его.
    """
    db = SessionLocal()
    
    try:
        # Ищем пользователя
        user = db.query(User).filter(User.email == email).first()
        
        if user:
            # Обновляем пароль
            new_hashed_password = get_password_hash_direct(new_password)
            user.hashed_password = new_hashed_password
            db.commit()
            print(f"Пароль для пользователя {email} успешно обновлен!")
        else:
            # Создаем нового пользователя
            new_hashed_password = get_password_hash_direct(new_password)
            new_user = User(
                email=email,
                hashed_password=new_hashed_password
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            print(f"Пользователь {email} успешно создан!")
        
        print(f"Email: {email}")
        print(f"Пароль: {new_password}")
        print(f"Хеш (первые 30 символов): {new_hashed_password[:30]}...")
        
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Использование:")
        print("  python reset_user_password.py <email> <new_password>")
        print("")
        print("Пример:")
        print("  python reset_user_password.py Uzer@gmail.com Uzer")
        print("")
        print("Для создания/обновления тестового пользователя:")
        print("  python reset_user_password.py test@example.com test123")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    reset_user_password(email, password)
