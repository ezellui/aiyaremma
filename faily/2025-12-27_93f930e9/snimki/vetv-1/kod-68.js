/**
 * Маршруты для эволюции концепций
 */

const express = require('express');
const router = express.Router();
const { asyncHandler } = require('@philos/shared');
const { authenticate, optionalAuthenticate } = require('../middleware/auth');
const evolutionController = require('../controllers/evolution.controller');

/**
 * @route   POST /api/evolution/analyze
 * @desc    Создание анализа эволюции концепции
 * @access  Private
 */
router.post(
  '/analyze',
  authenticate,
  asyncHandler(evolutionController.analyze)
);

/**
 * @route   GET /api/evolution/concepts/:conceptId
 * @desc    Получение анализа эволюции для концепции
 * @access  Public/Private
 */
router.get(
  '/concepts/:conceptId',
  optionalAuthenticate,
  asyncHandler(evolutionController.getConceptEvolution)
);

/**
 * @route   GET /api/evolution/:id
 * @desc    Получение конкретного анализа эволюции
 * @access  Public/Private
 */
router.get(
  '/:id',
  optionalAuthenticate,
  asyncHandler(evolutionController.getById)
);

/**
 * @route   PUT /api/evolution/:id
 * @desc    Обновление анализа эволюции
 * @access  Private
 */
router.put(
  '/:id',
  authenticate,
  asyncHandler(evolutionController.update)
);

/**
 * @route   DELETE /api/evolution/:id
 * @desc    Удаление анализа эволюции
 * @access  Private
 */
router.delete(
  '/:id',
  authenticate,
  asyncHandler(evolutionController.delete)
);

/**
 * @route   POST /api/evolution/suggest-changes
 * @desc    Предложение конкретных изменений для эволюции концепции
 * @access  Private
 */
router.post(
  '/suggest-changes',
  authenticate,
  asyncHandler(evolutionController.suggestChanges)
);

/**
 * @route   GET /api/evolution/scientific-context
 * @desc    Получение научного контекста для эволюции концепций
 * @access  Private
 */
router.get(
  '/scientific-context',
  authenticate,
  asyncHandler(evolutionController.getScientificContext)
);

module.exports = router;