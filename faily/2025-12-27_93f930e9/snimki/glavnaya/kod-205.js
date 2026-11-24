/**
 * Маршруты категорий
 */

const express = require('express');
const router = express.Router();
const Joi = require('joi');
const { asyncHandler } = require('@philos/shared');
const categoryController = require('../controllers/category.controller');
const { extractUserFromHeaders } = require('../middleware/auth.middleware');

// Middleware
router.use(extractUserFromHeaders);

//=============================================
// СХЕМЫ ВАЛИДАЦИИ
//=============================================

const createCategorySchema = Joi.object({
  name: Joi.string().min(2).max(200).required(),
  definition: Joi.string().min(10).max(2000).required(),
  type: Joi.string().required(),
  innovationDegree: Joi.string().valid(
    'традиционная',
    'модифицированная',
    'синтетическая',
    'инновационная',
    'революционная'
  ),
  certainty: Joi.number().min(0).max(1),
  metadata: Joi.object()
});

const updateCategorySchema = Joi.object({
  name: Joi.string().min(2).max(200),
  definition: Joi.string().min(10).max(2000),
  type: Joi.string(),
  innovationDegree: Joi.string().valid(
    'традиционная',
    'модифицированная',
    'синтетическая',
    'инновационная',
    'революционная'
  ),
  certainty: Joi.number().min(0).max(1)
});

const enrichCategorySchema = Joi.object({
  conceptName: Joi.string().required(),
  traditions: Joi.array().items(Joi.string()),
  philosophers: Joi.array().items(Joi.string())
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

// Получение категорий концепции
router.get('/concept/:conceptId',
  asyncHandler(categoryController.getByConceptId.bind(categoryController))
);

// Вычисление центральности
router.post('/concept/:conceptId/centrality',
  asyncHandler(categoryController.calculateCentrality.bind(categoryController))
);

// CRUD операции
router.post('/concept/:conceptId',
  validate(createCategorySchema),
  asyncHandler(categoryController.create.bind(categoryController))
);

router.get('/:id',
  asyncHandler(categoryController.getById.bind(categoryController))
);

router.put('/:id',
  validate(updateCategorySchema),
  asyncHandler(categoryController.update.bind(categoryController))
);

router.delete('/:id',
  asyncHandler(categoryController.delete.bind(categoryController))
);

// Обогащение
router.post('/:id/enrich',
  validate(enrichCategorySchema),
  asyncHandler(categoryController.enrich.bind(categoryController))
);

router.get('/:id/enriched',
  asyncHandler(categoryController.getEnrichedDescription.bind(categoryController))
);

module.exports = router;