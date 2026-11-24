/**
 * Подключение к PostgreSQL
 */

const { Pool } = require('pg');
const config = require('../config/config');
const logger = require('@philos/shared').logger.createServiceLogger(config.serviceName);

class PostgresConnection {
  constructor() {
    this.pool = null;
  }

  connect() {
    if (this.pool) {
      return this.pool;
    }

    this.pool = new Pool(config.database.postgres);

    this.pool.on('connect', () => {
      logger.info('PostgreSQL подключен');
    });

    this.pool.on('error', (err) => {
      logger.error('Неожиданная ошибка PostgreSQL:', err);
    });

    return this.pool;
  }

  async disconnect() {
    if (this.pool) {
      await this.pool.end();
      this.pool = null;
      logger.info('PostgreSQL отключен');
    }
  }

  getPool() {
    if (!this.pool) {
      this.connect();
    }
    return this.pool;
  }

  /**
   * Выполняет запрос к БД
   */
  async query(text, params) {
    const start = Date.now();
    try {
      const result = await this.getPool().query(text, params);
      const duration = Date.now() - start;
      logger.debug(`Executed query: ${text.substring(0, 100)}... Duration: ${duration}ms`);
      return result;
    } catch (error) {
      logger.error('Query error:', error);
      throw error;
    }
  }

  /**
   * Выполняет транзакцию
   */
  async transaction(callback) {
    const client = await this.getPool().connect();
    try {
      await client.query('BEGIN');
      const result = await callback(client);
      await client.query('COMMIT');
      return result;
    } catch (error) {
      await client.query('ROLLBACK');
      throw error;
    } finally {
      client.release();
    }
  }
}

module.exports = new PostgresConnection();