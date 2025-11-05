# Диаграмма микросервисной архитектуры проекта

## Визуальная схема архитектуры

```mermaid
graph TB
    Browser[Клиент<br/>Браузер]
    
    Catalog[Catalog Service<br/>Порт: 8000]
    Auth[Auth Service<br/>Порт: 8001]
    Cart[Cart Service<br/>Порт: 8005]
    Orders[Orders Service<br/>Порт: 8010]
    Users[Users Service<br/>Порт: 8011]
    Recommender[Recommender Service<br/>Порт: 8012]
    
    MySQL[(MySQL<br/>База Данных)]
    
    Browser -->|HTTP запросы| Catalog
    Browser -->|HTTP запросы| Auth
    Browser -->|HTTP запросы| Cart
    Browser -->|HTTP запросы| Orders
    Browser -->|HTTP запросы| Users
    Browser -->|HTTP запросы| Recommender
    
    Catalog -->|Подключение| MySQL
    Auth -->|Подключение| MySQL
    Cart -->|Подключение| MySQL
    Orders -->|Подключение| MySQL
    Users -->|Подключение| MySQL
    Recommender -->|Подключение| MySQL
    
    Recommender -->|GET /api/v1/products<br/>Получение списка книг| Catalog
    
    style Browser fill:#e1f5ff
    style MySQL fill:#fff4e1
    style Catalog fill:#e8f5e9
    style Auth fill:#e8f5e9
    style Cart fill:#e8f5e9
    style Orders fill:#e8f5e9
    style Users fill:#e8f5e9
    style Recommender fill:#e8f5e9
```

## Описание архитектуры

### Компоненты системы

1. **Клиент (Браузер)** - точка входа для всех пользовательских запросов
2. **Catalog Service** (порт 8000) - управление каталогом виниловых пластинок
3. **Auth Service** (порт 8001) - аутентификация и авторизация пользователей
4. **Cart Service** (порт 8005) - управление корзиной покупок
5. **Orders Service** (порт 8010) - обработка заказов
6. **Users Service** (порт 8011) - управление пользователями
7. **Recommender Service** (порт 8012) - AI-рекомендации и чат-консультант
8. **MySQL Database** - единая база данных для всех сервисов

### Потоки данных

1. **Клиент → Сервисы**: Все сервисы принимают HTTP запросы от клиента
2. **Сервисы → База Данных**: Все сервисы используют единую MySQL базу данных для хранения данных
3. **Recommender → Catalog**: Сервис рекомендаций обращается к каталогу для получения списка пластинок через эндпоинт `GET /api/v1/products`

### Особенности

- Все сервисы работают независимо друг от друга
- Единая база данных MySQL обеспечивает консистентность данных
- Recommender Service использует Catalog Service для получения актуального списка товаров при генерации рекомендаций
