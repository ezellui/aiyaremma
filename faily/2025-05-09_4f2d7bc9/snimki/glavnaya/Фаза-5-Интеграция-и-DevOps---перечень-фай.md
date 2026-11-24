# Фаза 5: Интеграция и DevOps

## Kubernetes-манифесты

### Деплойменты

#### Деплойменты для фронтенда
- `kubernetes/deployments/frontend-deployment.yaml` - Деплоймент для фронтенда

#### Деплойменты для API Gateway
- `kubernetes/deployments/api-gateway-deployment.yaml` - Деплоймент для API Gateway

#### Деплойменты для микросервисов
- `kubernetes/deployments/user-service-deployment.yaml` - Деплоймент для сервиса пользователей
- `kubernetes/deployments/concept-service-deployment.yaml` - Деплоймент для сервиса концепций
- `kubernetes/deployments/graph-service-deployment.yaml` - Деплоймент для сервиса графов
- `kubernetes/deployments/thesis-service-deployment.yaml` - Деплоймент для сервиса тезисов
- `kubernetes/deployments/synthesis-service-deployment.yaml` - Деплоймент для сервиса синтеза
- `kubernetes/deployments/claude-service-deployment.yaml` - Деплоймент для сервиса Claude
- `kubernetes/deployments/name-service-deployment.yaml` - Деплоймент для сервиса анализа названий
- `kubernetes/deployments/origin-service-deployment.yaml` - Деплоймент для сервиса определения происхождения
- `kubernetes/deployments/historical-service-deployment.yaml` - Деплоймент для сервиса исторической контекстуализации
- `kubernetes/deployments/practical-service-deployment.yaml` - Деплоймент для сервиса практического применения
- `kubernetes/deployments/dialogue-service-deployment.yaml` - Деплоймент для сервиса диалогической интерпретации
- `kubernetes/deployments/evolution-service-deployment.yaml` - Деплоймент для сервиса эволюции концепций

#### Деплойменты для баз данных и очередей
- `kubernetes/deployments/postgres-deployment.yaml` - Деплоймент для PostgreSQL
- `kubernetes/deployments/neo4j-deployment.yaml` - Деплоймент для Neo4j
- `kubernetes/deployments/mongodb-deployment.yaml` - Деплоймент для MongoDB
- `kubernetes/deployments/redis-deployment.yaml` - Деплоймент для Redis
- `kubernetes/deployments/rabbitmq-deployment.yaml` - Деплоймент для RabbitMQ

#### Деплойменты для мониторинга
- `kubernetes/deployments/prometheus-deployment.yaml` - Деплоймент для Prometheus
- `kubernetes/deployments/grafana-deployment.yaml` - Деплоймент для Grafana
- `kubernetes/deployments/elasticsearch-deployment.yaml` - Деплоймент для Elasticsearch
- `kubernetes/deployments/logstash-deployment.yaml` - Деплоймент для Logstash
- `kubernetes/deployments/kibana-deployment.yaml` - Деплоймент для Kibana

### Сервисы

#### Сервисы для фронтенда
- `kubernetes/services/frontend-service.yaml` - Сервис для фронтенда

#### Сервисы для API Gateway
- `kubernetes/services/api-gateway-service.yaml` - Сервис для API Gateway

#### Сервисы для микросервисов
- `kubernetes/services/user-service-service.yaml` - Сервис для сервиса пользователей
- `kubernetes/services/concept-service-service.yaml` - Сервис для сервиса концепций
- `kubernetes/services/graph-service-service.yaml` - Сервис для сервиса графов
- `kubernetes/services/thesis-service-service.yaml` - Сервис для сервиса тезисов
- `kubernetes/services/synthesis-service-service.yaml` - Сервис для сервиса синтеза
- `kubernetes/services/claude-service-service.yaml` - Сервис для сервиса Claude
- `kubernetes/services/name-service-service.yaml` - Сервис для сервиса анализа названий
- `kubernetes/services/origin-service-service.yaml` - Сервис для сервиса определения происхождения
- `kubernetes/services/historical-service-service.yaml` - Сервис для сервиса исторической контекстуализации
- `kubernetes/services/practical-service-service.yaml` - Сервис для сервиса практического применения
- `kubernetes/services/dialogue-service-service.yaml` - Сервис для сервиса диалогической интерпретации
- `kubernetes/services/evolution-service-service.yaml` - Сервис для сервиса эволюции концепций

