/**
 * Контроллер Claude запросов
 */

const { responseBuilder } = require('@philos/shared');
const claudeInteractionService = require('../services/claude-interaction.service');

class ClaudeController {
  /**
   * Валидация графа
   */
  async validateGraph(req, res) {
    const userId = req.user?.id || null;
    const { graphData } = req.body;

    const result = await claudeInteractionService.validateGraph(userId, graphData);

    return responseBuilder.success(res, result, 'Граф проанализирован');
  }

  /**
   * Обогащение категории
   */
  async enrichCategory(req, res) {
    const userId = req.user?.id || null;
    const { categoryData, conceptName, traditions, philosophers } = req.body;

    const result = await claudeInteractionService.enrichCategory(
      userId,
      categoryData,
      conceptName,
      traditions || [],
      philosophers || []
    );

    return responseBuilder.success(res, result, 'Категория обогащена');
  }

  /**
   * Обогащение связи
   */
  async enrichRelationship(req, res) {
    const userId = req.user?.id || null;
    const { relationshipData, category1, category2, conceptName } = req.body;

    const result = await claudeInteractionService.enrichRelationship(
      userId,
      relationshipData,
      category1,
      category2,
      conceptName
    );

    return responseBuilder.success(res, result, 'Связь обогащена');
  }

  /**
   * Генерация тезисов
   */
  async generateTheses(req, res) {
    const userId = req.user?.id || null;
    const { graphData, quantity, thesisType, style } = req.body;

    const result = await claudeInteractionService.generateTheses(
      userId,
      graphData,
      quantity,
      thesisType,
      style
    );

    return responseBuilder.success(res, result, 'Тезисы сгенерированы');
  }

  /**
   * Генерация графа из тезисов
   */
  async generateGraphFromTheses(req, res) {
    const userId = req.user?.id || null;
    const { theses } = req.body;

    const result = await claudeInteractionService.generateGraphFromTheses(userId, theses);

    return responseBuilder.success(res, result, 'Граф сгенерирован');
  }

  /**
   * Синтез концепций
   */
  async synthesizeConcepts(req, res) {
    const userId = req.user?.id || null;
    const { concept1, concept2, method, focus, innovationDegree } = req.body;

    const result = await claudeInteractionService.synthesizeConcepts(
      userId,
      concept1,
      concept2,
      method,
      focus,
      innovationDegree
    );

    return responseBuilder.success(res, result, 'Концепции синтезированы');
  }

  /**
   * Анализ совместимости
   */
  async analyzeCompatibility(req, res) {
    const userId = req.user?.id || null;
    const { concept1, concept2 } = req.body;

    const result = await claudeInteractionService.analyzeCompatibility(
      userId,
      concept1,
      concept2
    );

    return responseBuilder.success(res, result, 'Совместимость проанализирована');
  }

  /**
   * Создание диалога
   */
  async createDialogue(req, res) {
    const userId = req.user?.id || null;
    const { concept1, name1, concept2, name2, topic, options } = req.body;

    const result = await claudeInteractionService.createDialogue(
      userId,
      concept1,
      name1,
      concept2,
      name2,
      topic,
      options || {}
    );

    return responseBuilder.success(res, result, 'Диалог создан');
  }

  /**
   * Историческая контекстуализация
   */
  async contextualizeHistorically(req, res) {
    const userId = req.user?.id || null;
    const { conceptData, conceptName, traditions, philosophers, timeContext } = req.body;

    const result = await claudeInteractionService.contextualizeHistorically(
      userId,
      conceptData,
      conceptName,
      traditions || [],
      philosophers || [],
      timeContext || null
    );

    return responseBuilder.success(res, result, 'Исторический контекст добавлен');
  }

  /**
   * Практическое применение
   */
  async analyzePracticalApplication(req, res) {
    const userId = req.user?.id || null;
    const { conceptData, conceptName, domains, detailed } = req.body;

    const result = await claudeInteractionService.analyzePracticalApplication(
      userId,
      conceptData,
      conceptName,
      domains || null,
      detailed || false
    );

    return responseBuilder.success(res, result, 'Практические применения проанализированы');
  }

  /**
   * Эволюция концепции
   */
  async analyzeConceptEvolution(req, res) {
    const userId = req.user?.id || null;
    const { conceptData, conceptName } = req.body;

    const result = await claudeInteractionService.analyzeConceptEvolution(
      userId,
      conceptData,
      conceptName
    );

    return responseBuilder.success(res, result, 'Направления эволюции определены');
  }

  /**
   * Генерация названия
   */
  async generateConceptName(req, res) {
    const userId = req.user?.id || null;
    const { graphData, theses } = req.body;

    const result = await claudeInteractionService.generateConceptName(
      userId,
      graphData || null,
      theses || null
    );

    return responseBuilder.success(res, result, 'Название сгенерировано');
  }

  /**
   * Анализ названия
   */
  async analyzeConceptName(req, res) {
    const userId = req.user?.id || null;
    const { name, conceptData } = req.body;

    const result = await claudeInteractionService.analyzeConceptName(
      userId,
      name,
      conceptData || null
    );

    return responseBuilder.success(res, result, 'Название проанализировано');
  }

  /**
   * Анализ происхождения (граф)
   */
  async analyzeGraphOrigin(req, res) {
    const userId = req.user?.id || null;
    const { graphData } = req.body;

    const result = await claudeInteractionService.analyzeGraphOrigin(userId, graphData);

    return responseBuilder.success(res, result, 'Происхождение проанализировано');
  }

  /**
   * Анализ происхождения (тезисы)
   */
  async analyzeThesisOrigin(req, res) {
    const userId = req.user?.id || null;
    const { theses } = req.body;

    const result = await claudeInteractionService.analyzeThesisOrigin(userId, theses);

    return responseBuilder.success(res, result, 'Происхождение проанализировано');
  }

  /**
   * Критика синтеза
   */
  async critiqueSynthesis(req, res) {
    const userId = req.user?.id || null;
    const { synthesizedConcept } = req.body;

    const result = await claudeInteractionService.critiqueSynthesis(userId, synthesizedConcept);

    return responseBuilder.success(res, result, 'Критика проведена');
  }

  /**
   * Получение истории взаимодействий
   */
  async getInteractionHistory(req, res) {
    const userId = req.user?.id;
    const { limit, offset, queryType, status } = req.query;

    if (!userId) {
      return responseBuilder.error(res, 'Требуется аутентификация', 401);
    }

    const interactions = await claudeInteractionService.getUserInteractions(userId, {
      limit: parseInt(limit) || 50,
      offset: parseInt(offset) || 0,
      queryType,
      status
    });

    return responseBuilder.success(res, interactions);
  }

  /**
   * Получение деталей взаимодействия
   */
  async getInteractionDetails(req, res) {
    const userId = req.user?.id;
    const { id } = req.params;

    if (!userId) {
      return responseBuilder.error(res, 'Требуется аутентификация', 401);
    }

    const interaction = await claudeInteractionService.getInteractionDetails(id, userId);

    if (!interaction) {
      return responseBuilder.error(res, 'Взаимодействие не найдено', 404);
    }

    return responseBuilder.success(res, interaction);
  }

  /**
   * Получение статистики
   */
  async getUserStats(req, res) {
    const userId = req.user?.id;
    const { startDate, endDate } = req.query;

    if (!userId) {
      return responseBuilder.error(res, 'Требуется аутентификация', 401);
    }

    const stats = await claudeInteractionService.getUserStats(userId, startDate, endDate);

    return responseBuilder.success(res, stats);
  }
}

module.exports = new ClaudeController();