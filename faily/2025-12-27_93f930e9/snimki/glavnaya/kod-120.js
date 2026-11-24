/**
 * Маршруты аутентификации
 */

const express = require('express');
const router = express.Router();
const Joi = require('joi');
const { asyncHandler } = require('@philos/shared');
const authController = require('../controllers/auth.controller');
const { extractUserFromHeaders } = require('../middleware/auth.middleware');

// Middleware для извлечения данных пользователя из заголовков
router.use(extractUserFromHeaders);

// Схемы валидации
const registerSchema = Joi.object({
  username: Joi.string().min(3).max(50).required(),
  email: Joi.string().email().required(),
  password: Joi.string().min(8).required()
});

const loginSchema = Joi.object({
  email: Joi.string().email().required(),
  password: Joi.string().required()
});

const refreshSchema = Joi.object({
  refreshToken: Joi.string().required()
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
router.post('/register', 
  validate(registerSchema),
  asyncHandler(authController.register.bind(authController))
);

router.post('/login',
  validate(loginSchema),
  asyncHandler(authController.login.bind(authController))
);

router.post('/logout',
  asyncHandler(authController.logout.bind(authController))
);

router.post('/refresh',
  validate(refreshSchema),
  asyncHandler(authController.refresh.bind(authController))
);

router.get('/me',
  asyncHandler(authController.me.bind(authController))
);

module.exports = router;