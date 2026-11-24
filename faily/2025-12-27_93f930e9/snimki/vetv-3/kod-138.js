/**
 * Сервис управления философскими традициями
 */

const { NotFoundError, ConflictError, ValidationError } = require('@philos/shared');
const db = require('../db/postgres-connection');
const Tradition = require('../models/Tradition');

class TraditionService {
  /**
   * Создание традиции
   */
  async create(traditionData) {
    const tradition = new Tradition(traditionData);
    const dbData = tradition.toDB();

    const query = `
      INSERT INTO traditions (
        tradition_id, name, time_period, description,
        key_figures, related_traditions
      )
      VALUES ($1, $2, $3, $4, $5, $6)
      RETURNING *
    `;

    const values = [
      dbData.tradition_id,
      dbData.name,
      dbData.time_period,
      dbData.description,
      dbData.key_figures,
      dbData.related_traditions
    ];

    try {
      const result = await db.query(query, values);
      return Tradition.fromDB(result.rows[0]);
    } catch (error) {
      if (error.code === '23505') { // unique violation
        throw new ConflictError('Традиция с таким именем уже существует');
      }
      throw error;
    }
  }

  /**
   * Получение традиции по ID
   */
  async findById(traditionId) {
    const query = 'SELECT * FROM traditions WHERE tradition_id = $1';
    const result = await db.query(query, [traditionId]);

    if (result.rows.length === 0) {
      throw new NotFoundError('Tradition', traditionId);
    }

    return Tradition.fromDB(result.rows[0]);
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
   * Получение списка традиций
   */
  async findAll(pagination = {}) {
    const { page = 1, limit = 50 } = pagination;
    const offset = (page - 1) * limit;

    // Подсчет общего количества
    const countQuery = 'SELECT COUNT(*) FROM traditions';
    const countResult = await db.query(countQuery);
    const total = parseInt(countResult.rows[0].count, 10);

    const query = `
      SELECT * FROM traditions
      ORDER BY name ASC
      LIMIT $1 OFFSET $2
    `;

    const result = await db.query(query, [limit, offset]);

    return {
      traditions: result.rows.map(row => Tradition.fromDB(row)),
      pagination: {
        page,
        limit,
        total,
        totalPages: Math.ceil(total / limit)
      }
    };
  }

  /**
   * Обновление традиции
   */
  async update(traditionId, updateData) {
    const allowedFields = [
      'name', 'time_period', 'description',
      'key_figures', 'related_traditions'
    ];

    const updates = [];
    const values = [];
    let paramCount = 1;

    for (const [key, value] of Object.entries(updateData)) {
      if (allowedFields.includes(key)) {
        updates.push(`${key} = $${paramCount}`);
        
        if (key === 'key_figures' || key === 'related_traditions') {
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

    values.push(traditionId);

    const query = `
      UPDATE traditions
      SET ${updates.join(', ')}
      WHERE tradition_id = $${paramCount}
      RETURNING *
    `;

    const result = await db.query(query, values);

    if (result.rows.length === 0) {
      throw new NotFoundError('Tradition', traditionId);
    }

    return Tradition.fromDB(result.rows[0]);
  }

  /**
   * Удаление традиции
   */
  async delete(traditionId) {
    const query = 'DELETE FROM traditions WHERE tradition_id = $1 RETURNING *';
    const result = await db.query(query, [traditionId]);

    if (result.rows.length === 0) {
      throw new NotFoundError('Tradition', traditionId);
    }

    return Tradition.fromDB(result.rows[0]);
  }
}

module.exports = new TraditionService();