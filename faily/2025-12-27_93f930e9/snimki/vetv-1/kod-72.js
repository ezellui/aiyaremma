/**
 * Контроллер для работы с тезисами
 */

const responseBuilder = require('@philos/shared').responseBuilder;
const proxyService = require('../services/proxy');

class ThesisController {
  /**
   * Получение тезисов концепции
   */
  async getConceptTheses(req, res) {
    const { conceptId } = req.params;
    const { type, style } = req.query;
    const userHeaders = req.user ? proxyService.addUserHeaders(req.user) : {};
    
    const result = await proxyService.get(
      'thesis',
      `/api/theses/concepts/${conceptId}`,
      { type, style },
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Тезисы получены');
  }
  
  /**
   * Получение конкретного тезиса
   */
  async getById(req, res) {
    const { id } = req.params;
    const userHeaders = req.user ? proxyService.addUserHeaders(req.user) : {};
    
    const result = await proxyService.get(
      'thesis',
      `/api/theses/${id}`,
      {},
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Тезис получен');
  }
  
  /**
   * Генерация тезисов для концепции
   */
  async generateTheses(req, res) {
    const { conceptId } = req.params;
    const { quantity, thesisType, style } = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.post(
      'thesis',
      `/api/theses/concepts/${conceptId}`,
      { quantity, thesisType, style },
      userHeaders
    );
    
    return responseBuilder.created(res, result.data, 'Тезисы сгенерированы');
  }
  
  /**
   * Генерация тезисов с учётом количественных характеристик
   */
  async generateThesesWithCharacteristics(req, res) {
    const { conceptId } = req.params;
    const { quantity, thesisType, characteristicsConfig } = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.post(
      'thesis',
      `/api/theses/concepts/${conceptId}/generate-with-characteristics`,
      { quantity, thesisType, characteristicsConfig },
      userHeaders
    );
    
    return responseBuilder.created(res, result.data, 'Тезисы с характеристиками сгенерированы');
  }
  
  /**
   * Обновление тезиса
   */
  async update(req, res) {
    const { id } = req.params;
    const thesisData = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.put(
      'thesis',
      `/api/theses/${id}`,
      thesisData,
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Тезис обновлен');
  }
  
  /**
   * Удаление тезиса
   */
  async delete(req, res) {
    const { id } = req.params;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    await proxyService.delete(
      'thesis',
      `/api/theses/${id}`,
      userHeaders
    );
    
    return responseBuilder.noContent(res);
  }
  
  /**
   * Развитие и обоснование тезиса
   */
  async elaborate(req, res) {
    const { id } = req.params;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.post(
      'thesis',
      `/api/theses/${id}/elaborate`,
      {},
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Тезис развит и обоснован');
  }
  
  /**
   * Сравнение наборов тезисов
   */
  async compare(req, res) {
    const { thesesWithoutCharacteristics, thesesWithCharacteristics, characteristicsConfig } = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.post(
      'thesis',
      '/api/theses/compare',
      { thesesWithoutCharacteristics, thesesWithCharacteristics, characteristicsConfig },
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Сравнение тезисов выполнено');
  }
  
  /**
   * Анализ происхождения на основе тезисов
   */
  async analyzeOrigin(req, res) {
    const { thesisIds } = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.post(
      'thesis',
      '/api/theses/analyze-origin',
      { thesisIds },
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Анализ происхождения выполнен');
  }
}

module.exports = new ThesisController();