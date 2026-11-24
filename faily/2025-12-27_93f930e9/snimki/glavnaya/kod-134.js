/**
 * Сервис управления взаимодействиями с Claude
 */

const db = require('../db/postgres-connection');
const mongoDb = require('../db/mongo-connection');
const claudeClient = require('./claude-client.service');
const requestFormatter = require('./request-formatter.service');
const userApiKeyService = require('./user-api-key.service');
const logger = require('@philos/shared').logger.createServiceLogger('claude-service');
const { v4: uuidv4 } = require('uuid');

class ClaudeInteractionService {
  /**
   * Выполняет запрос к Claude с отслеживанием
   */
  async executeRequest(userId, queryType, queryContent, options = {}) {
    const interactionId = uuidv4();
    const startTime = Date.now();

    try {
      // Получаем API ключ пользователя или используем системный
      const { apiKey, usedUserKey } = await userApiKeyService.getApiKey(userId);

      logger.info('Выполнение запроса к Claude', {
        interactionId,
        userId,
        queryType,
        usedUserKey
      });

      // Отправляем запрос к Claude
      const response = await claudeClient.sendMessage(queryContent, {
        apiKey,
        ...options
      });

      // Рассчитываем стоимость
      const estimatedCost = claudeClient.estimateCost(
        response.usage.inputTokens,
        response.usage.outputTokens,
        response.model
      );

      // Сохраняем взаимодействие в PostgreSQL
      await this.recordInteraction({
        interactionId,
        userId,
        queryType,
        queryContent,
        responseContent: response.content,
        tokensUsed: response.usage.totalTokens,
        estimatedCost,
        status: 'success',
        usedUserKey,
        model: response.model,
        duration: Date.now() - startTime
      });

      // Обновляем статистику использования API ключа
      if (usedUserKey) {
        await userApiKeyService.recordUsage(userId, {
          operationType: queryType,
          tokensUsed: response.usage.totalTokens,
          estimatedCost
        });
      }

      return {
        interactionId,
        content: response.content,
        usage: response.usage,
        estimatedCost,
        model: response.model,
        usedUserKey
      };

    } catch (error) {
      logger.error('Ошибка выполнения запроса к Claude', {
        interactionId,
        userId,
        queryType,
        error: error.message
      });

      // Сохраняем неудачное взаимодействие
      await this.recordInteraction({
        interactionId,
        userId,
        queryType,
        queryContent,
        status: 'failed',
        errorMessage: error.message,
        duration: Date.now() - startTime
      });

      throw error;
    }
  }

  /**
   * Сохраняет запись взаимодействия в БД
   */
  async recordInteraction(data) {
    const query = `
      INSERT INTO claude_interactions (
        interaction_id, user_id, query_type, query_content,
        response_content, tokens_used, estimated_cost, status,
        used_user_key, error_message, model, request_metadata
      )
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
      RETURNING *
    `;

    const values = [
      data.interactionId,
      data.userId,
      data.queryType,
      data.queryContent,
      data.responseContent || null,
      data.tokensUsed || 0,
      data.estimatedCost || 0,
      data.status,
      data.usedUserKey || false,
      data.errorMessage || null,
      data.model || null,
      JSON.stringify({
        duration: data.duration,
        timestamp: new Date()
      })
    ];

    await db.query(query, values);
  }

  /**
   * Получает историю взаимодействий пользователя
   */
  async getUserInteractions(userId, options = {}) {
    const {
      limit = 50,
      offset = 0,
      queryType = null,
      status = null
    } = options;

    let query = `
      SELECT 
        interaction_id,
        query_type,
        tokens_used,
        estimated_cost,
        status,
        used_user_key,
        created_at
      FROM claude_interactions
      WHERE user_id = $1
    `;

    const params = [userId];
    let paramCount = 1;

    if (queryType) {
      paramCount++;
      query += ` AND query_type = $${paramCount}`;
      params.push(queryType);
    }

    if (status) {
      paramCount++;
      query += ` AND status = $${paramCount}`;
      params.push(status);
    }

    query += ` ORDER BY created_at DESC LIMIT $${paramCount + 1} OFFSET $${paramCount + 2}`;
    params.push(limit, offset);

    const result = await db.query(query, params);

    return result.rows;
  }

  /**
   * Получает детальную информацию о взаимодействии
   */
  async getInteractionDetails(interactionId, userId) {
    const query = `
      SELECT *
      FROM claude_interactions
      WHERE interaction_id = $1 AND user_id = $2
    `;

    const result = await db.query(query, [interactionId, userId]);

    if (result.rows.length === 0) {
      return null;
    }

    return result.rows[0];
  }

  /**
   * Получает статистику взаимодействий пользователя
   */
  async getUserStats(userId, startDate = null, endDate = null) {
    let query = `
      SELECT 
        COUNT(*) as total_interactions,
        COUNT(CASE WHEN status = 'success' THEN 1 END) as successful_interactions,
        COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_interactions,
        SUM(tokens_used) as total_tokens,
        SUM(estimated_cost) as total_cost,
        AVG(tokens_used) as avg_tokens_per_request
      FROM claude_interactions
      WHERE user_id = $1
    `;

    const params = [userId];
    let paramCount = 1;

    if (startDate) {
      paramCount++;
      query += ` AND created_at >= $${paramCount}`;
      params.push(startDate);
    }

    if (endDate) {
      paramCount++;
      query += ` AND created_at <= $${paramCount}`;
      params.push(endDate);
    }

    const result = await db.query(query, params);

    return result.rows[0];
  }

