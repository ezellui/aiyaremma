/**
 * Сервис управления философскими традициями
 */

const { NotFoundError, ConflictError } = require('@philos/shared');
const db = require('../db/postgres-connection');
const redisClient = require('../db/redis-client');
const Tradition = require('../models/Tradition');
const logger = require('@philos/shared').logger.createServiceLogger('concept-service');

class TraditionService {
  /**
   * Создание традиции
   */
  async create(traditionData) {
    // Проверка на дубликаты
    const existing = await this.findByName(traditionData.name);
    if (existing) {
      throw new ConflictError('Традиция с таким названием уже существует');
    }

    const tradition = new Tradition(traditionData);
    const dbData = tradition.toDB();

    const query = `
      INSERT INTO traditions (
        tradition_id, name, time_period,
        key_figures, related_traditions
      )
      VALUES ($1, $2, $3, $4, $5)
      RETURNING *
    `;

    const values = [
      dbData.tradition_id,
      dbData.name,
      dbData.time_period,
      JSON.stringify(dbData.key_figures),
      JSON.stringify(dbData.related_traditions)
    ];

    const result = await db.query(query, values);

    logger.info('Традиция создана', { traditionId: result.rows[0].tradition_id });

    return Tradition.fromDB(result.rows[0]);
  }

  /**
   * Получение традиции по ID
   */
  async findById(traditionId) {
    // Проверка кэша
    const cached = await redisClient.get(`tradition:${traditionId}`);
    if (cached) {
      return Tradition.fromDB(cached);
    }

    const query = 'SELECT * FROM traditions WHERE tradition_id = $1';
    const result = await db.query(query, [traditionId]);

    if (result.rows.length === 0) {
      return null;
    }

    const tradition = Tradition.fromDB(result.rows[0]);

    // Кэшируем на 1 час
    await redisClient.set(`tradition:${traditionId}`, result.rows[0], 3600);

    return tradition;
  }

  /**
   * Получение традиции по имени
   */
  async findByName(name) {
    const query = 'SELECT * FROM traditions WHERE name = $1';
    const result = await db.query(query, [name]);

    if (result.rows.length === 0) {
      return null;
    }

    return Tradition.fromDB(result.rows[0]);
  }

  /**
   * Получение всех традиций
   */
  async findAll(options = {}) {
    const { limit = 100, offset = 0 } = options;

    const query = `
      SELECT * FROM traditions
      ORDER BY name
      LIMIT $1 OFFSET $2
    `;

    const result = await db.query(query, [limit, offset]);

    return result.rows.map(row => Tradition.fromDB(row));
  }

  /**
   * Обновление традиции
   */
  async update(traditionId, updateData) {
    const tradition = await this.findById(traditionId);
    if (!tradition) {
      throw new NotFoundError('Tradition', traditionId);
    }

    const allowedFields = ['name', 'time_period', 'key_figures', 'related_traditions'];
    const updates = [];
    const values = [];
    let paramCount = 1;

    for (const [key, value] of Object.entries(updateData)) {
      if (allowedFields.includes(key)) {
        updates.push(`${key} = $${paramCount}`);
        values.push(['key_figures', 'related_traditions'].includes(key) ? JSON.stringify(value) : value);
        paramCount++;
      }
    }

    if (updates.length === 0) {
      return tradition;
    }

    values.push(traditionId);

    const query = `
      UPDATE traditions
      SET ${updates.join(', ')}
      WHERE tradition_id = $${paramCount}
      RETURNING *
    `;

    const result = await db.query(query, values);

    // Инвалидация кэша
    await redisClient.del(`tradition:${traditionId}`);

    return Tradition.fromDB(result.rows[0]);
  }

  /**
   * Удаление традиции
   */
  async delete(traditionId) {
    const tradition = await this.findById(traditionId);
    if (!tradition) {
      throw new NotFoundError('Tradition', traditionId);
    }

    const query = 'DELETE FROM traditions WHERE tradition_id = $1';
    await db.query(query, [traditionId]);

    // Инвалидация кэша
    await redisClient.del(`tradition:${traditionId}`);

    logger.info('Традиция удалена', { traditionId });
  }

  /**
   * Получение концепций традиции
   */
  async getConcepts(traditionId) {
    const query = `
      SELECT c.*, ct.relationship_strength
      FROM concepts c
      INNER JOIN concept_traditions ct ON c.concept_id = ct.concept_id
      WHERE ct.tradition_id = $1
      ORDER BY c.created_at DESC
    `;

    const result = await db.query(query, [traditionId]);

    return result.rows;
  }

  /**
   * Поиск традиций
   */
  async search(searchTerm, options = {}) {
    const { limit = 50, offset = 0 } = options;

    const query = `
      SELECT * FROM traditions
      WHERE name ILIKE $1 OR time_period ILIKE $1
      ORDER BY name
      LIMIT $2 OFFSET $3
    `;

    const result = await db.query(query, [`%${searchTerm}%`, limit, offset]);

    return result.rows.map(row => Tradition.fromDB(row));
  }
}

module.exports = new TraditionService();