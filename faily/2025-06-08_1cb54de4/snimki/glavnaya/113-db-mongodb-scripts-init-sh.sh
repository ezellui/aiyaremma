#!/bin/bash

# MongoDB Initialization Script
# Инициализирует базу данных MongoDB для сервиса философских концепций

set -e

# Конфигурация
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIGRATIONS_DIR="${SCRIPT_DIR}/../migrations"
SCHEMAS_DIR="${SCRIPT_DIR}/../schemas"
SEEDS_DIR="${SCRIPT_DIR}/../seeds"

# MongoDB параметры подключения
MONGO_HOST="${MONGO_HOST:-localhost}"
MONGO_PORT="${MONGO_PORT:-27017}"
MONGO_DATABASE="${MONGO_DATABASE:-philosophy_concepts}"
MONGO_USERNAME="${MONGO_USERNAME:-}"
MONGO_PASSWORD="${MONGO_PASSWORD:-}"
MONGO_AUTH_DB="${MONGO_AUTH_DB:-admin}"
MONGO_ROOT_USERNAME="${MONGO_ROOT_USERNAME:-root}"
MONGO_ROOT_PASSWORD="${MONGO_ROOT_PASSWORD:-}"

# Параметры инициализации
CREATE_USER="${CREATE_USER:-true}"
CREATE_DATABASE="${CREATE_DATABASE:-true}"
RUN_MIGRATIONS="${RUN_MIGRATIONS:-true}"
APPLY_SCHEMAS="${APPLY_SCHEMAS:-true}"
LOAD_SEEDS="${LOAD_SEEDS:-false}"
FORCE_REINIT="${FORCE_REINIT:-false}"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO:${NC} $1"
}

# Проверка наличия mongosh
check_mongosh() {
    if ! command -v mongosh &> /dev/null; then
        error "mongosh не найден. Установите MongoDB Shell."
        exit 1
    fi
}

# Проверка подключения к MongoDB
check_connection() {
    log "Проверка подключения к MongoDB..."
    
    local mongo_args=("--host=${MONGO_HOST}:${MONGO_PORT}")
    
    if [ -n "$MONGO_ROOT_USERNAME" ] && [ -n "$MONGO_ROOT_PASSWORD" ]; then
        mongo_args+=(
            "--username=$MONGO_ROOT_USERNAME"
            "--password=$MONGO_ROOT_PASSWORD"
            "--authenticationDatabase=admin"
        )
    fi
    
    mongo_args+=("--eval=db.version()")
    
    if mongosh "${mongo_args[@]}" > /dev/null 2>&1; then
        log "Подключение к MongoDB установлено"
        return 0
    else
        error "Не удалось подключиться к MongoDB"
        return 1
    fi
}

# Ожидание готовности MongoDB
wait_for_mongodb() {
    log "Ожидание готовности MongoDB..."
    
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if check_connection 2>/dev/null; then
            log "MongoDB готова к работе"
            return 0
        fi
        
        attempt=$((attempt + 1))
        info "Попытка $attempt из $max_attempts..."
        sleep 2
    done
    
    error "MongoDB не готова после $max_attempts попыток"
    exit 1
}

# Создание пользователя базы данных
create_database_user() {
    if [ "$CREATE_USER" != "true" ] || [ -z "$MONGO_USERNAME" ] || [ -z "$MONGO_PASSWORD" ]; then
        return 0
    fi
    
    log "Создание пользователя базы данных..."
    
    local user_script="
    // Переключение на базу данных
    use ${MONGO_DATABASE};
    
    // Проверка существования пользователя
    const userExists = db.getUsers().users.some(user => user.user === '${MONGO_USERNAME}');
    
    if (!userExists) {
        db.createUser({
            user: '${MONGO_USERNAME}',
            pwd: '${MONGO_PASSWORD}',
            roles: [
                { role: 'readWrite', db: '${MONGO_DATABASE}' },
                { role: 'dbAdmin', db: '${MONGO_DATABASE}' }
            ]
        });
        print('Пользователь ${MONGO_USERNAME} создан');
    } else {
        print('Пользователь ${MONGO_USERNAME} уже существует');
    }
    "
    
    local mongo_args=("--host=${MONGO_HOST}:${MONGO_PORT}")
    
    if [ -n "$MONGO_ROOT_USERNAME" ] && [ -n "$MONGO_ROOT_PASSWORD" ]; then
        mongo_args+=(
            "--username=$MONGO_ROOT_USERNAME"
            "--password=$MONGO_ROOT_PASSWORD"
            "--authenticationDatabase=admin"
        )
    fi
    
    mongo_args+=("--eval=$user_script")
    
    if mongosh "${mongo_args[@]}"; then
        log "Пользователь базы данных настроен"
    else
        error "Ошибка при создании пользователя"
        exit 1
    fi
}

