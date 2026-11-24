/**
 * Главный экспорт всех shared модулей
 */

// Константы
const categoryTypes = require('./constants/category-types');
const relationshipTypes = require('./constants/relationship-types');
const relationshipDirections = require('./constants/relationship-directions');
const innovationLevels = require('./constants/innovation-levels');
const thesisTypes = require('./constants/thesis-types');
const analysisTypes = require('./constants/analysis-types');
const httpStatus = require('./constants/http-status');
const validationRules = require('./constants/validation-rules');

// Утилиты
const logger = require('./utils/logger');
const validators = require('./utils/validators');
const errors = require('./utils/errors');
const responseBuilder = require('./utils/response-builder');

// Middleware
const asyncHandler = require('./middleware/async-handler');
const errorHandler = require('./middleware/error-handler');
const requestLogger = require('./middleware/request-logger');

module.exports = {
  // Константы
  ...categoryTypes,
  ...relationshipTypes,
  ...relationshipDirections,
  ...innovationLevels,
  ...thesisTypes,
  ...analysisTypes,
  ...httpStatus,
  VALIDATION_RULES: validationRules,
  
  // Утилиты
  logger,
  ...validators,
  ...errors,
  responseBuilder,
  
  // Middleware
  asyncHandler,
  errorHandler,
  requestLogger
};