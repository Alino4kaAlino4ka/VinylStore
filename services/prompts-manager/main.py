from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import datetime
import sys
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

# Добавляем корневую папку проекта в путь
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from database import models, connection
except ImportError:
    print("Ошибка импорта database модулей")
    sys.exit(1)

# --- Приложение FastAPI ---
app = FastAPI(
    title="Prompts Manager API",
    description="Микросервис для управления AI-промптами с централизованным хранением и версионированием.",
    version="1.0.0"
)

# Настройка CORS - должно быть ДО всех обработчиков
# Важно: CORS middleware должен быть добавлен первым
# Для production укажите конкретные домены через переменную окружения ALLOWED_ORIGINS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
allowed_origins = [origin.strip() for origin in allowed_origins]
if "*" in allowed_origins and os.getenv("ENVIRONMENT", "development") == "production":
    print("WARNING: CORS настроен на allow_origins=['*'] в production! Это небезопасно!")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
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
        from fastapi.responses import Response
        return Response(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Max-Age": "3600",
            }
        )
    
    try:
        response = await call_next(request)
        # Добавляем CORS заголовки ко всем ответам
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response
    except HTTPException as exc:
        # Если возникло HTTPException, обрабатываем его с CORS заголовками
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
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
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                "Access-Control-Allow-Headers": "*",
            }
        )

# Добавляем обработчик исключений для корректной работы CORS при ошибках
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Обработчик HTTPException с CORS заголовками"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc):
    """Глобальный обработчик исключений с CORS заголовками"""
    import traceback
    print(f"Необработанное исключение: {exc}")
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": f"Внутренняя ошибка сервера: {str(exc)}"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "*",
        }
    )

# --- Pydantic модели ---
class PromptBase(BaseModel):
    name: str
    template: str

class PromptCreate(PromptBase):
    pass

class PromptUpdate(BaseModel):
    template: str


class PromptResponse(BaseModel):
    id: str  # Строковый ID (например, 'recommendation_prompt')
    name: str
    template: str
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

# --- Дефолтные промпты ---
DEFAULT_DESCRIPTION_PROMPT = """Ты - эксперт по написанию продающих описаний для виниловых пластинок.

ТВОЯ ЗАДАЧА:
Создать развернутое, впечатляющее и продающее описание (500-800 символов) для виниловой пластинки.

ОПИСАНИЕ ДОЛЖНО БЫТЬ:
- Развернутым и детальным (500-800 символов минимум)
- Эмоциональным и захватывающим
- Содержащим конкретные детали о музыке, стиле, истории создания и атмосфере альбома
- Продающим и привлекающим внимание любителей музыки
- Уникальным для именно этой пластинки

СТРУКТУРА ОПИСАНИЯ (обязательно используй все элементы):
1. 🎯 ЗАЦЕПКА (первые 1-2 предложения): Яркое начало, которое сразу захватывает внимание
2. 🎵 МУЗЫКА И СТИЛЬ: Детальное описание музыкального направления, особенностей звучания и композиций
3. 🎤 ИСПОЛНИТЕЛЬ: Описание исполнителя или группы, их истории и влияния на музыку
4. 🌍 КОНТЕКСТ И ЭПОХА: Описание времени создания, культурного контекста и атмосферы эпохи
5. ⚡ УНИКАЛЬНЫЕ ОСОБЕННОСТИ: Что делает именно эту пластинку особенной и незабываемой
6. 💫 ЭМОЦИОНАЛЬНЫЙ ПОСЫЛ: Какие чувства вызовет прослушивание этой пластинки
7. 🎬 ПРИЗЫВ К ДЕЙСТВИЮ: Завершающее предложение, мотивирующее к покупке и прослушиванию

ОПИСАНИЕ ДОЛЖНО ЗВУЧАТЬ КАК ЗАХВАТЫВАЮЩИЙ ТРЕЙЛЕР К ФИЛЬМУ - ярко, динамично, эмоционально!"""

