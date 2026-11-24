/**
 * Маршруты философов
 */

const express = require('express');
const router = express.Router();
const Joi = require('joi');
const { asyncHandler } = require('@philos/shared');
const philosopherController = require('../controllers/philosopher.controller');
const { extractUserFromHeaders } = require('../middleware/auth.middleware');

router.use(extractUserFromHeaders);

// Схемы валидации
const createPhilosopherSchema = Joi.object({
  name: Joi.string().min(1).max(255).required(),
  birthYear: Joi.number().integer().min(-3000).max(2100).optional(),
  deathYear: Joi.number().integer().min(-3000).max(2100).optional(),
  description: Joi.string().optional(),
  traditions: Joi.array().items(Joi.string()).optional(),
  keyWorks: Joi.array().items(Joi.string()).optional()
});

const updatePhilosopherSchema = Joi.object({
  name: Joi.string().min(1).max(255).optional(),
  birthYear: Joi.number().integer().min(-3000).max(2100).optional(),
  deathYear: Joi.number().integer().min(-3000).max(2100).optional(),
  description: Joi.string().optional(),
  traditions: Joi.array().items(Joi.string()).optional(),
  keyWorks: Joi.array().items(Joi.string()).optional()
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
  asyncHandler(philosopherController.getAll.bind(philosopherController))
);

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

module.exports = router;