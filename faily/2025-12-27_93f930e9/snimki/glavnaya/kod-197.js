/**
 * Сервис управления связями между категориями
 */

const { NotFoundError, ValidationError } = require('@philos/shared');
const neo4jDb = require('../db/neo4j-connection');
const mongoDb = require('../db/mongo-connection');
const redisClient = require('../db/redis-client');
const Relationship = require('../models/Relationship');
const categoryService = require('./category.service');
const config = require('../config/config');
const logger = require('@philos/shared').logger.createServiceLogger('graph-service');

class RelationshipService {
  /**
   * Создание связи между категориями
   */
  async create(relationshipData, conceptId) {
    const relationship = new Relationship({
      ...relationshipData,
      concept_id: conceptId
    });

    // Проверка существования категорий
    const sourceCategory = await categoryService.findById(relationship.sourceCategoryId);
    const targetCategory = await categoryService.findById(relationship.targetCategoryId);

    if (!sourceCategory || !targetCategory) {
      throw new NotFoundError('Category', 'source or target');
    }

    // Проверка принадлежности концепции
    if (sourceCategory.conceptId !== conceptId || targetCategory.conceptId !== conceptId) {
      throw new ValidationError('Категории должны принадлежать указанной концепции');
    }

    // Проверка лимита связей
    const count = await this.countByCategoryId(relationship.sourceCategoryId);
    if (count >= config.graph.maxRelationshipsPerCategory) {
      throw new ValidationError(
        `Превышен лимит связей для категории (${config.graph.maxRelationshipsPerCategory})`
      );
    }

    // Создаем связь в Neo4j
    const cypher = `
      MATCH (source:Category {category_id: $sourceCategoryId})
      MATCH (target:Category {category_id: $targetCategoryId})
      CREATE (source)-[r:RELATED_TO $properties]->(target)
      RETURN r, source, target
    `;

    const params = {
      sourceCategoryId: relationship.sourceCategoryId,
      targetCategoryId: relationship.targetCategoryId,
      properties: relationship.toNeo4j()
    };

    const records = await neo4jDb.executeWrite(cypher, params);

    if (records.length === 0) {
      throw new Error('Не удалось создать связь');
    }

    // Инвалидация кэша
    await redisClient.del(`graph:${conceptId}`);

    logger.info('Связь создана', {
      relationshipId: relationship.relationshipId,
      conceptId,
      source: relationship.sourceCategoryId,
      target: relationship.targetCategoryId
    });

    return relationship;
  }

  /**
   * Получение связи по ID
   */
  async findById(relationshipId) {
    const cypher = `
      MATCH (source:Category)-[r:RELATED_TO {relationship_id: $relationshipId}]->(target:Category)
      RETURN r, source, target
    `;

    const records = await neo4jDb.executeRead(cypher, { relationshipId });

    if (records.length === 0) {
      return null;
    }

    const record = records[0];
    return Relationship.fromNeo4j(
      record.get('r').properties,
      record.get('source').properties,
      record.get('target').properties
    );
  }

  /**
   * Получение всех связей концепции
   */
  async findByConceptId(conceptId) {
    const cypher = `
      MATCH (source:Category {concept_id: $conceptId})-[r:RELATED_TO]->(target:Category {concept_id: $conceptId})
      RETURN r, source, target
      ORDER BY r.strength DESC
    `;

    const records = await neo4jDb.executeRead(cypher, { conceptId });

    return records.map(record => 
      Relationship.fromNeo4j(
        record.get('r').properties,
        record.get('source').properties,
        record.get('target').properties
      )
    );
  }

  /**
   * Получение связей категории
   */
  async findByCategoryId(categoryId) {
    const cypher = `
      MATCH (cat:Category {category_id: $categoryId})
      MATCH (cat)-[r:RELATED_TO]-(other:Category)
      RETURN r, 
             CASE WHEN startNode(r).category_id = $categoryId 
                  THEN startNode(r) 
                  ELSE endNode(r) END as source,
             CASE WHEN endNode(r).category_id = $categoryId 
                  THEN startNode(r) 
                  ELSE endNode(r) END as target
    `;

    const records = await neo4jDb.executeRead(cypher, { categoryId });

    return records.map(record => 
      Relationship.fromNeo4j(
        record.get('r').properties,
        record.get('source').properties,
        record.get('target').properties
      )
    );
  }

  /**
   * Подсчет связей категории
   */
  async countByCategoryId(categoryId) {
    const cypher = `
      MATCH (cat:Category {category_id: $categoryId})-[r:RELATED_TO]-()
      RETURN count(r) as count
    `;

    const records = await neo4jDb.executeRead(cypher, { categoryId });

    return records[0].get('count').toNumber();
  }

