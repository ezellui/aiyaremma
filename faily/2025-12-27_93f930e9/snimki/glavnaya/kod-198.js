/**
 * Сервис управления графами концепций
 */

const { NotFoundError } = require('@philos/shared');
const neo4jDb = require('../db/neo4j-connection');
const redisClient = require('../db/redis-client');
const categoryService = require('./category.service');
const relationshipService = require('./relationship.service');
const Graph = require('../models/Graph');
const axios = require('axios');
const config = require('../config/config');
const logger = require('@philos/shared').logger.createServiceLogger('graph-service');

class GraphService {
  /**
   * Получение полного графа концепции
   */
  async getGraph(conceptId) {
    // Проверка кэша
    const cached = await redisClient.get(`graph:${conceptId}`);
    if (cached) {
      return new Graph(cached);
    }

    // Получаем категории и связи
    const categories = await categoryService.findByConceptId(conceptId);
    const relationships = await relationshipService.findByConceptId(conceptId);

    if (categories.length === 0) {
      throw new NotFoundError('Graph for concept', conceptId);
    }

    // Получаем информацию о концепции
    const conceptInfo = await this.getConceptInfo(conceptId);

    const graph = new Graph({
      conceptId,
      conceptName: conceptInfo?.name || 'Unknown',
      categories,
      relationships,
      metadata: {
        categoryCount: categories.length,
        relationshipCount: relationships.length,
        lastUpdated: new Date()
      }
    });

    // Кэшируем на 1 час
    await redisClient.set(`graph:${conceptId}`, graph.toJSON(), 3600);

    return graph;
  }

  /**
   * Создание графа из данных
   */
  async createGraph(conceptId, graphData) {
    // Проверяем существование концепции
    const conceptInfo = await this.getConceptInfo(conceptId);
    if (!conceptInfo) {
      throw new NotFoundError('Concept', conceptId);
    }

    // Создаем категории пакетно
    const categories = await categoryService.createBatch(
      graphData.categories || [],
      conceptId
    );

    // Создаем связи пакетно
    const relationships = await relationshipService.createBatch(
      graphData.relationships || [],
      conceptId
    );

    // Вычисляем центральность
    await categoryService.calculateCentrality(conceptId);

    logger.info('Граф создан', {
      conceptId,
      categoriesCount: categories.length,
      relationshipsCount: relationships.length
    });

    // Получаем и возвращаем полный граф
    return await this.getGraph(conceptId);
  }

  /**
   * Обновление графа
   */
  async updateGraph(conceptId, graphData) {
    // Удаляем существующий граф
    await this.deleteGraph(conceptId);

    // Создаем новый граф
    return await this.createGraph(conceptId, graphData);
  }

  /**
   * Удаление графа
   */
  async deleteGraph(conceptId) {
    const cypher = `
      MATCH (c:Concept {concept_id: $conceptId})-[:HAS_CATEGORY]->(cat:Category)
      DETACH DELETE cat
    `;

    await neo4jDb.executeWrite(cypher, { conceptId });

    // Инвалидация кэша
    await redisClient.del(`graph:${conceptId}`);

    logger.info('Граф удален', { conceptId });
  }

  /**
   * Получение статистики графа
   */
  async getGraphStats(conceptId) {
    const cypher = `
      MATCH (c:Concept {concept_id: $conceptId})-[:HAS_CATEGORY]->(cat:Category)
      OPTIONAL MATCH (cat)-[r:RELATED_TO]->(:Category)
      RETURN 
        count(DISTINCT cat) as categoryCount,
        count(DISTINCT r) as relationshipCount,
        avg(cat.centrality) as avgCentrality,
        avg(r.strength) as avgStrength,
        max(cat.centrality) as maxCentrality,
        min(cat.centrality) as minCentrality
    `;

    const records = await neo4jDb.executeRead(cypher, { conceptId });

    if (records.length === 0) {
      throw new NotFoundError('Graph for concept', conceptId);
    }

    const record = records[0];

    return {
      categoryCount: record.get('categoryCount').toNumber(),
      relationshipCount: record.get('relationshipCount').toNumber(),
      avgCentrality: record.get('avgCentrality') || 0,
      avgStrength: record.get('avgStrength') || 0,
      maxCentrality: record.get('maxCentrality') || 0,
      minCentrality: record.get('minCentrality') || 0
    };
  }

