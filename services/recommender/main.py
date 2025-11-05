from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from typing import List, Optional
import httpx
import os
import sys
from openai import OpenAI
import json
import re
from dotenv import load_dotenv
import asyncio
from pathlib import Path

# Настройка кодировки для Windows - ДОЛЖНО БЫТЬ ПЕРВЫМ!
if sys.platform == "win32":
    try:
        # Используем reconfigure, если доступно (Python 3.7+)
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass  # Если не получилось - продолжаем работу

# Загружаем переменные окружения
# Пробуем разные пути для config.env
# Используем override=False, чтобы переменные окружения процесса имели приоритет
config_paths = [
    Path(__file__).parent.parent.parent / 'config.env',  # ../../config.env
    Path(__file__).parent.parent / 'config.env',         # ../config.env
    Path.cwd() / 'config.env',                           # текущая директория
]
config_loaded = False
for config_path in config_paths:
    if config_path.exists():
        load_dotenv(config_path, override=False)  # override=False - не перезаписывать существующие
        config_loaded = True
        try:
            print(f"[Config] Загружен config.env из {config_path}")
        except UnicodeEncodeError:
            print(f"[Config] Загружен config.env из {str(config_path)}")
        break

if not config_loaded:
    print("[Config] WARNING: config.env не найден, используем переменные окружения системы")

# Проверяем наличие API ключа при старте
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise ValueError('Необходимо установить переменную окружения OPENROUTER_API_KEY')
print(f"[Config] OK: OPENROUTER_API_KEY найден: {api_key[:20]}...")

# --- Приложение FastAPI ---
app = FastAPI(
    title="Recommender Service API",
    description="AI-рекомендации для виниловых пластинок - Ограниченный Контекст Core Domain",
    version="1.0.0"
)

# Настройка CORS
# Для production укажите конкретные домены через переменную окружения ALLOWED_ORIGINS
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = allowed_origins_env.split(",") if allowed_origins_env else ["*"]
allowed_origins = [origin.strip() for origin in allowed_origins]
if "*" in allowed_origins and os.getenv("ENVIRONMENT", "development") == "production":
    print("WARNING: CORS настроен на allow_origins=['*'] в production! Это небезопасно!")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Доступные модели LLM
AVAILABLE_MODELS = {
    "gemini-pro": "google/gemini-pro-1.5",
    "gemini-flash": "google/gemini-flash-1.5-8b",
    "claude-3": "anthropic/claude-3.5-sonnet",
    "gpt-4": "openai/gpt-4-turbo",
    "llama-3": "meta-llama/llama-3-8b-instruct"
}

# Вспомогательная функция для вызова синхронного OpenAI клиента в async контексте
async def call_openai_async(messages, model="openai/gpt-4o-mini", temperature=0.8, max_tokens=300):
    """Вызывает OpenAI API в отдельном потоке, чтобы не блокировать event loop"""
    def _sync_call():
        """Синхронная функция для выполнения в executor"""
        client = None
        http_client = None
        try:
            # Получаем API ключ
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError("OPENROUTER_API_KEY не установлен в переменных окружения")
            
            print(f"[LLM] Вызов модели {model} с {len(messages)} сообщениями...")
            
            # Создаем новый HTTP клиент и OpenAI клиент для каждого запроса
            http_client = httpx.Client(timeout=90.0)  # 90 секунд таймаут
            client = OpenAI(
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1",
                http_client=http_client,
                max_retries=1
            )
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            print(f"[LLM] Ответ получен, использовано токенов: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")
            return response
        except Exception as e:
            print(f"[LLM] Ошибка в _sync_call: {type(e).__name__}: {str(e)}")
            raise
        finally:
            # Закрываем HTTP клиент после использования
            if http_client:
                try:
                    http_client.close()
                except:
                    pass
    
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # Если нет running loop, создаем новый (для тестов)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # Используем ThreadPoolExecutor для неблокирующего выполнения
    return await loop.run_in_executor(None, _sync_call)

# Модели данных
class RecommendationRequest(BaseModel):
    user_preferences: Optional[str] = None
    current_books: Optional[List[int]] = None
    genre_preferences: Optional[List[str]] = None
    max_recommendations: Optional[int] = 5
    model: Optional[str] = "gpt-4"  # По умолчанию используем GPT-4

class RecommendationResponse(BaseModel):
    recommendations: List[dict]
    reasoning: str
    confidence_score: float

class Product(BaseModel):
    id: int
    name: str
    artist: str
    description: str
    price: float
    cover_url: Optional[str] = None

class DescriptionGenerationResponse(BaseModel):
    product_id: int
    generated_description: str
    success: bool
    message: str

class SimplePromptRequest(BaseModel):
    prompt: str

# Модели данных для чата
class ChatMessage(BaseModel):
    role: str  # "user" или "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str  # Текущее сообщение пользователя
    history: Optional[List[ChatMessage]] = []  # История диалога
    current_product_id: Optional[int] = None  # ID текущей пластинки (если на странице детализации)
    model: Optional[str] = "gpt-4"  # Модель LLM
    
    @field_validator('message')
    @classmethod
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError('Сообщение не может быть пустым')
        return v.strip()
    
    @field_validator('history', mode='before')
    @classmethod
    def validate_history(cls, v):
        if v is None:
            return []
        if not isinstance(v, list):
            raise ValueError('История должна быть списком')
        # Валидируем структуру каждого сообщения
        validated_history = []
        for msg in v:
            if isinstance(msg, dict):
                if 'role' not in msg or 'content' not in msg:
                    raise ValueError('Сообщение должно содержать поля role и content')
                # Проверяем, что role валиден
                if msg['role'] not in ['user', 'assistant']:
                    raise ValueError("Поле 'role' должно быть 'user' или 'assistant'")
                # content может быть пустым (для некоторых случаев это допустимо)
                validated_history.append(msg)
            elif isinstance(msg, ChatMessage):
                # Если уже объект ChatMessage, преобразуем в dict
                validated_history.append({'role': msg.role, 'content': msg.content})
            else:
                raise ValueError('Сообщение должно быть словарем или объектом ChatMessage')
        return validated_history

class ChatResponse(BaseModel):
    response: str  # Ответ консультанта
    success: bool

# Функция для получения промпта из prompts-manager (Headless AI - шаг 2)
async def get_prompt_from_manager(prompt_id: str) -> str:
    """Получает промпт из микросервиса prompts-manager по ID"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"http://127.0.0.1:8007/api/v1/prompts/{prompt_id}")
            response.raise_for_status()
            response_data = response.json()
            
            # Извлекаем поле template из ответа
            prompt_content = response_data.get("template", "")
            if not prompt_content:
                raise ValueError(f"Промпт '{prompt_id}' пустой или не содержит поле 'template'")
            
            return prompt_content
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"Промпт '{prompt_id}' не найден в prompts-manager. Убедитесь, что промпт создан."
            )
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении промпта '{prompt_id}' из prompts-manager: {str(e)}"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Не удалось подключиться к prompts-manager на порту 8007: {str(e)}. Убедитесь, что сервис запущен."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении промпта '{prompt_id}': {str(e)}"
        )

# Функция для получения списка пластинок из каталога (шаг 3)
async def get_books_from_catalog() -> List[Product]:
    """Получает список всех виниловых пластинок из микросервиса каталога"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("http://127.0.0.1:8000/api/v1/products")
            response.raise_for_status()
            response_data = response.json()
            
            # Извлекаем массив продуктов из ответа
            records_data = response_data.get("products", [])
            
            # Преобразуем данные в наши модели
            records = []
            for record in records_data:
                records.append(Product(
                    id=record["id"],
                    name=record["name"],
                    artist=record.get("artist") or record.get("author", ""),
                    description=record["description"],
                    price=record["price"],
                    cover_url=record.get("cover_url")
                ))
            return records
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении каталога: {str(e)}")

