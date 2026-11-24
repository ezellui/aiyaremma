/**
 * Классы ошибок и коды ошибок
 */

const HTTP_STATUS = require('../constants/http-status');

/**
 * Коды ошибок приложения
 */
const ErrorCodes = {
  // Общие ошибки
  INTERNAL_ERROR: 'INTERNAL_ERROR',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  NOT_FOUND: 'NOT_FOUND',
  UNAUTHORIZED: 'UNAUTHORIZED',
  FORBIDDEN: 'FORBIDDEN',
  CONFLICT: 'CONFLICT',
  
  // Ошибки баз данных
  DATABASE_ERROR: 'DATABASE_ERROR',
  CONNECTION_ERROR: 'CONNECTION_ERROR',
  
  // Ошибки бизнес-логики
  CONCEPT_NOT_FOUND: 'CONCEPT_NOT_FOUND',
  CATEGORY_NOT_FOUND: 'CATEGORY_NOT_FOUND',
  RELATIONSHIP_NOT_FOUND: 'RELATIONSHIP_NOT_FOUND',
  THESIS_NOT_FOUND: 'THESIS_NOT_FOUND',
  INVALID_GRAPH_STRUCTURE: 'INVALID_GRAPH_STRUCTURE',
  SYNTHESIS_ERROR: 'SYNTHESIS_ERROR',
  
  // Ошибки Claude API
  CLAUDE_API_ERROR: 'CLAUDE_API_ERROR',
  CLAUDE_RATE_LIMIT: 'CLAUDE_RATE_LIMIT',
  INVALID_API_KEY: 'INVALID_API_KEY'
};

/**
 * Базовый класс ошибки приложения
 */
class AppError extends Error {
  constructor(message, statusCode = HTTP_STATUS.INTERNAL_SERVER_ERROR, errorCode = ErrorCodes.INTERNAL_ERROR, isOperational = true) {
    super(message);
    
    this.statusCode = statusCode;
    this.errorCode = errorCode;
    this.isOperational = isOperational;
    this.timestamp = new Date().toISOString();
    
    Error.captureStackTrace(this, this.constructor);
  }
  
  toJSON() {
    return {
      error: {
        message: this.message,
        code: this.errorCode,
        statusCode: this.statusCode,
        timestamp: this.timestamp
      }
    };
  }
}

/**
 * Ошибка валидации
 */
class ValidationError extends AppError {
  constructor(message, errors = []) {
    super(message, HTTP_STATUS.BAD_REQUEST, ErrorCodes.VALIDATION_ERROR);
    this.errors = errors;
  }
  
  toJSON() {
    return {
      error: {
        message: this.message,
        code: this.errorCode,
        statusCode: this.statusCode,
        timestamp: this.timestamp,
        details: this.errors
      }
    };
  }
}

/**
 * Ошибка "не найдено"
 */
class NotFoundError extends AppError {
  constructor(resource, identifier) {
    super(
      `${resource} с идентификатором ${identifier} не найден`,
      HTTP_STATUS.NOT_FOUND,
      ErrorCodes.NOT_FOUND
    );
    this.resource = resource;
    this.identifier = identifier;
  }
}

/**
 * Ошибка аутентификации
 */
class UnauthorizedError extends AppError {
  constructor(message = 'Требуется аутентификация') {
    super(message, HTTP_STATUS.UNAUTHORIZED, ErrorCodes.UNAUTHORIZED);
  }
}

/**
 * Ошибка доступа
 */
class ForbiddenError extends AppError {
  constructor(message = 'Доступ запрещен') {
    super(message, HTTP_STATUS.FORBIDDEN, ErrorCodes.FORBIDDEN);
  }
}

/**
 * Ошибка конфликта
 */
class ConflictError extends AppError {
  constructor(message) {
    super(message, HTTP_STATUS.CONFLICT, ErrorCodes.CONFLICT);
  }
}

/**
 * Ошибка базы данных
 */
class DatabaseError extends AppError {
  constructor(message, originalError = null) {
    super(message, HTTP_STATUS.INTERNAL_SERVER_ERROR, ErrorCodes.DATABASE_ERROR, false);
    this.originalError = originalError;
  }
}

module.exports = {
  ErrorCodes,
  AppError,
  ValidationError,
  NotFoundError,
  UnauthorizedError,
  ForbiddenError,
  ConflictError,
  DatabaseError
};