/**
 * Redis клиент для API Gateway
 */

const Redis = require('ioredis');
const config = require('../config/config');
const logger = require('@philos/shared').logger.createServiceLogger(config.serviceName);

class RedisClient {
  constructor() {
    this.client = null;
    this.isConnected = false;
  }
  
  connect() {
    if (this.client) {
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
      }
    });
    
    this.client.on('connect', () => {
      this.isConnected = true;
      logger.info('Redis подключен');
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
      this.connect();
    }
    return this.client;
  }
  
  /**
   * Кэширует значение с TTL
   */
  async setCache(key, value, ttlSeconds = 3600) {
    try {
      const client = this.getClient();
      await client.setex(key, ttlSeconds, JSON.stringify(value));
      return true;
    } catch (error) {
      logger.error('Ошибка при сохранении в кэш:', error);
      return false;
    }
  }
  
  /**
   * Получает значение из кэша
   */
  async getCache(key) {
    try {
      const client = this.getClient();
      const value = await client.get(key);
      return value ? JSON.parse(value) : null;
    } catch (error) {
      logger.error('Ошибка при получении из кэша:', error);
      return null;
    }
  }
  
  /**
   * Удаляет значение из кэша
   */
  async deleteCache(key) {
    try {
      const client = this.getClient();
      await client.del(key);
      return true;
    } catch (error) {
      logger.error('Ошибка при удалении из кэша:', error);
      return false;
    }
  }
  
  /**
   * Удаляет все ключи по паттерну
   */
  async deleteCachePattern(pattern) {
    try {
      const client = this.getClient();
      const keys = await client.keys(`${config.redis.keyPrefix}${pattern}`);
      if (keys.length > 0) {
        // Удаляем префикс перед удалением
        const keysWithoutPrefix = keys.map(key => key.replace(config.redis.keyPrefix, ''));
        await client.del(...keysWithoutPrefix);
      }
      return true;
    } catch (error) {
      logger.error('Ошибка при удалении по паттерну:', error);
      return false;
    }
  }
}

module.exports = new RedisClient();