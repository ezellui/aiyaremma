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

  async connect() {
    if (this.driver) {
      return this.driver;
    }

    try {
      this.driver = neo4j.driver(
        config.database.neo4j.url,
        neo4j.auth.basic(
          config.database.neo4j.user,
          config.database.neo4j.password
        ),
        {
          maxConnectionPoolSize: 50,
          connectionAcquisitionTimeout: 30000
        }
      );

      // Проверка подключения
      await this.driver.verifyConnectivity();
      
      logger.info('Neo4j подключен');
      
      return this.driver;
    } catch (error) {
      logger.error('Ошибка подключения к Neo4j:', error);
      throw error;
    }
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
      throw new Error('Neo4j не подключен. Вызовите connect() сначала.');
    }
    return this.driver;
  }

  getSession(database = null) {
    const sessionConfig = {};
    if (database) {
      sessionConfig.database = database;
    }
    return this.getDriver().session(sessionConfig);
  }

  async executeRead(cypher, params = {}) {
    const session = this.getSession();
    try {
      const result = await session.executeRead(tx => 
        tx.run(cypher, params)
      );
      return result.records;
    } finally {
      await session.close();
    }
  }

  async executeWrite(cypher, params = {}) {
    const session = this.getSession();
    try {
      const result = await session.executeWrite(tx => 
        tx.run(cypher, params)
      );
      return result.records;
    } finally {
      await session.close();
    }
  }

  async executeTransaction(callback) {
    const session = this.getSession();
    try {
      return await session.executeWrite(callback);
    } finally {
      await session.close();
    }
  }
}

module.exports = new Neo4jConnection();