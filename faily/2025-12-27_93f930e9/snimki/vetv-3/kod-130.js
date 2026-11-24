/**
 * Конфигурация Concept Service
 */

module.exports = {
  env: process.env.NODE_ENV || 'development',
  port: parseInt(process.env.PORT, 10) || 4002,
  serviceName: process.env.SERVICE_NAME || 'concept-service',

  // CORS
  cors: {
    origin: process.env.CORS_ORIGIN || '*',
    credentials: true
  },

  // База данных PostgreSQL
  database: {
    host: process.env.POSTGRES_HOST || 'localhost',
    port: parseInt(process.env.POSTGRES_PORT, 10) || 5432,
    database: process.env.POSTGRES_DB || 'philos_concepts',
    user: process.env.POSTGRES_USER || 'philos',
    password: process.env.POSTGRES_PASSWORD || 'password',
    max: 20,
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 2000
  },

  // Redis
  redis: {
    url: process.env.REDIS_URL || 'redis://localhost:6379',
    keyPrefix: 'concept:'
  },

  // Внешние сервисы
  services: {
    graph: process.env.GRAPH_SERVICE_URL || 'http://localhost:4003',
    thesis: process.env.THESIS_SERVICE_URL || 'http://localhost:4004'
  },

  // Логирование
  logging: {
    level: process.env.LOG_LEVEL || 'debug'
  }
};