# Сложный системный промпт - наша интеллектуальная собственность (шаг 4)
def clean_markdown(text: str) -> str:
    """Очищает текст от Markdown символов для красивого отображения"""
    if not text:
        return ""
    
    # Убираем все оставшиеся Markdown жирный текст **text** -> text (обрабатываем вложенные случаи)
    while re.search(r'\*\*([^*]+)\*\*', text):
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    
    # Убираем одиночные звездочки *text* -> text (но не внутри **text**)
    text = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'\1', text)
    
    # Убираем заголовки ### (в начале строки и в середине текста)
    text = re.sub(r'#{1,6}\s+', '', text)
    
    # Убираем markdown списки - * + (в начале строки)
    text = re.sub(r'^[\s]*[-*+]\s+', '', text, flags=re.MULTILINE)
    
    # Убираем нумерованные списки типа "1. ", "2. " и т.д.
    text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
    
    # Убираем специальные кавычки, заменяем на обычные
    text = re.sub(r'[""\u201C\u201D\u201E\u201F\u2033\u2036]', '"', text)
    
    # Убираем оставшиеся одиночные звездочки (которые не были частью **)
    text = re.sub(r'\*+', '', text)
    
    # Убираем лишние пробелы в начале и конце строк
    lines = []
    for line in text.split('\n'):
        cleaned_line = line.strip()
        if cleaned_line:  # Пропускаем пустые строки для сжатия
            lines.append(cleaned_line)
    
    # Объединяем строки с правильными переносами
    text = '\n'.join(lines)
    
    # Убираем множественные переносы строк (более 2 подряд заменяем на 2)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Убираем множественные пробелы (более 1 подряд)
    text = re.sub(r' +', ' ', text)
    
    return text.strip()

def extract_recommendations_from_text(text: str, records: List[Product]) -> List[dict]:
    """
    Извлекает рекомендации из текстового ответа LLM, ища упоминания ID или названий пластинок.
    Возвращает список рекомендаций с информацией из каталога.
    """
    recommendations = []
    
    # Создаем словарь пластинок по ID и по названию для быстрого поиска
    records_dict = {record.id: record for record in records}
    records_by_name = {}
    for record in records:
        # Нормализуем название для поиска (убираем кавычки, приводим к нижнему регистру)
        normalized_name = re.sub(r'[""\u201C\u201D\u201E\u201F\u2033\u2036]', '', record.name).strip().lower()
        records_by_name[normalized_name] = record
        # Также добавляем варианты без некоторых слов
        name_parts = [part for part in normalized_name.split() if len(part) > 2]
        if len(name_parts) > 1:
            records_by_name[' '.join(name_parts)] = record
    
    found_records = {}  # record_id -> record object
    
    # Для обратной совместимости используем старые имена переменных внутри функции
    books = records
    books_dict = records_dict
    books_by_name = records_by_name
    found_books = found_records
    
    # Метод 1: Поиск по ID в тексте
    id_patterns = [
        r'ID[:\s]+(\d+)',
        r'\(ID[:\s]+(\d+)\)',
        r'ID\s*=\s*(\d+)',
        r'пластинка\s+(\d+)',
        r'#(\d+)',
    ]
    
    for pattern in id_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                book_id = int(match)
                if book_id in books_dict:
                    found_books[book_id] = books_dict[book_id]
            except ValueError:
                continue
    
    # Метод 2: Поиск по названиям пластинок (если не нашли по ID)
    if not found_books:
        # Ищем паттерны типа: "Название пластинки" - Исполнитель или **"Название"** - Исполнитель
        title_patterns = [
            r'[""\u201C\u201D\u201E\u201F\u2033\u2036]([^""\u201C\u201D\u201E\u201F\u2033\u2036]+)[""\u201C\u201D\u201E\u201F\u2033\u2036]',  # "Название"
            r'\*\*[""\u201C\u201D\u201E\u201F\u2033\u2036]([^""\u201C\u201D\u201E\u201F\u2033\u2036]+)[""\u201C\u201D\u201E\u201F\u2033\u2036]\*\*',  # **"Название"**
            r'\*\*([^*]+?)\*\*',  # **Название**
        ]
        
        found_titles = []
        for pattern in title_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Убираем кавычки и нормализуем
                book_title = re.sub(r'[""\u201C\u201D\u201E\u201F\u2033\u2036]', '', match).strip()
                if book_title and len(book_title) > 2:
                    found_titles.append(book_title)
        
        # Ищем пластинки по найденным названиям
        for book_title in found_titles:
            normalized_title = book_title.lower().strip()
            
            # Ищем точное совпадение
            if normalized_title in books_by_name:
                book = books_by_name[normalized_title]
                found_books[book.id] = book
                continue
            
            # Ищем частичное совпадение (содержит ключевые слова)
            best_match = None
            best_match_score = 0
            
            for norm_name, book in books_by_name.items():
                # Проверяем, содержит ли название ключевые слова из найденного текста
                title_words = [w for w in normalized_title.split() if len(w) > 2]
                book_words = [w for w in norm_name.split() if len(w) > 2]
                
                if title_words and book_words:
                    # Если более 50% слов совпадает
                    common_words = set(title_words) & set(book_words)
                    match_score = len(common_words) / max(len(title_words), len(book_words))
                    if match_score > best_match_score and match_score >= 0.4:  # Минимум 40% совпадения
                        best_match = book
                        best_match_score = match_score
            
            if best_match:
                found_books[best_match.id] = best_match
    
    # Если найдены пластинки, создаем рекомендации
    if found_books:
        for book_id, book in found_books.items():
            # Ищем причину рекомендации в тексте
            # Паттерны для поиска причины после упоминания пластинки
            reason_patterns = [
                rf'[""\u201C\u201D\u201E\u201F\u2033\u2036]?{re.escape(book.name)}[""\u201C\u201D\u201E\u201F\u2033\u2036]?[^\n]*?[-–]\s*([^\n]+?)(?:\n|Оценка|совпадение|$)',
                rf'\*\*{re.escape(book.name)}\*\*[^\n]*?[-–]\s*([^\n]+?)(?:\n|Оценка|совпадение|$)',
                rf'{re.escape(book.name)}[^\n]*?[Пп]ричина[:\s]+([^\n]+?)(?:\n|Оценка|совпадение|$)',
                rf'{re.escape(book.name)}[^\n]*?[Рр]асширение[^\n]*?([^\n]+?)(?:\n|Оценка|совпадение|$)',
            ]
            
            reason = "Подходит под ваши предпочтения"
            for pattern in reason_patterns:
                reason_match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if reason_match:
                    reason = clean_markdown(reason_match.group(1).strip())
                    if reason and len(reason) > 10:  # Минимальная длина причины
                        break
            
            # Если не нашли специфическую причину, ищем общее описание рядом с названием
            if reason == "Подходит под ваши предпочтения":
                # Ищем блок текста после упоминания пластинки (до следующего упоминания пластинки или раздела)
                book_pos = text.lower().find(book.name.lower())
                if book_pos != -1:
                    # Берем текст после упоминания пластинки (до 400 символов или до следующей пластинки)
                    context_start = book_pos + len(book.name)
                    context_end = min(context_start + 400, len(text))
                    
                    # Ищем причину в этом контексте
                    context = text[context_start:context_end]
                    # Ищем текст после дефиса или тире, до следующего упоминания оценки или совпадения
                    reason_match = re.search(r'[-–]\s*([^.\n]+(?:\n[^\d*\n][^.\n]*)?)(?:\n|Оценка|совпадение|$)', context, re.IGNORECASE)
                    if reason_match:
                        reason = clean_markdown(reason_match.group(1).strip())
            
            # Ищем score совпадения
            match_score = None
            # Ищем оценку рядом с упоминанием пластинки
            book_context = text[max(0, text.lower().find(book.name.lower()) - 100):text.lower().find(book.name.lower()) + 500]
            score_patterns = [
                r'(?:соответствие|совпадение|match|score|оценка)[:\s]+([0-9.]+)',
                r'([0-9.]+)\s*(?:из\s*1|%|балл)',
            ]
            for pattern in score_patterns:
                score_matches = re.findall(pattern, book_context, re.IGNORECASE)
                if score_matches:
                    try:
                        match_score = float(score_matches[0])
                        if match_score > 1.0:
                            match_score = match_score / 10.0  # Нормализуем если указан как процент
                        if match_score > 1.0:
                            match_score = match_score / 100.0  # Если всё ещё > 1, значит это процент
                        break
                    except:
                        pass
            
            recommendations.append({
                "id": book.id,
                "name": book.name,
                "artist": book.artist,
                "reason": reason[:300] if len(reason) > 300 else reason,  # Ограничиваем длину
                "match_score": match_score if match_score else 0.7  # Дефолтный score
            })
    
    return recommendations

