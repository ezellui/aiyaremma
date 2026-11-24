/**
 * Главный роутер Graph Service
 */

const express = require('express');
const router = express.Router();

const graphRoutes = require('./graph.routes');
const categoryRoutes = require('./category.routes');
const relationshipRoutes = require('./relationship.routes');

// Базовый маршрут
router.get('/', (req, res) => {
  res.json({
    message: 'Graph Service API',
    version: '1.0.0',
    endpoints: {
      graphs: '/graphs',
      categories: '/categories',
      relationships: '/relationships'
    }
  });
});

// Подключение маршрутов
router.use('/graphs', graphRoutes);
router.use('/categories', categoryRoutes);
router.use('/relationships', relationshipRoutes);

module.exports = router;