# Проверка существования базы данных
check_database_exists() {
    log "Проверка существования базы данных..."
    
    local check_script="
    const dbs = db.adminCommand('listDatabases').databases;
    const exists = dbs.some(db => db.name === '${MONGO_DATABASE}');
    print(exists ? 'exists' : 'not_exists');
    "
    
    local mongo_args=("--host=${MONGO_HOST}:${MONGO_PORT}")
    
    if [ -n "$MONGO_USERNAME" ] && [ -n "$MONGO_PASSWORD" ]; then
        mongo_args+=(
            "--username=$MONGO_USERNAME"
            "--password=$MONGO_PASSWORD"
            "--authenticationDatabase=$MONGO_AUTH_DB"
        )
    elif [ -n "$MONGO_ROOT_USERNAME" ] && [ -n "$MONGO_ROOT_PASSWORD" ]; then
        mongo_args+=(
            "--username=$MONGO_ROOT_USERNAME"
            "--password=$MONGO_ROOT_PASSWORD"
            "--authenticationDatabase=admin"
        )
    fi
    
    mongo_args+=("--quiet" "--eval=$check_script")
    
    local result=$(mongosh "${mongo_args[@]}" 2>/dev/null | tail -n1)
    
    if [ "$result" = "exists" ]; then
        return 0
    else
        return 1
    fi
}

