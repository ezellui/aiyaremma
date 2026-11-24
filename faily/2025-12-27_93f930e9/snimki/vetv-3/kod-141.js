/**
 * Контроллер традиций
 */

const { responseBuilder } = require('@philos/shared');
const traditionService = require('../services/tradition.service');

class TraditionController {
  async create(req, res) {
    const tradition = await traditionService.create(req.body);
    return responseBuilder.created(res, tradition.toJSON(), 'Традиция создана');
  }

  async getById(req, res) {
    const { id } = req.params;
    const tradition = await traditionService.findById(id);
    return responseBuilder.success(res, tradition.toJSON());
  }

  async getAll(req, res) {
    const pagination = {
      page: parseInt(req.query.page, 10) || 1,
      limit: parseInt(req.query.limit, 10) || 50
    };

    const result = await traditionService.findAll(pagination);

    return responseBuilder.paginated(
      res,
      result.traditions.map(t => t.toJSON()),
      result.pagination
    );
  }

  async update(req, res) {
    const { id } = req.params;
    const tradition = await traditionService.update(id, req.body);
    return responseBuilder.success(res, tradition.toJSON(), 'Традиция обновлена');
  }

  async delete(req, res) {
    const { id } = req.params;
    await traditionService.delete(id);
    return responseBuilder.success(res, null, 'Традиция удалена');
  }
}

module.exports = new TraditionController();