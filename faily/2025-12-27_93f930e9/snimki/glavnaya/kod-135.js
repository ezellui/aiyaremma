/**
 * Сервис для работы с API ключами пользователей
 */

const axios = require('axios');
const config = require('../config/config');
const redisClient = require('../db/redis-client');
const logger = require('@philos/shared').logger.createServiceLogger('claude-service');

class UserApiKeyService {
  /**
   * Получает API ключ пользователя из User Service
   */
  async getApiKey(userId) {
    if (!userId) {
      return {
        apiKey: config.claude.apiKey,
        usedUserKey: false
      };
    }

    try {
      // Проверяем кэш
      const cached = await redisClient.get(`api-key:${userId}`);
      if (cached !== null) {
        if (cached === 'NO_KEY') {
          return {
            apiKey: config.claude.apiKey,
            usedUserKey: false
          };
        }
        return {
          apiKey: cached,
          usedUserKey: true
        };
      }

      // Запрашиваем у User Service
      const response = await axios.get(
        `${config.services.user}/users/${userId}/api-key`,
        {
          timeout: 5000,
          headers: {
            'X-Service-Request': 'claude-service'
          }
        }
      );

      const userApiKey = response.data?.data?.apiKey;

      if (userApiKey) {
        // Кэшируем на 1 час
        await redisClient.set(`api-key:${userId}`, userApiKey, 3600);

        return {
          apiKey: userApiKey,
          usedUserKey: true
        };
      } else {
        // Кэшируем отсутствие ключа на 5 минут
        await redisClient.set(`api-key:${userId}`, 'NO_KEY', 300);

        return {
          apiKey: config.claude.apiKey,
          usedUserKey: false
        };
      }

    } catch (error) {
      logger.warn('Не удалось получить API ключ пользователя, используется системный', {
        userId,
        error: error.message
      });

      // При ошибке используем системный ключ
      return {
        apiKey: config.claude.apiKey,
        usedUserKey: false
      };
    }
  }

  /**
   * Инвалидирует кэш API ключа пользователя
   */
  async invalidateCache(userId) {
    await redisClient.del(`api-key:${userId}`);
  }

  /**
   * Записывает использование API через User Service
   */
  async recordUsage(userId, usageData) {
    try {
      await axios.post(
        `${config.services.user}/users/${userId}/api-usage`,
        usageData,
        {
          timeout: 5000,
          headers: {
            'X-Service-Request': 'claude-service'
          }
        }
      );
    } catch (error) {
      logger.error('Не удалось записать использование API', {
        userId,
        error: error.message
      });
      // Не пробрасываем ошибку, это не критично
    }
  }
}

module.exports = new UserApiKeyService();