/**
 * Конфигурация User Service
 */

module.exports = {
  env: process.env.NODE_ENV || 'development',
  port: parseInt(process.env.PORT, 10) || 4001,
  serviceName: process.env.SERVICE_NAME || 'user-service',

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
    keyPrefix: 'user:'
  },

  // JWT
  jwt: {
    secret: process.env.JWT_SECRET || 'your_jwt_secret_here',
    expiresIn: process.env.JWT_EXPIRES_IN || '7d',
    refreshExpiresIn: process.env.JWT_REFRESH_EXPIRES_IN || '30d'
  },

  // Encryption для API ключей
  encryption: {
    key: process.env.ENCRYPTION_KEY || 'change_this_to_32_char_string!'
  },

  // Логирование
  logging: {
    level: process.env.LOG_LEVEL || 'debug'
  }
};