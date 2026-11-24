/**
 * Конфигурация API Gateway
 */

module.exports = {
  env: process.env.NODE_ENV || 'development',
  port: parseInt(process.env.PORT, 10) || 4000,
  serviceName: process.env.SERVICE_NAME || 'api-gateway',

  // CORS
  cors: {
    origin: process.env.CORS_ORIGIN || '*',
    credentials: true
  },

  // JWT
  jwt: {
    secret: process.env.JWT_SECRET || 'your_jwt_secret_here',
    expiresIn: process.env.JWT_EXPIRES_IN || '7d',
    refreshExpiresIn: process.env.JWT_REFRESH_EXPIRES_IN || '30d'
  },

  // Redis
  redis: {
    url: process.env.REDIS_URL || 'redis://localhost:6379',
    keyPrefix: 'gateway:'
  },

  // Rate Limiting
  rateLimit: {
    windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS, 10) || 15 * 60 * 1000, // 15 минут
    max: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS, 10) || 100
  },

  // Микросервисы
  services: {
    user: process.env.USER_SERVICE_URL || 'http://localhost:4001',
    concept: process.env.CONCEPT_SERVICE_URL || 'http://localhost:4002',
    graph: process.env.GRAPH_SERVICE_URL || 'http://localhost:4003',
    thesis: process.env.THESIS_SERVICE_URL || 'http://localhost:4004',
    synthesis: process.env.SYNTHESIS_SERVICE_URL || 'http://localhost:4005',
    claude: process.env.CLAUDE_SERVICE_URL || 'http://localhost:4006',
    nameAnalysis: process.env.NAME_ANALYSIS_SERVICE_URL || 'http://localhost:4007',
    origin: process.env.ORIGIN_SERVICE_URL || 'http://localhost:4008',
    historical: process.env.HISTORICAL_SERVICE_URL || 'http://localhost:4009',
    practical: process.env.PRACTICAL_SERVICE_URL || 'http://localhost:4010',
    dialogue: process.env.DIALOGUE_SERVICE_URL || 'http://localhost:4011',
    evolution: process.env.EVOLUTION_SERVICE_URL || 'http://localhost:4012'
  },

  // Логирование
  logging: {
    level: process.env.LOG_LEVEL || 'debug'
  }
};