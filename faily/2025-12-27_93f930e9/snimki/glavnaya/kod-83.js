/**
 * Маршруты анализа названий
 */

const express = require('express');
const router = express.Router();
const { authenticate } = require('../middleware/auth');
const serviceProxies = require('../services/proxy');

// Все операции анализа названий требуют аутентификации
router.use('/', authenticate, serviceProxies.nameAnalysis);

module.exports = router;