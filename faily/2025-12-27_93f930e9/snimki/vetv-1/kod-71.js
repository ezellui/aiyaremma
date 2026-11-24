/**
 * Контроллер для работы с графами концепций
 */

const responseBuilder = require('@philos/shared').responseBuilder;
const proxyService = require('../services/proxy');

class GraphController {
  /**
   * Получение полного графа концепции
   */
  async getConceptGraph(req, res) {
    const { conceptId } = req.params;
    const userHeaders = req.user ? proxyService.addUserHeaders(req.user) : {};
    
    const result = await proxyService.get(
      'graph',
      `/api/graphs/concepts/${conceptId}`,
      {},
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Граф концепции получен');
  }
  
  /**
   * Создание категории в графе
   */
  async createCategory(req, res) {
    const { conceptId } = req.params;
    const categoryData = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.post(
      'graph',
      `/api/graphs/concepts/${conceptId}/categories`,
      categoryData,
      userHeaders
    );
    
    return responseBuilder.created(res, result.data, 'Категория создана');
  }
  
  /**
   * Обновление категории
   */
  async updateCategory(req, res) {
    const { id } = req.params;
    const categoryData = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.put(
      'graph',
      `/api/graphs/categories/${id}`,
      categoryData,
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Категория обновлена');
  }
  
  /**
   * Удаление категории
   */
  async deleteCategory(req, res) {
    const { id } = req.params;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    await proxyService.delete(
      'graph',
      `/api/graphs/categories/${id}`,
      userHeaders
    );
    
    return responseBuilder.noContent(res);
  }
  
  /**
   * Создание связи между категориями
   */
  async createRelationship(req, res) {
    const relationshipData = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.post(
      'graph',
      '/api/graphs/relationships',
      relationshipData,
      userHeaders
    );
    
    return responseBuilder.created(res, result.data, 'Связь создана');
  }
  
  /**
   * Обновление связи
   */
  async updateRelationship(req, res) {
    const { id } = req.params;
    const relationshipData = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.put(
      'graph',
      `/api/graphs/relationships/${id}`,
      relationshipData,
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Связь обновлена');
  }
  
  /**
   * Удаление связи
   */
  async deleteRelationship(req, res) {
    const { id } = req.params;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    await proxyService.delete(
      'graph',
      `/api/graphs/relationships/${id}`,
      userHeaders
    );
    
    return responseBuilder.noContent(res);
  }
  
  /**
   * Валидация графа концепции
   */
  async validateGraph(req, res) {
    const { conceptId } = req.params;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.post(
      'graph',
      `/api/graphs/concepts/${conceptId}/validate`,
      {},
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Валидация графа выполнена');
  }
  
  /**
   * Обогащение графа концепции
   */
  async enrichGraph(req, res) {
    const { conceptId } = req.params;
    const { categoryId, relationshipId } = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.post(
      'graph',
      `/api/graphs/concepts/${conceptId}/enrich`,
      { categoryId, relationshipId },
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Обогащение графа выполнено');
  }
  
  /**
   * Генерация графа из тезисов
   */
  async generateFromTheses(req, res) {
    const { thesisIds, conceptId } = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.post(
      'graph',
      '/api/graphs/from-theses',
      { thesisIds, conceptId },
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Граф сгенерирован из тезисов');
  }
  
  /**
   * Получение количественных характеристик графа
   */
  async getCharacteristics(req, res) {
    const { conceptId } = req.params;
    const userHeaders = req.user ? proxyService.addUserHeaders(req.user) : {};
    
    const result = await proxyService.get(
      'graph',
      `/api/graphs/concepts/${conceptId}/characteristics`,
      {},
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Характеристики графа получены');
  }
  
  /**
   * Обновление количественных характеристик категории
   */
  async updateCategoryCharacteristics(req, res) {
    const { id } = req.params;
    const characteristics = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.post(
      'graph',
      `/api/graphs/categories/${id}/characteristics`,
      characteristics,
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Характеристики категории обновлены');
  }
  
  /**
   * Обновление количественных характеристик связи
   */
  async updateRelationshipCharacteristics(req, res) {
    const { id } = req.params;
    const characteristics = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.post(
      'graph',
      `/api/graphs/relationships/${id}/characteristics`,
      characteristics,
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Характеристики связи обновлены');
  }
  
  /**
   * Анализ происхождения концепции на основе графа
   */
  async analyzeOrigin(req, res) {
    const { conceptId } = req.body;
    const userHeaders = proxyService.addUserHeaders(req.user);
    
    const result = await proxyService.post(
      'graph',
      '/api/graphs/analyze-origin',
      { conceptId },
      userHeaders
    );
    
    return responseBuilder.success(res, result.data, 'Анализ происхождения выполнен');
  }
}

module.exports = new GraphController();