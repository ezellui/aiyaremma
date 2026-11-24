/**
 * Middleware аутентификации для внутренних запросов
 */

const { UnauthorizedError } = require('@philos/shared');

/**
 * Извлекает данные пользователя из заголовков, установленных API Gateway
 */
function extractUserFromHeaders(req, res, next) {
  const userId = req.headers['x-user-id'];
  const userEmail = req.headers['x-user-email'];
  const userRole = req.headers['x-user-role'];

  if (userId) {
    req.user = {
      id: userId,
      email: userEmail,
      role: userRole
    };
  }

  next();
}

/**
 * Требует аутентификации
 */
function requireAuth(req, res, next) {
  if (!req.user) {
    return next(new UnauthorizedError('Требуется аутентификация'));
  }
  next();
}

module.exports = {
  extractUserFromHeaders,
  requireAuth
};