# Выполнение миграций
run_migrations() {
    if [ "$RUN_MIGRATIONS" != "true" ]; then
        return 0
    fi
    
    log "Выполнение миграций..."
    
    local mongo_args=("--host=${MONGO_HOST}:${MONGO_PORT}")
    
    if [ -n "$MONGO_USERNAME" ] && [ -n "$MONGO_PASSWORD" ]; then
        mongo_args+=(
            "--username=$MONGO_USERNAME"
            "--password=$MONGO_PASSWORD"
            "--authenticationDatabase=$MONGO_AUTH_DB"
        )
    fi
    
    mongo_args+=("$MONGO_DATABASE")
    
    # Выполнение миграций в порядке их номеров
    for migration in $(ls -1 "$MIGRATIONS_DIR"/*.js 2>/dev/null | sort); do
        if [ -f "$migration" ]; then
            local migration_name=$(basename "$migration")
            log "Выполнение миграции: $migration_name"
            
            if mongosh "${mongo_args[@]}" "$migration"; then
                log "Миграция $migration_name выполнена успешно"
            else
                error "Ошибка при выполнении миграции $migration_name"
                exit 1
            fi
        fi
    done
    
    log "Все миграции выполнены"
}

# Применение схем валидации
apply_validation_schemas() {
    if [ "$APPLY_SCHEMAS" != "true" ]; then
        return 0
    fi
    
    log "Применение схем валидации..."
    
    # Скрипт для применения схем
    local apply_schemas_script="${SCRIPT_DIR}/apply_schemas.js"
    
    cat > "$apply_schemas_script" << 'EOF'
// Применение схем валидации для коллекций MongoDB

const fs = require('fs');
const path = require('path');

// Путь к директории со схемами
const schemasDir = process.env.SCHEMAS_DIR || path.join(__dirname, '..', 'schemas');

// Загрузка и применение схем
const schemas = [
    'theses',
    'categoryDescriptions',
    'relationshipDescriptions',
    'conceptAnalyses',
    'dialogues',
    'historicalContexts',
    'practicalApplications',
    'conceptEvolutions',
    'generatedElements'
];

schemas.forEach(schemaName => {
    const schemaPath = path.join(schemasDir, `${schemaName}.js`);
    
    if (fs.existsSync(schemaPath)) {
        print(`Применение схемы для коллекции: ${schemaName}`);
        
        try {
            const schema = require(schemaPath);
            
            // Удаление существующей коллекции если требуется пересоздание
            if (process.env.FORCE_REINIT === 'true') {
                db[schemaName].drop();
            }
            
            // Создание коллекции с валидацией
            db.createCollection(schemaName, schema);
            
            // Создание индексов
            if (schema.indexes && Array.isArray(schema.indexes)) {
                schema.indexes.forEach(index => {
                    db[schemaName].createIndex(index.key, {
                        name: index.name,
                        unique: index.unique || false,
                        sparse: index.sparse || false,
                        background: true
                    });
                });
            }
            
            print(`Схема для ${schemaName} применена успешно`);
        } catch (e) {
            print(`Ошибка при применении схемы ${schemaName}: ${e.message}`);
        }
    }
});
EOF
    
    # Применение схем через Node.js скрипт
    local node_script="
    const schemas = {
        theses: require('${SCHEMAS_DIR}/theses.js'),
        categoryDescriptions: require('${SCHEMAS_DIR}/categoryDescriptions.js'),
        relationshipDescriptions: require('${SCHEMAS_DIR}/relationshipDescriptions.js'),
        conceptAnalyses: require('${SCHEMAS_DIR}/conceptAnalyses.js'),
        dialogues: require('${SCHEMAS_DIR}/dialogues.js'),
        historicalContexts: require('${SCHEMAS_DIR}/historicalContexts.js'),
        practicalApplications: require('${SCHEMAS_DIR}/practicalApplications.js'),
        conceptEvolutions: require('${SCHEMAS_DIR}/conceptEvolutions.js'),
        generatedElements: require('${SCHEMAS_DIR}/generatedElements.js')
    };
    
    Object.entries(schemas).forEach(([collectionName, schema]) => {
        try {
            // Применение валидатора
            db.runCommand({
                collMod: collectionName,
                validator: schema.validator
            });
            print(\`Валидация для \${collectionName} применена\`);
        } catch (e) {
            // Если коллекция не существует, создаем её
            db.createCollection(collectionName, schema);
            print(\`Коллекция \${collectionName} создана с валидацией\`);
        }
    });
    "
    
    local mongo_args=("--host=${MONGO_HOST}:${MONGO_PORT}")
    
    if [ -n "$MONGO_USERNAME" ] && [ -n "$MONGO_PASSWORD" ]; then
        mongo_args+=(
            "--username=$MONGO_USERNAME"
            "--password=$MONGO_PASSWORD"
            "--authenticationDatabase=$MONGO_AUTH_DB"
        )
    fi
    
    mongo_args+=("$MONGO_DATABASE" "--eval=$node_script")
    
    if mongosh "${mongo_args[@]}"; then
        log "Схемы валидации применены"
    else
        warning "Не удалось применить некоторые схемы валидации"
    fi
    
    # Удаление временного скрипта
    rm -f "$apply_schemas_script"
}

# Загрузка начальных данных
load_seed_data() {
    if [ "$LOAD_SEEDS" != "true" ]; then
        return 0
    fi
    
    log "Загрузка начальных данных..."
    
    local mongo_args=("--host=${MONGO_HOST}:${MONGO_PORT}")
    
    if [ -n "$MONGO_USERNAME" ] && [ -n "$MONGO_PASSWORD" ]; then
        mongo_args+=(
            "--username=$MONGO_USERNAME"
            "--password=$MONGO_PASSWORD"
            "--authenticationDatabase=$MONGO_AUTH_DB"
        )
    fi
    
    mongo_args+=("$MONGO_DATABASE")
    
    # Загрузка seed-файлов
    for seed in $(ls -1 "$SEEDS_DIR"/*.js 2>/dev/null | sort); do
        if [ -f "$seed" ]; then
            local seed_name=$(basename "$seed")
            log "Загрузка seed-данных: $seed_name"
            
            if mongosh "${mongo_args[@]}" "$seed"; then
                log "Seed-данные $seed_name загружены успешно"
            else
                warning "Ошибка при загрузке seed-данных $seed_name"
            fi
        fi
    done
}

# Проверка инициализации
verify_initialization() {
    log "Проверка инициализации базы данных..."
    
    local verify_script="
    const collections = [
        'theses',
        'categoryDescriptions',
        'relationshipDescriptions',
        'conceptAnalyses',
        'dialogues',
        'historicalContexts',
        'practicalApplications',
        'conceptEvolutions',
        'generatedElements'
    ];
    
    print('\\nСтатус коллекций:');
    let allExists = true;
    
    collections.forEach(col => {
        const exists = db.getCollectionNames().includes(col);
        const count = exists ? db[col].countDocuments() : 0;
        print(\`  \${col}: \${exists ? 'существует' : 'отсутствует'} (\${count} документов)\`);
        if (!exists) allExists = false;
    });
    
    print(allExists ? '\\nВсе коллекции созданы успешно' : '\\nНекоторые коллекции отсутствуют');
    "
    
    local mongo_args=("--host=${MONGO_HOST}:${MONGO_PORT}")
    
    if [ -n "$MONGO_USERNAME" ] && [ -n "$MONGO_PASSWORD" ]; then
        mongo_args+=(
            "--username=$MONGO_USERNAME"
            "--password=$MONGO_PASSWORD"
            "--authenticationDatabase=$MONGO_AUTH_DB"
        )
    fi
    
    mongo_args+=("$MONGO_DATABASE" "--eval=$verify_script")
    
    mongosh "${mongo_args[@]}"
}

# Основная функция
main() {
    log "=== Начало инициализации MongoDB ==="
    
    # Проверки
    check_mongosh
    wait_for_mongodb
    
    # Проверка существования базы данных
    if check_database_exists && [ "$FORCE_REINIT" != "true" ]; then
        warning "База данных $MONGO_DATABASE уже существует"
        read -p "Продолжить инициализацию? (y/n): " continue_init
        if [[ ! "$continue_init" =~ ^[Yy]$ ]]; then
            log "Инициализация отменена"
            exit 0
        fi
    fi
    
    # Создание пользователя
    create_database_user
    
    # Выполнение миграций
    run_migrations
    
    # Применение схем
    apply_validation_schemas
    
    # Загрузка начальных данных
    load_seed_data
    
    # Проверка
    verify_initialization
    
    log "=== Инициализация MongoDB завершена успешно ==="
    
    info "База данных: $MONGO_DATABASE"
    info "Сервер: $MONGO_HOST:$MONGO_PORT"
    if [ -n "$MONGO_USERNAME" ]; then
        info "Пользователь: $MONGO_USERNAME"
    fi
}

# Обработка прерывания
trap 'error "Процесс прерван"; exit 1' INT TERM

# Запуск основной функции
main "$@"
