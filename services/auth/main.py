from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.responses import Response, JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import sys
import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
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

# Добавляем корневую папку проекта в путь
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from database import models, connection
except ImportError:
    print("Ошибка импорта database модулей")
    sys.exit(1)

# --- Конфигурация безопасности ---
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-that-is-long-and-random-CHANGE-IN-PRODUCTION")
if SECRET_KEY == "your-super-secret-key-that-is-long-and-random-CHANGE-IN-PRODUCTION":
    print("WARNING: Используется дефолтный SECRET_KEY! Это небезопасно для production!")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Используем bcrypt напрямую для хеширования паролей
# Используем прямой bcrypt вместо passlib из-за проблем совместимости
import bcrypt

def get_password_hash(password: str) -> str:
    """Хеширует пароль используя bcrypt напрямую."""
    # Bcrypt имеет ограничение: пароль не может быть длиннее 72 байт
    # Если пароль длиннее, обрезаем его (это стандартное поведение)
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # Генерируем соль и хешируем пароль
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет пароль используя bcrypt напрямую."""
    if not hashed_password:
        print("Пустой хеш пароля")
        return False
    
    try:
        # Bcrypt имеет ограничение: пароль не может быть длиннее 72 байт
        # Обрезаем пароль до 72 байт для проверки (как при хешировании)
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        
        # Проверяем пароль используя bcrypt напрямую
        # Это работает с любыми валидными bcrypt хешами (включая созданные через passlib)
        return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))
    except ValueError as e:
        # ValueError может возникнуть если хеш невалиден
        print(f"Ошибка проверки пароля: невалидный формат хеша - {e}")
        return False
    except TypeError as e:
        # TypeError может возникнуть при неправильном типе данных
        print(f"Ошибка типа при проверке пароля: {e}")
        return False
    except Exception as e:
        # Другие неожиданные ошибки
        print(f"Неожиданная ошибка при проверке пароля: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- Приложение FastAPI ---
app = FastAPI(
    title="Authentication API",
    description="Микросервис для аутентификации пользователей.",
    version="1.0.0"
)

# Настройка CORS
# Для production укажите конкретные домены через переменной окружения ALLOWED_ORIGINS
environment = os.getenv("ENVIRONMENT", "development")
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")

if environment == "production":
    if allowed_origins_env == "*":
        print("WARNING: CORS настроен на allow_origins=['*'] в production! Это небезопасно!")
        allowed_origins = ["*"]
        allow_creds = False
    else:
        allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",")]
        allow_creds = True
else:
    # В development разрешаем все origins (включая null для локальных HTML файлов)
    allowed_origins = ["*"]
    allow_creds = False  # False для совместимости с allow_origins=["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allow_creds,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Добавляем middleware для гарантированного добавления CORS заголовков
# Важно: этот middleware выполняется ПОСЛЕ CORS middleware, но ПЕРЕД обработчиками исключений
@app.middleware("http")
async def add_cors_header(request: Request, call_next):
    """Добавляет CORS заголовки ко всем ответам"""
    # Обработка preflight OPTIONS запроса
    if request.method == "OPTIONS":
        return Response(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Max-Age": "3600",
            }
        )
    
    try:
        response = await call_next(request)
        # Добавляем CORS заголовки ко всем ответам
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
    except HTTPException as exc:
        # Если возникло HTTPException, обрабатываем его с CORS заголовками
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )
    except Exception as exc:
        # Для всех остальных исключений
        import traceback
        print(f"Необработанное исключение: {exc}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"detail": f"Внутренняя ошибка сервера: {str(exc)}"},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )

# Инициализация базы данных при запуске
@app.on_event("startup")
async def startup_event():
    """Инициализация базы данных при запуске приложения."""
    try:
        connection.init_db()
        print("База данных инициализирована успешно")
    except Exception as e:
        print(f"Ошибка инициализации базы данных: {e}")

# --- Pydantic модели ---
class UserCreate(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    email: str
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# --- Вспомогательные функции ---
def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Получает пользователя по email."""
    return db.query(models.User).filter(models.User.email == email).first()

def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    """Аутентифицирует пользователя по email и паролю."""
    try:
        user = get_user_by_email(db, email)
        if not user:
            return None
        
        # Проверяем пароль с обработкой ошибок
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    except Exception as e:
        print(f"Ошибка при аутентификации пользователя: {e}")
        import traceback
        traceback.print_exc()
        return None

# --- Зависимости ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(connection.get_db)) -> models.User:
    """
    Получает текущего пользователя из JWT токена.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user_by_email(db, email)
    if user is None:
        raise credentials_exception
    
    return user

# --- API эндпоинты ---

@app.get("/health", tags=["Health Check"])
def health_check():
    return {"status": "ok", "message": "Auth service is running"}

@app.options("/register")
def register_options():
    """Обработчик для CORS preflight запросов на /register"""
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Max-Age": "3600",
        }
    )

@app.options("/token")
def token_options():
    """Обработчик для CORS preflight запросов на /token"""
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Max-Age": "3600",
        }
    )

@app.post("/register", response_model=UserResponse, status_code=201, tags=["Authentication"])
def register_user(user: UserCreate, db: Session = Depends(connection.get_db)):
    """
    Регистрирует нового пользователя.
    """
    try:
        # Проверяем, существует ли уже пользователь с таким email
        db_user = get_user_by_email(db, user.email)
        if db_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        
        # Создаем нового пользователя
        hashed_password = get_password_hash(user.password)
        db_user = models.User(
            email=user.email,
            hashed_password=hashed_password
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    except HTTPException:
        raise
    except Exception as e:
        print(f"Ошибка при регистрации пользователя: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/token", response_model=Token, tags=["Authentication"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(connection.get_db)):
    """
    Выдает JWT токен для аутентифицированного пользователя.
    """
    try:
        user = authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Ошибка при аутентификации: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/users/me", response_model=UserResponse, tags=["Users"])
def read_users_me(current_user: models.User = Depends(get_current_user)):
    """
    Получает информацию о текущем пользователе.
    """
    return current_user

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)