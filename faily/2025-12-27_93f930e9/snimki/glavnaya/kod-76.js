/**
 * Маршруты аутентификации
 */

const express = require('express');
const router = express.Router();
const { authRateLimiter } = require('../middleware/rate-limiter');
const serviceProxies = require('../services/proxy');

// Все маршруты аутентификации проксируются к user-service
// с применением строгого rate limiting
router.use('/', authRateLimiter, serviceProxies.user);

module.exports = router;