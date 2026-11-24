/**
 * Middleware для логирования HTTP запросов
 */

const logger = require('../utils/logger');

function requestLogger(req, res, next) {
  const startTime = Date.now();
  
  // Логируем входящий запрос
  logger.http(`Incoming ${req.method} ${req.path}`);
  
  // Перехватываем завершение ответа
  res.on('finish', () => {
    const duration = Date.now() - startTime;
    const logMessage = `${req.method} ${req.path} ${res.statusCode} - ${duration}ms`;
    
    if (res.statusCode >= 500) {
      logger.error(logMessage);
    } else if (res.statusCode >= 400) {
      logger.warn(logMessage);
    } else {
      logger.http(logMessage);
    }
  });
  
  next();
}

module.exports = requestLogger;