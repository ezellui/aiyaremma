/**
 * Сервис управления философами
 */

const { NotFoundError, ConflictError } = require('@philos/shared');
const db = require('../db/postgres-connection');
const redisClient = require('../db/redis-client');
const Philosopher = require('../models/Philosopher');
const logger = require('@philos/shared').logger.createServiceLogger('concept-service');

class PhilosopherService {
  /**
   * Создание философа
   */
  async create(philosopherData) {
    // Проверка на дубликаты
    const existing = await this.findByName(philosopherData.name);
    if (existing) {
      throw new ConflictError('Философ с таким именем уже существует');
    }

    const philosopher = new Philosopher(philosopherData);
    const dbData = philosopher.toDB();

    const query = `
      INSERT INTO philosophers (
        philosopher_id, name, birth_year, death_year,
        traditions, key_works
      )
      VALUES ($1, $2, $3, $4, $5, $6)
      RETURNING *
    `;

    const values = [
      dbData.philosopher_id,
      dbData.name,
      dbData.birth_year,
      dbData.death_year,
      JSON.stringify(dbData.traditions),
      JSON.stringify(dbData.key_works)
    ];

    const result = await db.query(query, values);

    logger.info('Философ создан', { philosopherId: result.rows[0].philosopher_id });

    return Philosopher.fromDB(result.rows[0]);
  }

  /**
   * Получение философа по ID
   */
  async findById(philosopherId) {
    // Проверка кэша
    const cached = await redisClient.get(`philosopher:${philosopherId}`);
    if (cached) {
      return Philosopher.fromDB(cached);
    }

    const query = 'SELECT * FROM philosophers WHERE philosopher_id = $1';
    const result = await db.query(query, [philosopherId]);

    if (result.rows.length === 0) {
      return null;
    }

    const philosopher = Philosopher.fromDB(result.rows[0]);

    // Кэшируем на 1 час
    await redisClient.set(`philosopher:${philosopherId}`, result.rows[0], 3600);

    return philosopher;
  }

  /**
   * Получение философа по имени
   */
  async findByName(name) {
    const query = 'SELECT * FROM philosophers WHERE name = $1';
    const result = await db.query(query, [name]);

    if (result.rows.length === 0) {
      return null;
    }

    return Philosopher.fromDB(result.rows[0]);
  }

  /**
   * Получение всех философов
   */
  async findAll(options = {}) {
    const {
      limit = 100,
      offset = 0,
      tradition = null
    } = options;

    let query = 'SELECT * FROM philosophers';
    const params = [];
    let paramCount = 0;

    if (tradition) {
      paramCount++;
      query += ` WHERE traditions @> $${paramCount}::jsonb`;
      params.push(JSON.stringify([tradition]));
    }

    query += ` ORDER BY name LIMIT $${paramCount + 1} OFFSET $${paramCount + 2}`;
    params.push(limit, offset);

    const result = await db.query(query, params);

    return result.rows.map(row => Philosopher.fromDB(row));
  }

  /**
   * Обновление философа
   */
  async update(philosopherId, updateData) {
    const philosopher = await this.findById(philosopherId);
    if (!philosopher) {
      throw new NotFoundError('Philosopher', philosopherId);
    }

    const allowedFields = ['name', 'birth_year', 'death_year', 'traditions', 'key_works'];
    const updates = [];
    const values = [];
    let paramCount = 1;

    for (const [key, value] of Object.entries(updateData)) {
      if (allowedFields.includes(key)) {
        updates.push(`${key} = $${paramCount}`);
        values.push(['traditions', 'key_works'].includes(key) ? JSON.stringify(value) : value);
        paramCount++;
      }
    }

    if (updates.length === 0) {
      return philosopher;
    }

    values.push(philosopherId);

    const query = `
      UPDATE philosophers
      SET ${updates.join(', ')}
      WHERE philosopher_id = $${paramCount}
      RETURNING *
    `;

    const result = await db.query(query, values);

    // Инвалидация кэша
    await redisClient.del(`philosopher:${philosopherId}`);

    return Philosopher.fromDB(result.rows[0]);
  }

  /**
   * Удаление философа
   */
  async delete(philosopherId) {
    const philosopher = await this.findById(philosopherId);
    if (!philosopher) {
      throw new NotFoundError('Philosopher', philosopherId);
    }

    const query = 'DELETE FROM philosophers WHERE philosopher_id = $1';
    await db.query(query, [philosopherId]);

    // Инвалидация кэша
    await redisClient.del(`philosopher:${philosopherId}`);

    logger.info('Философ удален', { philosopherId });
  }

  /**
   * Получение концепций философа
   */
  async getConcepts(philosopherId) {
    const query = `
      SELECT c.*, cp.relationship_type
      FROM concepts c
      INNER JOIN concept_philosophers cp ON c.concept_id = cp.concept_id
      WHERE cp.philosopher_id = $1
      ORDER BY c.created_at DESC
    `;

    const result = await db.query(query, [philosopherId]);

    return result.rows;
  }

  /**
   * Поиск философов
   */
  async search(searchTerm, options = {}) {
    const { limit = 50, offset = 0 } = options;

    const query = `
      SELECT * FROM philosophers
      WHERE name ILIKE $1
      ORDER BY name
      LIMIT $2 OFFSET $3
    `;

    const result = await db.query(query, [`%${searchTerm}%`, limit, offset]);

    return result.rows.map(row => Philosopher.fromDB(row));
  }
}

module.exports = new PhilosopherService();