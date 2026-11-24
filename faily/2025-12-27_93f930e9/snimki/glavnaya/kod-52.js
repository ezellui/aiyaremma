/**
 * HTTP клиент для взаимодействия между микросервисами
 */

const axios = require('axios');
const logger = require('./logger');

class HttpClient {
  constructor(baseURL, timeout = 30000) {
    this.client = axios.create({
      baseURL,
      timeout,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    // Interceptor для логирования запросов
    this.client.interceptors.request.use(
      (config) => {
        logger.debug(`HTTP Request: ${config.method.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        logger.error('HTTP Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Interceptor для логирования ответов
    this.client.interceptors.response.use(
      (response) => {
        logger.debug(`HTTP Response: ${response.status} from ${response.config.url}`);
        return response;
      },
      (error) => {
        if (error.response) {
          logger.error(`HTTP Error Response: ${error.response.status} from ${error.config.url}`);
        } else if (error.request) {
          logger.error('HTTP No Response:', error.message);
        } else {
          logger.error('HTTP Error:', error.message);
        }
        return Promise.reject(error);
      }
    );
  }

  async get(url, config = {}) {
    const response = await this.client.get(url, config);
    return response.data;
  }

  async post(url, data, config = {}) {
    const response = await this.client.post(url, data, config);
    return response.data;
  }

  async put(url, data, config = {}) {
    const response = await this.client.put(url, data, config);
    return response.data;
  }

  async patch(url, data, config = {}) {
    const response = await this.client.patch(url, data, config);
    return response.data;
  }

  async delete(url, config = {}) {
    const response = await this.client.delete(url, config);
    return response.data;
  }

  /**
   * Устанавливает заголовок аутентификации
   */
  setAuthToken(token) {
    this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }

  /**
   * Удаляет заголовок аутентификации
   */
  removeAuthToken() {
    delete this.client.defaults.headers.common['Authorization'];
  }
}

module.exports = HttpClient;