/**
 * Маршруты для диалогической интерпретации
 */

const express = require('express');
const router = express.Router();
const { asyncHandler } = require('@philos/shared');
const { authenticate, optionalAuthenticate } = require('../middleware/auth');
const dialogueController = require('../controllers/dialogue.controller');

/**
 * @route   POST /api/dialogue
 * @desc    Создание нового диалога
 * @access  Private
 */
router.post(
  '/',
  authenticate,
  asyncHandler(dialogueController.create)
);

/**
 * @route   GET /api/dialogue/:id
 * @desc    Получение конкретного диалога
 * @access  Public/Private
 */
router.get(
  '/:id',
  optionalAuthenticate,
  asyncHandler(dialogueController.getById)
);

/**
 * @route   PUT /api/dialogue/:id
 * @desc    Обновление диалога
 * @access  Private
 */
router.put(
  '/:id',
  authenticate,
  asyncHandler(dialogueController.update)
);

/**
 * @route   DELETE /api/dialogue/:id
 * @desc    Удаление диалога
 * @access  Private
 */
router.delete(
  '/:id',
  authenticate,
  asyncHandler(dialogueController.delete)
);

/**
 * @route   GET /api/dialogue/concepts/:conceptId
 * @desc    Получение диалогов с участием концепции
 * @access  Public/Private
 */
router.get(
  '/concepts/:conceptId',
  optionalAuthenticate,
  asyncHandler(dialogueController.getByConceptId)
);

/**
 * @route   POST /api/dialogue/analyze
 * @desc    Анализ существующего диалога
 * @access  Private
 */
router.post(
  '/analyze',
  authenticate,
  asyncHandler(dialogueController.analyze)
);

/**
 * @route   GET /api/dialogue/questions
 * @desc    Получение предложений философских вопросов для диалога
 * @access  Private
 */
router.get(
  '/questions',
  authenticate,
  asyncHandler(dialogueController.suggestQuestions)
);

/**
 * @route   GET /api/dialogue/:dialogueId/arguments
 * @desc    Получение структурированных аргументов из диалога
 * @access  Public/Private
 */
router.get(
  '/:dialogueId/arguments',
  optionalAuthenticate,
  asyncHandler(dialogueController.getArguments)
);

module.exports = router;