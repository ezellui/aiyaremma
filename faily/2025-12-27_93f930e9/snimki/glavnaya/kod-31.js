/**
 * Построитель стандартизированных ответов API
 */

const HTTP_STATUS = require('../constants/http-status');

/**
 * Успешный ответ
 */
function success(res, data, message = 'Success', statusCode = HTTP_STATUS.OK) {
  return res.status(statusCode).json({
    success: true,
    message,
    data,
    timestamp: new Date().toISOString()
  });
}

/**
 * Ответ с созданным ресурсом
 */
function created(res, data, message = 'Resource created') {
  return success(res, data, message, HTTP_STATUS.CREATED);
}

/**
 * Ответ без содержимого
 */
function noContent(res) {
  return res.status(HTTP_STATUS.NO_CONTENT).send();
}

/**
 * Ответ с ошибкой
 */
function error(res, message, statusCode = HTTP_STATUS.INTERNAL_SERVER_ERROR, errorCode = null, details = null) {
  const response = {
    success: false,
    error: {
      message,
      code: errorCode,
      timestamp: new Date().toISOString()
    }
  };
  
  if (details) {
    response.error.details = details;
  }
  
  return res.status(statusCode).json(response);
}

/**
 * Ответ с пагинацией
 */
function paginated(res, data, pagination, message = 'Success') {
  return res.status(HTTP_STATUS.OK).json({
    success: true,
    message,
    data,
    pagination: {
      page: pagination.page,
      limit: pagination.limit,
      total: pagination.total,
      totalPages: Math.ceil(pagination.total / pagination.limit)
    },
    timestamp: new Date().toISOString()
  });
}

module.exports = {
  success,
  created,
  noContent,
  error,
  paginated
};