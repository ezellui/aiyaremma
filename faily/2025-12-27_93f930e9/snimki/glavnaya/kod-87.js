/**
 * Маршруты диалогов
 */

const express = require('express');
const router = express.Router();
const { authenticate, optionalAuthenticate } = require('../middleware/auth');
const serviceProxies = require('../services/proxy');

// Чтение доступно без аутентификации
router.get('*', optionalAuthenticate, serviceProxies.dialogue);

// Создание и изменение требуют аутентификации
router.post('*', authenticate, serviceProxies.dialogue);
router.put('*', authenticate, serviceProxies.dialogue);
router.patch('*', authenticate, serviceProxies.dialogue);
router.delete('*', authenticate, serviceProxies.dialogue);

module.exports = router;