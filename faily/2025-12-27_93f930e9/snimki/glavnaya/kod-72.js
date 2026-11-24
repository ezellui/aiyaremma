/**
 * Middleware аутентификации через JWT
 */

const jwt = require('jsonwebtoken');
const config = require('../config/config');
const redisClient = require('../config/redis');
const { UnauthorizedError } = require('@philos/shared');

/**
 * Извлекает токен из заголовка Authorization
 */
function extractToken(req) {
  const authHeader = req.headers.authorization;

  if (!authHeader) {
    return null;
  }

  const parts = authHeader.split(' ');

  if (parts.length !== 2 || parts[0] !== 'Bearer') {
    return null;
  }

  return parts[1];
}

/**
 * Проверяет, не находится ли токен в черном списке
 */
async function isTokenBlacklisted(token) {
  try {
    const key = `blacklist:${token}`;
    return await redisClient.exists(key);
  } catch (error) {
    // В случае ошибки Redis считаем токен валидным
    return false;
  }
}

/**
 * Middleware для проверки JWT токена
 */
async function authenticate(req, res, next) {
  try {
    const token = extractToken(req);

    if (!token) {
      throw new UnauthorizedError('Токен не предоставлен');
    }

    // Проверяем черный список
    const isBlacklisted = await isTokenBlacklisted(token);
    if (isBlacklisted) {
      throw new UnauthorizedError('Токен недействителен');
    }

    // Верифицируем токен
    const decoded = jwt.verify(token, config.jwt.secret);

    // Добавляем данные пользователя в запрос
    req.user = {
      id: decoded.userId,
      email: decoded.email,
      role: decoded.role
    };

    req.token = token;

    next();
  } catch (error) {
    if (error.name === 'JsonWebTokenError') {
      return next(new UnauthorizedError('Неверный токен'));
    }
    if (error.name === 'TokenExpiredError') {
      return next(new UnauthorizedError('Токен истек'));
    }
    next(error);
  }
}

/**
 * Опциональная аутентификация (не выбрасывает ошибку если токена нет)
 */
async function optionalAuthenticate(req, res, next) {
  try {
    const token = extractToken(req);

    if (!token) {
      return next();
    }

    const isBlacklisted = await isTokenBlacklisted(token);
    if (isBlacklisted) {
      return next();
    }

    const decoded = jwt.verify(token, config.jwt.secret);

    req.user = {
      id: decoded.userId,
      email: decoded.email,
      role: decoded.role
    };

    req.token = token;

    next();
  } catch (error) {
    // Игнорируем ошибки аутентификации
    next();
  }
}

/**
 * Проверяет роль пользователя
 */
function requireRole(...roles) {
  return (req, res, next) => {
    if (!req.user) {
      return next(new UnauthorizedError('Требуется аутентификация'));
    }

    if (!roles.includes(req.user.role)) {
      return next(new UnauthorizedError('Недостаточно прав'));
    }

    next();
  };
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
async function blacklistToken(token, expiresIn = 7 * 24 * 60 * 60) {
  try {
    const key = `blacklist:${token}`;
    await redisClient.set(key, true, expiresIn);
  } catch (error) {
    // Логируем ошибку, но не блокируем выход
    console.error('Error blacklisting token:', error);
  }
}

module.exports = {
  authenticate,
  optionalAuthenticate,
  requireRole,
  generateToken,
  generateRefreshToken,
  blacklistToken
};