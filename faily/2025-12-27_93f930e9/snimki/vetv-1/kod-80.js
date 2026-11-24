/**
 * Контроллер для эволюции концепций
 */

const responseBuilder = require('@philos/shared').responseBuilder;
const proxyService = require('../services/proxy');

class EvolutionController {
  /**
   * Создание анализа эволюции концепции
   */
  async analyze(req, res) {
    const { conceptId } = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.post(
      'evolution',
      '/api/evolution/analyze',
      { conceptId },
      userHeaders
    );
    
    return responseBuilder.created(res, result.data, 'Анализ эволюции создан');
  }
  
  /**
   * Получение анализа эволюции для концепции
   */
  async getConceptEvolution(req, res) {
    const { conceptId } = req.params;
    const userHeaders = req.user ? proxyService.addUserHeaders(req.user) : {};
    
    const result = await proxyService.get(
      'evolution',
      `/api/evolution/concepts/${conceptId}`,
      {},
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Эволюция концепции получена');
  }
  
  /**
   * Получение конкретного анализа эволюции
   */
  async getById(req, res) {
    const { id } = req.params;
    const userHeaders = req.user ? proxyService.addUserHeaders(req.user) : {};
    
    const result = await proxyService.get(
      'evolution',
      `/api/evolution/${id}`,
      {},
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Анализ эволюции получен');
  }
  
  /**
   * Обновление анализа эволюции
   */
  async update(req, res) {
    const { id } = req.params;
    const evolutionData = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.put(
      'evolution',
      `/api/evolution/${id}`,
      evolutionData,
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Анализ эволюции обновлен');
  }
  
  /**
   * Удаление анализа эволюции
   */
  async delete(req, res) {
    const { id } = req.params;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    await proxyService.delete(
      'evolution',
      `/api/evolution/${id}`,
      userHeaders
    );
    
    return responseBuilder.noContent(res);
  }
  
  /**
   * Предложение конкретных изменений для эволюции концепции
   */
  async suggestChanges(req, res) {
    const { conceptId, scientificAreas, socialContexts } = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.post(
      'evolution',
      '/api/evolution/suggest-changes',
      { conceptId, scientificAreas, socialContexts },
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Изменения для эволюции предложены');
  }
  
  /**
   * Получение научного контекста для эволюции концепций
   */
  async getScientificContext(req, res) {
    const { area } = req.query;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.get(
      'evolution',
      '/api/evolution/scientific-context',
      { area },
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Научный контекст получен');
  }
}

module.exports = new EvolutionController();