  /**
   * Получение подграфа (категории и их непосредственные связи)
   */
  async getSubgraph(categoryIds, conceptId) {
    const cypher = `
      MATCH (cat:Category {concept_id: $conceptId})
      WHERE cat.category_id IN $categoryIds
      OPTIONAL MATCH (cat)-[r:RELATED_TO]-(other:Category {concept_id: $conceptId})
      WHERE other.category_id IN $categoryIds
      RETURN collect(DISTINCT cat) as categories, 
             collect(DISTINCT r) as relationships
    `;

    const records = await neo4jDb.executeRead(cypher, {
      conceptId,
      categoryIds
    });

    if (records.length === 0) {
      return new Graph({ conceptId, categories: [], relationships: [] });
    }

    const record = records[0];
    const categories = record.get('categories').map(node => 
      categoryService.constructor.prototype.constructor.fromNeo4j(node.properties)
    );
    const relationships = record.get('relationships')
      .filter(r => r !== null)
      .map(rel => ({
        relationshipId: rel.properties.relationship_id,
        type: rel.properties.type,
        strength: rel.properties.strength
      }));

    return new Graph({
      conceptId,
      categories,
      relationships
    });
  }

  /**
   * Экспорт графа в различные форматы
   */
  async exportGraph(conceptId, format = 'json') {
    const graph = await this.getGraph(conceptId);

    switch (format) {
      case 'json':
        return graph.toJSON();

      case 'cytoscape':
        return this.toCytoscapeFormat(graph);

      case 'd3':
        return this.toD3Format(graph);

      case 'graphml':
        return this.toGraphMLFormat(graph);

      default:
        return graph.toJSON();
    }
  }

  /**
   * Преобразование в формат Cytoscape
   */
  toCytoscapeFormat(graph) {
    return {
      elements: {
        nodes: graph.categories.map(cat => ({
          data: {
            id: cat.categoryId,
            label: cat.name,
            type: cat.type,
            centrality: cat.centrality
          }
        })),
        edges: graph.relationships.map(rel => ({
          data: {
            id: rel.relationshipId,
            source: rel.sourceCategoryId,
            target: rel.targetCategoryId,
            label: rel.type,
            strength: rel.strength
          }
        }))
      }
    };
  }

  /**
   * Преобразование в формат D3
   */
  toD3Format(graph) {
    return {
      nodes: graph.categories.map(cat => ({
        id: cat.categoryId,
        name: cat.name,
        type: cat.type,
        centrality: cat.centrality,
        group: cat.type
      })),
      links: graph.relationships.map(rel => ({
        source: rel.sourceCategoryId,
        target: rel.targetCategoryId,
        type: rel.type,
        strength: rel.strength,
        value: rel.strength
      }))
    };
  }

  /**
   * Преобразование в формат GraphML
   */
  toGraphMLFormat(graph) {
    let graphml = '<?xml version="1.0" encoding="UTF-8"?>\n';
    graphml += '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">\n';
    graphml += '  <graph id="G" edgedefault="directed">\n';

    // Узлы
    graph.categories.forEach(cat => {
      graphml += `    <node id="${cat.categoryId}">\n`;
      graphml += `      <data key="name">${cat.name}</data>\n`;
      graphml += `      <data key="type">${cat.type}</data>\n`;
      graphml += `      <data key="centrality">${cat.centrality}</data>\n`;
      graphml += '    </node>\n';
    });

    // Рёбра
    graph.relationships.forEach(rel => {
      graphml += `    <edge source="${rel.sourceCategoryId}" target="${rel.targetCategoryId}">\n`;
      graphml += `      <data key="type">${rel.type}</data>\n`;
      graphml += `      <data key="strength">${rel.strength}</data>\n`;
      graphml += '    </edge>\n';
    });

    graphml += '  </graph>\n';
    graphml += '</graphml>';

    return graphml;
  }