DEFAULT_CHAT_CONSULTANT_PROMPT = """Ты - дружелюбный и профессиональный консультант по виниловым пластинкам в магазине "Винил Шоп". Твоя задача - помочь покупателю найти идеальную пластинку через живой диалог.

## ТВОЯ РОЛЬ
Ты - эксперт с глубоким знанием музыки, различных жанров, истории музыки и особенностей виниловых пластинок. Ты умеешь:
- Анализировать предпочтения пользователя через диалог
- Рекомендовать пластинки на основе вкусов покупателя
- Сравнивать разные пластинки и объяснять различия
- Находить похожие пластинки по стилю, настроению или исполнителю
- Давать советы по конкретным пластинкам
- Задавать уточняющие вопросы для лучшего понимания потребностей

## СТИЛЬ ОБЩЕНИЯ
- Дружелюбный, но профессиональный
- Неформальный, но не фамильярный
- Используй эмодзи умеренно для выразительности (💿 🎵 🎤 ⭐)
- Будь энтузиастом, но не навязчивым
- Отвечай кратко и по делу, но с достаточной детализацией
- Показывай искренний интерес к музыкальным предпочтениям пользователя

## ВАЖНЫЕ ПРАВИЛА
1. **Используй только информацию из каталога** - не выдумывай пластинки, которых нет в каталоге
2. **Указывай ID пластинок** - когда упоминаешь конкретную пластинку, указывай её ID (например: "Пластинка #5 - The Beatles - Abbey Road")
3. **Будь честным** - если не знаешь что-то или в каталоге нет подходящих вариантов, скажи об этом
4. **Задавай уточняющие вопросы** - если предпочтения неясны, задавай вопросы для лучшего понимания
5. **Анализируй каталог** - используй информацию о пластинках из каталога для рекомендаций
6. **Сравнивай обоснованно** - при сравнении пластинок указывай конкретные различия (жанр, стиль, цена, исполнитель)

## ФОРМАТ ОТВЕТОВ
- Отвечай естественным языком, как в обычном разговоре
- Можешь использовать эмодзи для выразительности, но не злоупотребляй
- Структурируй ответы для лучшей читаемости (короткие абзацы, списки)
- Когда рекомендуешь пластинки, указывай их ID, название, исполнителя и краткое обоснование

## КОНТЕКСТ
Тебе будет предоставлен каталог доступных пластинок с их ID, названиями, исполнителями, описаниями и ценами. Используй эту информацию для всех рекомендаций и ответов.

Помни: твоя цель - помочь покупателю найти пластинку, которая принесет ему радость и удовольствие!"""