async def create_system_prompt(books: List[Product], request: RecommendationRequest) -> str:
    """Создает сложный системный промпт для LLM, получая базовый промпт из prompts-manager (Headless AI)"""
    
    # Шаг 1: Получаем базовый промпт из prompts-manager
    base_prompt = await get_prompt_from_manager("recommendation_prompt")
    
    # Шаг 2: Дополняем промпт динамическими данными
    books_list = "\n".join([
        f"ID: {book.id} | Название: {book.name} | Исполнитель: {book.artist} | Описание: {book.description[:200]}... | Цена: {book.price}₽"
        for book in books
    ])
    
    # Формируем дополнение с каталогом и предпочтениями
    dynamic_content = f"""
## КАТАЛОГ ДОСТУПНЫХ ВИНИЛОВЫХ ПЛАСТИНОК
{books_list}

## ПРЕДПОЧТЕНИЯ ПОЛЬЗОВАТЕЛЯ
- Предпочтения: {request.user_preferences or "Не указаны"}
- Текущие пластинки: {request.current_books or "Не указаны"}
- Любимые жанры: {request.genre_preferences or "Не указаны"}
- Количество рекомендаций: {request.max_recommendations}
"""
    
    # Объединяем базовый промпт с динамическими данными
    system_prompt = f"{base_prompt}\n\n{dynamic_content}"

    return system_prompt

