/**
 * Сервис управления категориями
 */

const { NotFoundError, ValidationError } = require('@philos/shared');
const neo4jDb = require('../db/neo4j-connection');
const mongoDb = require('../db/mongo-connection');
const redisClient = require('../db/redis-client');
const Category = require('../models/Category');
const config = require('../config/config');
const logger = require('@philos/shared').logger.createServiceLogger('graph-service');

class CategoryService {
  /**
   * Создание категории
   */
  async create(categoryData, conceptId) {
    const category = new Category({
      ...categoryData,
      concept_id: conceptId
    });

    // Проверка лимита категорий
    const count = await this.countByConceptId(conceptId);
    if (count >= config.graph.maxCategoriesPerConcept) {
      throw new ValidationError(
        `Превышен лимит категорий для концепции (${config.graph.maxCategoriesPerConcept})`
      );
    }

    // Создаем узел в Neo4j
    const cypher = `
      MATCH (c:Concept {concept_id: $conceptId})
      CREATE (cat:Category $properties)
      CREATE (c)-[:HAS_CATEGORY]->(cat)
      RETURN cat
    `;

    const params = {
      conceptId,
      properties: category.toNeo4j()
    };

    const records = await neo4jDb.executeWrite(cypher, params);

    if (records.length === 0) {
      throw new NotFoundError('Concept', conceptId);
    }

    // Инвалидация кэша графа
    await redisClient.del(`graph:${conceptId}`);

    logger.info('Категория создана', {
      categoryId: category.categoryId,
      conceptId
    });

    return category;
  }

  /**
   * Получение категории по ID
   */
  async findById(categoryId) {
    const cypher = `
      MATCH (cat:Category {category_id: $categoryId})
      RETURN cat
    `;

    const records = await neo4jDb.executeRead(cypher, { categoryId });

    if (records.length === 0) {
      return null;
    }

    return Category.fromNeo4j(records[0].get('cat').properties);
  }

  /**
   * Получение всех категорий концепции
   */
  async findByConceptId(conceptId) {
    const cypher = `
      MATCH (c:Concept {concept_id: $conceptId})-[:HAS_CATEGORY]->(cat:Category)
      RETURN cat
      ORDER BY cat.name
    `;

    const records = await neo4jDb.executeRead(cypher, { conceptId });

    return records.map(record => 
      Category.fromNeo4j(record.get('cat').properties)
    );
  }

  /**
   * Подсчет категорий концепции
   */
  async countByConceptId(conceptId) {
    const cypher = `
      MATCH (c:Concept {concept_id: $conceptId})-[:HAS_CATEGORY]->(cat:Category)
      RETURN count(cat) as count
    `;

    const records = await neo4jDb.executeRead(cypher, { conceptId });

    return records[0].get('count').toNumber();
  }

  /**
   * Обновление категории
   */
  async update(categoryId, updateData) {
    const category = await this.findById(categoryId);
    if (!category) {
      throw new NotFoundError('Category', categoryId);
    }

    const allowedFields = ['name', 'definition', 'type', 'innovation_degree', 'certainty'];
    const updates = [];
    const params = { categoryId };

    for (const [key, value] of Object.entries(updateData)) {
      if (allowedFields.includes(key)) {
        updates.push(`cat.${key} = $${key}`);
        params[key] = value;
      }
    }

    if (updates.length === 0) {
      return category;
    }

    const cypher = `
      MATCH (cat:Category {category_id: $categoryId})
      SET ${updates.join(', ')}
      RETURN cat
    `;

    const records = await neo4jDb.executeWrite(cypher, params);

    // Инвалидация кэша
    await redisClient.del(`graph:${category.conceptId}`);

    return Category.fromNeo4j(records[0].get('cat').properties);
  }

  /**
   * Удаление категории
   */
  async delete(categoryId) {
    const category = await this.findById(categoryId);
    if (!category) {
      throw new NotFoundError('Category', categoryId);
    }

    // Удаляем категорию и все её связи
    const cypher = `
      MATCH (cat:Category {category_id: $categoryId})
      DETACH DELETE cat
    `;

    await neo4jDb.executeWrite(cypher, { categoryId });

    // Инвалидация кэша
    await redisClient.del(`graph:${category.conceptId}`);

    logger.info('Категория удалена', { categoryId });
  }

