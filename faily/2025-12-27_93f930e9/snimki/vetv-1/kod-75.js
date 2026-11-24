/**
 * Контроллер для анализа названий концепций
 */

const responseBuilder = require('@philos/shared').responseBuilder;
const proxyService = require('../services/proxy');

class NameAnalysisController {
  /**
   * Анализ названия концепции
   */
  async analyze(req, res) {
    const { conceptId, name } = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.post(
      'nameAnalysis',
      '/api/name-analysis/analyze',
      { conceptId, name },
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Анализ названия выполнен');
  }
  
  /**
   * Предложение альтернативных названий
   */
  async suggestAlternatives(req, res) {
    const { conceptId, count = 5 } = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.post(
      'nameAnalysis',
      '/api/name-analysis/suggest-alternatives',
      { conceptId, count },
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Альтернативные названия сгенерированы');
  }
  
  /**
   * Получение истории анализа названий
   */
  async getHistory(req, res) {
    const { page = 1, limit = 10 } = req.query;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.get(
      'nameAnalysis',
      '/api/name-analysis/history',
      { page, limit },
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'История анализа названий получена');
  }
}

module.exports = new NameAnalysisController();