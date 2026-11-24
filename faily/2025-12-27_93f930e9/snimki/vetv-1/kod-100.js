/**
 * Контроллер для управления пользователями
 */

const responseBuilder = require('@philos/shared').responseBuilder;
const proxyService = require('../services/proxy');
const { ForbiddenError } = require('@philos/shared');

class UserController {
  /**
   * Проверка прав доступа к профилю
   */
  checkAccess(userId, requestUserId) {
    if (userId !== requestUserId) {
      throw new ForbiddenError('Нет доступа к данному профилю');
    }
  }

  /**
   * Получение данных пользователя
   */
  async getById(req, res) {
    const { id } = req.params;
    this.checkAccess(id, req.user.userId);
    
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.get(
      'user',
      `/api/users/${id}`,
      {},
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Данные пользователя получены');
  }
  
  /**
   * Обновление данных пользователя
   */
  async update(req, res) {
    const { id } = req.params;
    this.checkAccess(id, req.user.userId);
    
    const userData = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.put(
      'user',
      `/api/users/${id}`,
      userData,
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Данные пользователя обновлены');
  }
  
  /**
   * Получение активности пользователя
   */
  async getActivity(req, res) {
    const { id } = req.params;
    this.checkAccess(id, req.user.userId);
    
    const { page = 1, limit = 20, activityType } = req.query;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.get(
      'user',
      `/api/users/${id}/activity`,
      { page, limit, activityType },
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Активность пользователя получена');
  }
  
  /**
   * Установка/обновление ключа API Claude
   */
  async setApiKey(req, res) {
    const { id } = req.params;
    this.checkAccess(id, req.user.userId);
    
    const { apiKey } = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.post(
      'user',
      `/api/users/${id}/api-key`,
      { apiKey },
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Ключ API сохранен');
  }
  
  /**
   * Удаление ключа API Claude
   */
  async deleteApiKey(req, res) {
    const { id } = req.params;
    this.checkAccess(id, req.user.userId);
    
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    await proxyService.delete(
      'user',
      `/api/users/${id}/api-key`,
      userHeaders
    );
    
    return responseBuilder.noContent(res);
  }
  
  /**
   * Получение статистики использования API
   */
  async getApiKeyUsage(req, res) {
    const { id } = req.params;
    this.checkAccess(id, req.user.userId);
    
    const { startDate, endDate } = req.query;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.get(
      'user',
      `/api/users/${id}/api-key/usage`,
      { startDate, endDate },
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Статистика использования получена');
  }
  
  /**
   * Создание совместного доступа к ключу API
   */
  async shareApiKey(req, res) {
    const { id } = req.params;
    this.checkAccess(id, req.user.userId);
    
    const { sharedWithId, expiresAt, permissions } = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.post(
      'user',
      `/api/users/${id}/api-key/share`,
      { sharedWithId, expiresAt, permissions },
      userHeaders
    );
    
    return responseBuilder.created(res, result.data, 'Совместный доступ создан');
  }
  
  /**
   * Получение доступных общих ключей
   */
  async getSharedKeys(req, res) {
    const { id } = req.params;
    this.checkAccess(id, req.user.userId);
    
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.get(
      'user',
      `/api/users/${id}/shared-keys`,
      {},
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Общие ключи получены');
  }
  
  /**
   * Отзыв совместного доступа
   */
  async revokeSharedKey(req, res) {
    const { id, shareId } = req.params;
    this.checkAccess(id, req.user.userId);
    
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    await proxyService.delete(
      'user',
      `/api/users/${id}/api-key/share/${shareId}`,
      userHeaders
    );
    
    return responseBuilder.noContent(res);
  }
}

module.exports = new UserController();