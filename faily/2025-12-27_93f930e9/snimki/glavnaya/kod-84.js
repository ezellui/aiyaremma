/**
 * Маршруты определения происхождения
 */

const express = require('express');
const router = express.Router();
const { authenticate } = require('../middleware/auth');
const serviceProxies = require('../services/proxy');

// Все операции определения происхождения требуют аутентификации
router.use('/', authenticate, serviceProxies.origin);

module.exports = router;