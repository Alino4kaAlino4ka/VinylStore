"""
Конфигурация для администраторов
"""

import secrets
import hashlib
import os
from dotenv import load_dotenv
from pathlib import Path

# Загружаем переменные окружения
config_paths = [
    Path(__file__).parent.parent.parent / 'config.env',
    Path(__file__).parent.parent / 'config.env',
    Path.cwd() / 'config.env',
]
for config_path in config_paths:
    if config_path.exists():
        load_dotenv(config_path, override=False)
        break

# Учетные данные администратора из переменных окружения
# ВАЖНО: Для production НЕ используйте дефолтные значения!
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# Предупреждение при использовании дефолтных значений
if ADMIN_USERNAME == "admin" and ADMIN_PASSWORD == "admin123":
    print("WARNING: Используются дефолтные учетные данные администратора!")
    print("WARNING: Это небезопасно для production! Установите ADMIN_USERNAME и ADMIN_PASSWORD в config.env")

ADMIN_CREDENTIALS = {
    "username": ADMIN_USERNAME,
    "password": ADMIN_PASSWORD
}

def verify_admin_credentials(username, password):
    """
    Проверяет учетные данные администратора
    
    Args:
        username (str): Имя пользователя
        password (str): Пароль
        
    Returns:
        bool: True если учетные данные верны, False в противном случае
    """
    return (username == ADMIN_CREDENTIALS["username"] and 
            password == ADMIN_CREDENTIALS["password"])

def generate_admin_token():
    """
    Генерирует простой токен для администратора
    
    Returns:
        str: Сгенерированный токен
    """
    # Создаем токен на основе секретного ключа и случайных данных
    # ВАЖНО: Используйте SECRET_KEY из переменных окружения для production!
    secret_key = os.getenv("SECRET_KEY", "admin_secret_key_2024")
    if secret_key == "admin_secret_key_2024":
        print("WARNING: Используется дефолтный secret_key для админ токенов!")
    random_data = secrets.token_hex(16)
    
    # Создаем хеш токена
    token_data = f"{secret_key}_{random_data}"
    token = hashlib.sha256(token_data.encode()).hexdigest()
    
    return token

def verify_admin_token(token):
    """
    Проверяет валидность токена администратора
    
    Args:
        token (str): Токен для проверки
        
    Returns:
        bool: True если токен валиден, False в противном случае
    """
    if not token:
        return False
    
    # Простая проверка длины и формата токена
    # В реальном приложении здесь была бы более сложная логика
    return len(token) == 64 and token.isalnum()
