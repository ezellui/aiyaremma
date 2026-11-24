/**
 * Маршруты концепций
 */

const express = require('express');
const router = express.Router();
const Joi = require('joi');
const { asyncHandler } = require('@philos/shared');
const conceptController = require('../controllers/concept.controller');
const { extractUserFromHeaders } = require('../middleware/auth.middleware');

// Middleware
router.use(extractUserFromHeaders);

//=============================================
// СХЕМЫ ВАЛИДАЦИИ
//=============================================

const createConceptSchema = Joi.object({
  name: Joi.string().min(3).max(200).required(),
  description: Joi.string().max(2000).required(),
  isSynthesis: Joi.boolean(),
  parentConcepts: Joi.array().items(Joi.string().uuid()),
  synthesisMethod: Joi.string(),
  innovationDegree: Joi.string().valid(
    'традиционная',
    'модифицированная',
    'синтетическая',
    'инновационная',
    'революционная'
  ),
  tags: Joi.array().items(Joi.string()),
  isPublic: Joi.boolean()
});

const updateConceptSchema = Joi.object({
  name: Joi.string().min(3).max(200),
  description: Joi.string().max(2000),
  tags: Joi.array().items(Joi.string()),
  isPublic: Joi.boolean()
});

const linkPhilosopherSchema = Joi.object({
  philosopherId: Joi.string().uuid().required(),
  relationshipType: Joi.string().required()
});

const linkTraditionSchema = Joi.object({
  traditionId: Joi.string().uuid().required(),
  relationshipStrength: Joi.number().min(0).max(1).required()
});

const advancedSearchSchema = Joi.object({
  searchTerm: Joi.string(),
  isSynthesis: Joi.boolean(),
  innovationDegree: Joi.string(),
  tags: Joi.array().items(Joi.string()),
  creatorId: Joi.string().uuid(),
  publicOnly: Joi.boolean(),
  sortBy: Joi.string().valid('created_at', 'name', 'last_modified'),
  sortOrder: Joi.string().valid('ASC', 'DESC')
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

// Поиск и списки
router.get('/search',
  asyncHandler(conceptController.search.bind(conceptController))
);

router.get('/search/tags',
  asyncHandler(conceptController.searchByTags.bind(conceptController))
);

router.post('/search/advanced',
  validate(advancedSearchSchema),
  asyncHandler(conceptController.advancedSearch.bind(conceptController))
);

router.get('/tags/popular',
  asyncHandler(conceptController.getPopularTags.bind(conceptController))
);

router.get('/public',
  asyncHandler(conceptController.getPublic.bind(conceptController))
);

router.get('/synthesized',
  asyncHandler(conceptController.getSynthesized.bind(conceptController))
);

router.get('/my',
  asyncHandler(conceptController.getUserConcepts.bind(conceptController))
);

// CRUD операции
router.post('/',
  validate(createConceptSchema),
  asyncHandler(conceptController.create.bind(conceptController))
);

router.get('/:id',
  asyncHandler(conceptController.getById.bind(conceptController))
);

router.put('/:id',
  validate(updateConceptSchema),
  asyncHandler(conceptController.update.bind(conceptController))
);

router.delete('/:id',
  asyncHandler(conceptController.delete.bind(conceptController))
);

// Связи
router.post('/:id/philosophers',
  validate(linkPhilosopherSchema),
  asyncHandler(conceptController.linkPhilosopher.bind(conceptController))
);

router.get('/:id/philosophers',
  asyncHandler(conceptController.getPhilosophers.bind(conceptController))
);

router.post('/:id/traditions',
  validate(linkTraditionSchema),
  asyncHandler(conceptController.linkTradition.bind(conceptController))
);

router.get('/:id/traditions',
  asyncHandler(conceptController.getTraditions.bind(conceptController))
);

// Статистика и аналитика
router.get('/:id/stats',
  asyncHandler(conceptController.getStats.bind(conceptController))
);

router.get('/:id/similar',
  asyncHandler(conceptController.findSimilar.bind(conceptController))
);

module.exports = router;