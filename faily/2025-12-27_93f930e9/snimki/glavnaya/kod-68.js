/**
 * Точка входа API Gateway
 */

require('dotenv').config();
const app = require('./app');
const config = require('./config/config');
const redisClient = require('./config/redis');
const logger = require('@philos/shared').logger.createServiceLogger(config.serviceName);

// Инициализация Redis
async function initializeRedis() {
  try {
    await redisClient.connect();
    logger.info('Redis успешно подключен');
  } catch (error) {
    logger.error('Ошибка подключения к Redis:', error);
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
  await initializeRedis();

  const server = app.listen(config.port, () => {
    logger.info(`${config.serviceName} запущен на порту ${config.port}`);
    logger.info(`Окружение: ${config.env}`);
    logger.info('Доступные маршруты:');
    logger.info('  - /health - Health check');
    logger.info('  - /api/auth - Аутентификация');
    logger.info('  - /api/users - Пользователи');
    logger.info('  - /api/concepts - Концепции');
    logger.info('  - /api/graphs - Графы');
    logger.info('  - /api/theses - Тезисы');
    logger.info('  - /api/synthesis - Синтез');
    logger.info('  - /api/claude - Claude AI');
    logger.info('  - /api/name-analysis - Анализ названий');
    logger.info('  - /api/origin - Определение происхождения');
    logger.info('  - /api/historical - Исторический контекст');
    logger.info('  - /api/practical - Практическое применение');
    logger.info('  - /api/dialogue - Диалоги');
    logger.info('  - /api/evolution - Эволюция концепций');
  });

  // Graceful shutdown
  const gracefulShutdown = async (signal) => {
    logger.info(`${signal} получен, завершение работы...`);

    server.close(async () => {
      logger.info('HTTP сервер закрыт');

      // Закрываем Redis
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