/**
 * Контроллер аутентификации
 */

const { responseBuilder } = require('@philos/shared');
const authService = require('../services/auth.service');

class AuthController {
  /**
   * Регистрация
   */
  async register(req, res) {
    const { username, email, password } = req.body;

    const result = await authService.register(username, email, password);

    return responseBuilder.created(res, result, 'Пользователь успешно зарегистрирован');
  }

  /**
   * Вход
   */
  async login(req, res) {
    const { email, password } = req.body;

    const result = await authService.login(email, password);

    return responseBuilder.success(res, result, 'Успешный вход');
  }

  /**
   * Выход
   */
  async logout(req, res) {
    const userId = req.user.id;
    const token = req.token;

    await authService.logout(userId, token);

    return responseBuilder.success(res, null, 'Успешный выход');
  }

  /**
   * Обновление токенов
   */
  async refresh(req, res) {
    const { refreshToken } = req.body;

    const result = await authService.refreshTokens(refreshToken);

    return responseBuilder.success(res, result, 'Токены обновлены');
  }

  /**
   * Получение текущего пользователя
   */
  async me(req, res) {
    const userId = req.user.id;
    const userService = require('../services/user.service');
    
    const user = await userService.findById(userId);

    return responseBuilder.success(res, user.toSafeJSON());
  }
}

module.exports = new AuthController();