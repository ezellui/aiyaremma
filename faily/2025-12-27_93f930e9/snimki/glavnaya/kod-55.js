/**
 * Базовый сервис для бизнес-логики
 */

const { NotFoundError, ValidationError } = require('@philos/shared');
const logger = require('@philos/shared').logger;

class BaseService {
  constructor(serviceName) {
    this.serviceName = serviceName;
    this.logger = logger.createServiceLogger(serviceName);
  }

  /**
   * Обработка ошибок
   */
  handleError(error, operation) {
    this.logger.error(`Error in ${operation}:`, error);
    throw error;
  }

  /**
   * Валидация ID
   */
  validateId(id, resourceName = 'Resource') {
    if (!id) {
      throw new ValidationError(`${resourceName} ID is required`);
    }
    // Можно добавить дополнительную валидацию UUID
  }

  /**
   * Проверка существования ресурса
   */
  ensureExists(resource, resourceName, id) {
    if (!resource) {
      throw new NotFoundError(resourceName, id);
    }
    return resource;
  }
}

module.exports = BaseService;