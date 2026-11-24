/**
 * Сервис поиска концепций
 */

const db = require('../db/postgres-connection');
const neo4jDb = require('../db/neo4j-connection');
const config = require('../config/config');
const Concept = require('../models/Concept');
const logger = require('@philos/shared').logger.createServiceLogger('concept-service');

class SearchService {
  /**
   * Полнотекстовый поиск концепций
   */
  async searchConcepts(searchTerm, options = {}) {
    const {
      limit = config.search.resultsLimit,
      offset = 0,
      userId = null,
      publicOnly = true
    } = options;

    let query = `
      SELECT 
        c.*,
        ts_rank(search_vector, plainto_tsquery('russian', $1)) AS rank
      FROM concepts c
      WHERE search_vector @@ plainto_tsquery('russian', $1)
    `;

    const params = [searchTerm];
    let paramCount = 1;

    if (publicOnly && !userId) {
      query += ' AND is_public = true';
    } else if (userId) {
      paramCount++;
      query += ` AND (is_public = true OR creator_id = $${paramCount})`;
      params.push(userId);
    }

    query += ` ORDER BY rank DESC, created_at DESC LIMIT $${paramCount + 1} OFFSET $${paramCount + 2}`;
    params.push(limit, offset);

    const result = await db.query(query, params);

    return result.rows.map(row => ({
      concept: Concept.fromDB(row),
      rank: parseFloat(row.rank)
    }));
  }

  /**
   * Поиск по тегам
   */
  async searchByTags(tags, options = {}) {
    const {
      limit = config.search.resultsLimit,
      offset = 0,
      userId = null,
      publicOnly = true
    } = options;

    let query = `
      SELECT * FROM concepts
      WHERE tags @> $1::jsonb
    `;

    const params = [JSON.stringify(tags)];
    let paramCount = 1;

    if (publicOnly && !userId) {
      query += ' AND is_public = true';
    } else if (userId) {
      paramCount++;
      query += ` AND (is_public = true OR creator_id = $${paramCount})`;
      params.push(userId);
    }

    query += ` ORDER BY created_at DESC LIMIT $${paramCount + 1} OFFSET $${paramCount + 2}`;
    params.push(limit, offset);

    const result = await db.query(query, params);

    return result.rows.map(row => Concept.fromDB(row));
  }

  /**
   * Поиск концепций по философу
   */
  async searchByPhilosopher(philosopherId, options = {}) {
    const { limit = config.search.resultsLimit, offset = 0 } = options;

    const query = `
      SELECT c.*, cp.relationship_type
      FROM concepts c
      INNER JOIN concept_philosophers cp ON c.concept_id = cp.concept_id
      WHERE cp.philosopher_id = $1 AND c.is_public = true
      ORDER BY c.created_at DESC
      LIMIT $2 OFFSET $3
    `;

    const result = await db.query(query, [philosopherId, limit, offset]);

    return result.rows.map(row => Concept.fromDB(row));
  }

  /**
   * Поиск концепций по традиции
   */
  async searchByTradition(traditionId, options = {}) {
    const { limit = config.search.resultsLimit, offset = 0 } = options;

    const query = `
      SELECT c.*, ct.relationship_strength
      FROM concepts c
      INNER JOIN concept_traditions ct ON c.concept_id = ct.concept_id
      WHERE ct.tradition_id = $1 AND c.is_public = true
      ORDER BY c.created_at DESC
      LIMIT $2 OFFSET $3
    `;

    const result = await db.query(query, [traditionId, limit, offset]);

    return result.rows.map(row => Concept.fromDB(row));
  }

  /**
   * Поиск похожих концепций через Neo4j
   */
  async findSimilar(conceptId, options = {}) {
    const { limit = 10 } = options;

    const cypher = `
      MATCH (c:Concept {concept_id: $conceptId})-[:HAS_CATEGORY]->(cat:Category)
      MATCH (similar:Concept)-[:HAS_CATEGORY]->(cat)
      WHERE similar.concept_id <> $conceptId
      WITH similar, count(cat) as sharedCategories
      ORDER BY sharedCategories DESC
      LIMIT $limit
      RETURN similar.concept_id as conceptId, sharedCategories
    `;

    const params = { conceptId, limit };

    const records = await neo4jDb.executeRead(cypher, params);

    const similarConceptIds = records.map(r => r.get('conceptId'));

    if (similarConceptIds.length === 0) {
      return [];
    }

    // Получаем полные данные из PostgreSQL
    const query = `
      SELECT * FROM concepts
      WHERE concept_id = ANY($1)
      ORDER BY created_at DESC
    `;

    const result = await db.query(query, [similarConceptIds]);

    return result.rows.map(row => Concept.fromDB(row));
  }

  /**
   * Расширенный поиск с фильтрами
   */
  async advancedSearch(filters, options = {}) {
    const {
      limit = config.search.resultsLimit,
      offset = 0,
      userId = null
    } = options;

    let query = 'SELECT * FROM concepts WHERE 1=1';
    const params = [];
    let paramCount = 0;

    // Фильтр по тексту
    if (filters.searchTerm) {
      paramCount++;
      query += ` AND search_vector @@ plainto_tsquery('russian', $${paramCount})`;
      params.push(filters.searchTerm);
    }

    // Фильтр по синтезу
    if (filters.isSynthesis !== undefined) {
      paramCount++;
      query += ` AND is_synthesis = $${paramCount}`;
      params.push(filters.isSynthesis);
    }

    // Фильтр по степени инновации
    if (filters.innovationDegree) {
      paramCount++;
      query += ` AND innovation_degree = $${paramCount}`;
      params.push(filters.innovationDegree);
    }

    // Фильтр по тегам
    if (filters.tags && filters.tags.length > 0) {
      paramCount++;
      query += ` AND tags @> $${paramCount}::jsonb`;
      params.push(JSON.stringify(filters.tags));
    }

    // Фильтр по создателю
    if (filters.creatorId) {
      paramCount++;
      query += ` AND creator_id = $${paramCount}`;
      params.push(filters.creatorId);
    }

    // Фильтр по видимости
    if (!userId || filters.publicOnly) {
      query += ' AND is_public = true';
    } else if (userId) {
      paramCount++;
      query += ` AND (is_public = true OR creator_id = $${paramCount})`;
      params.push(userId);
    }

    // Сортировка
    const sortField = filters.sortBy || 'created_at';
    const sortOrder = filters.sortOrder || 'DESC';
    query += ` ORDER BY ${sortField} ${sortOrder}`;

    query += ` LIMIT $${paramCount + 1} OFFSET $${paramCount + 2}`;
    params.push(limit, offset);

    const result = await db.query(query, params);

    return result.rows.map(row => Concept.fromDB(row));
  }

  /**
   * Получение популярных тегов
   */
  async getPopularTags(limit = 20) {
    const query = `
      SELECT 
        jsonb_array_elements_text(tags) as tag,
        COUNT(*) as count
      FROM concepts
      WHERE is_public = true
      GROUP BY tag
      ORDER BY count DESC, tag ASC
      LIMIT $1
    `;

    const result = await db.query(query, [limit]);

    return result.rows.map(row => ({
      tag: row.tag,
      count: parseInt(row.count)
    }));
  }
}

module.exports = new SearchService();