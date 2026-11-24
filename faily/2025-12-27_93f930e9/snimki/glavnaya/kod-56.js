/**
 * Базовый контроллер для обработки HTTP запросов
 */

const { responseBuilder } = require('@philos/shared');

class BaseController {
  constructor(service) {
    this.service = service;
  }

  /**
   * Обработка успешного ответа
   */
  sendSuccess(res, data, message = 'Success', statusCode = 200) {
    return responseBuilder.success(res, data, message, statusCode);
  }

  /**
   * Обработка ответа с созданным ресурсом
   */
  sendCreated(res, data, message = 'Resource created') {
    return responseBuilder.created(res, data, message);
  }

  /**
   * Обработка ответа без содержимого
   */
  sendNoContent(res) {
    return responseBuilder.noContent(res);
  }

  /**
   * Обработка пагинированного ответа
   */
  sendPaginated(res, data, pagination, message = 'Success') {
    return responseBuilder.paginated(res, data, pagination, message);
  }

  /**
   * Извлечение параметров пагинации из запроса
   */
  getPaginationParams(req) {
    const page = parseInt(req.query.page, 10) || 1;
    const limit = parseInt(req.query.limit, 10) || 10;
    const offset = (page - 1) * limit;

    return { page, limit, offset };
  }

  /**
   * Извлечение ID из параметров запроса
   */
  getIdParam(req, paramName = 'id') {
    return req.params[paramName];
  }
}

module.exports = BaseController;