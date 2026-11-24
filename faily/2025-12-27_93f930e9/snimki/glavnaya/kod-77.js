/**
 * Маршруты пользователей
 */

const express = require('express');
const router = express.Router();
const { authenticate } = require('../middleware/auth');
const serviceProxies = require('../services/proxy');

// Все маршруты пользователей требуют аутентификации
router.use('/', authenticate, serviceProxies.user);

module.exports = router;