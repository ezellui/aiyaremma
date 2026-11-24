/**
 * Маршруты для определения происхождения концепций
 */

const express = require('express');
const router = express.Router();
const { asyncHandler } = require('@philos/shared');
const { authenticate } = require('../middleware/auth');
const originController = require('../controllers/origin.controller');

/**
 * @route   POST /api/origin/detect
 * @desc    Определение происхождения концепции
 * @access  Private
 */
router.post(
  '/detect',
  authenticate,
  asyncHandler(originController.detect)
);

/**
 * @route   GET /api/origin/concepts/:conceptId
 * @desc    Получение данных о происхождении концепции
 * @access  Private
 */
router.get(
  '/concepts/:conceptId',
  authenticate,
  asyncHandler(originController.getConceptOrigin)
);

/**
 * @route   GET /api/origin/:id
 * @desc    Получение конкретного анализа происхождения
 * @access  Private
 */
router.get(
  '/:id',
  authenticate,
  asyncHandler(originController.getById)
);

module.exports = router;