/**
 * Маршруты для синтеза концепций
 */

const express = require('express');
const router = express.Router();
const { asyncHandler } = require('@philos/shared');
const { authenticate } = require('../middleware/auth');
const synthesisController = require('../controllers/synthesis.controller');

/**
 * @route   POST /api/synthesis/analyze-compatibility
 * @desc    Анализ совместимости концепций
 * @access  Private
 */
router.post(
  '/analyze-compatibility',
  authenticate,
  asyncHandler(synthesisController.analyzeCompatibility)
);

/**
 * @route   POST /api/synthesis
 * @desc    Создание синтезированной концепции
 * @access  Private
 */
router.post(
  '/',
  authenticate,
  asyncHandler(synthesisController.synthesize)
);

/**
 * @route   POST /api/synthesis/with-characteristics
 * @desc    Синтез с учётом количественных характеристик
 * @access  Private
 */
router.post(
  '/with-characteristics',
  authenticate,
  asyncHandler(synthesisController.synthesizeWithCharacteristics)
);

/**
 * @route   GET /api/synthesis/:id
 * @desc    Получение данных синтеза
 * @access  Private
 */
router.get(
  '/:id',
  authenticate,
  asyncHandler(synthesisController.getById)
);

/**
 * @route   POST /api/synthesis/:id/critique
 * @desc    Критический анализ синтезированной концепции
 * @access  Private
 */
router.post(
  '/:id/critique',
  authenticate,
  asyncHandler(synthesisController.critique)
);

/**
 * @route   GET /api/synthesis/history
 * @desc    Получение истории синтезов пользователя
 * @access  Private
 */
router.get(
  '/history',
  authenticate,
  asyncHandler(synthesisController.getHistory)
);

/**
 * @route   POST /api/synthesis/identify-concepts
 * @desc    Определение родительских концепций
 * @access  Private
 */
router.post(
  '/identify-concepts',
  authenticate,
  asyncHandler(synthesisController.identifyParentConcepts)
);

module.exports = router;