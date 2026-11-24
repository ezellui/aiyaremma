/**
 * Контроллер аутентификации
 */

const { validationResult } = require('express-validator');
const { ValidationError, UnauthorizedError } = require('@philos/shared');
const responseBuilder = require('@philos/shared').responseBuilder;
const proxyService = require('../services/proxy');
const { generateToken, generateRefreshToken, blacklistToken } = require('../middleware/auth');
const redisClient = require('../db/redis-client');

class AuthController {
  /**
   * Регистрация нового пользователя
   */
  async register(req, res) {
    // Проверка валидации
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      throw new ValidationError('Ошибка валидации данных', errors.array());
    }
    
    const { username, email, password } = req.body;
    
    // Проксируем запрос к user service
    const result = await proxyService.post('user', '/api/users/register', {
      username,
      email,
      password
    });
    
    // Генерируем токены
    const token = generateToken({
      userId: result.data.user.user_id,
      username: result.data.user.username,
      email: result.data.user.email
    });
    
    const refreshToken = generateRefreshToken({
      userId: result.data.user.user_id
    });
    
    // Сохраняем refresh token в Redis
    await redisClient.setCache(
      `refresh_token:${result.data.user.user_id}`,
      refreshToken,
      7 * 24 * 60 * 60 // 7 дней
    );
    
    return responseBuilder.created(res, {
      user: result.data.user,
      token,
      refreshToken
    }, 'Пользователь успешно зарегистрирован');
  }
  
  /**
   * Вход в систему
   */
  async login(req, res) {
    // Проверка валидации
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      throw new ValidationError('Ошибка валидации данных', errors.array());
    }
    
    const { email, password } = req.body;
    
    // Проксируем запрос к user service
    const result = await proxyService.post('user', '/api/users/login', {
      email,
      password
    });
    
    // Генерируем токены
    const token = generateToken({
      userId: result.data.user.user_id,
      username: result.data.user.username,
      email: result.data.user.email
    });
    
    const refreshToken = generateRefreshToken({
      userId: result.data.user.user_id
    });
    
    // Сохраняем refresh token в Redis
    await redisClient.setCache(
      `refresh_token:${result.data.user.user_id}`,
      refreshToken,
      7 * 24 * 60 * 60 // 7 дней
    );
    
    return responseBuilder.success(res, {
      user: result.data.user,
      token,
      refreshToken
    }, 'Вход выполнен успешно');
  }
  
  /**
   * Выход из системы
   */
  async logout(req, res) {
    const { userId } = req.user;
    const token = req.token;
    
    // Добавляем токен в черный список
    await blacklistToken(token);
    
    // Удаляем refresh token из Redis
    await redisClient.deleteCache(`refresh_token:${userId}`);
    
    return responseBuilder.success(res, null, 'Выход выполнен успешно');
  }
  
  /**
   * Обновление токена
   */
  async refresh(req, res) {
    const { refreshToken } = req.body;
    
    if (!refreshToken) {
      throw new UnauthorizedError('Refresh token не предоставлен');
    }
    
    // Верифицируем refresh token (используем тот же секрет)
    const jwt = require('jsonwebtoken');
    const config = require('../config/config');
    
    try {
      const decoded = jwt.verify(refreshToken, config.jwt.secret);
      
      // Проверяем, существует ли refresh token в Redis
      const storedToken = await redisClient.getCache(`refresh_token:${decoded.userId}`);
      
      if (!storedToken || storedToken !== refreshToken) {
        throw new UnauthorizedError('Недействительный refresh token');
      }
      
      // Получаем актуальные данные пользователя
      const userResult = await proxyService.get('user', `/api/users/${decoded.userId}`);
      
      // Генерируем новый access token
      const newToken = generateToken({
        userId: userResult.data.user_id,
        username: userResult.data.username,
        email: userResult.data.email
      });
      
      return responseBuilder.success(res, {
        token: newToken
      }, 'Токен обновлен успешно');
      
    } catch (error) {
      if (error.name === 'JsonWebTokenError' || error.name === 'TokenExpiredError') {
        throw new UnauthorizedError('Недействительный или истекший refresh token');
      }
      throw error;
    }
  }
  
  /**
   * Получение информации о текущем пользователе
   */
  async getCurrentUser(req, res) {
    const { userId } = req.user;
    
    // Получаем данные пользователя из user service
    const result = await proxyService.get('user', `/api/users/${userId}`);
    
    return responseBuilder.success(res, result.data, 'Данные пользователя получены');
  }
}

module.exports = new AuthController();