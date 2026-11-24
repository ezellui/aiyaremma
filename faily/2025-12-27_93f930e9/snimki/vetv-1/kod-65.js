/**
 * Маршруты для исторической контекстуализации
 */

const express = require('express');
const router = express.Router();
const { asyncHandler } = require('@philos/shared');
const { authenticate, optionalAuthenticate } = require('../middleware/auth');
const historicalController = require('../controllers/historical.controller');

/**
 * @route   POST /api/historical/analyze
 * @desc    Создание исторической контекстуализации
 * @access  Private
 */
router.post(
  '/analyze',
  authenticate,
  asyncHandler(historicalController.analyze)
);

/**
 * @route   GET /api/historical/concepts/:conceptId
 * @desc    Получение исторической контекстуализации концепции
 * @access  Public/Private
 */
router.get(
  '/concepts/:conceptId',
  optionalAuthenticate,
  asyncHandler(historicalController.getConceptContext)
);

/**
 * @route   GET /api/historical/:id
 * @desc    Получение конкретной исторической контекстуализации
 * @access  Public/Private
 */
router.get(
  '/:id',
  optionalAuthenticate,
  asyncHandler(historicalController.getById)
);

/**
 * @route   PUT /api/historical/:id
 * @desc    Обновление исторической контекстуализации
 * @access  Private
 */
router.put(
  '/:id',
  authenticate,
  asyncHandler(historicalController.update)
);

/**
 * @route   DELETE /api/historical/:id
 * @desc    Удаление исторической контекстуализации
 * @access  Private
 */
router.delete(
  '/:id',
  authenticate,
  asyncHandler(historicalController.delete)
);

/**
 * @route   GET /api/historical/traditions/:traditionId
 * @desc    Получение концепций, связанных с традицией
 * @access  Public/Private
 */
router.get(
  '/traditions/:traditionId',
  optionalAuthenticate,
  asyncHandler(historicalController.getByTradition)
);

/**
 * @route   GET /api/historical/philosophers/:philosopherId
 * @desc    Получение концепций, связанных с философом
 * @access  Public/Private
 */
router.get(
  '/philosophers/:philosopherId',
  optionalAuthenticate,
  asyncHandler(historicalController.getByPhilosopher)
);

module.exports = router;