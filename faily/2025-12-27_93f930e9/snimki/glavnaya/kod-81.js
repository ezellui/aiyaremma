/**
 * Маршруты синтеза концепций
 */

const express = require('express');
const router = express.Router();
const { authenticate } = require('../middleware/auth');
const serviceProxies = require('../services/proxy');

// Все операции синтеза требуют аутентификации
router.use('/', authenticate, serviceProxies.synthesis);

module.exports = router;