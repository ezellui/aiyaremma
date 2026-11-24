/**
 * Маршруты для работы с графами концепций
 */

const express = require('express');
const router = express.Router();
const { asyncHandler } = require('@philos/shared');
const { authenticate, optionalAuthenticate } = require('../middleware/auth');
const graphController = require('../controllers/graph.controller');

/**
 * @route   GET /api/graphs/concepts/:conceptId
 * @desc    Получение полного графа концепции
 * @access  Public/Private
 */
router.get(
  '/concepts/:conceptId',
  optionalAuthenticate,
  asyncHandler(graphController.getConceptGraph)
);

/**
 * @route   POST /api/graphs/concepts/:conceptId/categories
 * @desc    Создание категории в графе
 * @access  Private
 */
router.post(
  '/concepts/:conceptId/categories',
  authenticate,
  asyncHandler(graphController.createCategory)
);

/**
 * @route   GET /api/graphs/categories/:id
 * @desc    Получение категории по ID
 * @access  Public/Private
 */
router.get(
  '/categories/:id',
  optionalAuthenticate,
  asyncHandler(graphController.getCategoryById)
);

/**
 * @route   PUT /api/graphs/categories/:id
 * @desc    Обновление категории
 * @access  Private
 */
router.put(
  '/categories/:id',
  authenticate,
  asyncHandler(graphController.updateCategory)
);

/**
 * @route   DELETE /api/graphs/categories/:id
 * @desc    Удаление категории
 * @access  Private
 */
router.delete(
  '/categories/:id',
  authenticate,
  asyncHandler(graphController.deleteCategory)
);

/**
 * @route   POST /api/graphs/relationships
 * @desc    Создание связи между категориями
 * @access  Private
 */
router.post(
  '/relationships',
  authenticate,
  asyncHandler(graphController.createRelationship)
);

/**
 * @route   GET /api/graphs/relationships/:id
 * @desc    Получение связи по ID
 * @access  Public/Private
 */
router.get(
  '/relationships/:id',
  optionalAuthenticate,
  asyncHandler(graphController.getRelationshipById)
);

/**
 * @route   PUT /api/graphs/relationships/:id
 * @desc    Обновление связи
 * @access  Private
 */
router.put(
  '/relationships/:id',
  authenticate,
  asyncHandler(graphController.updateRelationship)
);

/**
 * @route   DELETE /api/graphs/relationships/:id
 * @desc    Удаление связи
 * @access  Private
 */
router.delete(
  '/relationships/:id',
  authenticate,
  asyncHandler(graphController.deleteRelationship)
);

/**
 * @route   POST /api/graphs/concepts/:conceptId/validate
 * @desc    Валидация графа концепции
 * @access  Private
 */
router.post(
  '/concepts/:conceptId/validate',
  authenticate,
  asyncHandler(graphController.validateGraph)
);

/**
 * @route   POST /api/graphs/concepts/:conceptId/enrich
 * @desc    Обогащение графа концепции
 * @access  Private
 */
router.post(
  '/concepts/:conceptId/enrich',
  authenticate,
  asyncHandler(graphController.enrichGraph)
);

/**
 * @route   POST /api/graphs/categories/:id/enrich
 * @desc    Обогащение конкретной категории
 * @access  Private
 */
router.post(
  '/categories/:id/enrich',
  authenticate,
  asyncHandler(graphController.enrichCategory)
);

/**
 * @route   POST /api/graphs/relationships/:id/enrich
 * @desc    Обогащение конкретной связи
 * @access  Private
 */
router.post(
  '/relationships/:id/enrich',
  authenticate,
  asyncHandler(graphController.enrichRelationship)
);

/**
 * @route   POST /api/graphs/from-theses
 * @desc    Генерация графа из тезисов
 * @access  Private
 */
router.post(
  '/from-theses',
  authenticate,
  asyncHandler(graphController.generateFromTheses)
);

/**
 * @route   GET /api/graphs/concepts/:conceptId/characteristics
 * @desc    Получение количественных характеристик графа
 * @access  Public/Private
 */
router.get(
  '/concepts/:conceptId/characteristics',
  optionalAuthenticate,
  asyncHandler(graphController.getCharacteristics)
);

/**
 * @route   POST /api/graphs/categories/:id/characteristics
 * @desc    Обновление количественных характеристик категории
 * @access  Private
 */
router.post(
  '/categories/:id/characteristics',
  authenticate,
  asyncHandler(graphController.updateCategoryCharacteristics)
);

/**
 * @route   POST /api/graphs/relationships/:id/characteristics
 * @desc    Обновление количественных характеристик связи
 * @access  Private
 */
router.post(
  '/relationships/:id/characteristics',
  authenticate,
  asyncHandler(graphController.updateRelationshipCharacteristics)
);

/**
 * @route   POST /api/graphs/categories/:id/characteristics/metadata
 * @desc    Получение философского обоснования для характеристики категории
 * @access  Private
 */
router.post(
  '/categories/:id/characteristics/metadata',
  authenticate,
  asyncHandler(graphController.getCategoryCharacteristicsMetadata)
);

/**
 * @route   POST /api/graphs/relationships/:id/characteristics/metadata
 * @desc    Получение философского обоснования для характеристики связи
 * @access  Private
 */
router.post(
  '/relationships/:id/characteristics/metadata',
  authenticate,
  asyncHandler(graphController.getRelationshipCharacteristicsMetadata)
);

/**
 * @route   POST /api/graphs/analyze-origin
 * @desc    Анализ происхождения концепции на основе графа
 * @access  Private
 */
router.post(
  '/analyze-origin',
  authenticate,
  asyncHandler(graphController.analyzeOrigin)
);

/**
 * @route   GET /api/graphs/templates/categories
 * @desc    Получение шаблонов категорий
 * @access  Public/Private
 */
router.get(
  '/templates/categories',
  optionalAuthenticate,
  asyncHandler(graphController.getCategoryTemplates)
);

/**
 * @route   GET /api/graphs/templates/relationships
 * @desc    Получение шаблонов типов связей
 * @access  Public/Private
 */
router.get(
  '/templates/relationships',
  optionalAuthenticate,
  asyncHandler(graphController.getRelationshipTemplates)
);

/**
 * @route   GET /api/graphs/generated-elements/:conceptId
 * @desc    Получение новых сгенерированных элементов для одобрения
 * @access  Private
 */
router.get(
  '/generated-elements/:conceptId',
  authenticate,
  asyncHandler(graphController.getGeneratedElements)
);

/**
 * @route   POST /api/graphs/generated-elements/approve
 * @desc    Одобрение новых элементов
 * @access  Private
 */
router.post(
  '/generated-elements/approve',
  authenticate,
  asyncHandler(graphController.approveGeneratedElements)
);

module.exports = router;