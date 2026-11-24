/**
 * Маршруты практического применения
 */

const express = require('express');
const router = express.Router();
const { authenticate, optionalAuthenticate } = require('../middleware/auth');
const serviceProxies = require('../services/proxy');

// Чтение доступно без аутентификации
router.get('*', optionalAuthenticate, serviceProxies.practical);

// Создание и изменение требуют аутентификации
router.post('*', authenticate, serviceProxies.practical);
router.put('*', authenticate, serviceProxies.practical);
router.patch('*', authenticate, serviceProxies.practical);
router.delete('*', authenticate, serviceProxies.practical);

module.exports = router;