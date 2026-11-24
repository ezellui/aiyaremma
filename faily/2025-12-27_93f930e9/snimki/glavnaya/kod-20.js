/**
 * Главный экспорт всех общих модулей
 */

module.exports = {
  // Константы
  constants: require('./constants'),
  
  // Утилиты
  logger: require('./utils/logger'),
  validators: require('./utils/validators'),
  AppError: require('./utils/errors').AppError,
  ErrorCodes: require('./utils/errors').ErrorCodes,
  
  // Middleware
  asyncHandler: require('./middleware/async-handler'),
  errorHandler: require('./middleware/error-handler'),
  requestLogger: require('./middleware/request-logger'),
  
  // Helpers
  responseBuilder: require('./utils/response-builder')
};