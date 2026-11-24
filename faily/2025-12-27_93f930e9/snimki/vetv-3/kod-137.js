/**
 * Сервис управления философами
 */

const { NotFoundError, ConflictError } = require('@philos/shared');
const db = require('../db/postgres-connection');
const redisClient = require('../db/redis-client');
const Philosopher = require('../models/Philosopher');

class PhilosopherService {
  /**
   * Создание философа
   */
  async create(philosopherData) {
    const philosopher = new Philosopher(philosopherData);
    const dbData = philosopher.toDB();

    const query = `
      INSERT INTO philosophers (
        philosopher_id, name, birth_year, death_year,
        description, traditions, key_works
      )
      VALUES ($1, $2, $3, $4, $5, $6, $7)
      RETURNING *
    `;

    const values = [
      dbData.philosopher_id,
      dbData.name,
      dbData.birth_year,
      dbData.death_year,
      dbData.description,
      dbData.traditions,
      dbData.key_works
    ];

    try {
      const result = await db.query(query, values);
      return Philosopher.fromDB(result.rows[0]);
    } catch (error) {
      if (error.code === '23505') { // unique violation
        throw new ConflictError('Философ с таким именем уже существует');
      }
      throw error;
    }
  }

  /**
   * Получение философа по ID
   */
  async findById(philosopherId) {
    const query = 'SELECT * FROM philosophers WHERE philosopher_id = $1';
    const result = await db.query(query, [philosopherId]);

    if (result.rows.length === 0) {
      throw new NotFoundError('Philosopher', philosopherId);
    }

    return Philosopher.fromDB(result.rows[0]);
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
   * Получение списка философов
   */
  async findAll(filters = {}, pagination = {}) {
    const { page = 1, limit = 50 } = pagination;
    const offset = (page - 1) * limit;

    let query = 'SELECT * FROM philosophers WHERE 1=1';
    const values = [];
    let paramCount = 1;

    // Фильтр по традиции
    if (filters.tradition) {
      query += ` AND traditions @> $${paramCount}`;
      values.push(JSON.stringify([filters.tradition]));
      paramCount++;
    }

    // Фильтр по периоду
    if (filters.startYear) {
      query += ` AND (birth_year >= $${paramCount} OR death_year >= $${paramCount})`;
      values.push(filters.startYear);
      paramCount++;
    }

    if (filters.endYear) {
      query += ` AND (birth_year <= $${paramCount} OR death_year <= $${paramCount})`;
      values.push(filters.endYear);
      paramCount++;
    }

    // Подсчет общего количества
    const countQuery = `SELECT COUNT(*) FROM (${query}) AS filtered`;
    const countResult = await db.query(countQuery, values);
    const total = parseInt(countResult.rows[0].count, 10);

    // Сортировка
    query += ' ORDER BY birth_year ASC NULLS LAST';

    // Пагинация
    query += ` LIMIT $${paramCount} OFFSET $${paramCount + 1}`;
    values.push(limit, offset);

    const result = await db.query(query, values);

    return {
      philosophers: result.rows.map(row => Philosopher.fromDB(row)),
      pagination: {
        page,
        limit,
        total,
        totalPages: Math.ceil(total / limit)
      }
    };
  }

  /**
   * Обновление философа
   */
  async update(philosopherId, updateData) {
    const allowedFields = [
      'name', 'birth_year', 'death_year', 'description',
      'traditions', 'key_works'
    ];

    const updates = [];
    const values = [];
    let paramCount = 1;

    for (const [key, value] of Object.entries(updateData)) {
      if (allowedFields.includes(key)) {
        updates.push(`${key} = $${paramCount}`);
        
        if (key === 'traditions' || key === 'key_works') {
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

    values.push(philosopherId);

    const query = `
      UPDATE philosophers
      SET ${updates.join(', ')}
      WHERE philosopher_id = $${paramCount}
      RETURNING *
    `;

    const result = await db.query(query, values);

    if (result.rows.length === 0) {
      throw new NotFoundError('Philosopher', philosopherId);
    }

    return Philosopher.fromDB(result.rows[0]);
  }

  /**
   * Удаление философа
   */
  async delete(philosopherId) {
    const query = 'DELETE FROM philosophers WHERE philosopher_id = $1 RETURNING *';
    const result = await db.query(query, [philosopherId]);

    if (result.rows.length === 0) {
      throw new NotFoundError('Philosopher', philosopherId);
    }

    return Philosopher.fromDB(result.rows[0]);
  }
}

module.exports = new PhilosopherService();