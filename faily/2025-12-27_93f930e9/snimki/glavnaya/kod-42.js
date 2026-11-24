/**
 * Главный роутер сервиса
 */

const express = require('express');
const router = express.Router();

// TODO: Импортировать специфичные роуты
// const exampleRoutes = require('./example.routes');

// TODO: Подключить роуты
// router.use('/example', exampleRoutes);

// Базовый маршрут для проверки
router.get('/', (req, res) => {
  res.json({
    message: 'API Service Template',
    version: '1.0.0',
    endpoints: []
  });
});

module.exports = router;