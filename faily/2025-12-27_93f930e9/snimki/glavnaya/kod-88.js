/**
 * Маршруты эволюции концепций
 */

const express = require('express');
const router = express.Router();
const { authenticate } = require('../middleware/auth');
const serviceProxies = require('../services/proxy');

// Все операции эволюции требуют аутентификации
router.use('/', authenticate, serviceProxies.evolution);

module.exports = router;