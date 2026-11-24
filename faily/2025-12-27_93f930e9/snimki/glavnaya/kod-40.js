/**
 * Конфигурация Express приложения
 */

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const { requestLogger, errorHandler } = require('@philos/shared');
const routes = require('./routes');
const config = require('./config/config');

const app = express();

// Безопасность
app.use(helmet());
app.use(cors(config.cors));

// Парсинг тела запроса
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Сжатие ответов
app.use(compression());

// Логирование запросов
app.use(requestLogger);

// Health check
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'healthy',
    service: config.serviceName,
    timestamp: new Date().toISOString()
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
      path: req.path
    }
  });
});

// Обработчик ошибок (должен быть последним)
app.use(errorHandler);

module.exports = app;