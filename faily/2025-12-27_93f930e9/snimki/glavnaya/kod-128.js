/**
 * Точка входа Claude Service
 */

require('dotenv').config();
const app = require('./app');
const config = require('./config/config');
const db = require('./db/postgres-connection');
const mongoDb = require('./db/mongo-connection');
const redisClient = require('./db/redis-client');
const logger = require('@philos/shared').logger.createServiceLogger(config.serviceName);

// Инициализация подключений
async function initialize() {
  try {
    // Подключаем PostgreSQL
    db.connect();
    logger.info('PostgreSQL подключен');

    // Подключаем MongoDB
    await mongoDb.connect();
    logger.info('MongoDB подключен');

    // Подключаем Redis
    await redisClient.connect();
    logger.info('Redis подключен');

  } catch (error) {
    logger.error('Ошибка инициализации:', error);
    process.exit(1);
  }
}

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
async function startServer() {
  await initialize();

  const server = app.listen(config.port, () => {
    logger.info(`${config.serviceName} запущен на порту ${config.port}`);
    logger.info(`Окружение: ${config.env}`);
    logger.info(`Claude Model: ${config.claude.model}`);
  });

  // Graceful shutdown
  const gracefulShutdown = async (signal) => {
    logger.info(`${signal} получен, завершение работы...`);

    server.close(async () => {
      logger.info('HTTP сервер закрыт');

      // Закрываем подключения
      await db.disconnect();
      await mongoDb.disconnect();
      await redisClient.disconnect();

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
}

startServer().catch((error) => {
  logger.error('Ошибка запуска сервера:', error);
  process.exit(1);
});