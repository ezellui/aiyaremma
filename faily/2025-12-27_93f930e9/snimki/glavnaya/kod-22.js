/**
 * Типы философских категорий
 */

const CATEGORY_TYPES = {
  ONTOLOGICAL: 'ontological',
  EPISTEMOLOGICAL: 'epistemological',
  AXIOLOGICAL: 'axiological',
  ETHICAL: 'ethical',
  AESTHETIC: 'aesthetic',
  METAPHYSICAL: 'metaphysical',
  LOGICAL: 'logical',
  PRACTICAL: 'practical',
  POLITICAL: 'political',
  THEOLOGICAL: 'theological',
  ANTHROPOLOGICAL: 'anthropological',
  SOCIAL: 'social',
  LINGUISTIC: 'linguistic',
  PHENOMENOLOGICAL: 'phenomenological',
  EXISTENTIAL: 'existential',
  ANALYTICAL: 'analytical',
  HERMENEUTICAL: 'hermeneutical',
  CROSS_DISCIPLINARY: 'cross_disciplinary'
};

const CATEGORY_TYPE_DESCRIPTIONS = {
  [CATEGORY_TYPES.ONTOLOGICAL]: 'Онтологическая категория',
  [CATEGORY_TYPES.EPISTEMOLOGICAL]: 'Эпистемологическая категория',
  [CATEGORY_TYPES.AXIOLOGICAL]: 'Аксиологическая категория',
  [CATEGORY_TYPES.ETHICAL]: 'Этическая категория',
  [CATEGORY_TYPES.AESTHETIC]: 'Эстетическая категория',
  [CATEGORY_TYPES.METAPHYSICAL]: 'Метафизическая категория',
  [CATEGORY_TYPES.LOGICAL]: 'Логическая категория',
  [CATEGORY_TYPES.PRACTICAL]: 'Практическая категория',
  [CATEGORY_TYPES.POLITICAL]: 'Политическая категория',
  [CATEGORY_TYPES.THEOLOGICAL]: 'Теологическая категория',
  [CATEGORY_TYPES.ANTHROPOLOGICAL]: 'Антропологическая категория',
  [CATEGORY_TYPES.SOCIAL]: 'Социальная категория',
  [CATEGORY_TYPES.LINGUISTIC]: 'Лингвистическая категория',
  [CATEGORY_TYPES.PHENOMENOLOGICAL]: 'Феноменологическая категория',
  [CATEGORY_TYPES.EXISTENTIAL]: 'Экзистенциальная категория',
  [CATEGORY_TYPES.ANALYTICAL]: 'Аналитическая категория',
  [CATEGORY_TYPES.HERMENEUTICAL]: 'Герменевтическая категория',
  [CATEGORY_TYPES.CROSS_DISCIPLINARY]: 'Междисциплинарная категория'
};

/**
 * Проверяет, является ли строка допустимым типом категории
 */
function isValidCategoryType(type) {
  return Object.values(CATEGORY_TYPES).includes(type);
}

/**
 * Получает описание типа категории
 */
function getCategoryTypeDescription(type) {
  return CATEGORY_TYPE_DESCRIPTIONS[type] || 'Неизвестный тип категории';
}

module.exports = {
  CATEGORY_TYPES,
  CATEGORY_TYPE_DESCRIPTIONS,
  isValidCategoryType,
  getCategoryTypeDescription
};