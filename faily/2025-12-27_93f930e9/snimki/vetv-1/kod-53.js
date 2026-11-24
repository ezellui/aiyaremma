/**
 * Middleware для аутентификации и авторизации
 */

const jwt = require('jsonwebtoken');
const { UnauthorizedError } = require('@philos/shared');
const config = require('../config/config');
const redisClient = require('../db/redis-client');

/**
 * Проверяет наличие и валидность JWT токена
 */
async function authenticate(req, res, next) {
  try {
    // Получаем токен из заголовка
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      throw new UnauthorizedError('Токен не предоставлен');
    }
    
    const token = authHeader.substring(7); // Убираем 'Bearer '
    
    // Проверяем, не находится ли токен в черном списке
    const isBlacklisted = await redisClient.getCache(`blacklist:${token}`);
    if (isBlacklisted) {
      throw new UnauthorizedError('Токен недействителен');
    }
    
    // Верифицируем токен
    const decoded = jwt.verify(token, config.jwt.secret);
    
    // Добавляем информацию о пользователе в запрос
    req.user = {
      userId: decoded.userId,
      username: decoded.username,
      email: decoded.email
    };
    
    // Добавляем токен для возможного использования
    req.token = token;
    
    next();
  } catch (error) {
    if (error.name === 'JsonWebTokenError') {
      next(new UnauthorizedError('Некорректный токен'));
    } else if (error.name === 'TokenExpiredError') {
      next(new UnauthorizedError('Токен истек'));
    } else {
      next(error);
    }
  }
}

/**
 * Опциональная аутентификация - не выбрасывает ошибку, если токен отсутствует
 */
async function optionalAuthenticate(req, res, next) {
  try {
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return next();
    }
    
    const token = authHeader.substring(7);
    
    // Проверяем черный список
    const isBlacklisted = await redisClient.getCache(`blacklist:${token}`);
    if (isBlacklisted) {
      return next();
    }
    
    // Верифицируем токен
    const decoded = jwt.verify(token, config.jwt.secret);
    
    req.user = {
      userId: decoded.userId,
      username: decoded.username,
      email: decoded.email
    };
    
    req.token = token;
    
    next();
  } catch (error) {
    // Игнорируем ошибки аутентификации в опциональном режиме
    next();
  }
}

/**
 * Генерирует JWT токен
 */
function generateToken(payload) {
  return jwt.sign(payload, config.jwt.secret, {
    expiresIn: config.jwt.expiresIn
  });
}

/**
 * Генерирует refresh токен
 */
function generateRefreshToken(payload) {
  return jwt.sign(payload, config.jwt.secret, {
    expiresIn: config.jwt.refreshExpiresIn
  });
}

/**
 * Добавляет токен в черный список
 */
async function blacklistToken(token) {
  try {
    const decoded = jwt.decode(token);
    if (!decoded || !decoded.exp) {
      return false;
    }
    
    // Вычисляем оставшееся время жизни токена
    const expiresIn = decoded.exp - Math.floor(Date.now() / 1000);
    
    if (expiresIn > 0) {
      await redisClient.setCache(`blacklist:${token}`, true, expiresIn);
    }
    
    return true;
  } catch (error) {
    return false;
  }
}

module.exports = {
  authenticate,
  optionalAuthenticate,
  generateToken,
  generateRefreshToken,
  blacklistToken
};