/**
 * Пользовательские классы ошибок
 */

/**
 * Базовый класс для всех ошибок приложения
 */
class AppError extends Error {
  constructor(message, statusCode = 500, errorCode = 'INTERNAL_ERROR', details = null) {
    super(message);
    this.name = this.constructor.name;
    this.statusCode = statusCode;
    this.errorCode = errorCode;
    this.details = details;
    this.isOperational = true;
    
    Error.captureStackTrace(this, this.constructor);
  }

  toJSON() {
    return {
      error: {
        name: this.name,
        message: this.message,
        code: this.errorCode,
        statusCode: this.statusCode,
        details: this.details
      }
    };
  }
}

/**
 * Ошибка валидации данных (400)
 */
class ValidationError extends AppError {
  constructor(message = 'Ошибка валидации данных', details = null) {
    super(message, 400, 'VALIDATION_ERROR', details);
  }
}

/**
 * Ресурс не найден (404)
 */
class NotFoundError extends AppError {
  constructor(resource = 'Ресурс', id = null) {
    const message = id ? `${resource} с ID ${id} не найден` : `${resource} не найден`;
    super(message, 404, 'NOT_FOUND');
    this.resource = resource;
    this.resourceId = id;
  }
}

/**
 * Неавторизован (401)
 */
class UnauthorizedError extends AppError {
  constructor(message = 'Неавторизованный доступ') {
    super(message, 401, 'UNAUTHORIZED');
  }
}

/**
 * Доступ запрещен (403)
 */
class ForbiddenError extends AppError {
  constructor(message = 'Доступ запрещен') {
    super(message, 403, 'FORBIDDEN');
  }
}

/**
 * Конфликт данных (409)
 */
class ConflictError extends AppError {
  constructor(message = 'Конфликт данных', details = null) {
    super(message, 409, 'CONFLICT', details);
  }
}

/**
 * Ошибка базы данных (500)
 */
class DatabaseError extends AppError {
  constructor(message = 'Ошибка базы данных', originalError = null) {
    super(message, 500, 'DATABASE_ERROR');
    this.originalError = originalError;
  }
}

/**
 * Ошибка внешнего сервиса (502)
 */
class ExternalServiceError extends AppError {
  constructor(serviceName, message = 'Ошибка внешнего сервиса', originalError = null) {
    super(message, 502, 'EXTERNAL_SERVICE_ERROR');
    this.serviceName = serviceName;
    this.originalError = originalError;
  }
}

/**
 * Ошибка недоступности сервиса (503)
 */
class ServiceUnavailableError extends AppError {
  constructor(message = 'Сервис временно недоступен') {
    super(message, 503, 'SERVICE_UNAVAILABLE');
  }
}

/**
 * Ошибка таймаута (504)
 */
class TimeoutError extends AppError {
  constructor(message = 'Превышено время ожидания') {
    super(message, 504, 'TIMEOUT');
  }
}

/**
 * Ошибка превышения лимита запросов (429)
 */
class RateLimitError extends AppError {
  constructor(message = 'Превышен лимит запросов', retryAfter = null) {
    super(message, 429, 'RATE_LIMIT_EXCEEDED');
    this.retryAfter = retryAfter;
  }
}

/**
 * Ошибка бизнес-логики (422)
 */
class BusinessLogicError extends AppError {
  constructor(message, details = null) {
    super(message, 422, 'BUSINESS_LOGIC_ERROR', details);
  }
}

/**
 * Коды ошибок
 */
const ErrorCodes = {
  // Общие
  INTERNAL_ERROR: 'INTERNAL_ERROR',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  NOT_FOUND: 'NOT_FOUND',
  UNAUTHORIZED: 'UNAUTHORIZED',
  FORBIDDEN: 'FORBIDDEN',
  CONFLICT: 'CONFLICT',
  
  // База данных
  DATABASE_ERROR: 'DATABASE_ERROR',
  DATABASE_CONNECTION_ERROR: 'DATABASE_CONNECTION_ERROR',
  QUERY_ERROR: 'QUERY_ERROR',
  
  // Внешние сервисы
  EXTERNAL_SERVICE_ERROR: 'EXTERNAL_SERVICE_ERROR',
  SERVICE_UNAVAILABLE: 'SERVICE_UNAVAILABLE',
  TIMEOUT: 'TIMEOUT',
  
  // Аутентификация
  INVALID_CREDENTIALS: 'INVALID_CREDENTIALS',
  TOKEN_EXPIRED: 'TOKEN_EXPIRED',
  TOKEN_INVALID: 'TOKEN_INVALID',
  TOKEN_BLACKLISTED: 'TOKEN_BLACKLISTED',
  
  // Бизнес-логика
  BUSINESS_LOGIC_ERROR: 'BUSINESS_LOGIC_ERROR',
  RATE_LIMIT_EXCEEDED: 'RATE_LIMIT_EXCEEDED',
  INSUFFICIENT_PERMISSIONS: 'INSUFFICIENT_PERMISSIONS',
  DUPLICATE_ENTRY: 'DUPLICATE_ENTRY',
  INVALID_STATE: 'INVALID_STATE',
  
  // Claude API
  CLAUDE_API_ERROR: 'CLAUDE_API_ERROR',
  CLAUDE_API_KEY_MISSING: 'CLAUDE_API_KEY_MISSING',
  CLAUDE_API_KEY_INVALID: 'CLAUDE_API_KEY_INVALID',
  CLAUDE_QUOTA_EXCEEDED: 'CLAUDE_QUOTA_EXCEEDED',
  
  // Графы
  GRAPH_VALIDATION_ERROR: 'GRAPH_VALIDATION_ERROR',
  CIRCULAR_DEPENDENCY: 'CIRCULAR_DEPENDENCY',
  INVALID_RELATIONSHIP: 'INVALID_RELATIONSHIP',
  
  // Синтез
  SYNTHESIS_ERROR: 'SYNTHESIS_ERROR',
  INCOMPATIBLE_CONCEPTS: 'INCOMPATIBLE_CONCEPTS'
};

/**
 * Проверка, является ли ошибка операционной
 */
function isOperationalError(error) {
  if (error instanceof AppError) {
    return error.isOperational;
  }
  return false;
}

module.exports = {
  AppError,
  ValidationError,
  NotFoundError,
  UnauthorizedError,
  ForbiddenError,
  ConflictError,
  DatabaseError,
  ExternalServiceError,
  ServiceUnavailableError,
  TimeoutError,
  RateLimitError,
  BusinessLogicError,
  ErrorCodes,
  isOperationalError
};