# Простой запуск сервисов

## Проблема
Сервисы не запускаются из-за ошибок в скрипте запуска.

## Решение - запуск отдельных сервисов

### Вариант 1: Запуск через отдельные терминалы (рекомендуется)

Откройте **2 отдельных терминала**:

**Терминал 1 - Catalog:**
```bash
python start_catalog_only.py
```

**Терминал 2 - Recommender:**
```bash
python start_recommender_only.py
```

### Вариант 2: Запуск напрямую через uvicorn

**Терминал 1 - Catalog:**
```bash
cd services/catalog
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

**Терминал 2 - Recommender:**
```bash
cd services/recommender
set OPENROUTER_API_KEY=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
python -m uvicorn main:app --host 127.0.0.1 --port 8004 --reload
```

## Проверка работы

После запуска откройте в браузере:
- Catalog API: http://127.0.0.1:8000/docs
- Recommender API: http://127.0.0.1:8004/docs

Или проверьте через скрипт:
```bash
python check_services_status.py
```

## Остановка

В каждом терминале нажмите `Ctrl+C`

