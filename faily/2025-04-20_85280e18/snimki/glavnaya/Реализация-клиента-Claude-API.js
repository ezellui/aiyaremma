// claude-client.js

const axios = require('axios');

/**
 * Клиент для работы с Claude API
 */
class ClaudeClient {
  /**
   * Создает экземпляр клиента Claude API
   * @param {Object} config - Параметры конфигурации
   * @param {string} config.apiKey - Ключ API для доступа к Claude
   * @param {string} config.model - Модель Claude для использования (по умолчанию: claude-3-7-sonnet-20250219)
   * @param {number} config.maxRetries - Максимальное количество повторных попыток (по умолчанию: 3)
   * @param {number} config.timeout - Таймаут запроса в миллисекундах (по умолчанию: 120000 мс = 2 минуты)
   */
  constructor(config) {
    this.apiKey = config.apiKey;
    this.model = config.model || 'claude-3-7-sonnet-20250219';
    this.maxRetries = config.maxRetries || 3;
    this.timeout = config.timeout || 120000;
    
    this.baseURL = 'https://api.anthropic.com/v1';
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: this.timeout,
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': this.apiKey,
        'anthropic-version': '2023-06-01'
      }
    });
  }

  /**
   * Отправляет сообщение к Claude API и возвращает ответ
   * @param {Object} params - Параметры запроса
   * @param {string} params.prompt - Текст запроса для Claude
   * @param {number} params.max_tokens - Максимальное количество токенов в ответе
   * @param {number} params.temperature - Температура генерации (0.0-1.0)
   * @returns {Promise<Object>} - Промис с ответом от Claude
   */
  async sendMessage(params) {
    const { prompt, max_tokens = 4000, temperature = 0.7 } = params;
    
    // Проверка наличия обязательных параметров
    if (!prompt) {
      throw new Error('Prompt is required');
    }
    
    // Форматирование запроса в соответствии с API Claude
    const requestBody = {
      model: this.model,
      prompt: `\n\nHuman: ${prompt}\n\nAssistant:`,
      max_tokens_to_sample: max_tokens,
      temperature: temperature
    };
    
    // Отправка запроса с поддержкой повторных попыток
    return this._sendWithRetry(() => {
      return this.client.post('/complete', requestBody);
    });
  }
  
  /**
   * Отправляет сообщение к Claude API в формате messages (новый формат API)
   * @param {Object} params - Параметры запроса
   * @param {Array} params.messages - Массив сообщений в формате messages API
   * @param {number} params.max_tokens - Максимальное количество токенов в ответе
   * @param {number} params.temperature - Температура генерации (0.0-1.0)
   * @returns {Promise<Object>} - Промис с ответом от Claude
   */
  async sendMessages(params) {
    const { messages, max_tokens = 4000, temperature = 0.7 } = params;
    
    // Проверка наличия обязательных параметров
    if (!messages || !Array.isArray(messages) || messages.length === 0) {
      throw new Error('Messages array is required and must not be empty');
    }
    
    // Форматирование запроса в соответствии с API Claude
    const requestBody = {
      model: this.model,
      messages: messages,
      max_tokens: max_tokens,
      temperature: temperature
    };
    
    // Отправка запроса с поддержкой повторных попыток
    return this._sendWithRetry(() => {
      return this.client.post('/messages', requestBody);
    });
  }

  /**
   * Вспомогательный метод для отправки запроса с поддержкой повторных попыток
   * @param {Function} requestFn - Функция, выполняющая запрос
   * @returns {Promise<Object>} - Результат запроса
   * @private
   */
  async _sendWithRetry(requestFn) {
    let lastError;
    
    for (let attempt = 0; attempt < this.maxRetries; attempt++) {
      try {
        const response = await requestFn();
        return response.data;
      } catch (error) {
        console.error(`Attempt ${attempt + 1} failed:`, error.message);
        
        // Сохраняем последнюю ошибку
        lastError = error;
        
        // Проверяем тип ошибки
        if (error.response) {
          // Если это ошибка от сервера (4xx или 5xx)
          const status = error.response.status;
          
          // Для некоторых ошибок нет смысла повторять запрос
          if (status === 400 || status === 401 || status === 403) {
            throw error;
          }
          
          // Для ошибок сервера (5xx) или rate limit (429) делаем паузу перед следующей попыткой
          if (status === 429 || status >= 500) {
            const delay = this._calculateBackoff(attempt);
            await this._sleep(delay);
            continue;
          }
        }
        
        // Для сетевых ошибок также делаем паузу
        if (error.code === 'ECONNABORTED' || error.code === 'ETIMEDOUT' || !error.response) {
          const delay = this._calculateBackoff(attempt);
          await this._sleep(delay);
          continue;
        }
        
        // Для прочих ошибок прекращаем попытки
        throw error;
      }
    }
    
    // Если все попытки исчерпаны, выбрасываем последнюю ошибку
    throw lastError || new Error('All retry attempts failed');
  }

  /**
   * Вычисляет время задержки с экспоненциальным увеличением
   * @param {number} attempt - Номер попытки (начиная с 0)
   * @returns {number} - Время задержки в миллисекундах
   * @private
   */
  _calculateBackoff(attempt) {
    // Начинаем с 1 секунды и увеличиваем экспоненциально
    const baseDelay = 1000;
    const maxDelay = 30000; // Максимальная задержка - 30 секунд
    
    // Экспоненциальное увеличение с небольшим случайным отклонением
    const delay = Math.min(
      maxDelay,
      baseDelay * Math.pow(2, attempt) * (0.8 + Math.random() * 0.4)
    );
    
    return delay;
  }

  /**
   * Приостанавливает выполнение на указанное время
   * @param {number} ms - Время в миллисекундах
   * @returns {Promise<void>}
   * @private
   */
  _sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

module.exports = ClaudeClient;
