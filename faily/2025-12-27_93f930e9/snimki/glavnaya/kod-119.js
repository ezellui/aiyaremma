/**
 * Главный роутер User Service
 */

const express = require('express');
const router = express.Router();

const authRoutes = require('./auth.routes');
const userRoutes = require('./user.routes');

// Базовый маршрут
router.get('/', (req, res) => {
  res.json({
    message: 'User Service API',
    version: '1.0.0',
    endpoints: {
      auth: '/auth',
      users: '/users'
    }
  });
});

// Подключение маршрутов
router.use('/auth', authRoutes);
router.use('/users', userRoutes);

module.exports = router;