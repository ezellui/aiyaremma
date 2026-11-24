#!/bin/bash

# MongoDB Backup Script
# Создает резервную копию всех коллекций MongoDB для сервиса философских концепций

set -e

# Конфигурация
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="${BACKUP_DIR:-/backup/mongodb}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="philosophy_concepts_mongodb_${TIMESTAMP}"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

# MongoDB параметры подключения
MONGO_HOST="${MONGO_HOST:-localhost}"
MONGO_PORT="${MONGO_PORT:-27017}"
MONGO_DATABASE="${MONGO_DATABASE:-philosophy_concepts}"
MONGO_USERNAME="${MONGO_USERNAME:-}"
MONGO_PASSWORD="${MONGO_PASSWORD:-}"
MONGO_AUTH_DB="${MONGO_AUTH_DB:-admin}"

# Параметры резервного копирования
COMPRESSION="${COMPRESSION:-gzip}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
PARALLEL_COLLECTIONS="${PARALLEL_COLLECTIONS:-4}"
OPLOG="${OPLOG:-false}"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Проверка наличия mongodump
check_mongodump() {
    if ! command -v mongodump &> /dev/null; then
        error "mongodump не найден. Установите MongoDB Database Tools."
        exit 1
    fi
}

# Создание директории для резервных копий
create_backup_directory() {
    if [ ! -d "$BACKUP_DIR" ]; then
        log "Создание директории для резервных копий: $BACKUP_DIR"
        mkdir -p "$BACKUP_DIR"
    fi
}

# Построение строки подключения
build_connection_string() {
    local conn_string=""
    
    if [ -n "$MONGO_USERNAME" ] && [ -n "$MONGO_PASSWORD" ]; then
        conn_string="mongodb://${MONGO_USERNAME}:${MONGO_PASSWORD}@${MONGO_HOST}:${MONGO_PORT}/${MONGO_DATABASE}?authSource=${MONGO_AUTH_DB}"
    else
        conn_string="mongodb://${MONGO_HOST}:${MONGO_PORT}/${MONGO_DATABASE}"
    fi
    
    echo "$conn_string"
}

# Выполнение резервного копирования
perform_backup() {
    log "Начало резервного копирования MongoDB..."
    log "База данных: $MONGO_DATABASE"
    log "Путь резервной копии: $BACKUP_PATH"
    
    local mongodump_args=(
        "--db=$MONGO_DATABASE"
        "--out=$BACKUP_PATH"
        "--numParallelCollections=$PARALLEL_COLLECTIONS"
    )
    
    # Добавление аутентификации если необходимо
    if [ -n "$MONGO_USERNAME" ] && [ -n "$MONGO_PASSWORD" ]; then
        mongodump_args+=(
            "--username=$MONGO_USERNAME"
            "--password=$MONGO_PASSWORD"
            "--authenticationDatabase=$MONGO_AUTH_DB"
        )
    fi
    
    # Добавление хоста и порта
    mongodump_args+=("--host=${MONGO_HOST}:${MONGO_PORT}")
    
    # Добавление сжатия
    if [ "$COMPRESSION" = "gzip" ]; then
        mongodump_args+=("--gzip")
    fi
    
    # Добавление oplog если требуется
    if [ "$OPLOG" = "true" ]; then
        mongodump_args+=("--oplog")
    fi
    
    # Выполнение mongodump
    if mongodump "${mongodump_args[@]}"; then
        log "Резервное копирование успешно завершено"
    else
        error "Ошибка при выполнении резервного копирования"
        exit 1
    fi
}

# Создание архива резервной копии
create_archive() {
    log "Создание архива резервной копии..."
    
    cd "$BACKUP_DIR"
    local archive_name="${BACKUP_NAME}.tar.gz"
    
    if tar -czf "$archive_name" "$BACKUP_NAME"; then
        log "Архив создан: $archive_name"
        
        # Удаление директории после архивации
        rm -rf "$BACKUP_NAME"
        
        # Вычисление размера архива
        local size=$(ls -lh "$archive_name" | awk '{print $5}')
        log "Размер архива: $size"
    else
        error "Ошибка при создании архива"
        exit 1
    fi
}

