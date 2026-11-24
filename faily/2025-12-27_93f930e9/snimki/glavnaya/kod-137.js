/**
 * Главный роутер Claude Service
 */

const express = require('express');
const router = express.Router();

const claudeRoutes = require('./claude.routes');

// Базовый маршрут
router.get('/', (req, res) => {
  res.json({
    message: 'Claude Service API',
    version: '1.0.0',
    endpoints: {
      claude: '/claude',
      interactions: '/interactions'
    }
  });
});

// Подключение маршрутов
router.use('/claude', claudeRoutes);

module.exports = router;