# --- Инициализация базы данных и дефолтных промптов при запуске ---
@app.on_event("startup")  # type: ignore
async def startup_event():
    """Инициализация базы данных и создание дефолтных промптов при запуске приложения."""
    print("🔄 Инициализация prompts-manager service...")
    try:
        # Используем DATABASE_URL из config.env (поддерживает SQLite и MySQL)
        # Если не указано, используем SQLite по умолчанию
        database_url = os.getenv("DATABASE_URL", "sqlite:///./audio_store.db")
        
        # Если это SQLite и путь относительный, делаем абсолютный путь
        if database_url.startswith("sqlite"):
            # Для обратной совместимости, если путь относительный, делаем его абсолютным
            if not os.path.isabs(database_url.split("///")[-1] if "///" in database_url else ""):
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
                db_path = os.path.join(project_root, 'audio_store.db').replace('\\', '/')
                database_url = f"sqlite:///{db_path}"
        
        # Обновляем engine с правильными настройками
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        # connect_args нужны только для SQLite
        connect_args = {}
        if database_url.startswith("sqlite"):
            connect_args = {"check_same_thread": False}
        
        connection.DATABASE_URL = database_url
        connection.engine = create_engine(
            connection.DATABASE_URL,
            connect_args=connect_args
        )
        connection.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=connection.engine
        )
        
        connection.init_db()
        print("База данных инициализирована успешно")
        
        # Создаем или обновляем дефолтные промпты
        db = connection.SessionLocal()
        try:
            # Дефолтный промпт для рекомендаций
            default_recommendation_template = """Ты - эксперт по виниловым пластинкам с глубоким пониманием музыкальных жанров, истории музыки и предпочтений слушателей. Твоя задача - создавать персонализированные рекомендации на основе анализа каталога и предпочтений пользователя.

## АЛГОРИТМ РЕКОМЕНДАЦИЙ
1. **Анализ предпочтений**: Изучи предпочтения пользователя, жанры и текущие пластинки в коллекции
2. **Семантический анализ**: Найди пластинки с похожими музыкальными стилями, настроением и атмосферой
3. **Диверсификация**: Предложи разнообразные варианты для расширения музыкального кругозора
4. **Ценовая оптимизация**: Учитывай бюджетные предпочтения
5. **Эмоциональная совместимость**: Подбери пластинки, которые вызовут нужные эмоции и подойдут к настроению пользователя

## ФОРМАТ ОТВЕТА
ОБЯЗАТЕЛЬНО верни ВАЛИДНЫЙ JSON объект со следующей структурой:
{
    "recommendations": [
        {
            "id": 1,
            "name": "Название пластинки",
            "artist": "Исполнитель",
            "author": "Исполнитель",
            "reason": "Почему рекомендую эту пластинку",
            "match_score": 0.9
        }
    ],
    "reasoning": "Объяснение логики рекомендаций",
    "confidence_score": 0.85
}

ВАЖНО:
- Всегда возвращай валидный JSON, который можно распарсить
- Поля id, name, artist (или author для обратной совместимости), reason, match_score обязательны для каждой рекомендации
- match_score должен быть от 0.0 до 1.0
- confidence_score должен быть от 0.0 до 1.0"""
            
            # Проверяем наличие промпта для рекомендаций
            recommendation_prompt = db.query(models.Prompt).filter(
                models.Prompt.id == "recommendation_prompt"
            ).first()
            
            if not recommendation_prompt:
                default_recommendation = models.Prompt(
                    id="recommendation_prompt",
                    name="Промпт для рекомендаций",
                    template=default_recommendation_template
                )
                db.add(default_recommendation)
                print("Создан дефолтный промпт: recommendation_prompt")
            else:
                # Проверяем, содержит ли промпт старые тексты про аудиокниги/книги
                template_lower = recommendation_prompt.template.lower()
                if "аудиокниг" in template_lower or "книг" in template_lower or "чтения" in template_lower or "литературных" in template_lower:
                    recommendation_prompt.template = default_recommendation_template
                    print("Обновлен промпт recommendation_prompt (найдены старые тексты про аудиокниги)")
            
            # Проверяем наличие промпта для описаний
            description_prompt = db.query(models.Prompt).filter(
                models.Prompt.id == "description_prompt"
            ).first()
            
            if not description_prompt:
                default_description = models.Prompt(
                    id="description_prompt",
                    name="Промпт для описаний",
                    template=DEFAULT_DESCRIPTION_PROMPT
                )
                db.add(default_description)
                print("Создан дефолтный промпт: description_prompt")
            else:
                # Проверяем, содержит ли промпт старые тексты про аудиокниги/книги
                template_lower = description_prompt.template.lower()
                if "аудиокниг" in template_lower or ("книг" in template_lower and "пластинк" not in template_lower) or "чтения" in template_lower or "читател" in template_lower:
                    description_prompt.template = DEFAULT_DESCRIPTION_PROMPT
                    print("Обновлен промпт description_prompt (найдены старые тексты про аудиокниги)")
            
            # Проверяем наличие промпта для чата-консультанта
            chat_prompt = db.query(models.Prompt).filter(
                models.Prompt.id == "chat_consultant_prompt"
            ).first()
            
            if not chat_prompt:
                default_chat = models.Prompt(
                    id="chat_consultant_prompt",
                    name="Промпт для чат-консультанта",
                    template=DEFAULT_CHAT_CONSULTANT_PROMPT
                )
                db.add(default_chat)
                print("Создан дефолтный промпт: chat_consultant_prompt")
            
            db.commit()
            print("✅ Дефолтные промпты проверены/созданы успешно")
        except Exception as e:
            db.rollback()
            print(f"❌ Ошибка при создании дефолтных промптов: {e}")
            import traceback
            traceback.print_exc()
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Ошибка инициализации базы данных: {e}")
        import traceback
        traceback.print_exc()

# --- Вспомогательные функции ---
def get_db():
    """Dependency для получения сессии БД."""
    db = connection.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API эндпоинты ---

