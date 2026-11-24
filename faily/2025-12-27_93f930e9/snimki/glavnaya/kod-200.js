/**
 * Контроллер связей
 */

const { responseBuilder } = require('@philos/shared');
const relationshipService = require('../services/relationship.service');
const axios = require('axios');
const config = require('../config/config');

class RelationshipController {
  /**
   * Создание связи
   */
  async create(req, res) {
    const userId = req.user?.id;
    const { conceptId } = req.params;
    const relationshipData = req.body;

    if (!userId) {
      return responseBuilder.error(res, 'Требуется аутентификация', 401);
    }

    const relationship = await relationshipService.create(relationshipData, conceptId);

    return responseBuilder.created(res, relationship.toJSON(), 'Связь создана');
  }

  /**
   * Получение связи по ID
   */
  async getById(req, res) {
    const { id } = req.params;

    const relationship = await relationshipService.findById(id);

    if (!relationship) {
      return responseBuilder.error(res, 'Связь не найдена', 404);
    }

    return responseBuilder.success(res, relationship.toJSON());
  }

  /**
   * Получение всех связей концепции
   */
  async getByConceptId(req, res) {
    const { conceptId } = req.params;

    const relationships = await relationshipService.findByConceptId(conceptId);

    return responseBuilder.success(res, relationships.map(r => r.toJSON()));
  }

  /**
   * Получение связей категории
   */
  async getByCategoryId(req, res) {
    const { categoryId } = req.params;

    const relationships = await relationshipService.findByCategoryId(categoryId);

    return responseBuilder.success(res, relationships.map(r => r.toJSON()));
  }

  /**
   * Обновление связи
   */
  async update(req, res) {
    const { id } = req.params;
    const userId = req.user?.id;
    const updateData = req.body;

    if (!userId) {
      return responseBuilder.error(res, 'Требуется аутентификация', 401);
    }

    const relationship = await relationshipService.update(id, updateData);

    return responseBuilder.success(res, relationship.toJSON(), 'Связь обновлена');
  }

  /**
   * Удаление связи
   */
  async delete(req, res) {
    const { id } = req.params;
    const userId = req.user?.id;

    if (!userId) {
      return responseBuilder.error(res, 'Требуется аутентификация', 401);
    }

    await relationshipService.delete(id);

    return responseBuilder.success(res, null, 'Связь удалена');
  }

  /**
   * Обогащение связи через Claude
   */
  async enrich(req, res) {
    const { id } = req.params;
    const userId = req.user?.id;
    const { category1Name, category2Name, conceptName } = req.body;

    if (!userId) {
      return responseBuilder.error(res, 'Требуется аутентификация', 401);
    }

    const relationship = await relationshipService.findById(id);
    if (!relationship) {
      return responseBuilder.error(res, 'Связь не найдена', 404);
    }

    // Запрос к Claude Service
    try {
      const response = await axios.post(
        `${config.services.claude}/claude/enrich-relationship`,
        {
          relationshipData: relationship.toJSON(),
          category1: category1Name,
          category2: category2Name,
          conceptName
        },
        {
          headers: {
            'Content-Type': 'application/json',
            'X-User-Id': userId
          }
        }
      );

      // Сохраняем обогащенное описание
      const enrichedData = {
        philosophicalFoundation: response.data.data.content,
        counterarguments: [],
        analogues: []
      };

      await relationshipService.saveEnrichedDescription(id, enrichedData);

      return responseBuilder.success(res, {
        relationship: relationship.toJSON(),
        enrichedDescription: enrichedData
      }, 'Связь обогащена');

    } catch (error) {
      return responseBuilder.error(
        res,
        `Ошибка обогащения связи: ${error.message}`,
        500
      );
    }
  }

  /**
   * Получение обогащенного описания
   */
  async getEnrichedDescription(req, res) {
    const { id } = req.params;

    const enrichedDescription = await relationshipService.getEnrichedDescription(id);

    if (!enrichedDescription) {
      return responseBuilder.error(res, 'Обогащенное описание не найдено', 404);
    }

    return responseBuilder.success(res, enrichedDescription);
  }

  /**
   * Поиск пути между категориями
   */
  async findPath(req, res) {
    const { sourceCategoryId, targetCategoryId } = req.query;
    const { maxDepth } = req.query;

    if (!sourceCategoryId || !targetCategoryId) {
      return responseBuilder.error(res, 'Необходимы sourceCategoryId и targetCategoryId', 400);
    }

    const path = await relationshipService.findPath(
      sourceCategoryId,
      targetCategoryId,
      parseInt(maxDepth) || 5
    );

    if (!path) {
      return responseBuilder.error(res, 'Путь не найден', 404);
    }

    return responseBuilder.success(res, path);
  }

  /**
   * Поиск циклов
   */
  async findCycles(req, res) {
    const { conceptId } = req.params;

    const cycles = await relationshipService.findCycles(conceptId);

    return responseBuilder.success(res, cycles);
  }
}

module.exports = new RelationshipController();