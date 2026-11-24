/**
 * Маршруты пользователей
 */

const express = require('express');
const router = express.Router();
const Joi = require('joi');
const { asyncHandler } = require('@philos/shared');
const userController = require('../controllers/user.controller');
const { extractUserFromHeaders, requireAuth } = require('../middleware/auth.middleware');

// Middleware
router.use(extractUserFromHeaders);
router.use(requireAuth);

// Схемы валидации
const updateUserSchema = Joi.object({
  username: Joi.string().min(3).max(50),
  email: Joi.string().email(),
  user_settings: Joi.object()
});

const apiKeySchema = Joi.object({
  apiKey: Joi.string().required()
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
router.get('/:id',
  asyncHandler(userController.getById.bind(userController))
);

router.put('/:id',
  validate(updateUserSchema),
  asyncHandler(userController.update.bind(userController))
);

router.post('/:id/api-key',
  validate(apiKeySchema),
  asyncHandler(userController.setApiKey.bind(userController))
);

router.delete('/:id/api-key',
  asyncHandler(userController.removeApiKey.bind(userController))
);

router.get('/:id/api-usage',
  asyncHandler(userController.getApiUsage.bind(userController))
);

router.post('/:id/deactivate',
  asyncHandler(userController.deactivate.bind(userController))
);

router.post('/:id/activate',
  asyncHandler(userController.activate.bind(userController))
);

module.exports = router;