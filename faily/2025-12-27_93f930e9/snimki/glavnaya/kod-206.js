/**
 * Маршруты связей
 */

const express = require('express');
const router = express.Router();
const Joi = require('joi');
const { asyncHandler } = require('@philos/shared');
const relationshipController = require('../controllers/relationship.controller');
const { extractUserFromHeaders } = require('../middleware/auth.middleware');

// Middleware
router.use(extractUserFromHeaders);

//=============================================
// СХЕМЫ ВАЛИДАЦИИ
//=============================================

const createRelationshipSchema = Joi.object({
  sourceCategoryId: Joi.string().uuid().required(),
  targetCategoryId: Joi.string().uuid().required(),
  type: Joi.string().required(),
  direction: Joi.string().valid('forward', 'backward', 'bidirectional').default('bidirectional'),
  strength: Joi.number().min(0).max(1).default(1),
  innovationDegree: Joi.string().valid(
    'традиционная',
    'модифицированная',
    'синтетическая',
    'инновационная',
    'революционная'
  ),
  description: Joi.string().max(1000),
  metadata: Joi.object()
});

const updateRelationshipSchema = Joi.object({
  type: Joi.string(),
  direction: Joi.string().valid('forward', 'backward', 'bidirectional'),
  strength: Joi.number().min(0).max(1),
  innovationDegree: Joi.string().valid(
    'традиционная',
    'модифицированная',
    'синтетическая',
    'инновационная',
    'революционная'
  ),
  description: Joi.string().max(1000)
});

const enrichRelationshipSchema = Joi.object({
  category1Name: Joi.string().required(),
  category2Name: Joi.string().required(),
  conceptName: Joi.string().required()
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

// Получение связей концепции
router.get('/concept/:conceptId',
  asyncHandler(relationshipController.getByConceptId.bind(relationshipController))
);

// Получение связей категории
router.get('/category/:categoryId',
  asyncHandler(relationshipController.getByCategoryId.bind(relationshipController))
);

// Поиск пути между категориями
router.get('/path',
  asyncHandler(relationshipController.findPath.bind(relationshipController))
);

// Поиск циклов
router.get('/concept/:conceptId/cycles',
  asyncHandler(relationshipController.findCycles.bind(relationshipController))
);

// CRUD операции
router.post('/concept/:conceptId',
  validate(createRelationshipSchema),
  asyncHandler(relationshipController.create.bind(relationshipController))
);

router.get('/:id',
  asyncHandler(relationshipController.getById.bind(relationshipController))
);

router.put('/:id',
  validate(updateRelationshipSchema),
  asyncHandler(relationshipController.update.bind(relationshipController))
);

router.delete('/:id',
  asyncHandler(relationshipController.delete.bind(relationshipController))
);

// Обогащение
router.post('/:id/enrich',
  validate(enrichRelationshipSchema),
  asyncHandler(relationshipController.enrich.bind(relationshipController))
);

router.get('/:id/enriched',
  asyncHandler(relationshipController.getEnrichedDescription.bind(relationshipController))
);

module.exports = router;