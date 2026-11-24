/**
 * Главный роутер Concept Service
 */

const express = require('express');
const router = express.Router();

const conceptRoutes = require('./concept.routes');
const philosopherRoutes = require('./philosopher.routes');
const traditionRoutes = require('./tradition.routes');

// Базовый маршрут
router.get('/', (req, res) => {
  res.json({
    message: 'Concept Service API',
    version: '1.0.0',
    endpoints: {
      concepts: '/concepts',
      philosophers: '/philosophers',
      traditions: '/traditions'
    }
  });
});

// Подключение маршрутов
router.use('/concepts', conceptRoutes);
router.use('/philosophers', philosopherRoutes);
router.use('/traditions', traditionRoutes);

module.exports = router;