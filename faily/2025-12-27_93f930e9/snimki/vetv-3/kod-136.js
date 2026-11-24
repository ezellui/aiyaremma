/**
 * Сервис управления концепциями
 */

const { NotFoundError, ValidationError, ForbiddenError } = require('@philos/shared');
const db = require('../db/postgres-connection');
const redisClient = require('../db/redis-client');
const Concept = require('../models/Concept');
const { HttpClient } = require('@philos/shared');
const config = require('../config/config');

class ConceptService {
  constructor() {
    this.graphClient = new HttpClient(config.services.graph);
    this.thesisClient = new HttpClient(config.services.thesis);
  }

  /**
   * Создание концепции
   */
  async create(conceptData, userId) {
    const concept = new Concept({
      ...conceptData,
      creator_id: userId
    });

    const dbData = concept.toDB();

    const query = `
      INSERT INTO concepts (
        concept_id, creator_id, name, description,
        is_synthesis, is_public, parent_concepts,
        synthesis_method, focus, innovation_degree,
        historical_context, tags
      )
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
      RETURNING *
    `;

    const values = [
      dbData.concept_id,
      dbData.creator_id,
      dbData.name,
      dbData.description,
      dbData.is_synthesis,
      dbData.is_public,
      dbData.parent_concepts,
      dbData.synthesis_method,
      dbData.focus,
      dbData.innovation_degree,
      dbData.historical_context,
      dbData.tags
    ];

    const result = await db.query(query, values);
    return Concept.fromDB(result.rows[0]);
  }

  /**
   * Получение концепции по ID
   */
  async findById(conceptId, userId = null) {
    // Проверка кэша
    const cached = await redisClient.get(`concept:${conceptId}`);
    if (cached) {
      const concept = Concept.fromDB(cached);
      
      // Проверка доступа к приватной концепции
      if (!concept.isPublic && userId !== concept.creatorId) {
        throw new ForbiddenError('Доступ к этой концепции запрещен');
      }
      
      return concept;
    }

    const query = 'SELECT * FROM concepts WHERE concept_id = $1 AND is_archived = FALSE';
    const result = await db.query(query, [conceptId]);

    if (result.rows.length === 0) {
      throw new NotFoundError('Concept', conceptId);
    }

    const concept = Concept.fromDB(result.rows[0]);

    // Проверка доступа
    if (!concept.isPublic && userId !== concept.creatorId) {
      throw new ForbiddenError('Доступ к этой концепции запрещен');
    }

    // Кэшируем на 1 час
    await redisClient.set(`concept:${conceptId}`, result.rows[0], 3600);

    // Инкремент просмотров
    await this.incrementViews(conceptId);

    return concept;
  }

  /**
   * Получение списка концепций с фильтрацией и пагинацией
   */
  async findAll(filters = {}, pagination = {}) {
    const { page = 1, limit = 10 } = pagination;
    const offset = (page - 1) * limit;

    let query = `
      SELECT * FROM concepts
      WHERE is_archived = FALSE
    `;
    
    const conditions = [];
    const values = [];
    let paramCount = 1;

    // Фильтр по публичности
    if (filters.isPublic !== undefined) {
      conditions.push(`is_public = $${paramCount}`);
      values.push(filters.isPublic);
      paramCount++;
    }

    // Фильтр по создателю
    if (filters.creatorId) {
      conditions.push(`creator_id = $${paramCount}`);
      values.push(filters.creatorId);
      paramCount++;
    }

    // Фильтр по синтезу
    if (filters.isSynthesis !== undefined) {
      conditions.push(`is_synthesis = $${paramCount}`);
      values.push(filters.isSynthesis);
      paramCount++;
    }

    // Фильтр по тегам
    if (filters.tags && filters.tags.length > 0) {
      conditions.push(`tags @> $${paramCount}`);
      values.push(JSON.stringify(filters.tags));
      paramCount++;
    }

    // Поиск по названию и описанию
    if (filters.search) {
      conditions.push(`search_vector @@ plainto_tsquery('russian', $${paramCount})`);
      values.push(filters.search);
      paramCount++;
    }

    if (conditions.length > 0) {
      query += ' AND ' + conditions.join(' AND ');
    }

    // Подсчет общего количества
    const countQuery = `SELECT COUNT(*) FROM (${query}) AS filtered`;
    const countResult = await db.query(countQuery, values);
    const total = parseInt(countResult.rows[0].count, 10);

    // Сортировка
    const sortBy = filters.sortBy || 'creation_date';
    const sortOrder = filters.sortOrder || 'DESC';
    query += ` ORDER BY ${sortBy} ${sortOrder}`;

    // Пагинация
    query += ` LIMIT $${paramCount} OFFSET $${paramCount + 1}`;
    values.push(limit, offset);

    const result = await db.query(query, values);

    return {
      concepts: result.rows.map(row => Concept.fromDB(row)),
      pagination: {
        page,
        limit,
        total,
        totalPages: Math.ceil(total / limit)
      }
    };
  }

