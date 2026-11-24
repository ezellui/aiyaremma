/**
 * Маршруты для практического применения концепций
 */

const express = require('express');
const router = express.Router();
const { asyncHandler } = require('@philos/shared');
const { authenticate, optionalAuthenticate } = require('../middleware/auth');
const practicalController = require('../controllers/practical.controller');

/**
 * @route   POST /api/practical/analyze
 * @desc    Создание анализа практического применения
 * @access  Private
 */
router.post(
  '/analyze',
  authenticate,
  asyncHandler(practicalController.analyze)
);

/**
 * @route   GET /api/practical/concepts/:conceptId
 * @desc    Получение анализа практического применения концепции
 * @access  Public/Private
 */
router.get(
  '/concepts/:conceptId',
  optionalAuthenticate,
  asyncHandler(practicalController.getConceptApplication)
);

/**
 * @route   GET /api/practical/:id
 * @desc    Получение конкретного анализа
 * @access  Public/Private
 */
router.get(
  '/:id',
  optionalAuthenticate,
  asyncHandler(practicalController.getById)
);

/**
 * @route   PUT /api/practical/:id
 * @desc    Обновление анализа
 * @access  Private
 */
router.put(
  '/:id',
  authenticate,
  asyncHandler(practicalController.update)
);

/**
 * @route   DELETE /api/practical/:id
 * @desc    Удаление анализа
 * @access  Private
 */
router.delete(
  '/:id',
  authenticate,
  asyncHandler(practicalController.delete)
);

/**
 * @route   GET /api/practical/domains/:domain
 * @desc    Получение концепций, применимых в определенной области
 * @access  Public/Private
 */
router.get(
  '/domains/:domain',
  optionalAuthenticate,
  asyncHandler(practicalController.getByDomain)
);

/**
 * @route   GET /api/practical/theses/:thesisId
 * @desc    Получение областей применения для конкретного тезиса
 * @access  Public/Private
 */
router.get(
  '/theses/:thesisId',
  optionalAuthenticate,
  asyncHandler(practicalController.getByThesis)
);

module.exports = router;