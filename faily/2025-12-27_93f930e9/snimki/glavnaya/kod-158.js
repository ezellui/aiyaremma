/**
 * Сервис управления концепциями
 */

const { NotFoundError, ValidationError, ConflictError } = require('@philos/shared');
const db = require('../db/postgres-connection');
const neo4jDb = require('../db/neo4j-connection');
const redisClient = require('../db/redis-client');
const Concept = require('../models/Concept');
const logger = require('@philos/shared').logger.createServiceLogger('concept-service');

class ConceptService {
  /**
   * Создание концепции
   */
  async create(conceptData, userId) {
    // Проверка на дубликаты по имени
    const existing = await this.findByName(conceptData.name);
    if (existing) {
      throw new ConflictError('Концепция с таким названием уже существует');
    }

    const concept = new Concept({
      ...conceptData,
      creator_id: userId
    });

    const dbData = concept.toDB();

    const query = `
      INSERT INTO concepts (
        concept_id, creator_id, name, description,
        is_synthesis, parent_concepts, synthesis_method,
        innovation_degree, tags, is_public
      )
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
      RETURNING *
    `;

    const values = [
      dbData.concept_id,
      dbData.creator_id,
      dbData.name,
      dbData.description,
      dbData.is_synthesis,
      JSON.stringify(dbData.parent_concepts),
      dbData.synthesis_method,
      dbData.innovation_degree,
      JSON.stringify(dbData.tags),
      dbData.is_public
    ];

    const result = await db.query(query, values);

    // Создаем узел в Neo4j
    await this.createNeo4jNode(result.rows[0]);

    return Concept.fromDB(result.rows[0]);
  }

  /**
   * Создание узла концепции в Neo4j
   */
  async createNeo4jNode(conceptData) {
    const cypher = `
      CREATE (c:Concept {
        concept_id: $conceptId,
        name: $name,
        description: $description,
        is_synthesis: $isSynthesis,
        created_at: datetime($createdAt)
      })
      RETURN c
    `;

    const params = {
      conceptId: conceptData.concept_id,
      name: conceptData.name,
      description: conceptData.description,
      isSynthesis: conceptData.is_synthesis,
      createdAt: conceptData.created_at.toISOString()
    };

    await neo4jDb.executeWrite(cypher, params);
    
    logger.info('Neo4j узел создан для концепции', { conceptId: conceptData.concept_id });
  }

  /**
   * Получение концепции по ID
   */
  async findById(conceptId) {
    // Проверка кэша
    const cached = await redisClient.get(`concept:${conceptId}`);
    if (cached) {
      return Concept.fromDB(cached);
    }

    const query = 'SELECT * FROM concepts WHERE concept_id = $1';
    const result = await db.query(query, [conceptId]);

    if (result.rows.length === 0) {
      return null;
    }

    const concept = Concept.fromDB(result.rows[0]);

    // Кэшируем на 1 час
    await redisClient.set(`concept:${conceptId}`, result.rows[0], 3600);

    return concept;
  }

  /**
   * Получение концепции по имени
   */
  async findByName(name) {
    const query = 'SELECT * FROM concepts WHERE name = $1';
    const result = await db.query(query, [name]);

    if (result.rows.length === 0) {
      return null;
    }

    return Concept.fromDB(result.rows[0]);
  }

