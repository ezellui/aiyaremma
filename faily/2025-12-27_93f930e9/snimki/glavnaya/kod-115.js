/**
 * Сервис управления пользователями
 */

const { NotFoundError, ValidationError } = require('@philos/shared');
const db = require('../db/postgres-connection');
const redisClient = require('../db/redis-client');
const User = require('../models/User');
const encryptionService = require('./encryption.service');

class UserService {
  /**
   * Создание пользователя
   */
  async create(userData) {
    const user = new User(userData);
    const dbData = user.toDB();

    const query = `
      INSERT INTO users (
        user_id, username, email, password_hash, role,
        user_settings, is_active, email_verified
      )
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
      RETURNING *
    `;

    const values = [
      dbData.user_id,
      dbData.username,
      dbData.email,
      dbData.password_hash,
      dbData.role,
      JSON.stringify(dbData.user_settings),
      dbData.is_active,
      dbData.email_verified
    ];

    const result = await db.query(query, values);
    return User.fromDB(result.rows[0]);
  }

  /**
   * Поиск пользователя по ID
   */
  async findById(userId) {
    // Проверка кэша
    const cached = await redisClient.get(`user:${userId}`);
    if (cached) {
      return User.fromDB(cached);
    }

    const query = 'SELECT * FROM users WHERE user_id = $1';
    const result = await db.query(query, [userId]);

    if (result.rows.length === 0) {
      return null;
    }

    const user = User.fromDB(result.rows[0]);

    // Кэшируем на 1 час
    await redisClient.set(`user:${userId}`, result.rows[0], 3600);

    return user;
  }

  /**
   * Поиск пользователя по email
   */
  async findByEmail(email) {
    const query = 'SELECT * FROM users WHERE email = $1';
    const result = await db.query(query, [email]);

    if (result.rows.length === 0) {
      return null;
    }

    return User.fromDB(result.rows[0]);
  }

  /**
   * Поиск пользователя по username
   */
  async findByUsername(username) {
    const query = 'SELECT * FROM users WHERE username = $1';
    const result = await db.query(query, [username]);

    if (result.rows.length === 0) {
      return null;
    }

    return User.fromDB(result.rows[0]);
  }

  /**
   * Обновление пользователя
   */
  async update(userId, updateData) {
    const allowedFields = ['username', 'email', 'user_settings'];
    const updates = [];
    const values = [];
    let paramCount = 1;

    for (const [key, value] of Object.entries(updateData)) {
      if (allowedFields.includes(key)) {
        updates.push(`${key} = $${paramCount}`);
        values.push(key === 'user_settings' ? JSON.stringify(value) : value);
        paramCount++;
      }
    }

    if (updates.length === 0) {
      throw new ValidationError('Нет полей для обновления');
    }

    values.push(userId);

    const query = `
      UPDATE users
      SET ${updates.join(', ')}, last_modified = CURRENT_TIMESTAMP
      WHERE user_id = $${paramCount}
      RETURNING *
    `;

    const result = await db.query(query, values);

    if (result.rows.length === 0) {
      throw new NotFoundError('User', userId);
    }

    // Инвалидация кэша
    await redisClient.del(`user:${userId}`);

    return User.fromDB(result.rows[0]);
  }

  /**
   * Обновление последнего входа
   */
  async updateLastLogin(userId) {
    const query = `
      UPDATE users
      SET last_login = CURRENT_TIMESTAMP
      WHERE user_id = $1
    `;

    await db.query(query, [userId]);

    // Инвалидация кэша
    await redisClient.del(`user:${userId}`);
  }

  /**
   * Установка API ключа Claude
   */
  async setApiKey(userId, apiKey) {
    const encrypted = encryptionService.encrypt(apiKey);

    const query = `
      UPDATE users
      SET claude_api_key_encrypted = $1,
          use_own_api_key = TRUE,
          api_key_added_at = CURRENT_TIMESTAMP
      WHERE user_id = $2
      RETURNING *
    `;

    const result = await db.query(query, [encrypted, userId]);

    if (result.rows.length === 0) {
      throw new NotFoundError('User', userId);
    }

    // Инвалидация кэша
    await redisClient.del(`user:${userId}`);

    return User.fromDB(result.rows[0]);
  }

  /**
   * Получение расшифрованного API ключа
   */
  async getApiKey(userId) {
    const user = await this.findById(userId);

    if (!user || !user.claudeApiKeyEncrypted) {
      return null;
    }

    return encryptionService.decrypt(user.claudeApiKeyEncrypted);
  }

  /**
   * Удаление API ключа
   */
  async removeApiKey(userId) {
    const query = `
      UPDATE users
      SET claude_api_key_encrypted = NULL,
          use_own_api_key = FALSE,
          api_key_added_at = NULL
      WHERE user_id = $1
      RETURNING *
    `;

    const result = await db.query(query, [userId]);

    if (result.rows.length === 0) {
      throw new NotFoundError('User', userId);
    }

    // Инвалидация кэша
    await redisClient.del(`user:${userId}`);

    return User.fromDB(result.rows[0]);
  }

  /**
   * Обновление времени использования API ключа
   */
  async updateApiKeyLastUsed(userId) {
    const query = `
      UPDATE users
      SET api_key_last_used = CURRENT_TIMESTAMP
      WHERE user_id = $1
    `;

    await db.query(query, [userId]);

    // Инвалидация кэша
    await redisClient.del(`user:${userId}`);
  }

  /**
   * Получение статистики использования API
   */
  async getApiUsageStats(userId, startDate = null, endDate = null) {
    const query = `
      SELECT * FROM get_api_usage_stats($1, $2, $3)
    `;

    const result = await db.query(query, [userId, startDate, endDate]);

    return result.rows[0] || {
      total_requests: 0,
      total_tokens: 0,
      total_cost: 0,
      by_operation: {}
    };
  }

  /**
   * Запись использования API
   */
  async recordApiUsage(usageData) {
    const query = `
      INSERT INTO api_key_usage (
        user_id, operation_type, tokens_used,
        estimated_cost, concept_id, request_metadata
      )
      VALUES ($1, $2, $3, $4, $5, $6)
      RETURNING *
    `;

    const values = [
      usageData.userId,
      usageData.operationType,
      usageData.tokensUsed || 0,
      usageData.estimatedCost || 0,
      usageData.conceptId || null,
      JSON.stringify(usageData.requestMetadata || {})
    ];

    await db.query(query, values);

    // Обновляем время последнего использования
    await this.updateApiKeyLastUsed(usageData.userId);
  }

  /**
   * Деактивация пользователя
   */
  async deactivate(userId) {
    const query = `
      UPDATE users
      SET is_active = FALSE
      WHERE user_id = $1
      RETURNING *
    `;

    const result = await db.query(query, [userId]);

    if (result.rows.length === 0) {
      throw new NotFoundError('User', userId);
    }

    // Инвалидация кэша
    await redisClient.del(`user:${userId}`);

    return User.fromDB(result.rows[0]);
  }

  /**
   * Активация пользователя
   */
  async activate(userId) {
    const query = `
      UPDATE users
      SET is_active = TRUE
      WHERE user_id = $1
      RETURNING *
    `;

    const result = await db.query(query, [userId]);

    if (result.rows.length === 0) {
      throw new NotFoundError('User', userId);
    }

    // Инвалидация кэша
    await redisClient.del(`user:${userId}`);

    return User.fromDB(result.rows[0]);
  }
}

module.exports = new UserService();