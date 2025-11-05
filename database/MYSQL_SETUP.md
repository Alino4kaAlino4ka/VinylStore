# Настройка MySQL для проекта

## Предварительные требования

1. MySQL установлен на вашем компьютере (диск C:)
2. MySQL сервис запущен
3. Установлен Python пакет `pymysql` (уже есть в requirements.txt)

## Шаги настройки

### 1. Создание базы данных

Выполните SQL скрипт для создания базы данных. Вы можете сделать это одним из способов:

#### Способ 1: Через MySQL командную строку
```bash
mysql -u root -p < database/create_mysql_database.sql
```

#### Способ 2: Через MySQL Workbench или другой клиент
- Откройте файл `database/create_mysql_database.sql`
- Выполните скрипт в MySQL клиенте

#### Способ 3: Вручную через MySQL командную строку
```sql
-- Создаем новую базу данных для нашего проекта
CREATE DATABASE audio_store CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Создаем специального пользователя для нашего приложения
CREATE USER 'user'@'localhost' IDENTIFIED BY '1234';

-- Выдаем этому пользователю полные права на управление нашей новой базой данных
GRANT ALL PRIVILEGES ON audio_store.* TO 'user'@'localhost';

-- Обновляем привилегии, чтобы изменения вступили в силу
FLUSH PRIVILEGES;
```

### 2. Проверка подключения

Убедитесь, что в файле `config.env` указана правильная строка подключения:
```
DATABASE_URL=mysql+pymysql://user:1234@localhost/audio_store
```

### 3. Инициализация таблиц

После создания базы данных, инициализируйте таблицы:
```bash
python init_db.py
```

Это создаст все необходимые таблицы в базе данных `audio_store`.

## Проверка подключения

Чтобы проверить, что подключение работает, можете запустить простой тест:

```python
from database.connection import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print("Подключение к MySQL успешно!")
```

## Устранение проблем

### Ошибка: Access denied for user 'user'@'localhost'
- Убедитесь, что пользователь создан и имеет правильный пароль
- Проверьте права доступа: `SHOW GRANTS FOR 'user'@'localhost';`

### Ошибка: Unknown database 'audio_store'
- Убедитесь, что база данных создана: `SHOW DATABASES;`
- Если её нет, выполните SQL скрипт из шага 1

### Ошибка: Can't connect to MySQL server
- Проверьте, что MySQL сервис запущен
- Проверьте, что MySQL слушает на порту 3306 (по умолчанию)
- Если MySQL использует другой порт, укажите его в строке подключения: `mysql+pymysql://user:1234@localhost:3307/audio_store`