# Проверка целостности резервной копии
verify_backup() {
    log "Проверка целостности резервной копии..."
    
    local archive_name="${BACKUP_NAME}.tar.gz"
    cd "$BACKUP_DIR"
    
    if tar -tzf "$archive_name" > /dev/null 2>&1; then
        log "Проверка целостности пройдена успешно"
    else
        error "Архив резервной копии поврежден"
        exit 1
    fi
}

# Создание метаданных резервной копии
create_metadata() {
    log "Создание метаданных резервной копии..."
    
    local metadata_file="${BACKUP_DIR}/${BACKUP_NAME}_metadata.json"
    
    cat > "$metadata_file" << EOF
{
    "backup_name": "${BACKUP_NAME}",
    "timestamp": "${TIMESTAMP}",
    "database": "${MONGO_DATABASE}",
    "host": "${MONGO_HOST}",
    "port": "${MONGO_PORT}",
    "mongodb_version": "$(mongodump --version | head -n1)",
    "compression": "${COMPRESSION}",
    "collections": [
        "theses",
        "categoryDescriptions",
        "relationshipDescriptions",
        "conceptAnalyses",
        "dialogues",
        "historicalContexts",
        "practicalApplications",
        "conceptEvolutions",
        "generatedElements"
    ],
    "backup_size": "$(ls -lh ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz | awk '{print $5}')",
    "backup_path": "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
}
EOF
    
    log "Метаданные сохранены в: $metadata_file"
}

# Очистка старых резервных копий
cleanup_old_backups() {
    log "Очистка резервных копий старше $RETENTION_DAYS дней..."
    
    local count=0
    
    # Поиск и удаление старых архивов
    while IFS= read -r file; do
        if [ -f "$file" ]; then
            rm -f "$file"
            ((count++))
            log "Удален: $(basename "$file")"
        fi
    done < <(find "$BACKUP_DIR" -name "philosophy_concepts_mongodb_*.tar.gz" -type f -mtime +$RETENTION_DAYS)
    
    # Удаление старых метаданных
    while IFS= read -r file; do
        if [ -f "$file" ]; then
            rm -f "$file"
            ((count++))
        fi
    done < <(find "$BACKUP_DIR" -name "philosophy_concepts_mongodb_*_metadata.json" -type f -mtime +$RETENTION_DAYS)
    
    if [ $count -gt 0 ]; then
        log "Удалено старых файлов: $count"
    else
        log "Старые резервные копии не найдены"
    fi
}

# Отправка уведомления (опционально)
send_notification() {
    if [ -n "$NOTIFICATION_WEBHOOK" ]; then
        local status=$1
        local message=$2
        
        curl -s -X POST "$NOTIFICATION_WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "{
                \"text\": \"MongoDB Backup ${status}\",
                \"attachments\": [{
                    \"color\": \"$([ "$status" = "SUCCESS" ] && echo "good" || echo "danger")\",
                    \"fields\": [{
                        \"title\": \"Database\",
                        \"value\": \"${MONGO_DATABASE}\",
                        \"short\": true
                    }, {
                        \"title\": \"Backup Name\",
                        \"value\": \"${BACKUP_NAME}\",
                        \"short\": true
                    }, {
                        \"title\": \"Message\",
                        \"value\": \"${message}\",
                        \"short\": false
                    }]
                }]
            }" > /dev/null
    fi
}

# Основная функция
main() {
    log "=== Начало процесса резервного копирования MongoDB ==="
    
    # Проверки
    check_mongodump
    create_backup_directory
    
    # Выполнение резервного копирования
    if perform_backup; then
        create_archive
        verify_backup
        create_metadata
        cleanup_old_backups
        
        log "=== Резервное копирование завершено успешно ==="
        send_notification "SUCCESS" "Backup completed successfully: ${BACKUP_NAME}.tar.gz"
        
        # Вывод информации о резервной копии
        echo
        log "Информация о резервной копии:"
        log "  Имя: ${BACKUP_NAME}.tar.gz"
        log "  Путь: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
        log "  Размер: $(ls -lh ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz | awk '{print $5}')"
        
        exit 0
    else
        error "Процесс резервного копирования завершился с ошибкой"
        send_notification "FAILURE" "Backup failed for database: ${MONGO_DATABASE}"
        exit 1
    fi
}

# Обработка прерывания
trap 'error "Процесс прерван"; exit 1' INT TERM

# Запуск основной функции
main "$@"