# Эндпоинт для генерации рекомендаций (шаг 2)
# Поддерживает как полный RecommendationRequest, так и простой промпт (SimplePromptRequest)
@app.post("/api/v1/recommendations/generate")
async def generate_recommendations(request: dict):
    """
    Генерирует персонализированные рекомендации виниловых пластинок на основе AI-анализа.
    Поддерживает два формата запроса:
    1. Простой промпт: {"prompt": "текст запроса"}
    2. Полный запрос: {"user_preferences": "...", "model": "...", ...}
    """
    try:
        # Проверяем тип запроса: простой промпт или полный RecommendationRequest
        is_simple_prompt = "prompt" in request and len(request) == 1
        
        # Шаг 3: Получаем список пластинок из каталога
        books = await get_books_from_catalog()
        print(f"Получено {len(books)} пластинок из каталога")
        
        if not books:
            raise HTTPException(status_code=404, detail="Каталог виниловых пластинок пуст")
        
        # Если простой промпт - обрабатываем его отдельно
        if is_simple_prompt:
            prompt = request["prompt"]
            print(f"Обработка простого промпта: {prompt[:50]}...")
            
            # Формируем системный промпт с каталогом пластинок
            books_list = "\n".join([
                f"ID: {book.id} | Название: {book.name} | Исполнитель: {book.artist} | Описание: {book.description[:200]}... | Цена: {book.price}₽"
                for book in books
            ])
            
            system_prompt = f"""Ты - эксперт по виниловым пластинкам. У тебя есть доступ к каталогу пластинок:

{books_list}

Твоя задача - помочь пользователю на основе его запроса."""
            
            # Вызываем LLM
            model_name = "openai/gpt-4o-mini"  # Используем быструю модель по умолчанию
            
            try:
                response = await call_openai_async(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    model=model_name,
                    temperature=0.7,
                    max_tokens=2000
                )
                
                # Проверяем, что ответ корректный
                if not response or not hasattr(response, 'choices') or not response.choices:
                    raise HTTPException(
                        status_code=500,
                        detail="Не удалось обработать ответ от AI. Попробуйте изменить промпт."
                    )
                
                # Возвращаем ответ как есть
                llm_response = response.choices[0].message.content
                if not llm_response:
                    raise HTTPException(
                        status_code=500,
                        detail="Не удалось обработать ответ от AI. Попробуйте изменить промпт."
                    )
                
                return {"response": llm_response}
                
            except httpx.HTTPStatusError as e:
                print(f"[ОШИБКА] HTTPStatusError при обращении к OpenRouter: {str(e)}")
                raise HTTPException(
                    status_code=502,
                    detail="Ошибка при обращении к внешнему AI сервису"
                )
            except json.JSONDecodeError as e:
                print(f"[ОШИБКА] JSONDecodeError при обработке ответа: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail="Не удалось обработать ответ от AI. Попробуйте изменить промпт."
                )
            except Exception as e:
                print(f"[ОШИБКА] Неожиданная ошибка при обработке простого промпта: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail="Не удалось обработать ответ от AI. Попробуйте изменить промпт."
                )
        
        # Иначе обрабатываем как полный RecommendationRequest
        print(f"Обработка полного запроса для пользователя: {request.get('user_preferences', 'N/A')}")
        
        # Преобразуем dict в RecommendationRequest для совместимости с create_system_prompt
        rec_request = RecommendationRequest(
            user_preferences=request.get("user_preferences"),
            current_books=request.get("current_books"),
            genre_preferences=request.get("genre_preferences"),
            max_recommendations=request.get("max_recommendations", 5),
            model=request.get("model", "gpt-4")
        )
        
        # Шаг 4: Создаем сложный системный промпт (Headless AI - получаем из prompts-manager)
        system_prompt = await create_system_prompt(books, rec_request)
        
        # Шаг 5: Вызываем LLM и получаем ответ
        try:
            # Получаем полное имя модели
            model_name = AVAILABLE_MODELS.get(rec_request.model, AVAILABLE_MODELS["gpt-4"])
            
            # Используем async обертку для неблокирующего вызова
            try:
                response = await call_openai_async(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": "Сгенерируй персонализированные рекомендации виниловых пластинок на основе предоставленной информации."}
                    ],
                    model=model_name,
                    temperature=0.7,
                    max_tokens=1500
                )
                
                # Проверяем, что ответ корректный
                if not response or not hasattr(response, 'choices') or not response.choices:
                    raise HTTPException(
                        status_code=500,
                        detail="Не удалось обработать ответ от AI. Попробуйте изменить промпт."
                    )
                
                # Парсим ответ от LLM
                llm_response = response.choices[0].message.content
                
                if not llm_response:
                    raise HTTPException(
                        status_code=500,
                        detail="Не удалось обработать ответ от AI. Попробуйте изменить промпт."
                    )
                
            except httpx.HTTPStatusError as e:
                print(f"[ОШИБКА] HTTPStatusError при обращении к OpenRouter: {str(e)}")
                raise HTTPException(
                    status_code=502,
                    detail="Ошибка при обращении к внешнему AI сервису"
                )
            
            # Пытаемся извлечь JSON из ответа
            parsed_response = None
            recommendations = []
            reasoning = llm_response
            confidence_score = 0.5
            
            try:
                # Ищем JSON в ответе
                json_start = llm_response.find('{')
                json_end = llm_response.rfind('}') + 1
                if json_start != -1 and json_end != 0:
                    json_str = llm_response[json_start:json_end]
                    parsed_response = json.loads(json_str)
                    print(f"[ПАРСИНГ] Успешно распарсен JSON из ответа LLM")
                else:
                    print(f"[ПАРСИНГ] JSON блок не найден в ответе, пытаемся извлечь рекомендации из текста")
                    # Пытаемся извлечь рекомендации из текста
                    extracted_recs = extract_recommendations_from_text(llm_response, books)
                    if extracted_recs:
                        recommendations = extracted_recs
                        print(f"[ПАРСИНГ] Извлечено {len(recommendations)} рекомендаций из текста")
                        # Ищем confidence_score в тексте
                        conf_match = re.search(r'(?:уверенность|confidence)[:\s]+([0-9.]+)', llm_response, re.IGNORECASE)
                        if conf_match:
                            try:
                                conf_val = float(conf_match.group(1))
                                if conf_val > 1.0:
                                    conf_val = conf_val / 100.0
                                confidence_score = min(max(conf_val, 0.0), 1.0)
                            except:
                                pass
            except json.JSONDecodeError as e:
                print(f"[ПАРСИНГ] Ошибка парсинга JSON: {str(e)}, пытаемся извлечь из текста")
                # Пытаемся извлечь рекомендации из текста как fallback
                extracted_recs = extract_recommendations_from_text(llm_response, books)
                if extracted_recs:
                    recommendations = extracted_recs
                    print(f"[ПАРСИНГ] Извлечено {len(recommendations)} рекомендаций из текста (fallback)")
                else:
                    # Если не удалось извлечь из текста - это ошибка
                    raise HTTPException(
                        status_code=500,
                        detail="Не удалось обработать ответ от AI. Попробуйте изменить промпт."
                    )
            except Exception as parse_error:
                print(f"[ПАРСИНГ] Общая ошибка парсинга: {str(parse_error)}")
                # Пытаемся извлечь рекомендации из текста как fallback
                try:
                    extracted_recs = extract_recommendations_from_text(llm_response, books)
                    if extracted_recs:
                        recommendations = extracted_recs
                        print(f"[ПАРСИНГ] Извлечено {len(recommendations)} рекомендаций из текста (fallback после ошибки)")
                    else:
                        raise HTTPException(
                            status_code=500,
                            detail="Не удалось обработать ответ от AI. Попробуйте изменить промпт."
                        )
                except HTTPException:
                    raise
                except Exception:
                    raise HTTPException(
                        status_code=500,
                        detail="Не удалось обработать ответ от AI. Попробуйте изменить промпт."
                    )
            
            # Если парсинг прошел успешно, используем данные из JSON
            if parsed_response:
                recommendations = parsed_response.get("recommendations", recommendations)
                # Если массив рекомендаций пустой, пытаемся извлечь из reasoning
                if not recommendations:
                    extracted_recs = extract_recommendations_from_text(
                        parsed_response.get("reasoning", reasoning), 
                        books
                    )
                    if extracted_recs:
                        recommendations = extracted_recs
                        print(f"[ПАРСИНГ] Извлечено {len(recommendations)} рекомендаций из reasoning (JSON был пустым)")
                
                reasoning = parsed_response.get("reasoning", reasoning)
                confidence_score = min(max(parsed_response.get("confidence_score", confidence_score), 0.0), 1.0)
            
            # Очищаем reasoning от Markdown для красивого отображения
            reasoning = clean_markdown(reasoning)
            
            # Валидируем рекомендации - проверяем, что все поля есть
            validated_recommendations = []
            for rec in recommendations:
                if isinstance(rec, dict):
                    # Если есть только id, дополняем данными из каталога
                    if "id" in rec:
                        book_id = rec.get("id")
                        book = next((b for b in books if b.id == book_id), None)
                        if book:
                            validated_recommendations.append({
                                "id": book.id,
                                "name": rec.get("name", book.name),
                                "artist": rec.get("artist", book.artist),
                                "reason": rec.get("reason", "Подходит под ваши предпочтения"),
                                "match_score": rec.get("match_score", 0.7)
                            })
                    elif "name" in rec:
                        # Если есть имя, пытаемся найти в каталоге
                        validated_recommendations.append(rec)
            
            recommendations = validated_recommendations if validated_recommendations else recommendations
            
            print(f"[РЕЗУЛЬТАТ] Найдено {len(recommendations)} рекомендаций, confidence: {confidence_score}")
            
            return RecommendationResponse(
                recommendations=recommendations,
                reasoning=reasoning,
                confidence_score=confidence_score
            )
            
        except HTTPException:
            # Пробрасываем HTTPException дальше
            raise
        except httpx.HTTPStatusError as e:
            print(f"[ОШИБКА] HTTPStatusError при обращении к OpenRouter (внешний блок): {str(e)}")
            raise HTTPException(
                status_code=502,
                detail="Ошибка при обращении к внешнему AI сервису"
            )
        except json.JSONDecodeError as e:
            print(f"[ОШИБКА] JSONDecodeError при обработке ответа (внешний блок): {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Не удалось обработать ответ от AI. Попробуйте изменить промпт."
            )
        except Exception as llm_error:
            print(f"[ОШИБКА] Неожиданная ошибка LLM: {str(llm_error)}")  # Логируем ошибку
            raise HTTPException(
                status_code=500, 
                detail="Не удалось обработать ответ от AI. Попробуйте изменить промпт."
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервиса: {str(e)}")

# Эндпоинт для AI-генерации описания пластинки (Оркестратор)
@app.post("/api/v1/recommendations/generate-description/{product_id}", response_model=DescriptionGenerationResponse, tags=["AI Description"])
async def generate_book_description(product_id: int):
    """
    Оркестратор для AI-генерации описания пластинки
    
    Шаги оркестрации:
    1. GET-запрос к catalog API для получения данных о пластинке
    2. Формирование промпта для LLM на основе данных пластинки
    3. Вызов внешней системы (LLM) для генерации описания
    4. PUT-запрос к catalog API для обновления description
    5. Возврат сгенерированного описания клиенту
    """
    try:
        # Шаг 1: GET-запрос к catalog API для получения данных о пластинке
        print(f"[Шаг 1] Получаем данные о пластинке с ID={product_id} из catalog API...")
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                catalog_response = await client.get(f"http://127.0.0.1:8000/api/v1/products/{product_id}")
                
                if catalog_response.status_code == 404:
                    raise HTTPException(
                        status_code=404, 
                        detail=f"Пластинка с ID {product_id} не найдена в каталоге. Убедитесь, что товар существует в catalog API (порт 8000), а не только в localStorage админ-панели."
                    )
                
                catalog_response.raise_for_status()
                book_data = catalog_response.json()
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail="Таймаут при получении данных из catalog API. Убедитесь, что catalog service запущен на порту 8000."
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Не удалось подключиться к catalog API на порту 8000: {str(e)}. Убедитесь, что сервис запущен."
            )
        
        # Извлекаем данные о пластинке с проверкой различных возможных полей
        book_name = (
            book_data.get('name') or 
            book_data.get('title') or 
            book_data.get('product_name') or 
            'Неизвестная пластинка'
        )
        book_artist = (
            book_data.get('artist') or 
            book_data.get('artist_name') or 
            book_data.get('artist_id') or 
            book_data.get('author') or  # Fallback для обратной совместимости
            book_data.get('author_name') or 
            book_data.get('author_id') or 
            'Неизвестный исполнитель'
        )
        current_desc = (
            book_data.get('description') or 
            book_data.get('desc') or 
            'Описание отсутствует'
        )
        
        # Валидация данных
        if not book_name or book_name == 'Неизвестная пластинка':
            raise HTTPException(
                status_code=400,
                detail=f"Не удалось получить название пластинки для ID {product_id}. Данные: {json.dumps(book_data, ensure_ascii=False)}"
            )
        
        if not book_artist or book_artist == 'Неизвестный исполнитель':
            print(f"⚠️  [Шаг 1] ВНИМАНИЕ: Исполнитель не найден для пластинки ID {product_id}, используем значение по умолчанию")
        
        print(f"[Шаг 1] Данные получены: ID={product_id}, Название='{book_name}', Исполнитель='{book_artist}'")
        print(f"[Шаг 1] Полные данные пластинки: {json.dumps(book_data, ensure_ascii=False, indent=2)[:500]}")
        print(f"[Шаг 1] Текущее описание (первые 100 символов): {current_desc[:100] if current_desc else 'отсутствует'}")
        
        # Шаг 2: Формирование промпта для LLM на основе данных пластинки (Headless AI - получаем из prompts-manager)
        print(f"[Шаг 2] Получаем базовый промпт из prompts-manager и формируем промпт для LLM для пластинки '{book_name}'...")
        
        # Получаем базовый промпт из prompts-manager
        base_description_prompt = await get_prompt_from_manager("description_prompt")
        
        # Определяем специфичные категории пластинок (для дополнительной логики)
        # Проверка на конкретных исполнителей для специальной обработки
        is_beatles = "beatles" in book_artist.lower() or "битлз" in book_artist.lower()
        
        # Формируем дополнение с данными о пластинке
        book_info_section = f"""
═══════════════════════════════════════════════════════════════
ПЛАСТИНКА ДЛЯ ОПИСАНИЯ (ЭТО ВАЖНО - ЗАПОМНИ НАЗВАНИЕ!):
═══════════════════════════════════════════════════════════════
НАЗВАНИЕ: "{book_name}"
ИСПОЛНИТЕЛЬ: {book_artist}
ID: {product_id}
═══════════════════════════════════════════════════════════════

КРИТИЧЕСКИ ВАЖНЫЕ ПРАВИЛА:
1. ⚠️ Описание создается ТОЛЬКО для "{book_name}" от {book_artist} - НЕ для других пластинок!
"""
        
        # Добавляем специфичные правила для пластинок не от The Beatles (пример)
        if not is_beatles:
            book_info_section += f"""2. 🚫 ЗАПРЕЩЕНО: Эта пластинка НЕ от The Beatles. ИСПОЛНИТЕЛЬ: {book_artist}. НИКОГДА не упоминай в описании:
   - The Beatles
   - Битлз
   - Элементы, характерные только для The Beatles
"""
        
        # Для пластинок от The Beatles добавляем специфичные инструкции
        if is_beatles:
            book_name_parts = book_name.lower()
            book_info_section += f"""2. ⚠️ КРИТИЧЕСКИ ВАЖНО - ЭТО КОНКРЕТНАЯ ПЛАСТИНКА СЕРИИ:
Это пластинка "{book_name}" - НЕ другая пластинка от The Beatles!

УНИКАЛЬНЫЕ ЭЛЕМЕНТЫ ЭТОЙ ПЛАСТИНКИ:
"{book_name_parts}" - это уникальная часть названия, которая отличает её от других пластинок исполнителя.

СТРОГИЕ ПРАВИЛА ДЛЯ РАЗВЕРНУТОГО ОПИСАНИЯ (500-800 символов):
- Создавай детальное, развернутое описание ТОЛЬКО для "{book_name}"
- ОБЯЗАТЕЛЬНО детально опиши композиции и особенности этой пластинки
- Опиши атмосферу и стиль именно этой пластинки
- Добавь детали о главных треках, которые включены в "{book_name}"
- НЕ упоминай названия других пластинок исполнителя
"""
        
        book_info_section += f"""3. 📝 Создавай описание с нуля на основе ТОЛЬКО названия "{book_name}" и исполнителя {book_artist}
4. ✅ УБЕДИСЬ, что описание содержит слова из названия "{book_name}" и описывает именно ЭТУ пластинку!

СТИЛЬ: увлекательный, продающий, детальный, эмоциональный для "{book_name}" от {book_artist}
"""
        
        # Объединяем базовый промпт с информацией о пластинке
        system_prompt = f"{base_description_prompt}\n\n{book_info_section}"

        # Формируем user_prompt - ВСЕГДА игнорируем старое описание, если это не пластинка от The Beatles
        # Это гарантирует, что модель не будет копировать неправильные описания
        current_desc_safe = ""
        if current_desc and current_desc != 'Описание отсутствует':
            # Если это НЕ пластинка от The Beatles - всегда помечаем старое описание как неверное
            # Это помогает избежать копирования неправильных описаний
            if not is_beatles:
                # Проверяем, содержит ли описание упоминания The Beatles
                desc_lower = current_desc.lower()
                has_beatles_mention = any(term in desc_lower for term in [
                    "beatles", "битлз"
                ])
                if has_beatles_mention and book_artist.lower() != "the beatles":
                    current_desc_safe = "[ВНИМАНИЕ: Текущее описание содержит ошибки - упоминает The Beatles, хотя это не та пластинка. ПОЛНОСТЬЮ ИГНОРИРУЙ это описание и создай новое с нуля!]"
                else:
                    # Даже если нет упоминаний, но описание слишком короткое или общее - лучше пересоздать
                    current_desc_safe = "[Текущее описание будет заменено - создай новое уникальное описание с нуля]"
            else:
                # Для пластинок от The Beatles можем использовать старое описание как референс
                current_desc_safe = current_desc[:150]
        else:
            current_desc_safe = "отсутствует"
        
        # Формируем user_prompt с явным указанием названия и исполнителя
        forbidden_warning = ""
        if not is_beatles:
            forbidden_warning = """
🚫 АБСОЛЮТНЫЙ ЗАПРЕТ:
- НЕ упоминай The Beatles, Битлз (если исполнитель не они)
- НЕ используй элементы, характерные только для The Beatles
- Эта пластинка "{book_name}" от исполнителя {book_artist} - это ДРУГОЕ произведение!
"""
        
        # Формируем специальный user_prompt с явным указанием уникальных элементов для пластинок от The Beatles
        unique_elements_instruction = ""
        if is_beatles:
            book_name_parts = book_name.lower()
            unique_elements_instruction = f"""
🎯 УНИКАЛЬНЫЕ ЭЛЕМЕНТЫ ДЛЯ ЭТОЙ ПЛАСТИНКИ:
Эта пластинка "{book_name_parts}" - это ключевая часть, которая отличает её от других!

ДЛЯ РАЗВЕРНУТОГО ОПИСАНИЯ (500-800 символов) ОБЯЗАТЕЛЬНО:
- ОБЯЗАТЕЛЬНО детально опиши композиции, включенные в "{book_name_parts}"
- Опиши уникальные музыкальные особенности и стиль именно этой пластинки
- Добавь детали о треках, их значении и месте в дискографии исполнителя в контексте "{book_name_parts}"
- Создай атмосферу и настроение, характерные именно для этой пластинки
- Используй яркие, эмоциональные формулировки для передачи музыкального настроения
- НЕ смешивай с информацией о других пластинках - фокусируйся ТОЛЬКО на "{book_name_parts}"
- Опиши, что делает именно эту пластинку особенной и незабываемой в дискографии
"""
        
        user_prompt = f"""═══════════════════════════════════════════════════════════════
СОЗДАЙ ОПИСАНИЕ ДЛЯ ЭТОЙ ПЛАСТИНКИ:
═══════════════════════════════════════════════════════════════
💿 НАЗВАНИЕ: "{book_name}"
🎤 ИСПОЛНИТЕЛЬ: {book_artist}
🔢 ID: {product_id}
═══════════════════════════════════════════════════════════════

⚠️ ВАЖНО: Текущее описание содержит ошибки - ИГНОРИРУЙ ЕГО!
Текущее описание (НЕ ИСПОЛЬЗУЙ): {current_desc_safe}

{forbidden_warning}
{unique_elements_instruction}

✅ ЗАДАНИЕ:
Создай с нуля новое, развернутое и впечатляющее описание (500-800 символов) ТОЛЬКО для пластинки "{book_name}" от исполнителя {book_artist}.

⚠️ ВАЖНО О ДЛИНЕ:
- Минимум 500 символов (это важно!)
- Рекомендуется 600-800 символов для полноты
- Не бойся быть детальным - чем больше конкретики, тем лучше
- Используй яркие эпитеты, динамичные формулировки, эмоциональные обороты

⚠️ КРИТИЧЕСКИ ВАЖНО:
- Описание должно быть для пластинки "{book_name}" - НЕ для другой пластинки!
- Описание должно содержать уникальные элементы из названия "{book_name}"
- Каждое слово в названии важно - используй их в описании!
- Если это серия - опиши именно ЭТУ пластинку, а не серию в целом!

📋 ЧТО ДЕЛАТЬ:
1. Начни описание с упоминания "{book_name}"
2. Используй информацию только об ЭТОЙ конкретной пластинке
3. Обязательно включи уникальные элементы из названия "{book_name}"
4. Опиши, что делает эту пластинку особенной
5. Сделай описание увлекательным и продающим

🚫 ЧТО НЕ ДЕЛАТЬ:
- НЕ упоминай другие пластинки или исполнителей
- НЕ используй информацию о других пластинках
- НЕ копируй описания других пластинок
{"- НЕ путай с другими пластинками исполнителя - это именно '{book_name}'!" if is_beatles else "- НЕ упоминай других исполнителей"}
- НЕ используй общие фразы без привязки к "{book_name}"

✨ ОПИСАНИЕ ДОЛЖНО: 
- Начинаться с яркой зацепки, которая сразу захватывает внимание
- Быть развернутым (500-800 символов) с детальным описанием композиций, стиля и атмосферы пластинки
- Содержать конкретные детали о музыке, стиле и особенностях именно этой пластинки
- Использовать эмоциональные и динамичные формулировки
- Быть продающим и мотивировать к прослушиванию
- Отражать уникальность именно этой пластинки "{book_name}"
- Создавать атмосферу и передавать настроение произведения

💡 СОВЕТЫ ДЛЯ СОЗДАНИЯ ВПЕЧАТЛЯЮЩЕГО ОПИСАНИЯ:
- Используй активные глаголы и динамичные конструкции
- Добавляй конкретные детали вместо общих фраз
- Создавай атмосферу через описание мира и настроения
- Покажи конфликты и интриги, которые ждут читателя
- Используй эпитеты и метафоры для создания образа
- Заверши призывом к действию

Напиши развернутое, детальное и впечатляющее описание прямо сейчас:"""
        
        # Шаг 3: Вызов внешней системы (LLM) для генерации описания
        print(f"[Шаг 3] Отправляем запрос к LLM для генерации описания...")
        
        # Проверяем наличие API ключа перед вызовом
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="OPENROUTER_API_KEY не установлен. Проверьте config.env или переменные окружения."
            )
        print(f"[Шаг 3] API ключ найден: {api_key[:20]}...")
        
        # ОТЛАДКА: Логируем промпт для проверки
        print(f"[DEBUG] System prompt (первые 300 символов): {system_prompt[:300]}...")
        print(f"[DEBUG] User prompt (первые 300 символов): {user_prompt[:300]}...")
        print(f"[DEBUG] Пластинка для описания: '{book_name}' от исполнителя {book_artist}")
        print(f"[DEBUG] Проверка исполнителя: is_beatles={is_beatles}")
        
        try:
            # Используем async-обертку для неблокирующего вызова LLM
            messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
            ]
            
            # Пробуем сначала более умную модель для точности, затем fallback
            llm_response = None
            models_to_try = [
                ("openai/gpt-4o-mini", "gpt-4o-mini"),  # Начинаем с надежной модели
                ("openai/gpt-4-turbo", "gpt-4-turbo"),  # Более умная модель для точности
                ("google/gemini-pro-1.5", "gemini-pro"),  # Затем пробуем Gemini Pro
            ]
            
            for model_id, model_name in models_to_try:
                try:
                    print(f"[Шаг 3] Пробуем модель {model_name} ({model_id})...")
                    # Используем более низкую температуру для точности и следования инструкциям
                    llm_response = await asyncio.wait_for(
                        call_openai_async(
                            messages=messages,
                            model=model_id,
                            temperature=0.7,  # Увеличиваем температуру для более творческих и впечатляющих описаний
                            max_tokens=1000  # Значительно увеличиваем лимит для развернутых описаний (500-800 символов)
                        ),
                        timeout=90.0
                    )
                    print(f"[Шаг 3] Модель {model_name} успешно ответила!")
                    break  # Успешно получили ответ, выходим из цикла
                except asyncio.TimeoutError:
                    print(f"[Шаг 3] Модель {model_name} таймаут, пробуем следующую...")
                    continue
                except Exception as e:
                    error_msg = str(e)
                    if "404" in error_msg or "not found" in error_msg.lower() or "no endpoints" in error_msg.lower():
                        print(f"[Шаг 3] Модель {model_name} недоступна (404), пробуем следующую...")
                        continue
                    else:
                        print(f"[Шаг 3] Ошибка модели {model_name}: {error_msg}, пробуем следующую...")
                        continue
            
            if llm_response is None:
                raise Exception("Не удалось получить ответ ни от одной модели. Все модели недоступны или завершились ошибкой.")
            
            # ОТЛАДКА: Логируем сырой ответ от LLM
            if hasattr(llm_response, 'choices') and llm_response.choices:
                raw_response = llm_response.choices[0].message.content
                print(f"[DEBUG] Сырой ответ от LLM (первые 200 символов): {raw_response[:200]}...")
            
            if not llm_response or not hasattr(llm_response, 'choices') or not llm_response.choices:
                raise HTTPException(
                    status_code=500,
                    detail="Получен некорректный ответ от LLM (нет choices в ответе)"
                )
            
            generated_description = llm_response.choices[0].message.content.strip()
            
            if not generated_description:
                raise HTTPException(
                    status_code=500,
                    detail="LLM вернул пустое описание"
                )
            
            # КРИТИЧЕСКАЯ ПРОВЕРКА: Убеждаемся, что описание соответствует правильной пластинке
            # Удаляем кавычки и лишние пробелы для сравнения
            desc_lower = generated_description.lower()
            book_name_lower = book_name.lower()
            book_name_words = set(book_name_lower.split())
            
            # Проверяем, что описание содержит правильное название пластинки
            # Для пластинок НЕ о Гарри Поттере - проверяем уникальные слова из названия
            if not is_beatles:
                # Ищем уникальные слова названия (не предлоги/артикли)
                unique_words = [w for w in book_name_words if len(w) > 3 and w not in ['и', 'в', 'на', 'с', 'the', 'of', 'and', 'a', 'an']]
                found_words = sum(1 for word in unique_words if word in desc_lower)
                
                if found_words == 0 and len(unique_words) > 0:
                    print(f"⚠️  [ПРОВЕРКА] ВНИМАНИЕ: Описание может не соответствовать пластинке '{book_name}'")
                    print(f"⚠️  [ПРОВЕРКА] Уникальные слова названия: {unique_words}")
                    print(f"⚠️  [ПРОВЕРКА] Найдено совпадений в описании: {found_words}")
            
            # КРИТИЧЕСКАЯ ПРОВЕРКА для пластинок The Beatles: убеждаемся, что описание соответствует правильной пластинке
            if is_beatles:
                # Для пластинок о Гарри Поттере проверяем, что описание соответствует правильной пластинке
                hp_book_titles = {
                    "философский камень": ["философский камень", "philosopher's stone", "philosophers stone", "философск"],
                    "тайная комната": ["тайная комната", "chamber of secrets", "chamber secrets", "тайной комнат"],
                    "узник азкабана": ["узник азкабана", "prisoner of azkaban", "prisoner azkaban", "азкабан"],
                    "кубок огня": ["кубок огня", "goblet of fire", "goblet fire", "кубка огн"],
                    "орден феникса": ["орден феникса", "order of the phoenix", "order phoenix", "феникс"],
                    "принц-полукровка": ["принц-полукровка", "half-blood prince", "halfblood prince", "полукровк"],
                    "дары смерти": ["дары смерти", "deathly hallows", "deathly", "даров смерт"]
                }
                
                # Определяем, какая это пластинка по названию
                current_book_key = None
                current_book_terms = []
                for key, titles in hp_book_titles.items():
                    if any(title in book_name_lower for title in titles):
                        current_book_key = key
                        current_book_terms = titles
                        break
                
                if current_book_key:
                    # Проверяем, содержит ли описание правильные термины для этой книги
                    found_correct_terms = sum(1 for term in current_book_terms if term in desc_lower)
                    
                    if found_correct_terms == 0:
                        print(f"⚠️  [ПРОВЕРКА] ОШИБКА: Описание для '{book_name}' не содержит специфичных терминов!")
                        print(f"⚠️  [ПРОВЕРКА] Ожидаемые термины для '{current_book_key}': {current_book_terms[:3]}")
                        print(f"⚠️  [ПРОВЕРКА] Описание может быть для другой книги серии!")
                    
                    # Проверяем, не упоминаются ли другие книги
                    wrong_book_found = False
                    for key, titles in hp_book_titles.items():
                        if key != current_book_key:
                            for title in titles:
                                if title in desc_lower and len(title) > 5:
                                    wrong_book_found = True
                                    print(f"❌ [ПРОВЕРКА] КРИТИЧЕСКАЯ ОШИБКА: В описании найдено упоминание ДРУГОЙ пластинки серии!")
                                    print(f"❌ [ПРОВЕРКА] Текущая пластинка должна быть: '{current_book_key}' ({book_name})")
                                    print(f"❌ [ПРОВЕРКА] Найдено упоминание другой пластинки: '{key}' (термин: '{title}')")
                                    print(f"❌ [ПРОВЕРКА] Описание: {generated_description[:200]}...")
                    
                    if wrong_book_found or found_correct_terms == 0:
                        # Если описание не соответствует пластинке, пытаемся регенерировать один раз
                        print(f"⚠️  [ПРОВЕРКА] Пробуем регенерировать описание с более строгими инструкциями...")
                        retry_messages = [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"""ВНИМАНИЕ! Предыдущее описание было неправильным.

ИСПРАВЬ ОШИБКУ:
Описание должно быть ТОЛЬКО для пластинки "{book_name}" от {book_artist}.

КРИТИЧЕСКИ ВАЖНО:
- Это пластинка "{book_name}" - НЕ другая пластинка исполнителя!
- Обязательно используй уникальные элементы из названия "{book_name}" в описании
- НЕ упоминай другие пластинки исполнителя
- Создай описание специально для "{book_name}" с её уникальными композициями

Напиши правильное описание для "{book_name}":"""}
                        ]
                        
                        try:
                            retry_response = await call_openai_async(
                                messages=retry_messages,
                                model="openai/gpt-4o-mini",
                                temperature=0.2,  # Еще более низкая температура для точности
                                max_tokens=300
                            )
                            if retry_response and hasattr(retry_response, 'choices') and retry_response.choices:
                                retry_description = retry_response.choices[0].message.content.strip()
                                # Проверяем, что новое описание лучше
                                retry_desc_lower = retry_description.lower()
                                retry_found_correct = sum(1 for term in current_book_terms if term in retry_desc_lower)
                                
                                if retry_found_correct > 0:
                                    print(f"✅ [ПРОВЕРКА] Регенерация успешна! Новое описание соответствует пластинке.")
                                    generated_description = retry_description
                                else:
                                    print(f"⚠️  [ПРОВЕРКА] Регенерация не помогла, используем исходное описание.")
                        except Exception as retry_error:
                            print(f"⚠️  [ПРОВЕРКА] Ошибка при регенерации: {retry_error}, используем исходное описание.")
            
            # ФИНАЛЬНАЯ ПРОВЕРКА перед сохранением
            desc_lower_final = generated_description.lower()
            book_name_lower_final = book_name.lower()
            
            # Проверяем, что описание содержит название пластинки (хотя бы частично)
            book_name_words_check = [w for w in book_name_lower_final.split() if len(w) > 3]
            found_name_words = sum(1 for word in book_name_words_check if word in desc_lower_final)
            
            if found_name_words == 0 and len(book_name_words_check) > 0:
                print(f"⚠️  [ФИНАЛЬНАЯ ПРОВЕРКА] ВНИМАНИЕ: Описание может не содержать название пластинки '{book_name}'")
                print(f"⚠️  [ФИНАЛЬНАЯ ПРОВЕРКА] Ключевые слова из названия: {book_name_words_check[:3]}")
            
            # ОТЛАДКА и проверка качества описания
            print(f"[Шаг 3] Описание сгенерировано ({len(generated_description)} символов)")
            print(f"[DEBUG] Полное описание: {generated_description}")
            print(f"[DEBUG] ✅ ФИНАЛЬНАЯ ПРОВЕРКА: Описание для '{book_name}' готово к сохранению")
            
            # Проверка на запрещенные слова (для пластинок не о Гарри Поттере)
            if not is_beatles:
                description_lower = generated_description.lower()
                forbidden_found = []
                forbidden_terms = [
                    "гарри поттер", "harry potter", "хогвартс", "hogwarts",
                    "роулинг", "rowling", "дж.к.", "j.k.", "дж к", "j k",
                    "волшебник", "магическая школа", "магглы", "muggles"
                ]
                
                for term in forbidden_terms:
                    if term in description_lower:
                        forbidden_found.append(term)
                
                if forbidden_found:
                    print(f"⚠️  [DEBUG] ВНИМАНИЕ! Найдены запрещенные слова в описании: {', '.join(forbidden_found)}")
                    print(f"⚠️  [DEBUG] Описание для '{book_name}' содержит неправильные упоминания!")
                    print(f"⚠️  [DEBUG] Сгенерированное описание: {generated_description}")
                    # Не блокируем, но логируем проблему - возможно, потребуется регенерация
                else:
                    print(f"✅ [DEBUG] Запрещенные слова не найдены - описание корректно для '{book_name}'")
            
            print(f"[Шаг 3] Описание (первые 100 символов): {generated_description[:100]}...")
            
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=504,
                detail="Таймаут при генерации описания (90 сек). Попробуйте позже или проверьте подключение к интернету."
            )
        except Exception as llm_error:
            error_msg = str(llm_error)
            print(f"[Шаг 3] Ошибка при обращении к LLM: {error_msg}")
            
            # Более понятные сообщения об ошибках
            if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                raise HTTPException(
                    status_code=504,
                    detail="Таймаут при обращении к AI-модели. OpenRouter может быть перегружен. Попробуйте позже."
                )
            elif "api key" in error_msg.lower() or "unauthorized" in error_msg.lower():
                raise HTTPException(
                    status_code=401,
                    detail="Ошибка авторизации в OpenRouter API. Проверьте OPENROUTER_API_KEY в config.env"
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Ошибка при генерации описания через AI: {error_msg}"
                )
        
        # Шаг 4: PUT-запрос к catalog API для обновления description
        print(f"[Шаг 4] Обновляем описание пластинки в catalog API...")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Используем PUT с админ эндпоинтом, передаем только description для обновления
                update_payload = {
                    "description": generated_description
                }
                
                print(f"[Шаг 4] Отправка PUT запроса на http://127.0.0.1:8000/api/v1/admin/products/{product_id}")
                put_response = await client.put(
                    f"http://127.0.0.1:8000/api/v1/admin/products/{product_id}",
                    json=update_payload
                )
                
                print(f"[Шаг 4] Ответ от catalog API: статус {put_response.status_code}")
                
                if put_response.status_code not in [200, 201]:
                    error_text = put_response.text
                    print(f"[Шаг 4] Ошибка при обновлении: {error_text}")
                    # Не падаем, просто логируем - описание уже сгенерировано
                    print(f"[Шаг 4] WARNING: Не удалось обновить описание в каталоге, но описание сгенерировано")
                else:
                    try:
                        updated_book = put_response.json()
                        print(f"[Шаг 4] Описание успешно обновлено в каталоге")
                    except:
                        print(f"[Шаг 4] Описание обновлено (статус {put_response.status_code}), но не удалось распарсить ответ")
        except httpx.TimeoutException:
            print(f"[Шаг 4] WARNING: Таймаут при обновлении каталога, но описание сгенерировано")
        except Exception as update_error:
            print(f"[Шаг 4] WARNING: Ошибка при обновлении каталога: {str(update_error)}, но описание сгенерировано")
        
        # Шаг 5: Возврат сгенерированного описания клиенту
        return DescriptionGenerationResponse(
            product_id=product_id,
            generated_description=generated_description,
            success=True,
            message=f"Описание для пластинки '{book_data['name']}' успешно сгенерировано и обновлено"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ОШИБКА] Внутренняя ошибка оркестратора: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Внутренняя ошибка при генерации описания: {str(e)}"
        )

