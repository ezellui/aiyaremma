/**
 * Сервис проксирования запросов к микросервисам
 */

const { createProxyMiddleware } = require('http-proxy-middleware');
const config = require('../config/config');
const logger = require('@philos/shared').logger.createServiceLogger(config.serviceName);

/**
 * Создает middleware для проксирования к микросервису
 */
function createServiceProxy(serviceUrl, serviceName) {
  return createProxyMiddleware({
    target: serviceUrl,
    changeOrigin: true,
    pathRewrite: (path, req) => {
      // Удаляем префикс /api из пути
      return path.replace(/^\/api/, '');
    },
    onProxyReq: (proxyReq, req, res) => {
      // Добавляем заголовки с информацией о пользователе
      if (req.user) {
        proxyReq.setHeader('X-User-Id', req.user.id);
        proxyReq.setHeader('X-User-Email', req.user.email);
        proxyReq.setHeader('X-User-Role', req.user.role);
      }

      // Добавляем заголовок с источником запроса
      proxyReq.setHeader('X-Gateway-Request', 'true');

      logger.debug(`Proxying ${req.method} ${req.path} to ${serviceName}`);
    },
    onProxyRes: (proxyRes, req, res) => {
      logger.debug(`Response from ${serviceName}: ${proxyRes.statusCode}`);
    },
    onError: (err, req, res) => {
      logger.error(`Proxy error for ${serviceName}:`, err);
      res.status(503).json({
        success: false,
        error: {
          message: `Сервис ${serviceName} временно недоступен`,
          code: 'SERVICE_UNAVAILABLE',
          service: serviceName
        }
      });
    }
  });
}

/**
 * Прокси для каждого микросервиса
 */
const serviceProxies = {
  user: createServiceProxy(config.services.user, 'user-service'),
  concept: createServiceProxy(config.services.concept, 'concept-service'),
  graph: createServiceProxy(config.services.graph, 'graph-service'),
  thesis: createServiceProxy(config.services.thesis, 'thesis-service'),
  synthesis: createServiceProxy(config.services.synthesis, 'synthesis-service'),
  claude: createServiceProxy(config.services.claude, 'claude-service'),
  nameAnalysis: createServiceProxy(config.services.nameAnalysis, 'name-analysis-service'),
  origin: createServiceProxy(config.services.origin, 'origin-service'),
  historical: createServiceProxy(config.services.historical, 'historical-service'),
  practical: createServiceProxy(config.services.practical, 'practical-service'),
  dialogue: createServiceProxy(config.services.dialogue, 'dialogue-service'),
  evolution: createServiceProxy(config.services.evolution, 'evolution-service')
};

module.exports = serviceProxies;