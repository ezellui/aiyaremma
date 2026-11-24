/**
 * Маршруты философов
 */

const express = require('express');
const router = express.Router();
const Joi = require('joi');
const { asyncHandler } = require('@philos/shared');
const philosopherController = require('../controllers/philosopher.controller');
const { extractUserFromHeaders } = require('../middleware/auth.middleware');

// Middleware
router.use(extractUserFromHeaders);

//=============================================
// СХЕМЫ ВАЛИДАЦИИ
//=============================================

const createPhilosopherSchema = Joi.object({
  name: Joi.string().min(2).max(200).required(),
  birthYear: Joi.number().integer().min(-3000).max(2100),
  deathYear: Joi.number().integer().min(-3000).max(2100),
  traditions: Joi.array().items(Joi.object({
    name: Joi.string().required(),
    period: Joi.string()
  })),
  keyWorks: Joi.array().items(Joi.string())
});

const updatePhilosopherSchema = Joi.object({
  name: Joi.string().min(2).max(200),
  birthYear: Joi.number().integer().min(-3000).max(2100),
  deathYear: Joi.number().integer().min(-3000).max(2100),
  traditions: Joi.array().items(Joi.object({
    name: Joi.string().required(),
    period: Joi.string()
  })),
  keyWorks: Joi.array().items(Joi.string())
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

// Поиск
router.get('/search',
  asyncHandler(philosopherController.search.bind(philosopherController))
);

// Получение всех философов
router.get('/',
  asyncHandler(philosopherController.getAll.bind(philosopherController))
);

// CRUD операции
router.post('/',
  validate(createPhilosopherSchema),
  asyncHandler(philosopherController.create.bind(philosopherController))
);

router.get('/:id',
  asyncHandler(philosopherController.getById.bind(philosopherController))
);

router.put('/:id',
  validate(updatePhilosopherSchema),
  asyncHandler(philosopherController.update.bind(philosopherController))
);

router.delete('/:id',
  asyncHandler(philosopherController.delete.bind(philosopherController))
);

// Связанные концепции
router.get('/:id/concepts',
  asyncHandler(philosopherController.getConcepts.bind(philosopherController))
);

module.exports = router;