#### Сервисы для баз данных и очередей
- `kubernetes/services/postgres-service.yaml` - Сервис для PostgreSQL
- `kubernetes/services/neo4j-service.yaml` - Сервис для Neo4j
- `kubernetes/services/mongodb-service.yaml` - Сервис для MongoDB
- `kubernetes/services/redis-service.yaml` - Сервис для Redis
- `kubernetes/services/rabbitmq-service.yaml` - Сервис для RabbitMQ

#### Сервисы для мониторинга
- `kubernetes/services/prometheus-service.yaml` - Сервис для Prometheus
- `kubernetes/services/grafana-service.yaml` - Сервис для Grafana
- `kubernetes/services/elasticsearch-service.yaml` - Сервис для Elasticsearch
- `kubernetes/services/logstash-service.yaml` - Сервис для Logstash
- `kubernetes/services/kibana-service.yaml` - Сервис для Kibana

### Ingress
- `kubernetes/ingress/ingress.yaml` - Основной Ingress-манифест

### ConfigMaps
- `kubernetes/config-maps/env-config.yaml` - ConfigMap для переменных окружения
- `kubernetes/config-maps/postgres-config.yaml` - ConfigMap для PostgreSQL
- `kubernetes/config-maps/neo4j-config.yaml` - ConfigMap для Neo4j
- `kubernetes/config-maps/mongodb-config.yaml` - ConfigMap для MongoDB
- `kubernetes/config-maps/redis-config.yaml` - ConfigMap для Redis
- `kubernetes/config-maps/rabbitmq-config.yaml` - ConfigMap для RabbitMQ
- `kubernetes/config-maps/logging-config.yaml` - ConfigMap для логирования
- `kubernetes/config-maps/prometheus-config.yaml` - ConfigMap для Prometheus
- `kubernetes/config-maps/grafana-config.yaml` - ConfigMap для Grafana

### Secrets
- `kubernetes/secrets/secret-template.yaml` - Шаблон для секретов
- `kubernetes/secrets/db-secrets-template.yaml` - Шаблон для секретов баз данных
- `kubernetes/secrets/api-keys-template.yaml` - Шаблон для секретов API-ключей

### Persistent Volumes
- `kubernetes/persistent-volumes/postgres-pv.yaml` - PV для PostgreSQL
- `kubernetes/persistent-volumes/neo4j-pv.yaml` - PV для Neo4j
- `kubernetes/persistent-volumes/mongodb-pv.yaml` - PV для MongoDB
- `kubernetes/persistent-volumes/rabbitmq-pv.yaml` - PV для RabbitMQ
- `kubernetes/persistent-volumes/elasticsearch-pv.yaml` - PV для Elasticsearch

### Horizontal Pod Autoscalers (HPA)
- `kubernetes/hpa/frontend-hpa.yaml` - HPA для фронтенда
- `kubernetes/hpa/api-gateway-hpa.yaml` - HPA для API Gateway
- `kubernetes/hpa/user-service-hpa.yaml` - HPA для сервиса пользователей
- `kubernetes/hpa/concept-service-hpa.yaml` - HPA для сервиса концепций
- `kubernetes/hpa/graph-service-hpa.yaml` - HPA для сервиса графов
- `kubernetes/hpa/thesis-service-hpa.yaml` - HPA для сервиса тезисов
- `kubernetes/hpa/synthesis-service-hpa.yaml` - HPA для сервиса синтеза
- `kubernetes/hpa/claude-service-hpa.yaml` - HPA для сервиса Claude

## CI/CD пайплайны

### GitHub Actions
- `.github/workflows/build.yml` - Сборка образов
- `.github/workflows/test.yml` - Тестирование
- `.github/workflows/deploy.yml` - Деплой
- `.github/workflows/lint.yml` - Линтинг кода
- `.github/workflows/pr-checks.yml` - Проверки для Pull Request

### Скрипты для CI/CD
- `scripts/ci/build-services.sh` - Скрипт для сборки сервисов
- `scripts/ci/run-tests.sh` - Скрипт для запуска тестов
- `scripts/ci/push-images.sh` - Скрипт для публикации образов
- `scripts/ci/deploy.sh` - Скрипт для деплоя
- `scripts/ci/update-config.sh` - Скрипт для обновления конфигурации

## Мониторинг и логирование

### Prometheus
- `monitoring/prometheus/prometheus.yml` - Конфигурация Prometheus
- `monitoring/prometheus/rules/alert-rules.yml` - Правила оповещений
- `monitoring/prometheus/rules/recording-rules.yml` - Правила записи

