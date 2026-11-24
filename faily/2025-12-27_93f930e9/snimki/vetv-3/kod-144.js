/**
 * Маршруты концепций
 */

const express = require('express');
const router = express.Router();
const Joi = require('joi');
const { asyncHandler, constants } = require('@philos/shared');
const conceptController = require('../controllers/concept.controller');
const { extractUserFromHeaders } = require('../middleware/auth.middleware');

// Middleware
router.use(extractUserFromHeaders);

// Схемы валидации
const createConceptSchema = Joi.object({
  name: Joi.string().min(1).max(255).required(),
  description: Joi.string().max(5000).optional(),
  isSynthesis: Joi.boolean().optional(),
  isPublic: Joi.boolean().optional(),
  parentConcepts: Joi.array().items(Joi.string().uuid()).optional(),
  synthesisMethod: Joi.string().max(100).optional(),
  focus: Joi.string().max(500).optional(),
  innovationDegree: Joi.number().min(1).max(5).optional(),
  historicalContext: Joi.string().optional(),
  tags: Joi.array().items(Joi.string()).optional()
});

const updateConceptSchema = Joi.object({
  name: Joi.string().min(1).max(255).optional(),
  description: Joi.string().max(5000).optional(),
  isPublic: Joi.boolean().optional(),
  focus: Joi.string().max(500).optional(),
  innovationDegree: Joi.number().min(1).max(5).optional(),
  historicalContext: Joi.string().optional(),
  tags: Joi.array().items(Joi.string()).optional()
});

const addPhilosopherSchema = Joi.object({
  philosopherId: Joi.string().uuid().required(),
  relationshipType: Joi.string().max(100).optional()
});

const addTraditionSchema = Joi.object({
  traditionId: Joi.string().uuid().required(),
  relationshipStrength: Joi.number().min(0).max(1).optional()
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

// Маршруты
router.get('/',
  asyncHandler(conceptController.getAll.bind(conceptController))
);

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

router.post('/:id/like',
  asyncHandler(conceptController.like.bind(conceptController))
);

router.post('/:id/philosophers',
  validate(addPhilosopherSchema),
  asyncHandler(conceptController.addPhilosopher.bind(conceptController))
);

router.get('/:id/philosophers',
  asyncHandler(conceptController.getPhilosophers.bind(conceptController))
);

router.post('/:id/traditions',
  validate(addTraditionSchema),
  asyncHandler(conceptController.addTradition.bind(conceptController))
);

router.get('/:id/traditions',
  asyncHandler(conceptController.getTraditions.bind(conceptController))
);

module.exports = router;