  /**
   * Валидация графа через Claude
   */
  async validateGraph(conceptId, userId) {
    const graph = await this.getGraph(conceptId);

    try {
      const response = await axios.post(
        `${config.services.claude}/claude/validate-graph`,
        { graphData: graph.toJSON() },
        {
          headers: {
            'Content-Type': 'application/json',
            'X-User-Id': userId
          }
        }
      );

      return response.data;
    } catch (error) {
      logger.error('Ошибка валидации графа через Claude', {
        conceptId,
        error: error.message
      });
      throw error;
    }
  }

  /**
   * Анализ графа
   */
  async analyzeGraph(conceptId) {
    const graph = await this.getGraph(conceptId);
    const stats = await this.getGraphStats(conceptId);

    // Находим центральные категории
    const centralCategories = graph.categories
      .sort((a, b) => (b.centrality || 0) - (a.centrality || 0))
      .slice(0, 5)
      .map(c => ({
        categoryId: c.categoryId,
        name: c.name,
        centrality: c.centrality
      }));

    // Находим изолированные категории
    const isolatedCategories = graph.categories
      .filter(cat => {
        const rels = graph.getCategoryRelationships(cat.categoryId);
        return rels.length === 0;
      })
      .map(c => ({
        categoryId: c.categoryId,
        name: c.name
      }));

    // Находим сильные связи
    const strongRelationships = graph.relationships
      .sort((a, b) => (b.strength || 0) - (a.strength || 0))
      .slice(0, 5)
      .map(r => ({
        relationshipId: r.relationshipId,
        source: graph.getCategoryById(r.sourceCategoryId)?.name,
        target: graph.getCategoryById(r.targetCategoryId)?.name,
        type: r.type,
        strength: r.strength
      }));

    // Проверка связности
    const isConnected = await this.isGraphConnected(conceptId);

    // Поиск циклов
    const cycles = await relationshipService.findCycles(conceptId);

    return {
      stats,
      centralCategories,
      isolatedCategories,
      strongRelationships,
      isConnected,
      cyclesCount: cycles.length,
      cycles: cycles.slice(0, 3) // Показываем только первые 3 цикла
    };
  }

  /**
   * Проверка связности графа
   */
  async isGraphConnected(conceptId) {
    const cypher = `
      MATCH (c:Concept {concept_id: $conceptId})-[:HAS_CATEGORY]->(start:Category)
      WITH start LIMIT 1
      MATCH path = (start)-[:RELATED_TO*]-(other:Category {concept_id: $conceptId})
      WITH collect(DISTINCT other) as reachable
      MATCH (c:Concept {concept_id: $conceptId})-[:HAS_CATEGORY]->(all:Category)
      WITH count(all) as total, size(reachable) as reachableCount
      RETURN reachableCount >= total as isConnected
    `;

    const records = await neo4jDb.executeRead(cypher, { conceptId });

    if (records.length === 0) {
      return false;
    }

    return records[0].get('isConnected');
  }

  /**
   * Получение информации о концепции из Concept Service
   */
  async getConceptInfo(conceptId) {
    try {
      const response = await axios.get(
        `${config.services.concept}/concepts/${conceptId}`,
        { timeout: 5000 }
      );

      return response.data?.data;
    } catch (error) {
      logger.warn('Не удалось получить информацию о концепции', {
        conceptId,
        error: error.message
      });
      return null;
    }
  }
}

module.exports = new GraphService();