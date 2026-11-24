/**
 * Точка входа API Gateway
 */

require('dotenv').config();
const app = require('./app');
const config = require('./config/config');
const redisClient = require('./db/redis-client');
const logger = require('@philos/shared').logger.createServiceLogger(config.serviceName);

// Подключаем Redis
redisClient.connect();

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
  logger.info('Доступные микросервисы:');
  Object.entries(config.services).forEach(([name, url]) => {
    logger.info(`  - ${name}: ${url}`);
  });
});

// Graceful shutdown
const gracefulShutdown = async (signal) => {
  logger.info(`${signal} получен, завершение работы...`);
  
  server.close(async () => {
    logger.info('HTTP сервер закрыт');
    
    // Закрываем Redis подключение
    try {
      await redisClient.disconnect();
    } catch (error) {
      logger.error('Ошибка при закрытии Redis:', error);
    }
    
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