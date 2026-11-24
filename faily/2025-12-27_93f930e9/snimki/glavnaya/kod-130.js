/**
 * Конфигурация Claude Service
 */

module.exports = {
  env: process.env.NODE_ENV || 'development',
  port: parseInt(process.env.PORT, 10) || 4006,
  serviceName: process.env.SERVICE_NAME || 'claude-service',

  // CORS
  cors: {
    origin: process.env.CORS_ORIGIN || '*',
    credentials: true
  },

  // База данных PostgreSQL
  database: {
    postgres: {
      host: process.env.POSTGRES_HOST || 'localhost',
      port: parseInt(process.env.POSTGRES_PORT, 10) || 5432,
      database: process.env.POSTGRES_DB || 'philos_concepts',
      user: process.env.POSTGRES_USER || 'philos',
      password: process.env.POSTGRES_PASSWORD || 'password',
      max: 20,
      idleTimeoutMillis: 30000,
      connectionTimeoutMillis: 2000
    },
    mongodb: {
      url: process.env.MONGO_URL || 'mongodb://philos:password@localhost:27017/philos_concepts'
    }
  },

  // Redis
  redis: {
    url: process.env.REDIS_URL || 'redis://localhost:6379',
    keyPrefix: 'claude:'
  },

  // RabbitMQ
  rabbitmq: {
    url: process.env.RABBITMQ_URL || 'amqp://philos:password@localhost:5672',
    queues: {
      claude: 'claude_requests',
      claudePriority: 'claude_requests_priority'
    }
  },

  // Claude API
  claude: {
    apiKey: process.env.CLAUDE_API_KEY || '',
    apiUrl: process.env.CLAUDE_API_URL || 'https://api.anthropic.com/v1/messages',
    model: process.env.CLAUDE_MODEL || 'claude-sonnet-4-20250514',
    maxTokens: parseInt(process.env.CLAUDE_MAX_TOKENS, 10) || 4096
  },

  // Внешние сервисы
  services: {
    user: process.env.USER_SERVICE_URL || 'http://localhost:4001'
  },

  // Таймауты
  timeouts: {
    sync: parseInt(process.env.SYNC_REQUEST_TIMEOUT, 10) || 30000,
    async: parseInt(process.env.ASYNC_REQUEST_TIMEOUT, 10) || 300000
  },

  // Логирование
  logging: {
    level: process.env.LOG_LEVEL || 'debug'
  }
};