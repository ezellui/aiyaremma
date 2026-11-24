/**
 * Контроллер графов
 */

const { responseBuilder } = require('@philos/shared');
const graphService = require('../services/graph.service');

class GraphController {
  /**
   * Получение графа концепции
   */
  async getGraph(req, res) {
    const { conceptId } = req.params;

    const graph = await graphService.getGraph(conceptId);

    return responseBuilder.success(res, graph.toJSON());
  }

  /**
   * Создание графа
   */
  async createGraph(req, res) {
    const userId = req.user?.id;
    const { conceptId } = req.params;
    const graphData = req.body;

    if (!userId) {
      return responseBuilder.error(res, 'Требуется аутентификация', 401);
    }

    const graph = await graphService.createGraph(conceptId, graphData);

    return responseBuilder.created(res, graph.toJSON(), 'Граф создан');
  }

  /**
   * Обновление графа
   */
  async updateGraph(req, res) {
    const userId = req.user?.id;
    const { conceptId } = req.params;
    const graphData = req.body;

    if (!userId) {
      return responseBuilder.error(res, 'Требуется аутентификация', 401);
    }

    const graph = await graphService.updateGraph(conceptId, graphData);

    return responseBuilder.success(res, graph.toJSON(), 'Граф обновлен');
  }

  /**
   * Удаление графа
   */
  async deleteGraph(req, res) {
    const userId = req.user?.id;
    const { conceptId } = req.params;

    if (!userId) {
      return responseBuilder.error(res, 'Требуется аутентификация', 401);
    }

    await graphService.deleteGraph(conceptId);

    return responseBuilder.success(res, null, 'Граф удален');
  }

  /**
   * Получение статистики графа
   */
  async getStats(req, res) {
    const { conceptId } = req.params;

    const stats = await graphService.getGraphStats(conceptId);

    return responseBuilder.success(res, stats);
  }

  /**
   * Получение подграфа
   */
  async getSubgraph(req, res) {
    const { conceptId } = req.params;
    const { categoryIds } = req.body;

    if (!categoryIds || !Array.isArray(categoryIds)) {
      return responseBuilder.error(res, 'Необходим массив categoryIds', 400);
    }

    const subgraph = await graphService.getSubgraph(categoryIds, conceptId);

    return responseBuilder.success(res, subgraph.toJSON());
  }

  /**
   * Экспорт графа
   */
  async exportGraph(req, res) {
    const { conceptId } = req.params;
    const { format } = req.query;

    const exported = await graphService.exportGraph(conceptId, format || 'json');

    if (format === 'graphml') {
      res.setHeader('Content-Type', 'application/xml');
      res.setHeader('Content-Disposition', `attachment; filename=graph-${conceptId}.graphml`);
      return res.send(exported);
    }

    return responseBuilder.success(res, exported);
  }

  /**
   * Валидация графа через Claude
   */
  async validateGraph(req, res) {
    const userId = req.user?.id;
    const { conceptId } = req.params;

    if (!userId) {
      return responseBuilder.error(res, 'Требуется аутентификация', 401);
    }

    const result = await graphService.validateGraph(conceptId, userId);

    return responseBuilder.success(res, result, 'Граф проверен');
  }

  /**
   * Анализ графа
   */
  async analyzeGraph(req, res) {
    const { conceptId } = req.params;

    const analysis = await graphService.analyzeGraph(conceptId);

    return responseBuilder.success(res, analysis);
  }
}

module.exports = new GraphController();