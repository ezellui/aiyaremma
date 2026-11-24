/**
 * Контроллер для работы с концепциями
 */

const responseBuilder = require('@philos/shared').responseBuilder;
const proxyService = require('../services/proxy');

class ConceptController {
  /**
   * Получение списка концепций
   */
  async getAll(req, res) {
    const { page = 1, limit = 10, search, userId } = req.query;
    const userHeaders = req.user ? proxyService.addUserHeaders(req.user) : {};
    
    const result = await proxyService.get(
      'concept',
      '/api/concepts',
      { page, limit, search, userId },
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Концепции получены');
  }
  
  /**
   * Получение концепции по ID
   */
  async getById(req, res) {
    const { id } = req.params;
    const userHeaders = req.user ? proxyService.addUserHeaders(req.user) : {};
    
    const result = await proxyService.get(
      'concept',
      `/api/concepts/${id}`,
      {},
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Концепция получена');
  }
  
  /**
   * Создание новой концепции
   */
  async create(req, res) {
    const conceptData = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.post(
      'concept',
      '/api/concepts',
      conceptData,
      userHeaders
    );
    
    return responseBuilder.created(res, result.data, 'Концепция создана');
  }
  
  /**
   * Обновление концепции
   */
  async update(req, res) {
    const { id } = req.params;
    const conceptData = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.put(
      'concept',
      `/api/concepts/${id}`,
      conceptData,
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Концепция обновлена');
  }
  
  /**
   * Удаление концепции
   */
  async delete(req, res) {
    const { id } = req.params;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    await proxyService.delete(
      'concept',
      `/api/concepts/${id}`,
      userHeaders
    );
    
    return responseBuilder.noContent(res);
  }
  
  /**
   * Генерация/установка названия концепции
   */
  async setName(req, res) {
    const { id } = req.params;
    const { name, generateAlternatives } = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.post(
      'concept',
      `/api/concepts/${id}/name`,
      { name, generateAlternatives },
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Название концепции обновлено');
  }
}

module.exports = new ConceptController();