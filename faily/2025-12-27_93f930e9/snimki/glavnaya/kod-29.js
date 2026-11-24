/**
 * Общие валидаторы на основе Joi
 */

const Joi = require('joi');
const { CATEGORY_TYPES } = require('../constants/category-types');
const { RELATIONSHIP_TYPES, RELATIONSHIP_DIRECTIONS } = require('../constants/relationship-types');
const { INNOVATION_LEVELS } = require('../constants/innovation-levels');

/**
 * Схема валидации UUID
 */
const uuidSchema = Joi.string().uuid({ version: 'uuidv4' });

/**
 * Схема валидации категории
 */
const categorySchema = Joi.object({
  name: Joi.string().min(1).max(255).required(),
  type: Joi.string().valid(...Object.values(CATEGORY_TYPES)).required(),
  definition: Joi.string().min(1).max(5000).required(),
  centrality: Joi.number().min(0).max(1).optional(),
  certainty: Joi.number().min(0).max(1).optional(),
  historical_significance: Joi.number().min(0).max(1).optional(),
  innovation_degree: Joi.number().valid(...Object.values(INNOVATION_LEVELS)).optional(),
  traditions: Joi.array().items(Joi.string()).optional(),
  philosophers: Joi.array().items(Joi.string()).optional()
});

/**
 * Схема валидации связи
 */
const relationshipSchema = Joi.object({
  type: Joi.string().valid(...Object.values(RELATIONSHIP_TYPES)).required(),
  direction: Joi.string().valid(...Object.values(RELATIONSHIP_DIRECTIONS)).required(),
  strength: Joi.number().min(0).max(1).optional(),
  certainty: Joi.number().min(0).max(1).optional(),
  innovation_degree: Joi.number().valid(...Object.values(INNOVATION_LEVELS)).optional(),
  source: Joi.string().max(500).optional(),
  traditions: Joi.array().items(Joi.string()).optional(),
  philosophers: Joi.array().items(Joi.string()).optional()
});

/**
 * Схема валидации концепции
 */
const conceptSchema = Joi.object({
  name: Joi.string().min(1).max(255).required(),
  description: Joi.string().min(1).max(5000).optional(),
  is_synthesis: Joi.boolean().optional(),
  parent_concepts: Joi.array().items(uuidSchema).optional(),
  synthesis_method: Joi.string().max(100).optional(),
  focus: Joi.string().max(500).optional(),
  innovation_degree: Joi.number().valid(...Object.values(INNOVATION_LEVELS)).optional()
});

/**
 * Схема валидации тезиса
 */
const thesisSchema = Joi.object({
  type: Joi.string().required(),
  content: Joi.string().min(1).max(5000).required(),
  related_categories: Joi.array().items(uuidSchema).optional(),
  style: Joi.string().max(100).optional(),
  generation_parameters: Joi.object().optional()
});

/**
 * Валидирует данные согласно схеме
 */
function validate(data, schema) {
  const { error, value } = schema.validate(data, { abortEarly: false });
  
  if (error) {
    const errors = error.details.map(detail => ({
      field: detail.path.join('.'),
      message: detail.message
    }));
    return { valid: false, errors };
  }
  
  return { valid: true, value };
}

module.exports = {
  schemas: {
    uuid: uuidSchema,
    category: categorySchema,
    relationship: relationshipSchema,
    concept: conceptSchema,
    thesis: thesisSchema
  },
  validate
};