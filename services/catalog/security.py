from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
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

# ====================================================================
# Конфигурация безопасности
# ====================================================================

SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-that-is-long-and-random-CHANGE-IN-PRODUCTION")
if SECRET_KEY == "your-super-secret-key-that-is-long-and-random-CHANGE-IN-PRODUCTION":
    print("WARNING: Используется дефолтный SECRET_KEY! Это небезопасно для production!")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Используем bcrypt для хеширования паролей (более безопасно, чем SHA-256)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Хеширует пароль используя bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет пароль."""
    return pwd_context.verify(plain_password, hashed_password)

# ====================================================================
# Функции для работы с JWT-токенами
# ====================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
