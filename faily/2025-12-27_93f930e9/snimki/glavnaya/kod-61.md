# Database Migrations

Эта папка содержит SQL миграции для PostgreSQL.

## Именование файлов

Формат: `XXX_description.sql`

Где:
- XXX - порядковый номер (001, 002, и т.д.)
- description - краткое описание миграции

## Примеры

- 001_create_users_table.sql
- 002_add_api_keys.sql
- 003_create_indexes.sql

## Выполнение миграций

Миграции выполняются автоматически при запуске контейнера PostgreSQL через docker-compose.