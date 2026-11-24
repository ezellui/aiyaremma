/**
 * Rate limiting middleware
 */

const rateLimit = require('express-rate-limit');
const RedisStore = require('rate-limit-redis');
const redisClient = require('../db/redis-client');
const config = require('../config/config');

/**
 * Создает rate limiter с Redis store
 */
const limiter = rateLimit({
  windowMs: config.rateLimit.windowMs,
  max: config.rateLimit.maxRequests,
  message: {
    success: false,
    error: {
      message: 'Слишком много запросов, попробуйте позже',
      code: 'RATE_LIMIT_EXCEEDED'
    }
  },
  standardHeaders: true,
  legacyHeaders: false,
  // Redis store для распределенного rate limiting
  store: new RedisStore({
    // @ts-expect-error - Known issue with types
    client: redisClient.getClient(),
    prefix: 'rate-limit:',
  }),
  // Функция для определения ключа (по IP или userId)
  keyGenerator: (req) => {
    // Если пользователь аутентифицирован, используем userId
    if (req.user && req.user.userId) {
      return `user:${req.user.userId}`;
    }
    // Иначе используем IP
    return req.ip;
  },
  // Пропускаем rate limiting для health check
  skip: (req) => {
    return req.path === '/health';
  }
});

/**
 * Строгий rate limiter для чувствительных операций
 */
const strictLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 минут
  max: 5, // 5 запросов
  message: {
    success: false,
    error: {
      message: 'Слишком много попыток, попробуйте позже',
      code: 'STRICT_RATE_LIMIT_EXCEEDED'
    }
  },
  standardHeaders: true,
  legacyHeaders: false,
  store: new RedisStore({
    // @ts-expect-error - Known issue with types
    client: redisClient.getClient(),
    prefix: 'rate-limit:strict:',
  }),
  keyGenerator: (req) => {
    if (req.user && req.user.userId) {
      return `user:${req.user.userId}`;
    }
    return req.ip;
  }
});

module.exports = limiter;
module.exports.strictLimiter = strictLimiter;