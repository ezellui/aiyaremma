/**
 * Маршруты традиций
 */

const express = require('express');
const router = express.Router();
const Joi = require('joi');
const { asyncHandler } = require('@philos/shared');
const traditionController = require('../controllers/tradition.controller');
const { extractUserFromHeaders } = require('../middleware/auth.middleware');

router.use(extractUserFromHeaders);

// Схемы валидации
const createTraditionSchema = Joi.object({
  name: Joi.string().min(1).max(255).required(),
  timePeriod: Joi.string().max(255).optional(),
  description: Joi.string().optional(),
  keyFigures: Joi.array().items(Joi.string()).optional(),
  relatedTraditions: Joi.array().items(Joi.string()).optional()
});

const updateTraditionSchema = Joi.object({
  name: Joi.string().min(1).max(255).optional(),
  timePeriod: Joi.string().max(255).optional(),
  description: Joi.string().optional(),
  keyFigures: Joi.array().items(Joi.string()).optional(),
  relatedTraditions: Joi.array().items(Joi.string()).optional()
});

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

router.get('/',
  asyncHandler(traditionController.getAll.bind(traditionController))
);

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

module.exports = router;