  /**
   * Обновление концепции
   */
  async update(conceptId, updateData, userId) {
    const concept = await this.findById(conceptId);
    if (!concept) {
      throw new NotFoundError('Concept', conceptId);
    }

    // Проверка прав (только создатель может обновлять)
    if (concept.creatorId !== userId) {
      throw new ValidationError('Недостаточно прав для обновления концепции');
    }

    const allowedFields = ['name', 'description', 'tags', 'is_public'];
    const updates = [];
    const values = [];
    let paramCount = 1;

    for (const [key, value] of Object.entries(updateData)) {
      if (allowedFields.includes(key)) {
        updates.push(`${key} = $${paramCount}`);
        values.push(key === 'tags' ? JSON.stringify(value) : value);
        paramCount++;
      }
    }

    if (updates.length === 0) {
      throw new ValidationError('Нет полей для обновления');
    }

    values.push(conceptId);

    const query = `
      UPDATE concepts
      SET ${updates.join(', ')}, last_modified = CURRENT_TIMESTAMP
      WHERE concept_id = $${paramCount}
      RETURNING *
    `;

    const result = await db.query(query, values);

    // Инвалидация кэша
    await redisClient.del(`concept:${conceptId}`);

    // Обновляем узел в Neo4j
    await this.updateNeo4jNode(conceptId, updateData);

    return Concept.fromDB(result.rows[0]);
  }

  /**
   * Обновление узла в Neo4j
   */
  async updateNeo4jNode(conceptId, updateData) {
    const updates = [];
    const params = { conceptId };

    if (updateData.name) {
      updates.push('c.name = $name');
      params.name = updateData.name;
    }

    if (updateData.description) {
      updates.push('c.description = $description');
      params.description = updateData.description;
    }

    if (updates.length === 0) return;

    const cypher = `
      MATCH (c:Concept {concept_id: $conceptId})
      SET ${updates.join(', ')}
      RETURN c
    `;

    await neo4jDb.executeWrite(cypher, params);
  }

  /**
   * Удаление концепции
   */
  async delete(conceptId, userId) {
    const concept = await this.findById(conceptId);
    if (!concept) {
      throw new NotFoundError('Concept', conceptId);
    }

    // Проверка прав
    if (concept.creatorId !== userId) {
      throw new ValidationError('Недостаточно прав для удаления концепции');
    }

    // Удаляем из PostgreSQL
    const query = 'DELETE FROM concepts WHERE concept_id = $1';
    await db.query(query, [conceptId]);

    // Инвалидация кэша
    await redisClient.del(`concept:${conceptId}`);

    // Удаляем узел из Neo4j
    await this.deleteNeo4jNode(conceptId);

    logger.info('Концепция удалена', { conceptId });
  }

  /**
   * Удаление узла из Neo4j
   */
  async deleteNeo4jNode(conceptId) {
    const cypher = `
      MATCH (c:Concept {concept_id: $conceptId})
      DETACH DELETE c
    `;

    await neo4jDb.executeWrite(cypher, { conceptId });
  }

  /**
   * Получение всех концепций пользователя
   */
  async findByUser(userId, options = {}) {
    const {
      limit = 50,
      offset = 0,
      includePublic = true
    } = options;

    let query = `
      SELECT * FROM concepts
      WHERE creator_id = $1
    `;

    const params = [userId];

    if (includePublic) {
      query += ' OR is_public = true';
    }

    query += ' ORDER BY created_at DESC LIMIT $2 OFFSET $3';
    params.push(limit, offset);

    const result = await db.query(query, params);

    return result.rows.map(row => Concept.fromDB(row));
  }

  /**
   * Получение публичных концепций
   */
  async findPublic(options = {}) {
    const {
      limit = 50,
      offset = 0
    } = options;

    const query = `
      SELECT * FROM concepts
      WHERE is_public = true
      ORDER BY created_at DESC
      LIMIT $1 OFFSET $2
    `;

    const result = await db.query(query, [limit, offset]);

    return result.rows.map(row => Concept.fromDB(row));
  }

  /**
   * Получение синтезированных концепций
   */
  async findSynthesized(options = {}) {
    const {
      limit = 50,
      offset = 0
    } = options;

    const query = `
      SELECT * FROM concepts
      WHERE is_synthesis = true AND is_public = true
      ORDER BY created_at DESC
      LIMIT $1 OFFSET $2
    `;

    const result = await db.query(query, [limit, offset]);

    return result.rows.map(row => Concept.fromDB(row));
  }

