/**
 * Маршруты аутентификации
 */

const express = require('express');
const { body } = require('express-validator');
const router = express.Router();
const { asyncHandler } = require('@philos/shared');
const { authenticate } = require('../middleware/auth');
const { strictLimiter } = require('../middleware/rate-limiter');
const authController = require('../controllers/auth.controller');

// Валидация регистрации
const registerValidation = [
  body('username')
    .isLength({ min: 3, max: 50 })
    .withMessage('Имя пользователя должно быть от 3 до 50 символов')
    .matches(/^[a-zA-Z0-9_-]+$/)
    .withMessage('Имя пользователя может содержать только буквы, цифры, дефис и подчеркивание'),
  body('email')
    .isEmail()
    .withMessage('Некорректный email')
    .normalizeEmail(),
  body('password')
    .isLength({ min: 8 })
    .withMessage('Пароль должен быть минимум 8 символов')
    .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/)
    .withMessage('Пароль должен содержать хотя бы одну строчную букву, одну заглавную и одну цифру')
];

// Валидация входа
const loginValidation = [
  body('email')
    .isEmail()
    .withMessage('Некорректный email')
    .normalizeEmail(),
  body('password')
    .notEmpty()
    .withMessage('Пароль обязателен')
];

/**
 * @route   POST /api/auth/register
 * @desc    Регистрация нового пользователя
 * @access  Public
 */
router.post(
  '/register',
  strictLimiter,
  registerValidation,
  asyncHandler(authController.register)
);

/**
 * @route   POST /api/auth/login
 * @desc    Вход в систему
 * @access  Public
 */
router.post(
  '/login',
  strictLimiter,
  loginValidation,
  asyncHandler(authController.login)
);

/**
 * @route   POST /api/auth/logout
 * @desc    Выход из системы
 * @access  Private
 */
router.post(
  '/logout',
  authenticate,
  asyncHandler(authController.logout)
);

/**
 * @route   POST /api/auth/refresh
 * @desc    Обновление токена
 * @access  Public
 */
router.post(
  '/refresh',
  asyncHandler(authController.refresh)
);

/**
 * @route   GET /api/auth/me
 * @desc    Получение информации о текущем пользователе
 * @access  Private
 */
router.get(
  '/me',
  authenticate,
  asyncHandler(authController.getCurrentUser)
);

module.exports = router;