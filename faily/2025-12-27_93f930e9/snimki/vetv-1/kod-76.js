/**
 * Контроллер для определения происхождения концепций
 */

const responseBuilder = require('@philos/shared').responseBuilder;
const proxyService = require('../services/proxy');

class OriginController {
  /**
   * Определение происхождения концепции
   */
  async detect(req, res) {
    const { conceptId, analysisType } = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.post(
      'origin',
      '/api/origin/detect',
      { conceptId, analysisType },
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Происхождение концепции определено');
  }
  
  /**
   * Получение данных о происхождении концепции
   */
  async getConceptOrigin(req, res) {
    const { conceptId } = req.params;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.get(
      'origin',
      `/api/origin/concepts/${conceptId}`,
      {},
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Данные о происхождении получены');
  }
  
  /**
   * Получение конкретного анализа происхождения
   */
  async getById(req, res) {
    const { id } = req.params;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.get(
      'origin',
      `/api/origin/${id}`,
      {},
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Анализ происхождения получен');
  }
}

module.exports = new OriginController();