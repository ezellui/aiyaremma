/**
 * Контроллер для взаимодействия с Claude
 */

const responseBuilder = require('@philos/shared').responseBuilder;
const proxyService = require('../services/proxy');

class ClaudeController {
  /**
   * Синхронный запрос к Claude
   */
  async query(req, res) {
    const { queryType, content, parameters } = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.post(
      'claude',
      '/api/claude/query',
      { queryType, content, parameters },
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Запрос к Claude выполнен');
  }
  
  /**
   * Асинхронный запрос к Claude (через очередь)
   */
  async queueQuery(req, res) {
    const { queryType, content, parameters } = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.post(
      'claude',
      '/api/claude/queue-query',
      { queryType, content, parameters },
      userHeaders
    );
    
    return responseBuilder.accepted(res, result.data, 'Запрос поставлен в очередь');
  }
  
  /**
   * Получение статуса и результата асинхронного запроса
   */
  async getTaskStatus(req, res) {
    const { id } = req.params;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.get(
      'claude',
      `/api/claude/tasks/${id}`,
      {},
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Статус задачи получен');
  }
  
  /**
   * Получение истории взаимодействий с Claude
   */
  async getInteractions(req, res) {
    const { page = 1, limit = 10, conceptId, queryType } = req.query;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.get(
      'claude',
      '/api/claude/interactions',
      { page, limit, conceptId, queryType },
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'История взаимодействий получена');
  }
  
  /**
   * Получение шаблонов запросов
   */
  async getTemplates(req, res) {
    const { category } = req.query;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.get(
      'claude',
      '/api/claude/templates',
      { category },
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Шаблоны запросов получены');
  }
}

module.exports = new ClaudeController();