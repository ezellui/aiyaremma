/**
 * Маршруты графов
 */

const express = require('express');
const router = express.Router();
const { authenticate, optionalAuthenticate } = require('../middleware/auth');
const serviceProxies = require('../services/proxy');

// Чтение графов доступно без аутентификации
router.get('*', optionalAuthenticate, serviceProxies.graph);

// Изменения требуют аутентификации
router.post('*', authenticate, serviceProxies.graph);
router.put('*', authenticate, serviceProxies.graph);
router.patch('*', authenticate, serviceProxies.graph);
router.delete('*', authenticate, serviceProxies.graph);

module.exports = router;