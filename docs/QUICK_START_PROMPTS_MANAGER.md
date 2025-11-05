# ⚡ Быстрый старт Prompts Manager

## 🚀 За 30 секунд

```bash
# 1. Запустить все сервисы (prompts-manager включен)
python start_services_final.py

# 2. Проверить работу
curl http://127.0.0.1:8007/health

# 3. Посмотреть все промпты
curl http://127.0.0.1:8007/api/v1/prompts

# 4. Получить промпт рекомендаций
curl http://127.0.0.1:8007/api/v1/prompts/recommendation_prompt
```

## 📋 Основные команды

### Запуск
```bash
# Все сервисы
python start_services_final.py

# Только prompts-manager
python start_prompts_manager.bat
# или
cd services/prompts-manager
python -c "from main import app; import uvicorn; uvicorn.run(app, host='127.0.0.1', port=8007)"
```

### Тестирование
```bash
# Быстрый тест
python test_prompts_manager_simple.py

# Полные тесты
pytest tests/test_prompts_manager.py -v
```

### API запросы
```bash
# Health check
curl http://127.0.0.1:8007/health

# Все промпты
curl http://127.0.0.1:8007/api/v1/prompts

# Конкретный промпт
curl http://127.0.0.1:8007/api/v1/prompts/recommendation_prompt

# Обновить промпт
curl -X PUT http://127.0.0.1:8007/api/v1/prompts/recommendation_prompt \
  -H "Content-Type: application/json" \
  -d '{"content": "Новый промпт"}'
```

## 📚 Документация

- **Полная документация:** `PROMPTS_MANAGER_FULL_DOCUMENTATION.md`
- **Отчет о тестировании:** `PROMPTS_MANAGER_TEST_REPORT.md`
- **Отчет о реализации:** `HEADLESS_AI_IMPLEMENTATION_REPORT.md`

## ✅ Статус

- ✅ Сервис работает
- ✅ API протестирован
- ✅ Интегрирован в систему запуска
- ✅ Документация создана

**Порт:** 8007  
**URL:** http://127.0.0.1:8007

