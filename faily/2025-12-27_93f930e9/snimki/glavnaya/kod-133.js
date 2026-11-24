/**
 * Клиент для взаимодействия с Claude API
 */

const Anthropic = require('@anthropic-ai/sdk');
const config = require('../config/config');
const logger = require('@philos/shared').logger.createServiceLogger(config.serviceName);
const { AppError } = require('@philos/shared');

class ClaudeClientService {
  constructor() {
    this.defaultClient = null;
    if (config.claude.apiKey) {
      this.defaultClient = new Anthropic({
        apiKey: config.claude.apiKey
      });
    }
  }

  /**
   * Создает клиента с пользовательским API ключом
   */
  createClient(apiKey) {
    if (!apiKey) {
      throw new AppError('API key is required', 400);
    }

    return new Anthropic({
      apiKey: apiKey
    });
  }

  /**
   * Получает клиента (пользовательский или дефолтный)
   */
  getClient(userApiKey = null) {
    if (userApiKey) {
      return this.createClient(userApiKey);
    }

    if (!this.defaultClient) {
      throw new AppError('Claude API key not configured', 500);
    }

    return this.defaultClient;
  }

  /**
   * Отправка запроса к Claude API
   */
  async sendMessage(prompt, options = {}) {
    const {
      apiKey = null,
      model = config.claude.model,
      maxTokens = config.claude.maxTokens,
      temperature = 1,
      system = null,
      metadata = {}
    } = options;

    const client = this.getClient(apiKey);

    const startTime = Date.now();

    try {
      logger.debug('Отправка запроса к Claude API', {
        model,
        maxTokens,
        promptLength: prompt.length,
        hasCustomKey: !!apiKey
      });

      const requestParams = {
        model,
        max_tokens: maxTokens,
        messages: [
          {
            role: 'user',
            content: prompt
          }
        ],
        temperature
      };

      if (system) {
        requestParams.system = system;
      }

      const response = await client.messages.create(requestParams);

      const duration = Date.now() - startTime;

      logger.info('Получен ответ от Claude API', {
        model,
        duration,
        inputTokens: response.usage.input_tokens,
        outputTokens: response.usage.output_tokens,
        stopReason: response.stop_reason
      });

      return {
        content: response.content[0].text,
        usage: {
          inputTokens: response.usage.input_tokens,
          outputTokens: response.usage.output_tokens,
          totalTokens: response.usage.input_tokens + response.usage.output_tokens
        },
        model: response.model,
        stopReason: response.stop_reason,
        metadata: {
          ...metadata,
          duration,
          timestamp: new Date()
        }
      };

    } catch (error) {
      const duration = Date.now() - startTime;

      logger.error('Ошибка Claude API', {
        error: error.message,
        duration,
        model,
        hasCustomKey: !!apiKey
      });

      // Обработка специфичных ошибок Anthropic
      if (error.status === 401) {
        throw new AppError('Invalid API key', 401);
      } else if (error.status === 429) {
        throw new AppError('Rate limit exceeded', 429);
      } else if (error.status === 500) {
        throw new AppError('Claude API service error', 503);
      }

      throw new AppError(`Claude API error: ${error.message}`, error.status || 500);
    }
  }

  /**
   * Отправка запроса со streaming (для будущего использования)
   */
  async sendMessageStream(prompt, options = {}) {
    const {
      apiKey = null,
      model = config.claude.model,
      maxTokens = config.claude.maxTokens,
      temperature = 1,
      system = null,
      onChunk = null
    } = options;

    const client = this.getClient(apiKey);

    try {
      const requestParams = {
        model,
        max_tokens: maxTokens,
        messages: [
          {
            role: 'user',
            content: prompt
          }
        ],
        temperature,
        stream: true
      };

      if (system) {
        requestParams.system = system;
      }

      const stream = await client.messages.create(requestParams);

      let fullText = '';
      let usage = null;

      for await (const event of stream) {
        if (event.type === 'content_block_delta') {
          const chunk = event.delta.text;
          fullText += chunk;
          
          if (onChunk) {
            onChunk(chunk);
          }
        } else if (event.type === 'message_delta') {
          usage = event.usage;
        }
      }

      return {
        content: fullText,
        usage,
        model
      };

    } catch (error) {
      logger.error('Ошибка Claude streaming API', {
        error: error.message,
        model
      });

      throw new AppError(`Claude streaming error: ${error.message}`, error.status || 500);
    }
  }

  /**
   * Подсчет приблизительной стоимости запроса
   */
  estimateCost(inputTokens, outputTokens, model = config.claude.model) {
    // Цены на Claude Sonnet 4 (примерные, обновить по текущим тарифам)
    const pricing = {
      'claude-sonnet-4-20250514': {
        input: 0.003,  // $ за 1K токенов
        output: 0.015  // $ за 1K токенов
      },
      'claude-sonnet-4-20241022': {
        input: 0.003,
        output: 0.015
      },
      'claude-haiku-4-20250514': {
        input: 0.00025,
        output: 0.00125
      }
    };

    const modelPricing = pricing[model] || pricing['claude-sonnet-4-20250514'];

    const inputCost = (inputTokens / 1000) * modelPricing.input;
    const outputCost = (outputTokens / 1000) * modelPricing.output;

    return inputCost + outputCost;
  }
}

module.exports = new ClaudeClientService();