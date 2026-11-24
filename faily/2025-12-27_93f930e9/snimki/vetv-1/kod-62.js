/**
 * Маршруты для взаимодействия с Claude
 */

const express = require('express');
const router = express.Router();
const { asyncHandler } = require('@philos/shared');
const { authenticate } = require('../middleware/auth');
const claudeController = require('../controllers/claude.controller');

/**
 * @route   POST /api/claude/query
 * @desc    Синхронный запрос к Claude
 * @access  Private
 */
router.post(
  '/query',
  authenticate,
  asyncHandler(claudeController.query)
);

/**
 * @route   POST /api/claude/queue-query
 * @desc    Асинхронный запрос к Claude (через очередь)
 * @access  Private
 */
router.post(
  '/queue-query',
  authenticate,
  asyncHandler(claudeController.queueQuery)
);

/**
 * @route   GET /api/claude/tasks/:id
 * @desc    Получение статуса и результата асинхронного запроса
 * @access  Private
 */
router.get(
  '/tasks/:id',
  authenticate,
  asyncHandler(claudeController.getTaskStatus)
);

/**
 * @route   GET /api/claude/interactions
 * @desc    Получение истории взаимодействий с Claude
 * @access  Private
 */
router.get(
  '/interactions',
  authenticate,
  asyncHandler(claudeController.getInteractions)
);

/**
 * @route   GET /api/claude/templates
 * @desc    Получение шаблонов запросов
 * @access  Private
 */
router.get(
  '/templates',
  authenticate,
  asyncHandler(claudeController.getTemplates)
);

module.exports = router;