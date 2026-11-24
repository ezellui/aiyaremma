/**
 * Маршруты графов
 */

const express = require('express');
const router = express.Router();
const Joi = require('joi');
const { asyncHandler } = require('@philos/shared');
const graphController = require('../controllers/graph.controller');
const { extractUserFromHeaders } = require('../middleware/auth.middleware');

// Middleware
router.use(extractUserFromHeaders);

//=============================================
// СХЕМЫ ВАЛИДАЦИИ
//=============================================

const graphDataSchema = Joi.object({
  categories: Joi.array().items(Joi.object({
    name: Joi.string().required(),
    definition: Joi.string().required(),
    type: Joi.string().required(),
    innovationDegree: Joi.string(),
    certainty: Joi.number().min(0).max(1),
    metadata: Joi.object()
  })).required(),
  relationships: Joi.array().items(Joi.object({
    sourceCategoryId: Joi.string().uuid().required(),
    targetCategoryId: Joi.string().uuid().required(),
    type: Joi.string().required(),
    direction: Joi.string().valid('forward', 'backward', 'bidirectional'),
    strength: Joi.number().min(0).max(1),
    innovationDegree: Joi.string(),
    description: Joi.string()
  }))
});

const subgraphSchema = Joi.object({
  categoryIds: Joi.array().items(Joi.string().uuid()).min(1).required()
});

// Middleware валидации
function validate(schema) {
  return (req, res, next) => {
    const { error, value } = schema.validate(req.body);
    
    if (error) {
      return res.status(400).json({
        success: false,
        error: {
          message: 'Ошибка валидации',
          details: error.details.map(d => ({
            field: d.path.join('.'),
            message: d.message
          }))
        }
      });
    }
    
    req.body = value;
    next();
  };
}

//=============================================
// МАРШРУТЫ
//=============================================

// Получение графа
router.get('/:conceptId',
  asyncHandler(graphController.getGraph.bind(graphController))
);

// Создание графа
router.post('/:conceptId',
  validate(graphDataSchema),
  asyncHandler(graphController.createGraph.bind(graphController))
);

// Обновление графа
router.put('/:conceptId',
  validate(graphDataSchema),
  asyncHandler(graphController.updateGraph.bind(graphController))
);

// Удаление графа
router.delete('/:conceptId',
  asyncHandler(graphController.deleteGraph.bind(graphController))
);

// Статистика графа
router.get('/:conceptId/stats',
  asyncHandler(graphController.getStats.bind(graphController))
);

// Получение подграфа
router.post('/:conceptId/subgraph',
  validate(subgraphSchema),
  asyncHandler(graphController.getSubgraph.bind(graphController))
);

// Экспорт графа
router.get('/:conceptId/export',
  asyncHandler(graphController.exportGraph.bind(graphController))
);

// Валидация графа
router.post('/:conceptId/validate',
  asyncHandler(graphController.validateGraph.bind(graphController))
);

// Анализ графа
router.get('/:conceptId/analyze',
  asyncHandler(graphController.analyzeGraph.bind(graphController))
);

module.exports = router;