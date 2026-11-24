/**
 * Маршруты концепций
 */

const express = require('express');
const router = express.Router();
const { authenticate, optionalAuthenticate } = require('../middleware/auth');
const serviceProxies = require('../services/proxy');

// Публичные концепции доступны без аутентификации (только чтение)
router.get('/', optionalAuthenticate, serviceProxies.concept);
router.get('/:id', optionalAuthenticate, serviceProxies.concept);

// Создание, изменение и удаление требуют аутентификации
router.post('/', authenticate, serviceProxies.concept);
router.put('/:id', authenticate, serviceProxies.concept);
router.patch('/:id', authenticate, serviceProxies.concept);
router.delete('/:id', authenticate, serviceProxies.concept);

module.exports = router;