/**
 * Маршруты традиций
 */

const express = require('express');
const router = express.Router();
const Joi = require('joi');
const { asyncHandler } = require('@philos/shared');
const traditionController = require('../controllers/tradition.controller');
const { extractUserFromHeaders } = require('../middleware/auth.middleware');

// Middleware
router.use(extractUserFromHeaders);

//=============================================
// СХЕМЫ ВАЛИДАЦИИ
//=============================================

const createTraditionSchema = Joi.object({
  name: Joi.string().min(2).max(200).required(),
  timePeriod: Joi.string().max(200).required(),
  keyFigures: Joi.array().items(Joi.string()),
  relatedTraditions: Joi.array().items(Joi.object({
    name: Joi.string().required(),
    relationship: Joi.string()
  }))
});

const updateTraditionSchema = Joi.object({
  name: Joi.string().min(2).max(200),
  timePeriod: Joi.string().max(200),
  keyFigures: Joi.array().items(Joi.string()),
  relatedTraditions: Joi.array().items(Joi.object({
    name: Joi.string().required(),
    relationship: Joi.string()
  }))
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
  asyncHandler(traditionController.search.bind(traditionController))
);

// Получение всех традиций
router.get('/',
  asyncHandler(traditionController.getAll.bind(traditionController))
);

// CRUD операции
router.post('/',
  validate(createTraditionSchema),
  asyncHandler(traditionController.create.bind(traditionController))
);

router.get('/:id',
  asyncHandler(traditionController.getById.bind(traditionController))
);

router.put('/:id',
  validate(updateTraditionSchema),
  asyncHandler(traditionController.update.bind(traditionController))
);

router.delete('/:id',
  asyncHandler(traditionController.delete.bind(traditionController))
);

// Связанные концепции
router.get('/:id/concepts',
  asyncHandler(traditionController.getConcepts.bind(traditionController))
);

module.exports = router;