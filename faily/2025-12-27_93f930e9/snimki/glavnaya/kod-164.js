/**
 * Контроллер традиций
 */

const { responseBuilder } = require('@philos/shared');
const traditionService = require('../services/tradition.service');

class TraditionController {
  /**
   * Создание традиции
   */
  async create(req, res) {
    const userId = req.user?.id;
    const traditionData = req.body;

    if (!userId) {
      return responseBuilder.error(res, 'Требуется аутентификация', 401);
    }

    // Только админы могут создавать традиции
    if (req.user.role !== 'admin') {
      return responseBuilder.error(res, 'Недостаточно прав', 403);
    }

    const tradition = await traditionService.create(traditionData);

    return responseBuilder.created(res, tradition.toJSON(), 'Традиция создана');
  }

  /**
   * Получение традиции по ID
   */
  async getById(req, res) {
    const { id } = req.params;

    const tradition = await traditionService.findById(id);

    if (!tradition) {
      return responseBuilder.error(res, 'Традиция не найдена', 404);
    }

    return responseBuilder.success(res, tradition.toJSON());
  }

  /**
   * Получение всех традиций
   */
  async getAll(req, res) {
    const { limit, offset } = req.query;

    const traditions = await traditionService.findAll({
      limit: parseInt(limit) || 100,
      offset: parseInt(offset) || 0
    });

    return responseBuilder.success(res, traditions.map(t => t.toJSON()));
  }

  /**
   * Обновление традиции
   */
  async update(req, res) {
    const { id } = req.params;
    const userId = req.user?.id;
    const updateData = req.body;

    if (!userId) {
      return responseBuilder.error(res, 'Требуется аутентификация', 401);
    }

    // Только админы могут обновлять традиции
    if (req.user.role !== 'admin') {
      return responseBuilder.error(res, 'Недостаточно прав', 403);
    }

    const tradition = await traditionService.update(id, updateData);

    return responseBuilder.success(res, tradition.toJSON(), 'Традиция обновлена');
  }

  /**
   * Удаление традиции
   */
  async delete(req, res) {
    const { id } = req.params;
    const userId = req.user?.id;

    if (!userId) {
      return responseBuilder.error(res, 'Требуется аутентификация', 401);
    }

    // Только админы могут удалять традиции
    if (req.user.role !== 'admin') {
      return responseBuilder.error(res, 'Недостаточно прав', 403);
    }

    await traditionService.delete(id);

    return responseBuilder.success(res, null, 'Традиция удалена');
  }

  /**
   * Получение концепций традиции
   */
  async getConcepts(req, res) {
    const { id } = req.params;

    const concepts = await traditionService.getConcepts(id);

    return responseBuilder.success(res, concepts);
  }

  /**
   * Поиск традиций
   */
  async search(req, res) {
    const { q, limit, offset } = req.query;

    const results = await traditionService.search(q, {
      limit: parseInt(limit) || 50,
      offset: parseInt(offset) || 0
    });

    return responseBuilder.success(res, results.map(t => t.toJSON()));
  }
}

module.exports = new TraditionController();