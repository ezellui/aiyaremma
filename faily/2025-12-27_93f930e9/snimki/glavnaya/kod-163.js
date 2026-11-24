/**
 * Контроллер философов
 */

const { responseBuilder } = require('@philos/shared');
const philosopherService = require('../services/philosopher.service');

class PhilosopherController {
  /**
   * Создание философа
   */
  async create(req, res) {
    const userId = req.user?.id;
    const philosopherData = req.body;

    if (!userId) {
      return responseBuilder.error(res, 'Требуется аутентификация', 401);
    }

    // Только админы могут создавать философов
    if (req.user.role !== 'admin') {
      return responseBuilder.error(res, 'Недостаточно прав', 403);
    }

    const philosopher = await philosopherService.create(philosopherData);

    return responseBuilder.created(res, philosopher.toJSON(), 'Философ создан');
  }

  /**
   * Получение философа по ID
   */
  async getById(req, res) {
    const { id } = req.params;

    const philosopher = await philosopherService.findById(id);

    if (!philosopher) {
      return responseBuilder.error(res, 'Философ не найден', 404);
    }

    return responseBuilder.success(res, philosopher.toJSON());
  }

  /**
   * Получение всех философов
   */
  async getAll(req, res) {
    const { limit, offset, tradition } = req.query;

    const philosophers = await philosopherService.findAll({
      limit: parseInt(limit) || 100,
      offset: parseInt(offset) || 0,
      tradition
    });

    return responseBuilder.success(res, philosophers.map(p => p.toJSON()));
  }

  /**
   * Обновление философа
   */
  async update(req, res) {
    const { id } = req.params;
    const userId = req.user?.id;
    const updateData = req.body;

    if (!userId) {
      return responseBuilder.error(res, 'Требуется аутентификация', 401);
    }

    // Только админы могут обновлять философов
    if (req.user.role !== 'admin') {
      return responseBuilder.error(res, 'Недостаточно прав', 403);
    }

    const philosopher = await philosopherService.update(id, updateData);

    return responseBuilder.success(res, philosopher.toJSON(), 'Философ обновлен');
  }

  /**
   * Удаление философа
   */
  async delete(req, res) {
    const { id } = req.params;
    const userId = req.user?.id;

    if (!userId) {
      return responseBuilder.error(res, 'Требуется аутентификация', 401);
    }

    // Только админы могут удалять философов
    if (req.user.role !== 'admin') {
      return responseBuilder.error(res, 'Недостаточно прав', 403);
    }

    await philosopherService.delete(id);

    return responseBuilder.success(res, null, 'Философ удален');
  }

  /**
   * Получение концепций философа
   */
  async getConcepts(req, res) {
    const { id } = req.params;

    const concepts = await philosopherService.getConcepts(id);

    return responseBuilder.success(res, concepts);
  }

  /**
   * Поиск философов
   */
  async search(req, res) {
    const { q, limit, offset } = req.query;

    const results = await philosopherService.search(q, {
      limit: parseInt(limit) || 50,
      offset: parseInt(offset) || 0
    });

    return responseBuilder.success(res, results.map(p => p.toJSON()));
  }
}

module.exports = new PhilosopherController();