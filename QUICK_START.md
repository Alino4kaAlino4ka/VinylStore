# 🚀 Быстрый старт Vinyl Shop

## Предварительные требования

- Python 3.9+
- MySQL (для production) или SQLite (для development)
- Все зависимости из `requirements.txt`

## 📦 Установка

### 1. Клонирование и установка зависимостей

```bash
# Установка зависимостей
pip install -r requirements.txt
```

### 2. Настройка конфигурации

```bash
# Скопируйте пример конфигурации
cp config/config.env.example config.env

# Отредактируйте config.env и заполните:
# - OPENROUTER_API_KEY
# - SECRET_KEY (сгенерируйте: python -c "import secrets; print(secrets.token_urlsafe(32))")
# - DATABASE_URL
# - TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID (опционально)
# - SMTP настройки (опционально)
```

### 3. Настройка базы данных

```bash
# Инициализация базы данных
python scripts/utils/db/init_db.py

# Заполнение тестовыми данными (опционально)
python scripts/utils/db/seed_db.py
```

### 4. Запуск сервисов

```bash
# Запуск всех сервисов
python scripts/launch/start_all_services.py

# Или через batch файл (Windows)
scripts/launch/start_all_services.bat
```

### 5. Проверка работы

Откройте в браузере:
- **Главная страница:** `src/index.html`
- **Каталог:** `src/catalog.html`
- **Админ-панель:** `src/admin/admin.html` (login: admin, password: admin123)

**API документация:**
- Catalog: http://127.0.0.1:8000/docs
- Auth: http://127.0.0.1:8001/docs
- Orders: http://127.0.0.1:8010/docs
- Users: http://127.0.0.1:8011/docs
- Recommender: http://127.0.0.1:8012/docs
- Cart: http://127.0.0.1:8005/docs
- Prompts Manager: http://127.0.0.1:8007/docs

### 6. Запуск тестов

```bash
# Полный набор тестов
python tests/test_full_suite.py

# Комплексные тесты
python tests/test_comprehensive.py

# Все тесты промптов
python tests/run_all_tests.py
```

## 🔧 Полезные команды

```bash
# Добавление тестового пользователя
python scripts/utils/admin/add_test_user.py

# Сброс пароля пользователя
python scripts/utils/admin/reset_user_password.py

# Проверка статуса сервисов
python scripts/utils/testing/check_services_status.py

# Создание дефолтных промптов
python scripts/utils/db/create_default_prompts.py
```

## 📚 Дополнительная документация

- [README.md](README.md) - полная документация
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - структура проекта
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - чеклист деплоя
- [SECURITY.md](SECURITY.md) - безопасность
- [docs/](docs/) - дополнительная документация

## ⚠️ Важные замечания

1. **Для production:** Измените SECRET_KEY и ADMIN_PASSWORD в config.env
2. **Для production:** Установите ENVIRONMENT=production
3. **Для production:** Настройте CORS для конкретных доменов
4. **config.env не должен попадать в Git!** (уже в .gitignore)

## 🆘 Проблемы?

- Проверьте логи в `logs/` директории
- Убедитесь, что все сервисы запущены
- Проверьте health endpoints: http://127.0.0.1:8000/health
- См. [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) для диагностики

