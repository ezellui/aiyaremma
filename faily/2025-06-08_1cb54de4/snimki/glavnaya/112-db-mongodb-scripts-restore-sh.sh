#!/bin/bash

# MongoDB Restore Script
# Восстанавливает данные MongoDB из резервной копии для сервиса философских концепций

set -e

# Конфигурация
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="${BACKUP_DIR:-/backup/mongodb}"
RESTORE_TEMP_DIR="/tmp/mongodb_restore_$$"

# MongoDB параметры подключения
MONGO_HOST="${MONGO_HOST:-localhost}"
MONGO_PORT="${MONGO_PORT:-27017}"
MONGO_DATABASE="${MONGO_DATABASE:-philosophy_concepts}"
MONGO_USERNAME="${MONGO_USERNAME:-}"
MONGO_PASSWORD="${MONGO_PASSWORD:-}"
MONGO_AUTH_DB="${MONGO_AUTH_DB:-admin}"

# Параметры восстановления
DROP_EXISTING="${DROP_EXISTING:-false}"
PRESERVE_UUID="${PRESERVE_UUID:-true}"
NO_OPTIONS_RESTORE="${NO_OPTIONS_RESTORE:-false}"
PARALLEL_COLLECTIONS="${PARALLEL_COLLECTIONS:-4}"

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

# Функция для очистки временных файлов
cleanup() {
    if [ -d "$RESTORE_TEMP_DIR" ]; then
        log "Очистка временных файлов..."
        rm -rf "$RESTORE_TEMP_DIR"
    fi
}

# Установка обработчика для очистки при выходе
trap cleanup EXIT

# Проверка наличия mongorestore
check_mongorestore() {
    if ! command -v mongorestore &> /dev/null; then
        error "mongorestore не найден. Установите MongoDB Database Tools."
        exit 1
    fi
}

