/**
 * Контроллер пользователей
 */

const { responseBuilder } = require('@philos/shared');
const userService = require('../services/user.service');

class UserController {
  /**
   * Получение пользователя по ID
   */
  async getById(req, res) {
    const { id } = req.params;

    const user = await userService.findById(id);

    if (!user) {
      return responseBuilder.error(res, 'Пользователь не найден', 404);
    }

    return responseBuilder.success(res, user.toSafeJSON());
  }

  /**
   * Обновление пользователя
   */
  async update(req, res) {
    const { id } = req.params;
    const updateData = req.body;

    // Проверка прав (пользователь может обновлять только свой профиль или админ)
    if (req.user.id !== id && req.user.role !== 'admin') {
      return responseBuilder.error(res, 'Недостаточно прав', 403);
    }

    const user = await userService.update(id, updateData);

    return responseBuilder.success(res, user.toSafeJSON(), 'Профиль обновлен');
  }

  /**
   * Установка API ключа Claude
   */
  async setApiKey(req, res) {
    const { id } = req.params;
    const { apiKey } = req.body;

    // Проверка прав
    if (req.user.id !== id) {
      return responseBuilder.error(res, 'Недостаточно прав', 403);
    }

    const user = await userService.setApiKey(id, apiKey);

    return responseBuilder.success(res, user.toSafeJSON(), 'API ключ установлен');
  }

  /**
   * Удаление API ключа
   */
  async removeApiKey(req, res) {
    const { id } = req.params;

    // Проверка прав
    if (req.user.id !== id) {
      return responseBuilder.error(res, 'Недостаточно прав', 403);
    }

    const user = await userService.removeApiKey(id);

    return responseBuilder.success(res, user.toSafeJSON(), 'API ключ удален');
  }

  /**
   * Получение статистики использования API
   */
  async getApiUsage(req, res) {
    const { id } = req.params;
    const { startDate, endDate } = req.query;

    // Проверка прав
    if (req.user.id !== id && req.user.role !== 'admin') {
      return responseBuilder.error(res, 'Недостаточно прав', 403);
    }

    const stats = await userService.getApiUsageStats(id, startDate, endDate);

    return responseBuilder.success(res, stats);
  }

  /**
   * Деактивация пользователя
   */
  async deactivate(req, res) {
    const { id } = req.params;

    // Только админ может деактивировать пользователей
    if (req.user.role !== 'admin') {
      return responseBuilder.error(res, 'Недостаточно прав', 403);
    }

    const user = await userService.deactivate(id);

    return responseBuilder.success(res, user.toSafeJSON(), 'Пользователь деактивирован');
  }

  /**
   * Активация пользователя
   */
  async activate(req, res) {
    const { id } = req.params;

    // Только админ может активировать пользователей
    if (req.user.role !== 'admin') {
      return responseBuilder.error(res, 'Недостаточно прав', 403);
    }

    const user = await userService.activate(id);

    return responseBuilder.success(res, user.toSafeJSON(), 'Пользователь активирован');
  }
}

module.exports = new UserController();