### Grafana
- `monitoring/grafana/dashboards/overview.json` - Дашборд общего обзора
- `monitoring/grafana/dashboards/frontend.json` - Дашборд фронтенда
- `monitoring/grafana/dashboards/api-gateway.json` - Дашборд API Gateway
- `monitoring/grafana/dashboards/services.json` - Дашборд сервисов
- `monitoring/grafana/dashboards/databases.json` - Дашборд баз данных
- `monitoring/grafana/dashboards/rabbitmq.json` - Дашборд RabbitMQ
- `monitoring/grafana/dashboards/claude.json` - Дашборд взаимодействия с Claude
- `monitoring/grafana/dashboards/business-metrics.json` - Дашборд бизнес-метрик
- `monitoring/grafana/provisioning/datasources/prometheus.yml` - Конфигурация источника данных Prometheus

### ELK Stack
- `monitoring/logstash/pipeline/logstash.conf` - Конфигурация пайплайна Logstash
- `monitoring/logstash/config/logstash.yml` - Конфигурация Logstash
- `monitoring/elasticsearch/config/elasticsearch.yml` - Конфигурация Elasticsearch
- `monitoring/kibana/config/kibana.yml` - Конфигурация Kibana
- `monitoring/kibana/dashboards/logs-dashboard.json` - Дашборд логов в Kibana

## Конфигурация для продакшн-окружения

### Docker Compose для продакшн
- `docker-compose.prod.yml` - Файл Docker Compose для продакшн-окружения

### Nginx конфигурация
- `nginx/nginx.conf` - Основная конфигурация Nginx
- `nginx/conf.d/frontend.conf` - Конфигурация для фронтенда
- `nginx/conf.d/api-gateway.conf` - Конфигурация для API Gateway

## Документация и руководства

### Документация по развертыванию
- `docs/deployment/README.md` - Общая информация о развертывании
- `docs/deployment/kubernetes.md` - Развертывание в Kubernetes
- `docs/deployment/docker-compose.md` - Развертывание с помощью Docker Compose
- `docs/deployment/scaling.md` - Масштабирование системы
- `docs/deployment/monitoring.md` - Настройка мониторинга и логирования
- `docs/deployment/backup-restore.md` - Резервное копирование и восстановление

### Документация по архитектуре
- `docs/architecture/README.md` - Общая информация об архитектуре
- `docs/architecture/microservices.md` - Описание микросервисов
- `docs/architecture/communication.md` - Коммуникация между сервисами
- `docs/architecture/databases.md` - Структура баз данных
- `docs/architecture/caching.md` - Стратегии кэширования
- `docs/architecture/messaging.md` - Обмен сообщениями

### Документация по API
- `docs/api/README.md` - Общая информация об API
- `docs/api/user-service.md` - API сервиса пользователей
- `docs/api/concept-service.md` - API сервиса концепций
- `docs/api/graph-service.md` - API сервиса графов
- `docs/api/thesis-service.md` - API сервиса тезисов
- `docs/api/synthesis-service.md` - API сервиса синтеза
- `docs/api/claude-service.md` - API сервиса Claude
- `docs/api/name-service.md` - API сервиса анализа названий
- `docs/api/origin-service.md` - API сервиса определения происхождения
- `docs/api/historical-service.md` - API сервиса исторической контекстуализации
- `docs/api/practical-service.md` - API сервиса практического применения
- `docs/api/dialogue-service.md` - API сервиса диалогической интерпретации
- `docs/api/evolution-service.md` - API сервиса эволюции концепций

### Руководства для разработчиков
- `docs/development/README.md` - Общая информация для разработчиков
- `docs/development/setup.md` - Настройка окружения разработки
- `docs/development/coding-standards.md` - Стандарты кодирования
- `docs/development/testing.md` - Тестирование
- `docs/development/debugging.md` - Отладка
- `docs/development/contributing.md` - Руководство по вкладу в проект

### Руководства для пользователей
- `docs/user-guides/README.md` - Общая информация для пользователей
- `docs/user-guides/getting-started.md` - Начало работы
- `docs/user-guides/concept-creation.md` - Создание концепций
- `docs/user-guides/graph-editing.md` - Редактирование графов
- `docs/user-guides/thesis-generation.md` - Генерация тезисов
- `docs/user-guides/synthesis.md` - Синтез концепций
- `docs/user-guides/advanced-features.md` - Продвинутые функции