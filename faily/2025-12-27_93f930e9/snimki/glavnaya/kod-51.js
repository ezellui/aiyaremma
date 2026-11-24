/**
 * Подключение к Neo4j
 */

const neo4j = require('neo4j-driver');
const config = require('../config/config');
const logger = require('@philos/shared').logger.createServiceLogger(config.serviceName);

class Neo4jConnection {
  constructor() {
    this.driver = null;
  }

  connect() {
    if (this.driver) {
      return this.driver;
    }

    this.driver = neo4j.driver(
      config.database.neo4j.url,
      neo4j.auth.basic(config.database.neo4j.user, config.database.neo4j.password),
      {
        maxConnectionPoolSize: 50,
        connectionAcquisitionTimeout: 2000,
      }
    );

    logger.info('Neo4j драйвер инициализирован');

    return this.driver;
  }

  async disconnect() {
    if (this.driver) {
      await this.driver.close();
      this.driver = null;
      logger.info('Neo4j отключен');
    }
  }

  getDriver() {
    if (!this.driver) {
      this.connect();
    }
    return this.driver;
  }

  /**
   * Создает сессию для работы с БД
   */
  getSession(database = null) {
    const sessionConfig = database ? { database } : {};
    return this.getDriver().session(sessionConfig);
  }

  /**
   * Выполняет Cypher запрос
   */
  async run(cypher, params = {}, database = null) {
    const session = this.getSession(database);
    try {
      const result = await session.run(cypher, params);
      return result;
    } catch (error) {
      logger.error('Neo4j query error:', error);
      throw error;
    } finally {
      await session.close();
    }
  }

  /**
   * Выполняет транзакцию
   */
  async executeTransaction(callback, database = null) {
    const session = this.getSession(database);
    try {
      const result = await session.executeWrite(callback);
      return result;
    } catch (error) {
      logger.error('Neo4j transaction error:', error);
      throw error;
    } finally {
      await session.close();
    }
  }
}

module.exports = new Neo4jConnection();