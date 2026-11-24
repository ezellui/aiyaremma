/**
 * Контроллер категорий
 */

const { responseBuilder } = require('@philos/shared');
const categoryService = require('../services/category.service');
const axios = require('axios');
const config = require('../config/config');

class CategoryController {
  /**
   * Создание категории
   */
  async create(req, res) {
    const userId = req.user?.id;
    const { conceptId } = req.params;
    const categoryData = req.body;

    if (!userId) {
      return responseBuilder.error(res, 'Требуется аутентификация', 401);
    }

    const category = await categoryService.create(categoryData, conceptId);

    return responseBuilder.created(res, category.toJSON(), 'Категория создана');
  }

  /**
   * Получение категории по ID
   */
  async getById(req, res) {
    const { id } = req.params;

    const category = await categoryService.findById(id);

    if (!category) {
      return responseBuilder.error(res, 'Категория не найдена', 404);
    }

    return responseBuilder.success(res, category.toJSON());
  }

  /**
   * Получение всех категорий концепции
   */
  async getByConceptId(req, res) {
    const { conceptId } = req.params;

    const categories = await categoryService.findByConceptId(conceptId);

    return responseBuilder.success(res, categories.map(c => c.toJSON()));
  }

  /**
   * Обновление категории
   */
  async update(req, res) {
    const { id } = req.params;
    const userId = req.user?.id;
    const updateData = req.body;

    if (!userId) {
      return responseBuilder.error(res, 'Требуется аутентификация', 401);
    }

    const category = await categoryService.update(id, updateData);

    return responseBuilder.success(res, category.toJSON(), 'Категория обновлена');
  }

  /**
   * Удаление категории
   */
  async delete(req, res) {
    const { id } = req.params;
    const userId = req.user?.id;

    if (!userId) {
      return responseBuilder.error(res, 'Требуется аутентификация', 401);
    }

    await categoryService.delete(id);

    return responseBuilder.success(res, null, 'Категория удалена');
  }

  /**
   * Обогащение категории через Claude
   */
  async enrich(req, res) {
    const { id } = req.params;
    const userId = req.user?.id;
    const { conceptName, traditions, philosophers } = req.body;

    if (!userId) {
      return responseBuilder.error(res, 'Требуется аутентификация', 401);
    }

    const category = await categoryService.findById(id);
    if (!category) {
      return responseBuilder.error(res, 'Категория не найдена', 404);
    }

    // Запрос к Claude Service
    try {
      const response = await axios.post(
        `${config.services.claude}/claude/enrich-category`,
        {
          categoryData: category.toJSON(),
          conceptName,
          traditions: traditions || [],
          philosophers: philosophers || []
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
        detailedDescription: response.data.data.content,
        alternativeInterpretations: [],
        historicalAnalogues: []
      };

      await categoryService.saveEnrichedDescription(id, enrichedData);

      return responseBuilder.success(res, {
        category: category.toJSON(),
        enrichedDescription: enrichedData
      }, 'Категория обогащена');

    } catch (error) {
      return responseBuilder.error(
        res,
        `Ошибка обогащения категории: ${error.message}`,
        500
      );
    }
  }

  /**
   * Получение обогащенного описания
   */
  async getEnrichedDescription(req, res) {
    const { id } = req.params;

    const enrichedDescription = await categoryService.getEnrichedDescription(id);

    if (!enrichedDescription) {
      return responseBuilder.error(res, 'Обогащенное описание не найдено', 404);
    }

    return responseBuilder.success(res, enrichedDescription);
  }

  /**
   * Вычисление центральности
   */
  async calculateCentrality(req, res) {
    const { conceptId } = req.params;
    const { algorithm } = req.query;
    const userId = req.user?.id;

    if (!userId) {
      return responseBuilder.error(res, 'Требуется аутентификация', 401);
    }

    const results = await categoryService.calculateCentrality(
      conceptId,
      algorithm || 'pagerank'
    );

    return responseBuilder.success(res, results, 'Центральность вычислена');
  }
}

module.exports = new CategoryController();