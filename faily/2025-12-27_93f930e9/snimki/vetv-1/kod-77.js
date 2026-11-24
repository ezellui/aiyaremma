/**
 * Контроллер для исторической контекстуализации
 */

const responseBuilder = require('@philos/shared').responseBuilder;
const proxyService = require('../services/proxy');

class HistoricalController {
  /**
   * Создание исторической контекстуализации
   */
  async analyze(req, res) {
    const { conceptId, traditions, philosophers, timeContext } = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.post(
      'historical',
      '/api/historical/analyze',
      { conceptId, traditions, philosophers, timeContext },
      userHeaders
    );
    
    return responseBuilder.created(res, result.data, 'Историческая контекстуализация создана');
  }
  
  /**
   * Получение исторической контекстуализации концепции
   */
  async getConceptContext(req, res) {
    const { conceptId } = req.params;
    const userHeaders = req.user ? proxyService.addUserHeaders(req.user) : {};
    
    const result = await proxyService.get(
      'historical',
      `/api/historical/concepts/${conceptId}`,
      {},
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Исторический контекст получен');
  }
  
  /**
   * Получение конкретной исторической контекстуализации
   */
  async getById(req, res) {
    const { id } = req.params;
    const userHeaders = req.user ? proxyService.addUserHeaders(req.user) : {};
    
    const result = await proxyService.get(
      'historical',
      `/api/historical/${id}`,
      {},
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Историческая контекстуализация получена');
  }
  
  /**
   * Обновление исторической контекстуализации
   */
  async update(req, res) {
    const { id } = req.params;
    const contextData = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.put(
      'historical',
      `/api/historical/${id}`,
      contextData,
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Историческая контекстуализация обновлена');
  }
  
  /**
   * Удаление исторической контекстуализации
   */
  async delete(req, res) {
    const { id } = req.params;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    await proxyService.delete(
      'historical',
      `/api/historical/${id}`,
      userHeaders
    );
    
    return responseBuilder.noContent(res);
  }
  
  /**
   * Получение концепций, связанных с традицией
   */
  async getByTradition(req, res) {
    const { traditionId } = req.params;
    const userHeaders = req.user ? proxyService.addUserHeaders(req.user) : {};
    
    const result = await proxyService.get(
      'historical',
      `/api/historical/traditions/${traditionId}`,
      {},
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Концепции традиции получены');
  }
  
  /**
   * Получение концепций, связанных с философом
   */
  async getByPhilosopher(req, res) {
    const { philosopherId } = req.params;
    const userHeaders = req.user ? proxyService.addUserHeaders(req.user) : {};
    
    const result = await proxyService.get(
      'historical',
      `/api/historical/philosophers/${philosopherId}`,
      {},
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Концепции философа получены');
  }
}

module.exports = new HistoricalController();