@app.get("/api/v1/prompts", response_model=List[PromptResponse])
def get_prompts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    GET-list: Получить список всех промптов.
    """
    try:
        prompts = db.query(models.Prompt).offset(skip).limit(limit).all()
        # Явно преобразуем SQLAlchemy объекты в Pydantic модели
        result = [
            PromptResponse(
                id=prompt.id,
                name=prompt.name,
                template=prompt.template
            )
            for prompt in prompts
        ]
        return result
    except Exception as e:
        print(f"Ошибка при получении промптов: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ошибка при получении промптов: {str(e)}")


@app.get("/api/v1/prompts/{prompt_id}", response_model=PromptResponse)
def get_prompt(prompt_id: str, db: Session = Depends(get_db)):
    """
    GET-one: Получить конкретный промпт по ID.
    """
    try:
        prompt = db.query(models.Prompt).filter(models.Prompt.id == prompt_id).first()
        if not prompt:
            raise HTTPException(
                status_code=404, 
                detail=f"Промпт '{prompt_id}' не найден"
            )
        # Явно преобразуем SQLAlchemy объект в Pydantic модель
        return PromptResponse(
            id=prompt.id,
            name=prompt.name,
            template=prompt.template
        )
    except HTTPException:
        raise  # Передаем HTTPException дальше, обработчик добавит CORS
    except Exception as e:
        print(f"Ошибка при получении промпта: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Ошибка при получении промпта: {str(e)}"
        )

@app.put("/api/v1/prompts/{prompt_id}", response_model=PromptResponse)
def update_prompt(prompt_id: str, prompt_update: PromptUpdate, db: Session = Depends(get_db)):
    """
    PUT-update: Обновить содержимое промпта по ID.
    """
    prompt = db.query(models.Prompt).filter(models.Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail=f"Промпт '{prompt_id}' не найден")
    
    prompt.template = prompt_update.template
    
    try:
        db.commit()
        db.refresh(prompt)
        # Явно преобразуем SQLAlchemy объект в Pydantic модель
        return PromptResponse(
            id=prompt.id,
            name=prompt.name,
            template=prompt.template
        )
    except Exception as e:
        db.rollback()
        print(f"Ошибка при обновлении промпта: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ошибка при обновлении промпта: {str(e)}")


@app.post("/api/v1/prompts/{prompt_id}/reset", response_model=PromptResponse)
def reset_prompt(prompt_id: str, db: Session = Depends(get_db)):
    """
    POST-reset: Сброс промпта к дефолтному значению.
    """
    # Дефолтный промпт для рекомендаций
    default_recommendation_template = """Ты - эксперт по виниловым пластинкам с глубоким пониманием музыкальных жанров, истории музыки и предпочтений слушателей. Твоя задача - создавать персонализированные рекомендации на основе анализа каталога и предпочтений пользователя.

## АЛГОРИТМ РЕКОМЕНДАЦИЙ
1. **Анализ предпочтений**: Изучи предпочтения пользователя, жанры и текущие пластинки в коллекции
2. **Семантический анализ**: Найди пластинки с похожими музыкальными стилями, настроением и атмосферой
3. **Диверсификация**: Предложи разнообразные варианты для расширения музыкального кругозора
4. **Ценовая оптимизация**: Учитывай бюджетные предпочтения
5. **Эмоциональная совместимость**: Подбери пластинки, которые вызовут нужные эмоции и подойдут к настроению пользователя

## ФОРМАТ ОТВЕТА
ОБЯЗАТЕЛЬНО верни ВАЛИДНЫЙ JSON объект со следующей структурой:
{
    "recommendations": [
        {
            "id": 1,
            "name": "Название пластинки",
            "artist": "Исполнитель",
            "author": "Исполнитель",
            "reason": "Почему рекомендую эту пластинку",
            "match_score": 0.9
        }
    ],
    "reasoning": "Объяснение логики рекомендаций",
    "confidence_score": 0.85
}

ВАЖНО:
- Всегда возвращай валидный JSON, который можно распарсить
- Поля id, name, artist (или author для обратной совместимости), reason, match_score обязательны для каждой рекомендации
- match_score должен быть от 0.0 до 1.0
- confidence_score должен быть от 0.0 до 1.0"""
    
    prompt = db.query(models.Prompt).filter(models.Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail=f"Промпт '{prompt_id}' не найден")
    
    # Определяем дефолтный шаблон в зависимости от типа промпта
    if prompt_id == "recommendation_prompt":
        prompt.template = default_recommendation_template
    elif prompt_id == "description_prompt":
        prompt.template = DEFAULT_DESCRIPTION_PROMPT
    elif prompt_id == "chat_consultant_prompt":
        prompt.template = DEFAULT_CHAT_CONSULTANT_PROMPT
    else:
        raise HTTPException(
            status_code=400, 
            detail=f"Промпт '{prompt_id}' не имеет дефолтного значения для сброса"
        )
    
    try:
        db.commit()
        db.refresh(prompt)
        return PromptResponse(
            id=prompt.id,
            name=prompt.name,
            template=prompt.template
        )
    except Exception as e:
        db.rollback()
        print(f"Ошибка при сбросе промпта: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ошибка при сбросе промпта: {str(e)}")

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "prompts-manager"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8007)

