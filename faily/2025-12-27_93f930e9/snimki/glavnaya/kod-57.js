/**
 * Middleware для валидации запросов
 */

const { ValidationError } = require('@philos/shared');

/**
 * Создает middleware для валидации с использованием Joi схемы
 */
function validate(schema, property = 'body') {
  return (req, res, next) => {
    const { error, value } = schema.validate(req[property], {
      abortEarly: false,
      stripUnknown: true
    });

    if (error) {
      const errors = error.details.map(detail => ({
        field: detail.path.join('.'),
        message: detail.message
      }));
      
      return next(new ValidationError('Validation failed', errors));
    }

    // Заменяем оригинальные данные валидированными
    req[property] = value;
    next();
  };
}

/**
 * Валидация параметров пути
 */
function validateParams(schema) {
  return validate(schema, 'params');
}

/**
 * Валидация query параметров
 */
function validateQuery(schema) {
  return validate(schema, 'query');
}

/**
 * Валидация тела запроса
 */
function validateBody(schema) {
  return validate(schema, 'body');
}

module.exports = {
  validate,
  validateParams,
  validateQuery,
  validateBody
};