  //=============================================
  // ВЫСОКОУРОВНЕВЫЕ МЕТОДЫ ДЛЯ РАЗЛИЧНЫХ ЗАПРОСОВ
  //=============================================

  /**
   * Валидация графа
   */
  async validateGraph(userId, graphData) {
    const prompt = requestFormatter.formatGraphValidationRequest(graphData);

    return await this.executeRequest(userId, 'graph_validation', prompt);
  }

  /**
   * Обогащение категории
   */
  async enrichCategory(userId, categoryData, conceptName, traditions, philosophers) {
    const prompt = requestFormatter.formatCategoryEnrichmentRequest(
      categoryData,
      conceptName,
      traditions,
      philosophers
    );

    return await this.executeRequest(userId, 'category_enrichment', prompt);
  }

  /**
   * Обогащение связи
   */
  async enrichRelationship(userId, relationshipData, category1, category2, conceptName) {
    const prompt = requestFormatter.formatRelationshipEnrichmentRequest(
      relationshipData,
      category1,
      category2,
      conceptName
    );

    return await this.executeRequest(userId, 'relationship_enrichment', prompt);
  }

  /**
   * Генерация тезисов
   */
  async generateTheses(userId, graphData, quantity, thesisType, style) {
    const prompt = requestFormatter.formatThesisGenerationRequest(
      graphData,
      quantity,
      thesisType,
      style
    );

    return await this.executeRequest(userId, 'thesis_generation', prompt);
  }

  /**
   * Генерация графа из тезисов
   */
  async generateGraphFromTheses(userId, theses) {
    const prompt = requestFormatter.formatThesisToGraphRequest(theses);

    return await this.executeRequest(userId, 'graph_generation', prompt);
  }

  /**
   * Синтез концепций
   */
  async synthesizeConcepts(userId, concept1, concept2, method, focus, innovationDegree) {
    const prompt = requestFormatter.formatConceptSynthesisRequest(
      concept1,
      concept2,
      method,
      focus,
      innovationDegree
    );

    return await this.executeRequest(userId, 'concept_synthesis', prompt, {
      maxTokens: 8192 // Больше токенов для синтеза
    });
  }

  /**
   * Анализ совместимости концепций
   */
  async analyzeCompatibility(userId, concept1, concept2) {
    const prompt = requestFormatter.formatConceptCompatibilityRequest(concept1, concept2);

    return await this.executeRequest(userId, 'compatibility_analysis', prompt);
  }

  /**
   * Создание диалога
   */
  async createDialogue(userId, concept1, name1, concept2, name2, topic, options) {
    const prompt = requestFormatter.formatDialogueRequest(
      concept1,
      name1,
      concept2,
      name2,
      topic,
      options
    );

    return await this.executeRequest(userId, 'dialogue_generation', prompt, {
      maxTokens: 8192 // Больше токенов для диалога
    });
  }

  /**
   * Историческая контекстуализация
   */
  async contextualizeHistorically(userId, conceptData, conceptName, traditions, philosophers, timeContext) {
    const prompt = requestFormatter.formatHistoricalContextRequest(
      conceptData,
      conceptName,
      traditions,
      philosophers,
      timeContext
    );

    return await this.executeRequest(userId, 'historical_context', prompt);
  }

  /**
   * Практическое применение
   */
  async analyzePracticalApplication(userId, conceptData, conceptName, domains, detailed) {
    const prompt = requestFormatter.formatPracticalApplicationRequest(
      conceptData,
      conceptName,
      domains,
      detailed
    );

    return await this.executeRequest(userId, 'practical_application', prompt);
  }

  /**
   * Эволюция концепции
   */
  async analyzeConceptEvolution(userId, conceptData, conceptName) {
    const prompt = requestFormatter.formatConceptEvolutionRequest(conceptData, conceptName);

    return await this.executeRequest(userId, 'concept_evolution', prompt);
  }

  /**
   * Генерация названия концепции
   */
  async generateConceptName(userId, graphData, theses) {
    const prompt = requestFormatter.formatConceptNameGenerationRequest(graphData, theses);

    return await this.executeRequest(userId, 'name_generation', prompt);
  }

  /**
   * Анализ названия концепции
   */
  async analyzeConceptName(userId, name, conceptData) {
    const prompt = requestFormatter.formatConceptNameAnalysisRequest(name, conceptData);

    return await this.executeRequest(userId, 'name_analysis', prompt);
  }

  /**
   * Анализ происхождения (граф)
   */
  async analyzeGraphOrigin(userId, graphData) {
    const prompt = requestFormatter.formatGraphOriginAnalysisRequest(graphData);

    return await this.executeRequest(userId, 'origin_analysis_graph', prompt);
  }

  /**
   * Анализ происхождения (тезисы)
   */
  async analyzeThesisOrigin(userId, theses) {
    const prompt = requestFormatter.formatThesisOriginAnalysisRequest(theses);

    return await this.executeRequest(userId, 'origin_analysis_thesis', prompt);
  }

  /**
   * Критика синтеза
   */
  async critiqueSynthesis(userId, synthesizedConcept) {
    const prompt = requestFormatter.formatSynthesisCritiqueRequest(synthesizedConcept);

    return await this.executeRequest(userId, 'synthesis_critique', prompt);
  }
}

module.exports = new ClaudeInteractionService();