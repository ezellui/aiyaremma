/**
 * Redis клиент для API Gateway
 */

const Redis = require('ioredis');
const config = require('./config');
const logger = require('@philos/shared').logger.createServiceLogger(config.serviceName);

class RedisClient {
  constructor() {
    this.client = null;
    this.isConnected = false;
  }

  async connect() {
    if (this.client && this.isConnected) {
      return this.client;
    }

    this.client = new Redis(config.redis.url, {
      keyPrefix: config.redis.keyPrefix,
      retryStrategy(times) {
        const delay = Math.min(times * 50, 2000);
        return delay;
      },
      reconnectOnError(err) {
        logger.error('Redis reconnect on error:', err);
        return true;
      },
      maxRetriesPerRequest: 3
    });

    this.client.on('connect', () => {
      this.isConnected = true;
      logger.info('Redis подключен');
    });

    this.client.on('ready', () => {
      logger.info('Redis готов к работе');
    });

    this.client.on('error', (err) => {
      this.isConnected = false;
      logger.error('Ошибка Redis:', err);
    });

    this.client.on('close', () => {
      this.isConnected = false;
      logger.warn('Redis соединение закрыто');
    });

    return this.client;
  }

  async disconnect() {
    if (this.client) {
      await this.client.quit();
      this.client = null;
      this.isConnected = false;
      logger.info('Redis отключен');
    }
  }

  getClient() {
    if (!this.client) {
      throw new Error('Redis не подключен. Вызовите connect() сначала.');
    }
    return this.client;
  }

  /**
   * Сохраняет значение с TTL
   */
  async set(key, value, ttl = 3600) {
    try {
      const serialized = JSON.stringify(value);
      await this.getClient().setex(key, ttl, serialized);
    } catch (error) {
      logger.error('Redis SET error:', error);
      throw error;
    }
  }

  /**
   * Получает значение
   */
  async get(key) {
    try {
      const value = await this.getClient().get(key);
      return value ? JSON.parse(value) : null;
    } catch (error) {
      logger.error('Redis GET error:', error);
      throw error;
    }
  }

  /**
   * Удаляет значение
   */
  async del(key) {
    try {
      await this.getClient().del(key);
    } catch (error) {
      logger.error('Redis DEL error:', error);
      throw error;
    }
  }

  /**
   * Проверяет существование ключа
   */
  async exists(key) {
    try {
      const result = await this.getClient().exists(key);
      return result === 1;
    } catch (error) {
      logger.error('Redis EXISTS error:', error);
      throw error;
    }
  }
}

module.exports = new RedisClient();