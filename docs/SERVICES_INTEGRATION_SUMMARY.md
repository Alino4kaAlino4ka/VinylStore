# 📋 Сводка интеграции сервисов Prompts Manager и Recommender

## ✅ Согласованность портов

### Prompts Manager
- **Порт:** 8007
- **Health endpoint:** `http://127.0.0.1:8007/health`
- **API base URL:** `http://127.0.0.1:8007/api/v1`

### Recommender
- **Порт:** 8004
- **Health endpoint:** `http://127.0.0.1:8004/health`
- **API base URL:** `http://127.0.0.1:8004/api/v1`
- **Подключение к Prompts Manager:** `http://127.0.0.1:8007/api/v1/prompts/{prompt_id}`

## 🔗 API Endpoints

### Prompts Manager (`services/prompts-manager/main.py`)

1. **GET `/api/v1/prompts`** 
   - Возвращает список всех промптов
   - Response: `List[PromptResponse]`
   - Используется: Admin Panel

2. **GET `/api/v1/prompts/{prompt_id}`**
   - Возвращает конкретный промпт по ID
   - Response: `PromptResponse` с полями: `id`, `name`, `template`
   - Используется: Recommender Service

3. **PUT `/api/v1/prompts/{prompt_id}`**
   - Обновляет содержимое промпта (`template`)
   - Request body: `{"template": "новый текст промпта"}`
   - Используется: Admin Panel

4. **GET `/health`**
   - Health check endpoint
   - Response: `{"status": "ok", "service": "prompts-manager"}`

### Recommender (`services/recommender/main.py`)

1. **POST `/api/v1/recommendations/generate`**
   - Генерирует рекомендации с использованием промпта из prompts-manager
   - Вызывает: `get_prompt_from_manager("recommendation_prompt")`

2. **POST `/api/v1/recommendations/generate-description/{product_id}`**
   - Генерирует описание товара с использованием промпта из prompts-manager
   - Вызывает: `get_prompt_from_manager("description_prompt")`

3. **GET `/health`**
   - Health check endpoint

## 🔄 Интеграция (Headless AI Architecture)

### Функция `get_prompt_from_manager()` в Recommender

```python
async def get_prompt_from_manager(prompt_id: str) -> str:
    """Получает промпт из микросервиса prompts-manager по ID"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"http://127.0.0.1:8007/api/v1/prompts/{prompt_id}")
        response_data = response.json()
        return response_data.get("template", "")
```

### Использование промптов

1. **Рекомендации:**
   - В функции `create_system_prompt()` вызывается `await get_prompt_from_manager("recommendation_prompt")`
   - Базовый промпт дополняется динамическими данными (каталог, предпочтения)

2. **Описания:**
   - В функции `generate_book_description()` вызывается `await get_prompt_from_manager("description_prompt")`
   - Базовый промпт дополняется данными о пластинке

## 🗄️ Дефолтные промпты

При первом запуске `prompts-manager` автоматически создаются:

1. **`recommendation_prompt`**
   - ID: `"recommendation_prompt"`
   - Name: `"Промпт для рекомендаций"`
   - Используется для генерации рекомендаций виниловых пластинок

2. **`description_prompt`**
   - ID: `"description_prompt"`
   - Name: `"Промпт для описаний"`
   - Используется для генерации описаний товаров

## 📊 Модель данных

### PromptResponse (Pydantic)
```python
class PromptResponse(BaseModel):
    id: str      # Строковый ID (например, 'recommendation_prompt')
    name: str    # Человекочитаемое название
    template: str # Текст промпта
```

### Prompt (SQLAlchemy)
```python
class Prompt(Base):
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    template = Column(Text, nullable=False)
```

## ✅ Согласованность полей

- ✅ Все сервисы используют поле `template` (не `content`)
- ✅ Все API используют `prompt_id` (не `prompt_name`)
- ✅ Порты согласованы (8007 для prompts-manager, 8004 для recommender)
- ✅ CORS настроен правильно (`allow_origins=["*"]`)
- ✅ Обработка ошибок реализована

## 🚀 Порядок запуска

В `start_services_final.py`:
1. Catalog (8000)
2. Auth (8001)
3. Orders (8002)
4. Users (8003)
5. **Prompts Manager (8007)** ← Должен быть запущен ДО Recommender
6. **Recommender (8004)** ← Зависит от Catalog и Prompts Manager
7. Cart (8005)

## 🔧 Исправления выполнены

1. ✅ Исправлена сериализация SQLAlchemy → Pydantic (явное преобразование)
2. ✅ Исправлены поля (`template` вместо `content`)
3. ✅ Исправлены API endpoints (`prompt_id` вместо `prompt_name`)
4. ✅ Улучшена обработка ошибок на сервере и клиенте
5. ✅ CORS настроен правильно

## 📝 Статус

✅ **ВСЕ СЕРВИСЫ СОГЛАСОВАНЫ И ГОТОВЫ К РАБОТЕ**

