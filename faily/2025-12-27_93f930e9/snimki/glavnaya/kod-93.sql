-- Создание базы данных и расширений
CREATE DATABASE philos_concepts;

\c philos_concepts;

-- Расширение для UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Расширение для криптографии
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Установка временной зоны
SET timezone = 'UTC';

-- Комментарий к базе данных
COMMENT ON DATABASE philos_concepts IS 'База данных платформы философских концепций';