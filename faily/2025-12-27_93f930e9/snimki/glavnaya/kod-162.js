/**
 * Контроллер концепций
 */

const { responseBuilder } = require('@philos/shared');
const conceptService = require('../services/concept.service');
const searchService = require('../services/search.service');

class ConceptController {
  /**
   * Создание концепции
   */
  async create(req, res) {
    const userId = req.user?.id;
    const conceptData = req.body;

    if (!userId) {
      return responseBuilder.error(res, 'Требуется аутентификация', 401);
    }

    const concept = await conceptService.create(conceptData, userId);

    return responseBuilder.created(res, concept.toJSON(), 'Концепция создана');
  }

  /**
   * Получение концепции по ID
   */
  async getById(req, res) {
    const { id } = req.params;

    const concept = await conceptService.findById(id);

    if (!concept) {
      return responseBuilder.error(res, 'Концепция не найдена', 404);
    }

    return responseBuilder.success(res, concept.toJSON());
  }

  /**
   * Обновление концепции
   */
  async update(req, res) {
    const { id } = req.params;
    const userId = req.user?.id;
    const updateData = req.body;

    if (!userId) {
      return responseBuilder.error(res, 'Требуется аутентификация', 401);
    }

    const concept = await conceptService.update(id, updateData, userId);

    return responseBuilder.success(res, concept.toJSON(), 'Концепция обновлена');
  }

  /**
   * Удаление концепции
   */
  async delete(req, res) {
    const { id } = req.params;
    const userId = req.user?.id;

    if (!userId) {
      return responseBuilder.error(res, 'Требуется аутентификация', 401);
    }

    await conceptService.delete(id, userId);

    return responseBuilder.success(res, null, 'Концепция удалена');
  }

  /**
   * Получение концепций пользователя
   */
  async getUserConcepts(req, res) {
    const userId = req.user?.id;
    const { limit, offset, includePublic } = req.query;

    if (!userId) {
      return responseBuilder.error(res, 'Требуется аутентификация', 401);
    }

    const concepts = await conceptService.findByUser(userId, {
      limit: parseInt(limit) || 50,
      offset: parseInt(offset) || 0,
      includePublic: includePublic === 'true'
    });

    return responseBuilder.success(res, concepts.map(c => c.toJSON()));
  }

  /**
   * Получение публичных концепций
   */
  async getPublic(req, res) {
    const { limit, offset } = req.query;

    const concepts = await conceptService.findPublic({
      limit: parseInt(limit) || 50,
      offset: parseInt(offset) || 0
    });

    return responseBuilder.success(res, concepts.map(c => c.toJSON()));
  }

  /**
   * Получение синтезированных концепций
   */
  async getSynthesized(req, res) {
    const { limit, offset } = req.query;

    const concepts = await conceptService.findSynthesized({
      limit: parseInt(limit) || 50,
      offset: parseInt(offset) || 0
    });

    return responseBuilder.success(res, concepts.map(c => c.toJSON()));
  }

  /**
   * Связывание с философом
   */
  async linkPhilosopher(req, res) {
    const { id } = req.params;
    const userId = req.user?.id;
    const { philosopherId, relationshipType } = req.body;

    if (!userId) {
      return responseBuilder.error(res, 'Требуется аутентификация', 401);
    }

    await conceptService.linkPhilosopher(id, philosopherId, relationshipType, userId);

    return responseBuilder.success(res, null, 'Философ связан с концепцией');
  }

  /**
   * Связывание с традицией
   */
  async linkTradition(req, res) {
    const { id } = req.params;
    const userId = req.user?.id;
    const { traditionId, relationshipStrength } = req.body;

    if (!userId) {
      return responseBuilder.error(res, 'Требуется аутентификация', 401);
    }

    await conceptService.linkTradition(id, traditionId, relationshipStrength, userId);

    return responseBuilder.success(res, null, 'Традиция связана с концепцией');
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
   * Получение традиций концепции
   */
  async getTraditions(req, res) {
    const { id } = req.params;

    const traditions = await conceptService.getTraditions(id);

    return responseBuilder.success(res, traditions);
  }

  /**
   * Получение статистики концепции
   */
  async getStats(req, res) {
    const { id } = req.params;

    const stats = await conceptService.getStats(id);

    return responseBuilder.success(res, stats);
  }

  /**
   * Поиск концепций
   */
  async search(req, res) {
    const userId = req.user?.id;
    const { q, limit, offset, publicOnly } = req.query;

    const results = await searchService.searchConcepts(q, {
      limit: parseInt(limit) || 50,
      offset: parseInt(offset) || 0,
      userId,
      publicOnly: publicOnly !== 'false'
    });

    return responseBuilder.success(res, results);
  }

  /**
   * Поиск по тегам
   */
  async searchByTags(req, res) {
    const userId = req.user?.id;
    const { tags, limit, offset, publicOnly } = req.query;

    const tagArray = Array.isArray(tags) ? tags : [tags];

    const results = await searchService.searchByTags(tagArray, {
      limit: parseInt(limit) || 50,
      offset: parseInt(offset) || 0,
      userId,
      publicOnly: publicOnly !== 'false'
    });

    return responseBuilder.success(res, results.map(c => c.toJSON()));
  }

  /**
   * Расширенный поиск
   */
  async advancedSearch(req, res) {
    const userId = req.user?.id;
    const filters = req.body;
    const { limit, offset } = req.query;

    const results = await searchService.advancedSearch(filters, {
      limit: parseInt(limit) || 50,
      offset: parseInt(offset) || 0,
      userId
    });

    return responseBuilder.success(res, results.map(c => c.toJSON()));
  }

  /**
   * Поиск похожих концепций
   */
  async findSimilar(req, res) {
    const { id } = req.params;
    const { limit } = req.query;

    const similar = await searchService.findSimilar(id, {
      limit: parseInt(limit) || 10
    });

    return responseBuilder.success(res, similar.map(c => c.toJSON()));
  }

  /**
   * Получение популярных тегов
   */
  async getPopularTags(req, res) {
    const { limit } = req.query;

    const tags = await searchService.getPopularTags(parseInt(limit) || 20);

    return responseBuilder.success(res, tags);
  }
}

module.exports = new ConceptController();