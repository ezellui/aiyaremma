/**
 * Конфигурация Express приложения API Gateway
 */

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const { requestLogger, errorHandler } = require('@philos/shared');
const rateLimiter = require('./middleware/rate-limiter');
const routes = require('./routes');
const config = require('./config/config');

const app = express();

// Безопасность
app.use(helmet());

// CORS
app.use(cors({
  origin: config.cors.origin,
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

// Парсинг тела запроса
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Сжатие ответов
app.use(compression());

// Логирование запросов
app.use(requestLogger);

// Rate limiting
app.use(rateLimiter);

// Health check
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'healthy',
    service: config.serviceName,
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

// API routes
app.use('/api', routes);

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    success: false,
    error: {
      message: 'Маршрут не найден',
      path: req.path,
      method: req.method
    }
  });
});

// Обработчик ошибок (должен быть последним)
app.use(errorHandler);

module.exports = app;