/**
 * Точка входа микросервиса
 */

require('dotenv').config();
const app = require('./app');
const config = require('./config/config');
const logger = require('@philos/shared').logger.createServiceLogger(config.serviceName);

// Обработка необработанных ошибок
process.on('uncaughtException', (error) => {
  logger.error('Uncaught Exception:', error);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  logger.error('Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

// Запуск сервера
const server = app.listen(config.port, () => {
  logger.info(`${config.serviceName} запущен на порту ${config.port}`);
  logger.info(`Окружение: ${config.env}`);
});

// Graceful shutdown
const gracefulShutdown = (signal) => {
  logger.info(`${signal} получен, завершение работы...`);
  
  server.close(() => {
    logger.info('HTTP сервер закрыт');
    
    // Закрываем подключения к БД
    // TODO: добавить закрытие подключений
    
    process.exit(0);
  });
  
  // Принудительное завершение через 10 секунд
  setTimeout(() => {
    logger.error('Принудительное завершение работы');
    process.exit(1);
  }, 10000);
};

process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));