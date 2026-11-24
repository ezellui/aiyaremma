/**
 * Маршруты тезисов
 */

const express = require('express');
const router = express.Router();
const { authenticate, optionalAuthenticate } = require('../middleware/auth');
const serviceProxies = require('../services/proxy');

// Чтение тезисов доступно без аутентификации
router.get('*', optionalAuthenticate, serviceProxies.thesis);

// Создание и изменение требуют аутентификации
router.post('*', authenticate, serviceProxies.thesis);
router.put('*', authenticate, serviceProxies.thesis);
router.patch('*', authenticate, serviceProxies.thesis);
router.delete('*', authenticate, serviceProxies.thesis);

module.exports = router;