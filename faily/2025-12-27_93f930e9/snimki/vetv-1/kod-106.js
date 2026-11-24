/**
 * Схемы валидации с использованием Joi
 */

const Joi = require('joi');
const { CATEGORY_TYPES } = require('../constants/category-types');
const { RELATIONSHIP_TYPES } = require('../constants/relationship-types');
const { INNOVATION_LEVELS } = require('../constants/innovation-levels');
const { THESIS_TYPES } = require('../constants/thesis-types');
const { ANALYSIS_TYPES } = require('../constants/analysis-types');
const VALIDATION_RULES = require('../constants/validation-rules');

/**
 * UUID схема
 */
const uuidSchema = Joi.string()
  .uuid({ version: 'uuidv4' })
  .required()
  .messages({
    'string.guid': 'Неверный формат UUID',
    'any.required': 'UUID обязателен'
  });

/**
 * Опциональный UUID
 */
const optionalUuidSchema = Joi.string()
  .uuid({ version: 'uuidv4' })
  .allow(null)
  .messages({
    'string.guid': 'Неверный формат UUID'
  });

/**
 * Схема для категории
 */
const categorySchema = Joi.object({
  name: Joi.string()
    .min(VALIDATION_RULES.category.name.minLength)
    .max(VALIDATION_RULES.category.name.maxLength)
    .required()
    .messages({
      'string.min': `Название категории должно содержать минимум ${VALIDATION_RULES.category.name.minLength} символа`,
      'string.max': `Название категории не должно превышать ${VALIDATION_RULES.category.name.maxLength} символов`,
      'any.required': 'Название категории обязательно'
    }),
  
  type: Joi.string()
    .valid(...CATEGORY_TYPES)
    .required()
    .messages({
      'any.only': `Тип категории должен быть одним из: ${CATEGORY_TYPES.join(', ')}`,
      'any.required': 'Тип категории обязателен'
    }),
  
  definition: Joi.string()
    .min(VALIDATION_RULES.category.definition.minLength)
    .max(VALIDATION_RULES.category.definition.maxLength)
    .allow('')
    .messages({
      'string.min': `Определение должно содержать минимум ${VALIDATION_RULES.category.definition.minLength} символов`,
      'string.max': `Определение не должно превышать ${VALIDATION_RULES.category.definition.maxLength} символов`
    }),
  
  innovation_degree: Joi.number()
    .integer()
    .min(INNOVATION_LEVELS.TRADITIONAL)
    .max(INNOVATION_LEVELS.REVOLUTIONARY)
    .allow(null)
    .messages({
      'number.min': `Степень инновационности должна быть минимум ${INNOVATION_LEVELS.TRADITIONAL}`,
      'number.max': `Степень инновационности должна быть максимум ${INNOVATION_LEVELS.REVOLUTIONARY}`
    }),
  
  concept_id: uuidSchema
});

/**
 * Схема для обновления категории
 */
const categoryUpdateSchema = Joi.object({
  name: Joi.string()
    .min(VALIDATION_RULES.category.name.minLength)
    .max(VALIDATION_RULES.category.name.maxLength),
  
  definition: Joi.string()
    .min(VALIDATION_RULES.category.definition.minLength)
    .max(VALIDATION_RULES.category.definition.maxLength)
    .allow(''),
  
  innovation_degree: Joi.number()
    .integer()
    .min(INNOVATION_LEVELS.TRADITIONAL)
    .max(INNOVATION_LEVELS.REVOLUTIONARY)
    .allow(null)
}).min(1);

/**
 * Схема для связи
 */
const relationshipSchema = Joi.object({
  type: Joi.string()
    .valid(...RELATIONSHIP_TYPES)
    .required()
    .messages({
      'any.only': `Тип связи должен быть одним из: ${RELATIONSHIP_TYPES.join(', ')}`,
      'any.required': 'Тип связи обязателен'
    }),
  
  from_category_id: uuidSchema,
  
  to_category_id: uuidSchema,
  
  description: Joi.string()
    .min(VALIDATION_RULES.relationship.description.minLength)
    .max(VALIDATION_RULES.relationship.description.maxLength)
    .allow('')
    .messages({
      'string.min': `Описание должно содержать минимум ${VALIDATION_RULES.relationship.description.minLength} символов`,
      'string.max': `Описание не должно превышать ${VALIDATION_RULES.relationship.description.maxLength} символов`
    }),
  
  innovation_degree: Joi.number()
    .integer()
    .min(INNOVATION_LEVELS.TRADITIONAL)
    .max(INNOVATION_LEVELS.REVOLUTIONARY)
    .allow(null)
});

