/**
 * Контроллер для диалогической интерпретации
 */

const responseBuilder = require('@philos/shared').responseBuilder;
const proxyService = require('../services/proxy');

class DialogueController {
  /**
   * Создание нового диалога
   */
  async create(req, res) {
    const { concept1Id, concept2Id, topic, options } = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.post(
      'dialogue',
      '/api/dialogue',
      { concept1Id, concept2Id, topic, options },
      userHeaders
    );
    
    return responseBuilder.created(res, result.data, 'Диалог создан');
  }
  
  /**
   * Получение конкретного диалога
   */
  async getById(req, res) {
    const { id } = req.params;
    const userHeaders = req.user ? proxyService.addUserHeaders(req.user) : {};
    
    const result = await proxyService.get(
      'dialogue',
      `/api/dialogue/${id}`,
      {},
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Диалог получен');
  }
  
  /**
   * Обновление диалога
   */
  async update(req, res) {
    const { id } = req.params;
    const dialogueData = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.put(
      'dialogue',
      `/api/dialogue/${id}`,
      dialogueData,
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Диалог обновлен');
  }
  
  /**
   * Удаление диалога
   */
  async delete(req, res) {
    const { id } = req.params;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    await proxyService.delete(
      'dialogue',
      `/api/dialogue/${id}`,
      userHeaders
    );
    
    return responseBuilder.noContent(res);
  }
  
  /**
   * Получение диалогов с участием концепции
   */
  async getByConceptId(req, res) {
    const { conceptId } = req.params;
    const userHeaders = req.user ? proxyService.addUserHeaders(req.user) : {};
    
    const result = await proxyService.get(
      'dialogue',
      `/api/dialogue/concepts/${conceptId}`,
      {},
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Диалоги концепции получены');
  }
  
  /**
   * Анализ существующего диалога
   */
  async analyze(req, res) {
    const { dialogueId } = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.post(
      'dialogue',
      '/api/dialogue/analyze',
      { dialogueId },
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Анализ диалога выполнен');
  }
  
  /**
   * Получение предложений философских вопросов для диалога
   */
  async suggestQuestions(req, res) {
    const { concept1Id, concept2Id, count = 5 } = req.query;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.get(
      'dialogue',
      '/api/dialogue/questions',
      { concept1Id, concept2Id, count },
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Вопросы для диалога предложены');
  }
  
  /**
   * Получение структурированных аргументов из диалога
   */
  async getArguments(req, res) {
    const { dialogueId } = req.params;
    const userHeaders = req.user ? proxyService.addUserHeaders(req.user) : {};
    
    const result = await proxyService.get(
      'dialogue',
      `/api/dialogue/${dialogueId}/arguments`,
      {},
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Аргументы диалога получены');
  }
}

module.exports = new DialogueController();