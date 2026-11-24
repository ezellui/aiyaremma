/**
 * Сервис для проксирования запросов к микросервисам
 */

const axios = require('axios');
const { AppError } = require('@philos/shared');
const logger = require('@philos/shared').logger.createServiceLogger('proxy');
const config = require('../config/config');

class ProxyService {
  /**
   * Создает axios instance с базовой конфигурацией
   */
  createClient(baseURL, timeout = 30000) {
    return axios.create({
      baseURL,
      timeout,
      headers: {
        'Content-Type': 'application/json'
      }
    });
  }
  
  /**
   * Проксирует запрос к микросервису
   */
  async forward(serviceName, path, method = 'GET', data = null, headers = {}, params = {}) {
    try {
      const serviceUrl = config.services[serviceName];
      
      if (!serviceUrl) {
        throw new AppError(`Сервис ${serviceName} не найден`, 500, 'SERVICE_NOT_FOUND');
      }
      
      const client = this.createClient(serviceUrl);
      
      logger.debug(`Проксирование ${method} запроса к ${serviceName}${path}`);
      
      const response = await client.request({
        url: path,
        method,
        data,
        headers,
        params
      });
      
      return response.data;
    } catch (error) {
      this.handleProxyError(error, serviceName);
    }
  }
  
  /**
   * GET запрос
   */
  async get(serviceName, path, params = {}, headers = {}) {
    return this.forward(serviceName, path, 'GET', null, headers, params);
  }
  
  /**
   * POST запрос
   */
  async post(serviceName, path, data, headers = {}) {
    return this.forward(serviceName, path, 'POST', data, headers);
  }
  
  /**
   * PUT запрос
   */
  async put(serviceName, path, data, headers = {}) {
    return this.forward(serviceName, path, 'PUT', data, headers);
  }
  
  /**
   * PATCH запрос
   */
  async patch(serviceName, path, data, headers = {}) {
    return this.forward(serviceName, path, 'PATCH', data, headers);
  }
  
  /**
   * DELETE запрос
   */
  async delete(serviceName, path, headers = {}) {
    return this.forward(serviceName, path, 'DELETE', null, headers);
  }
  
  /**
   * Обрабатывает ошибки проксирования
   */
  handleProxyError(error, serviceName) {
    if (error.response) {
      // Сервис ответил с ошибкой
      const { status, data } = error.response;
      
      logger.error(`Ошибка от ${serviceName}: ${status}`, data);
      
      throw new AppError(
        data.error?.message || data.message || 'Ошибка микросервиса',
        status,
        data.error?.code || 'SERVICE_ERROR'
      );
    } else if (error.request) {
      // Запрос был отправлен, но ответа не получено
      logger.error(`Нет ответа от ${serviceName}:`, error.message);
      
      throw new AppError(
        `Сервис ${serviceName} недоступен`,
        503,
        'SERVICE_UNAVAILABLE'
      );
    } else {
      // Ошибка при настройке запроса
      logger.error(`Ошибка при проксировании к ${serviceName}:`, error.message);
      
      throw new AppError(
        'Внутренняя ошибка прокси',
        500,
        'PROXY_ERROR'
      );
    }
  }
  
  /**
   * Передает информацию о пользователе в заголовках
   */
  addUserHeaders(user) {
    if (!user) {
      return {};
    }
    
    return {
      'X-User-Id': user.userId,
      'X-User-Username': user.username,
      'X-User-Email': user.email
    };
  }
}

module.exports = new ProxyService();