/**
 * Схема для обновления связи
 */
const relationshipUpdateSchema = Joi.object({
  description: Joi.string()
    .min(VALIDATION_RULES.relationship.description.minLength)
    .max(VALIDATION_RULES.relationship.description.maxLength)
    .allow(''),
  
  innovation_degree: Joi.number()
    .integer()
    .min(INNOVATION_LEVELS.TRADITIONAL)
    .max(INNOVATION_LEVELS.REVOLUTIONARY)
    .allow(null)
}).min(1);

/**
 * Схема для концепции
 */
const conceptSchema = Joi.object({
  name: Joi.string()
    .min(VALIDATION_RULES.concept.name.minLength)
    .max(VALIDATION_RULES.concept.name.maxLength)
    .required()
    .messages({
      'string.min': `Название должно содержать минимум ${VALIDATION_RULES.concept.name.minLength} символа`,
      'string.max': `Название не должно превышать ${VALIDATION_RULES.concept.name.maxLength} символов`,
      'any.required': 'Название обязательно'
    }),
  
  description: Joi.string()
    .min(VALIDATION_RULES.concept.description.minLength)
    .max(VALIDATION_RULES.concept.description.maxLength)
    .allow('')
    .messages({
      'string.min': `Описание должно содержать минимум ${VALIDATION_RULES.concept.description.minLength} символов`,
      'string.max': `Описание не должно превышать ${VALIDATION_RULES.concept.description.maxLength} символов`
    }),
  
  focus: Joi.string()
    .min(VALIDATION_RULES.concept.focus.minLength)
    .max(VALIDATION_RULES.concept.focus.maxLength)
    .allow('')
    .messages({
      'string.min': `Фокус должен содержать минимум ${VALIDATION_RULES.concept.focus.minLength} символов`,
      'string.max': `Фокус не должен превышать ${VALIDATION_RULES.concept.focus.maxLength} символов`
    }),
  
  is_synthesis: Joi.boolean().default(false),
  
  parent_concepts: Joi.array()
    .items(uuidSchema)
    .allow(null),
  
  synthesis_method: Joi.string()
    .allow('', null),
  
  innovation_degree: Joi.number()
    .integer()
    .min(INNOVATION_LEVELS.TRADITIONAL)
    .max(INNOVATION_LEVELS.REVOLUTIONARY)
    .allow(null),
  
  historical_context: Joi.string()
    .allow('', null)
});

/**
 * Схема для обновления концепции
 */
const conceptUpdateSchema = Joi.object({
  name: Joi.string()
    .min(VALIDATION_RULES.concept.name.minLength)
    .max(VALIDATION_RULES.concept.name.maxLength),
  
  description: Joi.string()
    .min(VALIDATION_RULES.concept.description.minLength)
    .max(VALIDATION_RULES.concept.description.maxLength)
    .allow(''),
  
  focus: Joi.string()
    .min(VALIDATION_RULES.concept.focus.minLength)
    .max(VALIDATION_RULES.concept.focus.maxLength)
    .allow(''),
  
  innovation_degree: Joi.number()
    .integer()
    .min(INNOVATION_LEVELS.TRADITIONAL)
    .max(INNOVATION_LEVELS.REVOLUTIONARY)
    .allow(null),
  
  historical_context: Joi.string()
    .allow('', null)
}).min(1);

/**
 * Схема для тезиса
 */
