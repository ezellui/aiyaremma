/**
 * Маршруты для управления пользователями
 */

const express = require('express');
const router = express.Router();
const { asyncHandler } = require('@philos/shared');
const { authenticate } = require('../middleware/auth');
const userController = require('../controllers/user.controller');

/**
 * @route   GET /api/users/:id
 * @desc    Получение данных пользователя
 * @access  Private
 */
router.get(
  '/:id',
  authenticate,
  asyncHandler(userController.getById)
);

/**
 * @route   PUT /api/users/:id
 * @desc    Обновление данных пользователя
 * @access  Private
 */
router.put(
  '/:id',
  authenticate,
  asyncHandler(userController.update)
);

/**
 * @route   GET /api/users/:id/activity
 * @desc    Получение активности пользователя
 * @access  Private
 */
router.get(
  '/:id/activity',
  authenticate,
  asyncHandler(userController.getActivity)
);

/**
 * @route   POST /api/users/:id/api-key
 * @desc    Установка/обновление ключа API Claude
 * @access  Private
 */
router.post(
  '/:id/api-key',
  authenticate,
  asyncHandler(userController.setApiKey)
);

/**
 * @route   DELETE /api/users/:id/api-key
 * @desc    Удаление ключа API Claude
 * @access  Private
 */
router.delete(
  '/:id/api-key',
  authenticate,
  asyncHandler(userController.deleteApiKey)
);

/**
 * @route   GET /api/users/:id/api-key/usage
 * @desc    Получение статистики использования API
 * @access  Private
 */
router.get(
  '/:id/api-key/usage',
  authenticate,
  asyncHandler(userController.getApiKeyUsage)
);

/**
 * @route   POST /api/users/:id/api-key/share
 * @desc    Создание совместного доступа к ключу API
 * @access  Private
 */
router.post(
  '/:id/api-key/share',
  authenticate,
  asyncHandler(userController.shareApiKey)
);

/**
 * @route   GET /api/users/:id/shared-keys
 * @desc    Получение доступных общих ключей
 * @access  Private
 */
router.get(
  '/:id/shared-keys',
  authenticate,
  asyncHandler(userController.getSharedKeys)
);

/**
 * @route   DELETE /api/users/:id/api-key/share/:shareId
 * @desc    Отзыв совместного доступа
 * @access  Private
 */
router.delete(
  '/:id/api-key/share/:shareId',
  authenticate,
  asyncHandler(userController.revokeSharedKey)
);

module.exports = router;