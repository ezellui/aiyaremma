/**
 * Rate limiting middleware с использованием Redis
 */

const rateLimit = require('express-rate-limit');
const RedisStore = require('rate-limit-redis');
const redisClient = require('../config/redis');
const config = require('../config/config');

/**
 * Глобальный rate limiter
 */
const globalRateLimiter = rateLimit({
  windowMs: config.rateLimit.windowMs,
  max: config.rateLimit.max,
  store: new RedisStore({
    client: redisClient.getClient(),
    prefix: 'ratelimit:global:'
  }),
  message: {
    success: false,
    error: {
      message: 'Слишком много запросов, попробуйте позже',
      code: 'RATE_LIMIT_EXCEEDED'
    }
  },
  standardHeaders: true,
  legacyHeaders: false,
  handler: (req, res) => {
    res.status(429).json({
      success: false,
      error: {
        message: 'Слишком много запросов с этого IP, попробуйте позже',
        code: 'RATE_LIMIT_EXCEEDED',
        retryAfter: req.rateLimit.resetTime
      }
    });
  }
});

/**
 * Rate limiter для аутентификации (более строгий)
 */
const authRateLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 минут
  max: 5, // 5 попыток
  store: new RedisStore({
    client: redisClient.getClient(),
    prefix: 'ratelimit:auth:'
  }),
  skipSuccessfulRequests: true,
  handler: (req, res) => {
    res.status(429).json({
      success: false,
      error: {
        message: 'Слишком много попыток входа, попробуйте через 15 минут',
        code: 'AUTH_RATE_LIMIT_EXCEEDED'
      }
    });
  }
});

/**
 * Rate limiter для Claude API (ограничение на пользователя)
 */
const claudeRateLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 час
  max: 100, // 100 запросов в час
  store: new RedisStore({
    client: redisClient.getClient(),
    prefix: 'ratelimit:claude:'
  }),
  keyGenerator: (req) => {
    // Используем ID пользователя если аутентифицирован, иначе IP
    return req.user ? `user:${req.user.id}` : `ip:${req.ip}`;
  },
  handler: (req, res) => {
    res.status(429).json({
      success: false,
      error: {
        message: 'Превышен лимит запросов к Claude API',
        code: 'CLAUDE_RATE_LIMIT_EXCEEDED',
        limit: 100,
        window: '1 hour'
      }
    });
  }
});

module.exports = globalRateLimiter;
module.exports.authRateLimiter = authRateLimiter;
module.exports.claudeRateLimiter = claudeRateLimiter;