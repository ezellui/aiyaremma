/**
 * Подключение к MongoDB
 */

const { MongoClient } = require('mongodb');
const config = require('../config/config');
const logger = require('@philos/shared').logger.createServiceLogger(config.serviceName);

class MongoConnection {
  constructor() {
    this.client = null;
    this.db = null;
  }

  async connect() {
    if (this.client && this.client.topology && this.client.topology.isConnected()) {
      return this.db;
    }

    try {
      this.client = await MongoClient.connect(config.database.mongodb.url, {
        maxPoolSize: 10,
        minPoolSize: 5,
        serverSelectionTimeoutMS: 5000,
        socketTimeoutMS: 45000,
      });

      this.db = this.client.db();
      
      logger.info('MongoDB подключен');
      
      return this.db;
    } catch (error) {
      logger.error('Ошибка подключения к MongoDB:', error);
      throw error;
    }
  }

  async disconnect() {
    if (this.client) {
      await this.client.close();
      this.client = null;
      this.db = null;
      logger.info('MongoDB отключен');
    }
  }

  getDb() {
    if (!this.db) {
      throw new Error('MongoDB не подключен. Вызовите connect() сначала.');
    }
    return this.db;
  }

  /**
   * Получает коллекцию
   */
  getCollection(name) {
    return this.getDb().collection(name);
  }
}

module.exports = new MongoConnection();