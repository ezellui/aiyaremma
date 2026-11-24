/**
 * Маршруты для работы с тезисами
 */

const express = require('express');
const router = express.Router();
const { asyncHandler } = require('@philos/shared');
const { authenticate, optionalAuthenticate } = require('../middleware/auth');
const thesisController = require('../controllers/thesis.controller');

/**
 * @route   GET /api/theses/concepts/:conceptId
 * @desc    Получение тезисов концепции
 * @access  Public/Private
 */
router.get(
  '/concepts/:conceptId',
  optionalAuthenticate,
  asyncHandler(thesisController.getConceptTheses)
);

/**
 * @route   GET /api/theses/:id
 * @desc    Получение конкретного тезиса
 * @access  Public/Private
 */
router.get(
  '/:id',
  optionalAuthenticate,
  asyncHandler(thesisController.getById)
);

/**
 * @route   POST /api/theses/concepts/:conceptId
 * @desc    Генерация тезисов для концепции
 * @access  Private
 */
router.post(
  '/concepts/:conceptId',
  authenticate,
  asyncHandler(thesisController.generateTheses)
);

/**
 * @route   POST /api/theses/concepts/:conceptId/generate-with-characteristics
 * @desc    Генерация тезисов с учётом количественных характеристик
 * @access  Private
 */
router.post(
  '/concepts/:conceptId/generate-with-characteristics',
  authenticate,
  asyncHandler(thesisController.generateThesesWithCharacteristics)
);

/**
 * @route   PUT /api/theses/:id
 * @desc    Обновление тезиса
 * @access  Private
 */
router.put(
  '/:id',
  authenticate,
  asyncHandler(thesisController.update)
);

/**
 * @route   DELETE /api/theses/:id
 * @desc    Удаление тезиса
 * @access  Private
 */
router.delete(
  '/:id',
  authenticate,
  asyncHandler(thesisController.delete)
);

/**
 * @route   POST /api/theses/:id/elaborate
 * @desc    Развитие и обоснование тезиса
 * @access  Private
 */
router.post(
  '/:id/elaborate',
  authenticate,
  asyncHandler(thesisController.elaborate)
);

/**
 * @route   POST /api/theses/compare
 * @desc    Сравнение наборов тезисов
 * @access  Private
 */
router.post(
  '/compare',
  authenticate,
  asyncHandler(thesisController.compare)
);

/**
 * @route   POST /api/theses/analyze-origin
 * @desc    Анализ происхождения на основе тезисов
 * @access  Private
 */
router.post(
  '/analyze-origin',
  authenticate,
  asyncHandler(thesisController.analyzeOrigin)
);

module.exports = router;