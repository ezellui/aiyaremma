/**
 * Контроллер для синтеза концепций
 */

const responseBuilder = require('@philos/shared').responseBuilder;
const proxyService = require('../services/proxy');

class SynthesisController {
  /**
   * Анализ совместимости концепций
   */
  async analyzeCompatibility(req, res) {
    const { concept1Id, concept2Id } = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.post(
      'synthesis',
      '/api/synthesis/analyze-compatibility',
      { concept1Id, concept2Id },
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Анализ совместимости выполнен');
  }
  
  /**
   * Создание синтезированной концепции
   */
  async synthesize(req, res) {
    const { concept1Id, concept2Id, method, focus, innovationDegree } = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.post(
      'synthesis',
      '/api/synthesis',
      { concept1Id, concept2Id, method, focus, innovationDegree },
      userHeaders
    );
    
    return responseBuilder.created(res, result.data, 'Синтезированная концепция создана');
  }
  
  /**
   * Синтез с учётом количественных характеристик
   */
  async synthesizeWithCharacteristics(req, res) {
    const { concept1Id, concept2Id, method, focus, innovationDegree, characteristicsConfig } = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.post(
      'synthesis',
      '/api/synthesis/with-characteristics',
      { concept1Id, concept2Id, method, focus, innovationDegree, characteristicsConfig },
      userHeaders
    );
    
    return responseBuilder.created(res, result.data, 'Синтез с характеристиками выполнен');
  }
  
  /**
   * Получение данных синтеза
   */
  async getById(req, res) {
    const { id } = req.params;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.get(
      'synthesis',
      `/api/synthesis/${id}`,
      {},
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Данные синтеза получены');
  }
  
  /**
   * Критический анализ синтезированной концепции
   */
  async critique(req, res) {
    const { id } = req.params;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.post(
      'synthesis',
      `/api/synthesis/${id}/critique`,
      {},
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Критический анализ выполнен');
  }
  
  /**
   * Получение истории синтезов пользователя
   */
  async getHistory(req, res) {
    const { page = 1, limit = 10 } = req.query;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.get(
      'synthesis',
      '/api/synthesis/history',
      { page, limit },
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'История синтезов получена');
  }
  
  /**
   * Определение родительских концепций
   */
  async identifyParentConcepts(req, res) {
    const { conceptId, analysisType } = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.post(
      'synthesis',
      '/api/synthesis/identify-concepts',
      { conceptId, analysisType },
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Родительские концепции определены');
  }
}

module.exports = new SynthesisController();