  /**
   * Связывание концепции с философом
   */
  async linkPhilosopher(conceptId, philosopherId, relationshipType, userId) {
    const concept = await this.findById(conceptId);
    if (!concept) {
      throw new NotFoundError('Concept', conceptId);
    }

    // Проверка прав
    if (concept.creatorId !== userId) {
      throw new ValidationError('Недостаточно прав для связывания концепции');
    }

    const query = `
      INSERT INTO concept_philosophers (concept_id, philosopher_id, relationship_type)
      VALUES ($1, $2, $3)
      ON CONFLICT (concept_id, philosopher_id) 
      DO UPDATE SET relationship_type = $3
      RETURNING *
    `;

    await db.query(query, [conceptId, philosopherId, relationshipType]);

    // Инвалидация кэша
    await redisClient.del(`concept:${conceptId}`);

    logger.info('Концепция связана с философом', { conceptId, philosopherId });
  }

  /**
   * Связывание концепции с традицией
   */
  async linkTradition(conceptId, traditionId, relationshipStrength, userId) {
    const concept = await this.findById(conceptId);
    if (!concept) {
      throw new NotFoundError('Concept', conceptId);
    }

    // Проверка прав
    if (concept.creatorId !== userId) {
      throw new ValidationError('Недостаточно прав для связывания концепции');
    }

    const query = `
      INSERT INTO concept_traditions (concept_id, tradition_id, relationship_strength)
      VALUES ($1, $2, $3)
      ON CONFLICT (concept_id, tradition_id) 
      DO UPDATE SET relationship_strength = $3
      RETURNING *
    `;

    await db.query(query, [conceptId, traditionId, relationshipStrength]);

    // Инвалидация кэша
    await redisClient.del(`concept:${conceptId}`);

    logger.info('Концепция связана с традицией', { conceptId, traditionId });
  }

  /**
   * Получение философов концепции
   */
  async getPhilosophers(conceptId) {
    const query = `
      SELECT p.*, cp.relationship_type
      FROM philosophers p
      INNER JOIN concept_philosophers cp ON p.philosopher_id = cp.philosopher_id
      WHERE cp.concept_id = $1
    `;

    const result = await db.query(query, [conceptId]);

    return result.rows;
  }

  /**
   * Получение традиций концепции
   */
  async getTraditions(conceptId) {
    const query = `
      SELECT t.*, ct.relationship_strength
      FROM traditions t
      INNER JOIN concept_traditions ct ON t.tradition_id = ct.tradition_id
      WHERE ct.concept_id = $1
    `;

    const result = await db.query(query, [conceptId]);

    return result.rows;
  }

  /**
   * Получение статистики концепции
   */
  async getStats(conceptId) {
    const concept = await this.findById(conceptId);
    if (!concept) {
      throw new NotFoundError('Concept', conceptId);
    }

    // Получаем статистику из Neo4j
    const cypher = `
      MATCH (c:Concept {concept_id: $conceptId})
      OPTIONAL MATCH (c)-[:HAS_CATEGORY]->(cat:Category)
      OPTIONAL MATCH (cat)-[r:RELATED_TO]->(:Category)
      RETURN 
        count(DISTINCT cat) as categoryCount,
        count(DISTINCT r) as relationshipCount,
        avg(cat.centrality) as avgCentrality,
        avg(r.strength) as avgStrength
    `;

    const records = await neo4jDb.executeRead(cypher, { conceptId });

    const neo4jStats = records[0] ? {
      categoryCount: records[0].get('categoryCount').toNumber(),
      relationshipCount: records[0].get('relationshipCount').toNumber(),
      avgCentrality: records[0].get('avgCentrality'),
      avgStrength: records[0].get('avgStrength')
    } : {
      categoryCount: 0,
      relationshipCount: 0,
      avgCentrality: 0,
      avgStrength: 0
    };

    return {
      ...concept.toJSON(),
      graph: neo4jStats,
      philosophers: (await this.getPhilosophers(conceptId)).length,
      traditions: (await this.getTraditions(conceptId)).length
    };
  }
}

module.exports = new ConceptService();