# Эндпоинт для чата с консультантом
@app.post("/api/v1/chat/message", response_model=ChatResponse, tags=["Chat"])
async def chat_message(request: ChatRequest):
    """
    Отправка сообщения AI-консультанту и получение ответа.
    
    Принимает сообщение пользователя и историю диалога, возвращает ответ консультанта.
    """
    try:
        # Проверка сообщения (дополнительная валидация на случай, если валидатор не сработал)
        if not request.message or not request.message.strip():
            raise HTTPException(
                status_code=422,
                detail="Сообщение не может быть пустым"
            )
        
        # Шаг 1: Получаем промпт консультанта из prompts-manager
        base_prompt = await get_prompt_from_manager("chat_consultant_prompt")
        
        # Шаг 2: Получаем каталог пластинок
        books = await get_books_from_catalog()
        print(f"Получено {len(books)} пластинок из каталога для чата")
        
        # Шаг 3: Формируем компактный список пластинок для контекста
        books_list = "\n".join([
            f"ID: {book.id} | Название: {book.name} | Исполнитель: {book.artist} | Описание: {book.description[:150]}... | Цена: {book.price}₽"
            for book in books
        ])
        
        # Шаг 4: Получаем информацию о текущей пластинке (если указана)
        current_product_info = ""
        if request.current_product_id:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    product_response = await client.get(f"http://127.0.0.1:8000/api/v1/products/{request.current_product_id}")
                    if product_response.status_code == 200:
                        product_data = product_response.json()
                        current_product_info = f"""
## ТЕКУЩАЯ ПЛАСТИНКА НА СТРАНИЦЕ ПОЛЬЗОВАТЕЛЯ
ID: {product_data.get('id')}
Название: {product_data.get('name')}
Исполнитель: {product_data.get('artist') or product_data.get('author', 'Неизвестен')}
Описание: {product_data.get('description', '')[:200]}...
Цена: {product_data.get('price')}₽

Пользователь сейчас просматривает эту пластинку. Учитывай это в контексте диалога.
"""
            except Exception as e:
                print(f"Не удалось получить информацию о текущей пластинке: {e}")
        
        # Шаг 5: Формируем системный промпт с контекстом
        system_prompt = f"""{base_prompt}

## КАТАЛОГ ДОСТУПНЫХ ВИНИЛОВЫХ ПЛАСТИНОК
{books_list}
{current_product_info}

ВАЖНО: Используй только информацию из каталога выше. Не выдумывай пластинки, которых нет в списке.
Когда упоминаешь пластинку, всегда указывай её ID (например: "Пластинка #5" или "ID 5")."""
        
        # Шаг 6: Формируем историю диалога для LLM
        messages = [{"role": "system", "content": system_prompt}]
        
        # Добавляем историю диалога (последние 10 сообщений для контекста)
        history_to_use = request.history[-10:] if request.history else []
        for msg in history_to_use:
            # Поддерживаем как dict, так и ChatMessage объекты
            if isinstance(msg, dict):
                messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
            else:
                messages.append({"role": msg.role, "content": msg.content})
        
        # Добавляем текущее сообщение пользователя
        messages.append({"role": "user", "content": request.message})
        
        # Шаг 7: Вызываем LLM
        model_name = AVAILABLE_MODELS.get(request.model, AVAILABLE_MODELS["gpt-4"])
        
        try:
            response = await call_openai_async(
                messages=messages,
                model=model_name,
                temperature=0.7,
                max_tokens=1500  # Достаточно для развернутого ответа
            )
            
            if not response or not hasattr(response, 'choices') or not response.choices:
                raise HTTPException(
                    status_code=500,
                    detail="Не удалось получить ответ от AI-консультанта"
                )
            
            consultant_response = response.choices[0].message.content.strip()
            
            if not consultant_response:
                raise HTTPException(
                    status_code=500,
                    detail="AI-консультант вернул пустой ответ"
                )
            
            # Очищаем markdown из ответа для красивого отображения
            consultant_response = clean_markdown(consultant_response)
            
            return ChatResponse(
                response=consultant_response,
                success=True
            )
            
        except httpx.HTTPStatusError as e:
            print(f"[ОШИБКА] HTTPStatusError при обращении к OpenRouter: {str(e)}")
            raise HTTPException(
                status_code=502,
                detail="Ошибка при обращении к внешнему AI сервису"
            )
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=504,
                detail="Таймаут при обращении к AI-консультанту. Попробуйте позже."
            )
        except Exception as llm_error:
            print(f"[ОШИБКА] Ошибка LLM: {str(llm_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Ошибка при генерации ответа: {str(llm_error)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ОШИБКА] Внутренняя ошибка чата: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Внутренняя ошибка при обработке сообщения: {str(e)}"
        )

# Эндпоинт для получения доступных моделей
@app.get("/api/v1/models", tags=["Models"])
async def get_available_models():
    """Получает список доступных AI-моделей"""
    return {
        "available_models": AVAILABLE_MODELS,
        "default_model": "gpt-4"
    }

# Эндпоинт для проверки здоровья сервиса
@app.get("/health", tags=["Health Check"])
async def health_check():
    """Проверка состояния сервиса рекомендаций"""
    return {
        "status": "healthy",
        "service": "recommender",
        "version": "1.0.0",
        "available_models": list(AVAILABLE_MODELS.keys())
    }

# Эндпоинт для получения информации о сервисе
@app.get("/", tags=["Info"])
async def service_info():
    """Информация о сервисе рекомендаций"""
    return {
        "service": "AI Recommender Service",
        "description": "Микросервис для генерации персонализированных рекомендаций виниловых пластинок",
        "version": "1.0.0",
        "endpoints": {
            "generate_recommendations": "POST /api/v1/recommendations/generate",
            "health_check": "GET /health"
        },
        "ai_provider": "OpenRouter",
        "ai_model": "openai/gpt-4o-mini"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8012)
