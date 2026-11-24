/**
 * Маршруты для работы с концепциями
 */

const express = require('express');
const router = express.Router();
const { asyncHandler } = require('@philos/shared');
const { authenticate, optionalAuthenticate } = require('../middleware/auth');
const conceptController = require('../controllers/concept.controller');

/**
 * @route   GET /api/concepts
 * @desc    Получение списка концепций
 * @access  Public/Private
 */
router.get(
  '/',
  optionalAuthenticate,
  asyncHandler(conceptController.getAll)
);

/**
 * @route   GET /api/concepts/:id
 * @desc    Получение концепции по ID
 * @access  Public/Private
 */
router.get(
  '/:id',
  optionalAuthenticate,
  asyncHandler(conceptController.getById)
);

/**
 * @route   POST /api/concepts
 * @desc    Создание новой концепции
 * @access  Private
 */
router.post(
  '/',
  authenticate,
  asyncHandler(conceptController.create)
);

/**
 * @route   PUT /api/concepts/:id
 * @desc    Обновление концепции
 * @access  Private
 */
router.put(
  '/:id',
  authenticate,
  asyncHandler(conceptController.update)
);

/**
 * @route   DELETE /api/concepts/:id
 * @desc    Удаление концепции
 * @access  Private
 */
router.delete(
  '/:id',
  authenticate,
  asyncHandler(conceptController.delete)
);

/**
 * @route   POST /api/concepts/:id/name
 * @desc    Генерация/установка названия концепции
 * @access  Private
 */
router.post(
  '/:id/name',
  authenticate,
  asyncHandler(conceptController.setName)
);

module.exports = router;