/**
 * Маршруты для анализа названий концепций
 */

const express = require('express');
const router = express.Router();
const { asyncHandler } = require('@philos/shared');
const { authenticate } = require('../middleware/auth');
const nameAnalysisController = require('../controllers/name-analysis.controller');

/**
 * @route   POST /api/name-analysis/analyze
 * @desc    Анализ названия концепции
 * @access  Private
 */
router.post(
  '/analyze',
  authenticate,
  asyncHandler(nameAnalysisController.analyze)
);

/**
 * @route   POST /api/name-analysis/suggest-alternatives
 * @desc    Предложение альтернативных названий
 * @access  Private
 */
router.post(
  '/suggest-alternatives',
  authenticate,
  asyncHandler(nameAnalysisController.suggestAlternatives)
);

/**
 * @route   GET /api/name-analysis/history
 * @desc    Получение истории анализа названий
 * @access  Private
 */
router.get(
  '/history',
  authenticate,
  asyncHandler(nameAnalysisController.getHistory)
);

module.exports = router;