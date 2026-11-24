/**
 * Контроллер философов
 */

const { responseBuilder } = require('@philos/shared');
const philosopherService = require('../services/philosopher.service');

class PhilosopherController {
  async create(req, res) {
    const philosopher = await philosopherService.create(req.body);
    return responseBuilder.created(res, philosopher.toJSON(), 'Философ создан');
  }

  async getById(req, res) {
    const { id } = req.params;
    const philosopher = await philosopherService.findById(id);
    return responseBuilder.success(res, philosopher.toJSON());
  }

  async getAll(req, res) {
    const filters = {
      tradition: req.query.tradition,
      startYear: req.query.startYear ? parseInt(req.query.startYear, 10) : undefined,
      endYear: req.query.endYear ? parseInt(req.query.endYear, 10) : undefined
    };

    const pagination = {
      page: parseInt(req.query.page, 10) || 1,
      limit: parseInt(req.query.limit, 10) || 50
    };

    const result = await philosopherService.findAll(filters, pagination);

    return responseBuilder.paginated(
      res,
      result.philosophers.map(p => p.toJSON()),
      result.pagination
    );
  }

  async update(req, res) {
    const { id } = req.params;
    const philosopher = await philosopherService.update(id, req.body);
    return responseBuilder.success(res, philosopher.toJSON(), 'Философ обновлен');
  }

  async delete(req, res) {
    const { id } = req.params;
    await philosopherService.delete(id);
    return responseBuilder.success(res, null, 'Философ удален');
  }
}

module.exports = new PhilosopherController();