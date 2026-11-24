/**
 * Redis клиент с переподключением
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
}

module.exports = new RedisClient();