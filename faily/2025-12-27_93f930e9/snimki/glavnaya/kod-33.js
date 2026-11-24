/**
 * Централизованный обработчик ошибок
 */

const logger = require('../utils/logger');
const { AppError } = require('../utils/errors');
const HTTP_STATUS = require('../constants/http-status');

function errorHandler(err, req, res, next) {
  let error = err;
  
  // Если это не наша кастомная ошибка, создаем AppError
  if (!(error instanceof AppError)) {
    const statusCode = error.statusCode || HTTP_STATUS.INTERNAL_SERVER_ERROR;
    const message = error.message || 'Внутренняя ошибка сервера';
    error = new AppError(message, statusCode, 'INTERNAL_ERROR', false);
  }
  
  // Логируем ошибку
  if (error.isOperational) {
    logger.warn({
      message: error.message,
      statusCode: error.statusCode,
      errorCode: error.errorCode,
      path: req.path,
      method: req.method
    });
  } else {
    logger.error({
      message: error.message,
      statusCode: error.statusCode,
      errorCode: error.errorCode,
      stack: error.stack,
      path: req.path,
      method: req.method
    });
  }
  
  // Отправляем ответ
  res.status(error.statusCode).json(error.toJSON());
}

module.exports = errorHandler;