  /**
   * Обновление концепции
   */
  async update(conceptId, updateData, userId) {
    // Проверка прав
    const concept = await this.findById(conceptId);
    if (concept.creatorId !== userId) {
      throw new ForbiddenError('Вы не можете редактировать эту концепцию');
    }

    const allowedFields = [
      'name', 'description', 'is_public', 'focus',
      'innovation_degree', 'historical_context', 'tags'
    ];
    
    const updates = [];
    const values = [];
    let paramCount = 1;

    for (const [key, value] of Object.entries(updateData)) {
      if (allowedFields.includes(key)) {
        const dbKey = key.replace(/([A-Z])/g, '_$1').toLowerCase();
        updates.push(`${dbKey} = $${paramCount}`);
        
        if (key === 'tags') {
          values.push(JSON.stringify(value));
        } else {
          values.push(value);
        }
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

    if (result.rows.length === 0) {
      throw new NotFoundError('Concept', conceptId);
    }

    // Инвалидация кэша
    await redisClient.del(`concept:${conceptId}`);

    return Concept.fromDB(result.rows[0]);
  }

  /**
   * Удаление концепции (архивирование)
   */
  async delete(conceptId, userId) {
    // Проверка прав
    const concept = await this.findById(conceptId);
    if (concept.creatorId !== userId) {
      throw new ForbiddenError('Вы не можете удалить эту концепцию');
    }

    const query = `
      UPDATE concepts
      SET is_archived = TRUE, last_modified = CURRENT_TIMESTAMP
      WHERE concept_id = $1
      RETURNING *
    `;

    const result = await db.query(query, [conceptId]);

    if (result.rows.length === 0) {
      throw new NotFoundError('Concept', conceptId);
    }

    // Инвалидация кэша
    await redisClient.del(`concept:${conceptId}`);

    return Concept.fromDB(result.rows[0]);
  }

  /**
   * Инкремент просмотров
   */
  async incrementViews(conceptId) {
    const query = `
      UPDATE concepts
      SET views_count = views_count + 1
      WHERE concept_id = $1
    `;

    await db.query(query, [conceptId]);

    // Инвалидация кэша
    await redisClient.del(`concept:${conceptId}`);
  }

  /**
   * Инкремент лайков
   */
  async incrementLikes(conceptId) {
    const query = `
      UPDATE concepts
      SET likes_count = likes_count + 1
      WHERE concept_id = $1
      RETURNING *
    `;

    const result = await db.query(query, [conceptId]);

    // Инвалидация кэша
    await redisClient.del(`concept:${conceptId}`);

    return Concept.fromDB(result.rows[0]);
  }

  /**
   * Связывание концепции с философом
   */
  async addPhilosopher(conceptId, philosopherId, relationshipType = 'influenced_by') {
    const query = `
      INSERT INTO concept_philosophers (concept_id, philosopher_id, relationship_type)
      VALUES ($1, $2, $3)
      ON CONFLICT (concept_id, philosopher_id) DO UPDATE
      SET relationship_type = $3
      RETURNING *
    `;

    await db.query(query, [conceptId, philosopherId, relationshipType]);

    // Инвалидация кэша
    await redisClient.del(`concept:${conceptId}`);
    await redisClient.del(`concept:${conceptId}:philosophers`);
  }

  /**
   * Получение философов концепции
   */
  async getPhilosophers(conceptId) {
    // Проверка кэша
    const cached = await redisClient.get(`concept:${conceptId}:philosophers`);
    if (cached) {
      return cached;
    }

    const query = `
      SELECT p.*, cp.relationship_type
      FROM philosophers p
      JOIN concept_philosophers cp ON p.philosopher_id = cp.philosopher_id
      WHERE cp.concept_id = $1
    `;

    const result = await db.query(query, [conceptId]);

    const philosophers = result.rows;

    // Кэшируем на 1 час
    await redisClient.set(`concept:${conceptId}:philosophers`, philosophers, 3600);

    return philosophers;
  }

  /**
   * Связывание концепции с традицией
   */
  async addTradition(conceptId, traditionId, relationshipStrength = 1.0) {
    const query = `
      INSERT INTO concept_traditions (concept_id, tradition_id, relationship_strength)
      VALUES ($1, $2, $3)
      ON CONFLICT (concept_id, tradition_id) DO UPDATE
      SET relationship_strength = $3
      RETURNING *
    `;

    await db.query(query, [conceptId, traditionId, relationshipStrength]);

    // Инвалидация кэша
    await redisClient.del(`concept:${conceptId}`);
    await redisClient.del(`concept:${conceptId}:traditions`);
  }

  /**
   * Получение традиций концепции
   */
  async getTraditions(conceptId) {
    // Проверка кэша
    const cached = await redisClient.get(`concept:${conceptId}:traditions`);
    if (cached) {
      return cached;
    }

    const query = `
      SELECT t.*, ct.relationship_strength
      FROM traditions t
      JOIN concept_traditions ct ON t.tradition_id = ct.tradition_id
      WHERE ct.concept_id = $1
    `;

    const result = await db.query(query, [conceptId]);

    const traditions = result.rows;

    // Кэшируем на 1 час
    await redisClient.set(`concept:${conceptId}:traditions`, traditions, 3600);

    return traditions;
  }

  /**
   * Получение полной информации о концепции (с графом и тезисами)
   */
  async getFullConcept(conceptId, userId = null) {
    const concept = await this.findById(conceptId, userId);

    try {
      // Получаем граф из Graph Service
      const graph = await this.graphClient.get(`/concepts/${conceptId}`);
      concept.graph = graph;
    } catch (error) {
      concept.graph = null;
    }

    try {
      // Получаем тезисы из Thesis Service
      const theses = await this.thesisClient.get(`/concepts/${conceptId}`);
      concept.theses = theses;
    } catch (error) {
      concept.theses = [];
    }

    // Получаем связанных философов
    concept.philosophers = await this.getPhilosophers(conceptId);

    // Получаем связанные традиции
    concept.traditions = await this.getTraditions(conceptId);

    return concept;
  }
}

module.exports = new ConceptService();