const thesisSchema = Joi.object({
  concept_id: uuidSchema,
  
  type: Joi.string()
    .valid(...THESIS_TYPES)
    .required()
    .messages({
      'any.only': `Тип тезиса должен быть одним из: ${THESIS_TYPES.join(', ')}`,
      'any.required': 'Тип тезиса обязателен'
    }),
  
  content: Joi.string()
    .min(VALIDATION_RULES.thesis.content.minLength)
    .max(VALIDATION_RULES.thesis.content.maxLength)
    .required()
    .messages({
      'string.min': `Содержание должно содержать минимум ${VALIDATION_RULES.thesis.content.minLength} символов`,
      'string.max': `Содержание не должно превышать ${VALIDATION_RULES.thesis.content.maxLength} символов`,
      'any.required': 'Содержание обязательно'
    }),
  
  related_categories: Joi.array()
    .items(uuidSchema)
    .allow(null),
  
  style: Joi.string()
    .allow('', null)
});

/**
 * Схема для регистрации пользователя
 */
const userRegistrationSchema = Joi.object({
  username: Joi.string()
    .min(VALIDATION_RULES.user.username.minLength)
    .max(VALIDATION_RULES.user.username.maxLength)
    .pattern(VALIDATION_RULES.user.username.pattern)
    .required()
    .messages({
      'string.min': `Имя пользователя должно содержать минимум ${VALIDATION_RULES.user.username.minLength} символа`,
      'string.max': `Имя пользователя не должно превышать ${VALIDATION_RULES.user.username.maxLength} символов`,
      'string.pattern.base': 'Имя пользователя может содержать только буквы, цифры, дефисы и подчеркивания',
      'any.required': 'Имя пользователя обязательно'
    }),
  
  email: Joi.string()
    .pattern(VALIDATION_RULES.user.email.pattern)
    .required()
    .messages({
      'string.pattern.base': 'Неверный формат email',
      'any.required': 'Email обязателен'
    }),
  
  password: Joi.string()
    .min(VALIDATION_RULES.user.password.minLength)
    .max(VALIDATION_RULES.user.password.maxLength)
    .required()
    .messages({
      'string.min': `Пароль должен содержать минимум ${VALIDATION_RULES.user.password.minLength} символов`,
      'string.max': `Пароль не должен превышать ${VALIDATION_RULES.user.password.maxLength} символов`,
      'any.required': 'Пароль обязателен'
    })
});

/**
 * Схема для входа пользователя
 */
const userLoginSchema = Joi.object({
  email: Joi.string()
    .pattern(VALIDATION_RULES.user.email.pattern)
    .required()
    .messages({
      'string.pattern.base': 'Неверный формат email',
      'any.required': 'Email обязателен'
    }),
  
  password: Joi.string()
    .required()
    .messages({
      'any.required': 'Пароль обязателен'
    })
});

/**
 * Схема для пагинации
 */
const paginationSchema = Joi.object({
  page: Joi.number()
    .integer()
    .min(VALIDATION_RULES.pagination.page.min)
    .default(VALIDATION_RULES.pagination.page.default),
  
  limit: Joi.number()
    .integer()
    .min(VALIDATION_RULES.pagination.limit.min)
    .max(VALIDATION_RULES.pagination.limit.max)
    .default(VALIDATION_RULES.pagination.limit.default)
});

/**
 * Схема для анализа
 */
const analysisSchema = Joi.object({
  concept_id: uuidSchema,
  
  analysis_type: Joi.string()
    .valid(...ANALYSIS_TYPES)
    .required()
    .messages({
      'any.only': `Тип анализа должен быть одним из: ${ANALYSIS_TYPES.join(', ')}`,
      'any.required': 'Тип анализа обязателен'
    }),
  
  parameters: Joi.object().allow(null)
});

/**
 * Валидация с выбросом ошибки
 */
function validate(schema, data) {
  const { error, value } = schema.validate(data, { 
    abortEarly: false,
    stripUnknown: true
  });
  
  if (error) {
    const errors = error.details.map(detail => ({
      field: detail.path.join('.'),
      message: detail.message
    }));
    
    const ValidationError = require('./errors').ValidationError;
    throw new ValidationError('Ошибка валидации данных', errors);
  }
  
  return value;
}

module.exports = {
  // Схемы
  uuidSchema,
  optionalUuidSchema,
  categorySchema,
  categoryUpdateSchema,
  relationshipSchema,
  relationshipUpdateSchema,
  conceptSchema,
  conceptUpdateSchema,
  thesisSchema,
  userRegistrationSchema,
  userLoginSchema,
  paginationSchema,
  analysisSchema,
  
  // Функция валидации
  validate
};