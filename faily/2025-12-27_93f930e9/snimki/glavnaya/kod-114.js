/**
 * Сервис аутентификации
 */

const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { UnauthorizedError, ValidationError, ConflictError } = require('@philos/shared');
const config = require('../config/config');
const userService = require('./user.service');
const redisClient = require('../db/redis-client');

class AuthService {
  /**
   * Регистрация нового пользователя
   */
  async register(username, email, password) {
    // Проверка существования пользователя
    const existingUser = await userService.findByEmail(email);
    if (existingUser) {
      throw new ConflictError('Пользователь с таким email уже существует');
    }

    const existingUsername = await userService.findByUsername(username);
    if (existingUsername) {
      throw new ConflictError('Пользователь с таким именем уже существует');
    }

    // Хэширование пароля
    const passwordHash = await bcrypt.hash(password, 10);

    // Создание пользователя
    const user = await userService.create({
      username,
      email,
      password_hash: passwordHash
    });

    // Генерация токенов
    const accessToken = this.generateAccessToken(user);
    const refreshToken = this.generateRefreshToken(user);

    // Сохранение refresh токена в Redis
    await this.saveRefreshToken(user.userId, refreshToken);

    return {
      user: user.toSafeJSON(),
      accessToken,
      refreshToken
    };
  }

  /**
   * Вход пользователя
   */
  async login(email, password) {
    // Поиск пользователя
    const user = await userService.findByEmail(email);
    if (!user) {
      throw new UnauthorizedError('Неверный email или пароль');
    }

    // Проверка активности
    if (!user.isActive) {
      throw new UnauthorizedError('Аккаунт деактивирован');
    }

    // Проверка пароля
    const isPasswordValid = await bcrypt.compare(password, user.passwordHash);
    if (!isPasswordValid) {
      throw new UnauthorizedError('Неверный email или пароль');
    }

    // Обновление времени последнего входа
    await userService.updateLastLogin(user.userId);

    // Генерация токенов
    const accessToken = this.generateAccessToken(user);
    const refreshToken = this.generateRefreshToken(user);

    // Сохранение refresh токена
    await this.saveRefreshToken(user.userId, refreshToken);

    return {
      user: user.toSafeJSON(),
      accessToken,
      refreshToken
    };
  }

  /**
   * Выход пользователя
   */
  async logout(userId, token) {
    // Удаление refresh токена из Redis
    await redisClient.del(`refresh:${userId}`);

    // Добавление access токена в черный список
    const decoded = jwt.decode(token);
    const expiresIn = decoded.exp - Math.floor(Date.now() / 1000);
    if (expiresIn > 0) {
      await redisClient.set(`blacklist:${token}`, true, expiresIn);
    }
  }

  /**
   * Обновление токенов
   */
  async refreshTokens(refreshToken) {
    try {
      // Верификация refresh токена
      const decoded = jwt.verify(refreshToken, config.jwt.secret);

      // Проверка наличия в Redis
      const storedToken = await redisClient.get(`refresh:${decoded.userId}`);
      if (storedToken !== refreshToken) {
        throw new UnauthorizedError('Недействительный refresh токен');
      }

      // Получение пользователя
      const user = await userService.findById(decoded.userId);
      if (!user || !user.isActive) {
        throw new UnauthorizedError('Пользователь не найден или деактивирован');
      }

      // Генерация новых токенов
      const newAccessToken = this.generateAccessToken(user);
      const newRefreshToken = this.generateRefreshToken(user);

      // Сохранение нового refresh токена
      await this.saveRefreshToken(user.userId, newRefreshToken);

      return {
        accessToken: newAccessToken,
        refreshToken: newRefreshToken
      };
    } catch (error) {
      if (error.name === 'JsonWebTokenError' || error.name === 'TokenExpiredError') {
        throw new UnauthorizedError('Недействительный refresh токен');
      }
      throw error;
    }
  }

  /**
   * Генерация access токена
   */
  generateAccessToken(user) {
    return jwt.sign(
      {
        userId: user.userId,
        email: user.email,
        role: user.role
      },
      config.jwt.secret,
      { expiresIn: config.jwt.expiresIn }
    );
  }

  /**
   * Генерация refresh токена
   */
  generateRefreshToken(user) {
    return jwt.sign(
      {
        userId: user.userId,
        type: 'refresh'
      },
      config.jwt.secret,
      { expiresIn: config.jwt.refreshExpiresIn }
    );
  }

  /**
   * Сохранение refresh токена в Redis
   */
  async saveRefreshToken(userId, token) {
    // TTL = 30 дней
    const ttl = 30 * 24 * 60 * 60;
    await redisClient.set(`refresh:${userId}`, token, ttl);
  }
}

module.exports = new AuthService();