  /**
   * Обновление связи
   */
  async update(relationshipId, updateData) {
    const relationship = await this.findById(relationshipId);
    if (!relationship) {
      throw new NotFoundError('Relationship', relationshipId);
    }

    const allowedFields = ['type', 'direction', 'strength', 'innovation_degree', 'description'];
    const updates = [];
    const params = { relationshipId };

    for (const [key, value] of Object.entries(updateData)) {
      if (allowedFields.includes(key)) {
        updates.push(`r.${key} = $${key}`);
        params[key] = value;
      }
    }

    if (updates.length === 0) {
      return relationship;
    }

    const cypher = `
      MATCH ()-[r:RELATED_TO {relationship_id: $relationshipId}]->()
      SET ${updates.join(', ')}
      RETURN r
    `;

    await neo4jDb.executeWrite(cypher, params);

    // Инвалидация кэша
    await redisClient.del(`graph:${relationship.conceptId}`);

    // Получаем обновленную связь
    return await this.findById(relationshipId);
  }

  /**
   * Удаление связи
   */
  async delete(relationshipId) {
    const relationship = await this.findById(relationshipId);
    if (!relationship) {
      throw new NotFoundError('Relationship', relationshipId);
    }

    const cypher = `
      MATCH ()-[r:RELATED_TO {relationship_id: $relationshipId}]->()
      DELETE r
    `;

    await neo4jDb.executeWrite(cypher, { relationshipId });

    // Инвалидация кэша
    await redisClient.del(`graph:${relationship.conceptId}`);

    logger.info('Связь удалена', { relationshipId });
  }

  /**
   * Пакетное создание связей
   */
  async createBatch(relationshipsData, conceptId) {
    const relationships = relationshipsData.map(data => 
      new Relationship({ ...data, concept_id: conceptId })
    );

    const cypher = `
      UNWIND $relationships as relData
      MATCH (source:Category {category_id: relData.source_category_id})
      MATCH (target:Category {category_id: relData.target_category_id})
      CREATE (source)-[r:RELATED_TO]->(target)
      SET r = relData.properties
      RETURN count(r) as count
    `;

    const params = {
      relationships: relationships.map(r => ({
        source_category_id: r.sourceCategoryId,
        target_category_id: r.targetCategoryId,
        properties: r.toNeo4j()
      }))
    };

    const records = await neo4jDb.executeWrite(cypher, params);

    // Инвалидация кэша
    await redisClient.del(`graph:${conceptId}`);

    logger.info('Связи созданы пакетно', {
      conceptId,
      count: records[0].get('count').toNumber()
    });

    return relationships;
  }

  /**
   * Получение обогащенного описания связи из MongoDB
   */
  async getEnrichedDescription(relationshipId) {
    const collection = mongoDb.getCollection('relationship_descriptions');

    const result = await collection.findOne({ relationship_id: relationshipId });

    return result;
  }

  /**
   * Сохранение обогащенного описания в MongoDB
   */
  async saveEnrichedDescription(relationshipId, enrichedData) {
    const collection = mongoDb.getCollection('relationship_descriptions');

    const document = {
      relationship_id: relationshipId,
      philosophical_foundation: enrichedData.philosophicalFoundation,
      counterarguments: enrichedData.counterarguments || [],
      analogues: enrichedData.analogues || [],
      is_approved: false,
      created_at: new Date(),
      updated_at: new Date()
    };

    await collection.updateOne(
      { relationship_id: relationshipId },
      { $set: document },
      { upsert: true }
    );

    logger.info('Обогащенное описание связи сохранено', { relationshipId });

    return document;
  }

  /**
   * Поиск пути между категориями
   */
  async findPath(sourceCategoryId, targetCategoryId, maxDepth = 5) {
    const cypher = `
      MATCH path = shortestPath(
        (source:Category {category_id: $sourceCategoryId})
        -[r:RELATED_TO*1..${maxDepth}]-
        (target:Category {category_id: $targetCategoryId})
      )
      RETURN path
    `;

    const records = await neo4jDb.executeRead(cypher, {
      sourceCategoryId,
      targetCategoryId
    });

    if (records.length === 0) {
      return null;
    }

    const path = records[0].get('path');
    const nodes = path.segments.map(seg => seg.start.properties);
    nodes.push(path.end.properties);

    const relationships = path.segments.map(seg => seg.relationship.properties);

    return {
      categories: nodes,
      relationships,
      length: path.length
    };
  }

  /**
   * Поиск циклов в графе
   */
  async findCycles(conceptId) {
    const cypher = `
      MATCH (c:Concept {concept_id: $conceptId})-[:HAS_CATEGORY]->(start:Category)
      MATCH path = (start)-[r:RELATED_TO*2..10]->(start)
      WHERE ALL(rel IN r WHERE rel.concept_id = $conceptId)
      RETURN path
      LIMIT 10
    `;

    const records = await neo4jDb.executeRead(cypher, { conceptId });

    return records.map(record => {
      const path = record.get('path');
      return {
        categories: path.segments.map(seg => seg.start.properties.category_id),
        length: path.length
      };
    });
  }
}

module.exports = new RelationshipService();