  /**
   * Пакетное создание категорий
   */
  async createBatch(categoriesData, conceptId) {
    const categories = categoriesData.map(data => 
      new Category({ ...data, concept_id: conceptId })
    );

    // Проверка лимита
    const existingCount = await this.countByConceptId(conceptId);
    if (existingCount + categories.length > config.graph.maxCategoriesPerConcept) {
      throw new ValidationError(
        `Превышен лимит категорий для концепции (${config.graph.maxCategoriesPerConcept})`
      );
    }

    const cypher = `
      MATCH (c:Concept {concept_id: $conceptId})
      UNWIND $categories as catData
      CREATE (cat:Category)
      SET cat = catData
      CREATE (c)-[:HAS_CATEGORY]->(cat)
      RETURN cat
    `;

    const params = {
      conceptId,
      categories: categories.map(c => c.toNeo4j())
    };

    await neo4jDb.executeWrite(cypher, params);

    // Инвалидация кэша
    await redisClient.del(`graph:${conceptId}`);

    logger.info('Категории созданы пакетно', {
      conceptId,
      count: categories.length
    });

    return categories;
  }

  /**
   * Получение обогащенного описания категории из MongoDB
   */
  async getEnrichedDescription(categoryId) {
    const collection = mongoDb.getCollection('category_descriptions');

    const result = await collection.findOne({ category_id: categoryId });

    return result;
  }

  /**
   * Сохранение обогащенного описания в MongoDB
   */
  async saveEnrichedDescription(categoryId, enrichedData) {
    const collection = mongoDb.getCollection('category_descriptions');

    const document = {
      category_id: categoryId,
      detailed_description: enrichedData.detailedDescription,
      alternative_interpretations: enrichedData.alternativeInterpretations || [],
      historical_analogues: enrichedData.historicalAnalogues || [],
      related_categories: enrichedData.relatedCategories || [],
      is_approved: false,
      created_at: new Date(),
      updated_at: new Date()
    };

    await collection.updateOne(
      { category_id: categoryId },
      { $set: document },
      { upsert: true }
    );

    logger.info('Обогащенное описание категории сохранено', { categoryId });

    return document;
  }

  /**
   * Вычисление центральности категорий
   */
  async calculateCentrality(conceptId, algorithm = 'pagerank') {
    let cypher;

    if (algorithm === 'pagerank') {
      cypher = `
        MATCH (c:Concept {concept_id: $conceptId})-[:HAS_CATEGORY]->(cat:Category)
        CALL gds.pageRank.stream({
          nodeProjection: 'Category',
          relationshipProjection: {
            RELATED_TO: {
              orientation: 'NATURAL'
            }
          },
          nodeQuery: 'MATCH (cat:Category) WHERE cat.concept_id = "' + $conceptId + '" RETURN id(cat) as id',
          relationshipQuery: 'MATCH (source:Category)-[r:RELATED_TO]->(target:Category) 
                              WHERE source.concept_id = "' + $conceptId + '" 
                              AND target.concept_id = "' + $conceptId + '" 
                              RETURN id(source) as source, id(target) as target, r.strength as weight'
        })
        YIELD nodeId, score
        WITH gds.util.asNode(nodeId) AS cat, score
        SET cat.centrality = score
        RETURN cat.category_id as categoryId, score
      `;
    } else if (algorithm === 'degree') {
      cypher = `
        MATCH (c:Concept {concept_id: $conceptId})-[:HAS_CATEGORY]->(cat:Category)
        OPTIONAL MATCH (cat)-[r:RELATED_TO]-()
        WITH cat, count(r) as degree
        SET cat.centrality = degree * 0.01
        RETURN cat.category_id as categoryId, cat.centrality as score
      `;
    } else {
      throw new ValidationError('Неподдерживаемый алгоритм центральности');
    }

    const records = await neo4jDb.executeWrite(cypher, { conceptId });

    // Инвалидация кэша
    await redisClient.del(`graph:${conceptId}`);

    return records.map(r => ({
      categoryId: r.get('categoryId'),
      centrality: r.get('score')
    }));
  }
}

module.exports = new CategoryService();