# Список доступных резервных копий
list_backups() {
    log "Доступные резервные копии:"
    echo
    
    local backups=($(find "$BACKUP_DIR" -name "philosophy_concepts_mongodb_*.tar.gz" -type f | sort -r))
    
    if [ ${#backups[@]} -eq 0 ]; then
        warning "Резервные копии не найдены в $BACKUP_DIR"
        exit 1
    fi
    
    for i in "${!backups[@]}"; do
        local backup_file=$(basename "${backups[$i]}")
        local backup_date=$(echo "$backup_file" | grep -oP '\d{8}_\d{6}')
        local backup_size=$(ls -lh "${backups[$i]}" | awk '{print $5}')
        
        # Попытка прочитать метаданные
        local metadata_file="${backups[$i]%.tar.gz}_metadata.json"
        local db_info=""
        if [ -f "$metadata_file" ]; then
            db_info=$(jq -r '.database // "unknown"' "$metadata_file" 2>/dev/null || echo "unknown")
        fi
        
        printf "%2d) %s [%s] - База: %s\n" $((i+1)) "$backup_file" "$backup_size" "$db_info"
    done
    
    echo
}

# Выбор резервной копии
select_backup() {
    local backup_file="$1"
    
    if [ -z "$backup_file" ]; then
        list_backups
        
        read -p "Выберите номер резервной копии для восстановления (или путь к файлу): " selection
        
        if [[ "$selection" =~ ^[0-9]+$ ]]; then
            local backups=($(find "$BACKUP_DIR" -name "philosophy_concepts_mongodb_*.tar.gz" -type f | sort -r))
            local index=$((selection - 1))
            
            if [ $index -ge 0 ] && [ $index -lt ${#backups[@]} ]; then
                backup_file="${backups[$index]}"
            else
                error "Неверный выбор"
                exit 1
            fi
        else
            backup_file="$selection"
        fi
    fi
    
    if [ ! -f "$backup_file" ]; then
        error "Файл резервной копии не найден: $backup_file"
        exit 1
    fi
    
    echo "$backup_file"
}

# Проверка подключения к MongoDB
check_connection() {
    log "Проверка подключения к MongoDB..."
    
    local mongo_args=()
    
    if [ -n "$MONGO_USERNAME" ] && [ -n "$MONGO_PASSWORD" ]; then
        mongo_args+=(
            "--username=$MONGO_USERNAME"
            "--password=$MONGO_PASSWORD"
            "--authenticationDatabase=$MONGO_AUTH_DB"
        )
    fi
    
    mongo_args+=("--host=${MONGO_HOST}:${MONGO_PORT}")
    mongo_args+=("--eval=db.version()")
    
    if mongosh "${mongo_args[@]}" > /dev/null 2>&1; then
        log "Подключение к MongoDB установлено"
    else
        error "Не удалось подключиться к MongoDB"
        exit 1
    fi
}

# Создание резервной копии текущих данных
backup_current_data() {
    if [ "$DROP_EXISTING" = "true" ]; then
        read -p "Создать резервную копию текущих данных перед восстановлением? (y/n): " create_backup
        
        if [[ "$create_backup" =~ ^[Yy]$ ]]; then
            log "Создание резервной копии текущих данных..."
            
            local backup_script="${SCRIPT_DIR}/backup.sh"
            if [ -x "$backup_script" ]; then
                "$backup_script"
            else
                warning "Скрипт резервного копирования не найден или не исполняемый"
            fi
        fi
    fi
}

# Распаковка резервной копии
extract_backup() {
    local backup_file="$1"
    
    log "Распаковка резервной копии..."
    
    mkdir -p "$RESTORE_TEMP_DIR"
    
    if tar -xzf "$backup_file" -C "$RESTORE_TEMP_DIR"; then
        log "Резервная копия успешно распакована"
        
        # Поиск директории с данными
        local data_dir=$(find "$RESTORE_TEMP_DIR" -name "$MONGO_DATABASE" -type d | head -n1)
        
        if [ -z "$data_dir" ]; then
            # Попытка найти директорию с именем резервной копии
            data_dir=$(find "$RESTORE_TEMP_DIR" -maxdepth 1 -type d ! -path "$RESTORE_TEMP_DIR" | head -n1)
        fi
        
        if [ -z "$data_dir" ] || [ ! -d "$data_dir" ]; then
            error "Не удалось найти данные для восстановления"
            exit 1
        fi
        
        echo "$data_dir"
    else
        error "Ошибка при распаковке резервной копии"
        exit 1
    fi
}

# Подтверждение восстановления
confirm_restore() {
    local backup_file="$1"
    
    echo
    warning "ВНИМАНИЕ: Вы собираетесь восстановить базу данных из резервной копии"
    info "Резервная копия: $(basename "$backup_file")"
    info "Целевая база данных: $MONGO_DATABASE"
    info "MongoDB сервер: $MONGO_HOST:$MONGO_PORT"
    
    if [ "$DROP_EXISTING" = "true" ]; then
        warning "Существующие данные будут УДАЛЕНЫ!"
    else
        info "Существующие данные будут сохранены (могут возникнуть конфликты)"
    fi
    
    echo
    read -p "Продолжить восстановление? (yes/no): " confirmation
    
    if [ "$confirmation" != "yes" ]; then
        log "Восстановление отменено"
        exit 0
    fi
}

# Выполнение восстановления
perform_restore() {
    local data_dir="$1"
    
    log "Начало восстановления MongoDB..."
    
    local mongorestore_args=(
        "--db=$MONGO_DATABASE"
        "--numParallelCollections=$PARALLEL_COLLECTIONS"
    )
    
    # Добавление аутентификации если необходимо
    if [ -n "$MONGO_USERNAME" ] && [ -n "$MONGO_PASSWORD" ]; then
        mongorestore_args+=(
            "--username=$MONGO_USERNAME"
            "--password=$MONGO_PASSWORD"
            "--authenticationDatabase=$MONGO_AUTH_DB"
        )
    fi
    
    # Добавление хоста и порта
    mongorestore_args+=("--host=${MONGO_HOST}:${MONGO_PORT}")
    
    # Добавление опций восстановления
    if [ "$DROP_EXISTING" = "true" ]; then
        mongorestore_args+=("--drop")
    fi
    
    if [ "$PRESERVE_UUID" = "true" ]; then
        mongorestore_args+=("--preserveUUID")
    fi
    
    if [ "$NO_OPTIONS_RESTORE" = "true" ]; then
        mongorestore_args+=("--noOptionsRestore")
    fi
    
    # Проверка наличия gzip
    if ls "$data_dir"/*.gz > /dev/null 2>&1; then
        mongorestore_args+=("--gzip")
    fi
    
    # Добавление пути к данным
    mongorestore_args+=("$data_dir")
    
    # Выполнение mongorestore
    if mongorestore "${mongorestore_args[@]}"; then
        log "Восстановление успешно завершено"
    else
        error "Ошибка при выполнении восстановления"
        exit 1
    fi
}

# Проверка восстановленных данных
verify_restore() {
    log "Проверка восстановленных данных..."
    
    local mongo_args=()
    
    if [ -n "$MONGO_USERNAME" ] && [ -n "$MONGO_PASSWORD" ]; then
        mongo_args+=(
            "--username=$MONGO_USERNAME"
            "--password=$MONGO_PASSWORD"
            "--authenticationDatabase=$MONGO_AUTH_DB"
        )
    fi
    
    mongo_args+=("--host=${MONGO_HOST}:${MONGO_PORT}")
    mongo_args+=("$MONGO_DATABASE")
    mongo_args+=("--eval")
    
    # Скрипт для проверки коллекций
    local check_script='
    const collections = [
        "theses",
        "categoryDescriptions",
        "relationshipDescriptions",
        "conceptAnalyses",
        "dialogues",
        "historicalContexts",
        "practicalApplications",
        "conceptEvolutions",
        "generatedElements"
    ];
    
    print("\\nПроверка коллекций:");
    collections.forEach(col => {
        const count = db[col].countDocuments();
        print(`  ${col}: ${count} документов`);
    });
    
    print("\\nСтатистика базы данных:");
    const stats = db.stats();
    print(`  Размер данных: ${(stats.dataSize / 1024 / 1024).toFixed(2)} MB`);
    print(`  Размер индексов: ${(stats.indexSize / 1024 / 1024).toFixed(2)} MB`);
    print(`  Общий размер: ${(stats.storageSize / 1024 / 1024).toFixed(2)} MB`);
    '
    
    mongo_args+=("$check_script")
    
    if mongosh "${mongo_args[@]}"; then
        log "Проверка данных завершена"
    else
        warning "Не удалось выполнить проверку данных"
    fi
}

# Обновление индексов
update_indexes() {
    log "Обновление индексов..."
    
    local indexes_script="${SCRIPT_DIR}/../migrations/00002_create_indexes.js"
    
    if [ -f "$indexes_script" ]; then
        local mongo_args=()
        
        if [ -n "$MONGO_USERNAME" ] && [ -n "$MONGO_PASSWORD" ]; then
            mongo_args+=(
                "--username=$MONGO_USERNAME"
                "--password=$MONGO_PASSWORD"
                "--authenticationDatabase=$MONGO_AUTH_DB"
            )
        fi
        
        mongo_args+=("--host=${MONGO_HOST}:${MONGO_PORT}")
        mongo_args+=("$MONGO_DATABASE")
        mongo_args+=("$indexes_script")
        
        if mongosh "${mongo_args[@]}" > /dev/null 2>&1; then
            log "Индексы успешно обновлены"
        else
            warning "Не удалось обновить индексы"
        fi
    else
        warning "Скрипт создания индексов не найден"
    fi
}

# Основная функция
main() {
    log "=== Начало процесса восстановления MongoDB ==="
    
    # Проверки
    check_mongorestore
    check_connection
    
    # Выбор резервной копии
    local backup_file=$(select_backup "$1")
    log "Выбрана резервная копия: $(basename "$backup_file")"
    
    # Подтверждение
    confirm_restore "$backup_file"
    
    # Создание резервной копии текущих данных
    backup_current_data
    
    # Распаковка
    local data_dir=$(extract_backup "$backup_file")
    
    # Восстановление
    perform_restore "$data_dir"
    
    # Проверка
    verify_restore
    
    # Обновление индексов
    update_indexes
    
    log "=== Восстановление завершено успешно ==="
    
    # Отправка уведомления если настроено
    if [ -n "$NOTIFICATION_WEBHOOK" ]; then
        curl -s -X POST "$NOTIFICATION_WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "{\"text\": \"MongoDB восстановлена из резервной копии: $(basename "$backup_file")\"}" > /dev/null
    fi
}

# Обработка прерывания
trap 'error "Процесс прерван"; cleanup; exit 1' INT TERM

# Запуск основной функции
main "$@"
