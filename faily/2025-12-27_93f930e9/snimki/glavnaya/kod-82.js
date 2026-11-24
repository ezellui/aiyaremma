/**
 * Маршруты Claude AI
 */

const express = require('express');
const router = express.Router();
const { authenticate } = require('../middleware/auth');
const { claudeRateLimiter } = require('../middleware/rate-limiter');
const serviceProxies = require('../services/proxy');

// Все запросы к Claude требуют аутентификации и имеют строгий rate limit
router.use('/', authenticate, claudeRateLimiter, serviceProxies.claude);

module.exports = router;