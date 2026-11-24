/**
 * Маршруты исторического контекста
 */

const express = require('express');
const router = express.Router();
const { authenticate, optionalAuthenticate } = require('../middleware/auth');
const serviceProxies = require('../services/proxy');

// Чтение доступно без аутентификации
router.get('*', optionalAuthenticate, serviceProxies.historical);

// Создание и изменение требуют аутентификации
router.post('*', authenticate, serviceProxies.historical);
router.put('*', authenticate, serviceProxies.historical);
router.patch('*', authenticate, serviceProxies.historical);
router.delete('*', authenticate, serviceProxies.historical);

module.exports = router;