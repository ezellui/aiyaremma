/**
 * Контроллер концепций
 */

const { responseBuilder } = require('@philos/shared');
const conceptService = require('../services/concept.service');

class ConceptController {
  /**
   * Создание концепции
   */
  async create(req, res) {
    const conceptData = req.body;
    const userId = req.user?.id;

    const concept = await conceptService.create(conceptData, userId);

    return responseBuilder.created(res, concept.toJSON(), 'Концепция создана');
  }

  /**
   * Получение концепции
   */
  async getById(req, res) {
    const { id } = req.params;
    const userId = req.user?.id;
    const { full } = req.query;

    let concept;
    if (full === 'true') {
      concept = await conceptService.getFullConcept(id, userId);
    } else {
      concept = await conceptService.findById(id, userId);
    }

    return responseBuilder.success(res, concept.toJSON ? concept.toJSON() : concept);
  }

  /**
   * Получение списка концепций
   */
  async getAll(req, res) {
    const filters = {
      isPublic: req.query.isPublic === 'true',
      creatorId: req.query.creatorId,
      isSynthesis: req.query.isSynthesis === 'true',
      tags: req.query.tags ? req.query.tags.split(',') : undefined,
      search: req.query.search,
      sortBy: req.query.sortBy,
      sortOrder: req.query.sortOrder
    };

    const pagination = {
      page: parseInt(req.query.page, 10) || 1,
      limit: parseInt(req.query.limit, 10) || 10
    };

    const result = await conceptService.findAll(filters, pagination);

    return responseBuilder.paginated(
      res,
      result.concepts.map(c => c.toJSON()),
      result.pagination
    );
  }

  /**
   * Обновление концепции
   */
  async update(req, res) {
    const { id } = req.params;
    const updateData = req.body;
    const userId = req.user?.id;

    const concept = await conceptService.update(id, updateData, userId);

    return responseBuilder.success(res, concept.toJSON(), 'Концепция обновлена');
  }

  /**
   * Удаление концепции
   */
  async delete(req, res) {
    const { id } = req.params;
    const userId = req.user?.id;

    await conceptService.delete(id, userId);

    return responseBuilder.success(res, null, 'Концепция удалена');
  }

  /**
   * Добавление лайка
   */
  async like(req, res) {
    const { id } = req.params;

    const concept = await conceptService.incrementLikes(id);

    return responseBuilder.success(res, concept.toJSON(), 'Лайк добавлен');
  }

  /**
   * Добавление философа к концепции
   */
  async addPhilosopher(req, res) {
    const { id } = req.params;
    const { philosopherId, relationshipType } = req.body;

    await conceptService.addPhilosopher(id, philosopherId, relationshipType);

    return responseBuilder.success(res, null, 'Философ добавлен');
  }

  /**
   * Получение философов концепции
   */
  async getPhilosophers(req, res) {
    const { id } = req.params;

    const philosophers = await conceptService.getPhilosophers(id);

    return responseBuilder.success(res, philosophers);
  }

  /**
   * Добавление традиции к концепции
   */
  async addTradition(req, res) {
    const { id } = req.params;
    const { traditionId, relationshipStrength } = req.body;

    await conceptService.addTradition(id, traditionId, relationshipStrength);

    return responseBuilder.success(res, null, 'Традиция добавлена');
  }

  /**
   * Получение традиций концепции
   */
  async getTraditions(req, res) {
    const { id } = req.params;

    const traditions = await conceptService.getTraditions(id);

    return responseBuilder.success(res, traditions);
  }
}

module.exports = new ConceptController();