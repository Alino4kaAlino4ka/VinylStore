-- Скрипт для создания базы данных audio_store в MySQL
-- Выполните этот скрипт от имени пользователя root или другого пользователя с правами на создание баз данных

-- Создаем новую базу данных для нашего проекта
CREATE DATABASE audio_store CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Создаем специального пользователя для нашего приложения
CREATE USER 'user'@'localhost' IDENTIFIED BY '1234';

-- Выдаем этому пользователю полные права на управление нашей новой базой данных
GRANT ALL PRIVILEGES ON audio_store.* TO 'user'@'localhost';

-- Обновляем привилегии, чтобы изменения вступили в силу
FLUSH PRIVILEGES;

