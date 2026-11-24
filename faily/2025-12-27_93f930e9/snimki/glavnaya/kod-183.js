/**
 * Кастомные валидаторы
 */

const Joi = require('joi');

/**
 * Валидатор UUID
 */
const uuidValidator = Joi.string().uuid();

/**
 * Валидатор степени инновации
 */
const innovationDegreeValidator = Joi.string().valid(
  'традиционная',
  'модифицированная',
  'синтетическая',
  'инновационная',
  'революционная'
);

/**
 * Валидатор тегов
 */
const tagsValidator = Joi.array()
  .items(Joi.string().min(2).max(50))
  .max(20);

/**
 * Валидатор пагинации
 */
const paginationValidator = {
  limit: Joi.number().integer().min(1).max(100).default(50),
  offset: Joi.number().integer().min(0).default(0)
};

/**
 * Проверка прав доступа к концепции
 */
function canAccessConcept(concept, userId) {
  if (!concept) {
    return false;
  }

  // Публичные концепции доступны всем
  if (concept.isPublic) {
    return true;
  }

  // Приватные концепции доступны только создателю
  return concept.creatorId === userId;
}

/**
 * Проверка прав на редактирование концепции
 */
function canEditConcept(concept, userId) {
  if (!concept || !userId) {
    return false;
  }

  return concept.creatorId === userId;
}

module.exports = {
  uuidValidator,
  innovationDegreeValidator,
  tagsValidator,
  paginationValidator,
  canAccessConcept,
  canEditConcept
};