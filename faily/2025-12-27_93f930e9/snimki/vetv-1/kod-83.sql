-- Создание базы данных (если не существует)
-- В Docker PostgreSQL база создается автоматически через POSTGRES_DB
-- Этот файл для создания расширений и базовой структуры

-- Включаем расширение для UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Включаем расширение для криптографии
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Создаем схему для приложения
CREATE SCHEMA IF NOT EXISTS philos;

-- Устанавливаем схему по умолчанию
SET search_path TO philos, public;