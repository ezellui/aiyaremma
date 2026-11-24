/**
 * Контроллер для практического применения концепций
 */

const responseBuilder = require('@philos/shared').responseBuilder;
const proxyService = require('../services/proxy');

class PracticalController {
  /**
   * Создание анализа практического применения
   */
  async analyze(req, res) {
    const { conceptId, domains, detailed } = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.post(
      'practical',
      '/api/practical/analyze',
      { conceptId, domains, detailed },
      userHeaders
    );
    
    return responseBuilder.created(res, result.data, 'Анализ практического применения создан');
  }
  
  /**
   * Получение анализа практического применения концепции
   */
  async getConceptApplication(req, res) {
    const { conceptId } = req.params;
    const userHeaders = req.user ? proxyService.addUserHeaders(req.user) : {};
    
    const result = await proxyService.get(
      'practical',
      `/api/practical/concepts/${conceptId}`,
      {},
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Практическое применение получено');
  }
  
  /**
   * Получение конкретного анализа
   */
  async getById(req, res) {
    const { id } = req.params;
    const userHeaders = req.user ? proxyService.addUserHeaders(req.user) : {};
    
    const result = await proxyService.get(
      'practical',
      `/api/practical/${id}`,
      {},
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Анализ получен');
  }
  
  /**
   * Обновление анализа
   */
  async update(req, res) {
    const { id } = req.params;
    const applicationData = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.put(
      'practical',
      `/api/practical/${id}`,
      applicationData,
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Анализ обновлен');
  }
  
  /**
   * Удаление анализа
   */
  async delete(req, res) {
    const { id } = req.params;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    await proxyService.delete(
      'practical',
      `/api/practical/${id}`,
      userHeaders
    );
    
    return responseBuilder.noContent(res);
  }
  
  /**
   * Получение концепций, применимых в определенной области
   */
  async getByDomain(req, res) {
    const { domain } = req.params;
    const userHeaders = req.user ? proxyService.addUserHeaders(req.user) : {};
    
    const result = await proxyService.get(
      'practical',
      `/api/practical/domains/${domain}`,
      {},
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Концепции области получены');
  }
  
  /**
   * Получение областей применения для конкретного тезиса
   */
  async getByThesis(req, res) {
    const { thesisId } = req.params;
    const userHeaders = req.user ? proxyService.addUserHeaders(req.user) : {};
    
    const result = await proxyService.get(
      'practical',
      `/api/practical/theses/${thesisId}`,
      {},
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Области применения тезиса получены');
  }
}

module.exports = new PracticalController();