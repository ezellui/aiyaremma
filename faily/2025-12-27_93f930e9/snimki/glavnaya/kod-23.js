/**
 * Типы связей между категориями
 */

const RELATIONSHIP_TYPES = {
  HIERARCHICAL: 'hierarchical',
  CAUSAL: 'causal',
  DIALECTICAL: 'dialectical',
  CORRELATIONAL: 'correlational',
  DISJUNCTIVE: 'disjunctive',
  CONJUNCTIVE: 'conjunctive',
  CONTRADICTION: 'contradiction',
  COMPLEMENTARY: 'complementary',
  EMERGENCE: 'emergence',
  NECESSARY_CONDITION: 'necessary_condition',
  SUFFICIENT_CONDITION: 'sufficient_condition',
  IDENTITY: 'identity',
  ANALOGY: 'analogy',
  IMPLEMENTATION: 'implementation',
  INSTANTIATION: 'instantiation',
  GENERALIZATION: 'generalization',
  PART_WHOLE: 'part_whole',
  MEANS_END: 'means_end',
  DEDUCTIVE: 'deductive',
  INDUCTIVE: 'inductive',
  ABDUCTIVE: 'abductive',
  TEMPORAL: 'temporal',
  CONCEPTUAL: 'conceptual',
  DEFINITIONAL: 'definitional',
  MANIFESTATION: 'manifestation',
  FOUNDATIONAL: 'foundational',
  RECOGNITION: 'recognition',
  REFLEXION: 'reflexion',
  DEVELOPMENT: 'development'
};

const RELATIONSHIP_DIRECTIONS = {
  UNIDIRECTIONAL: 'unidirectional',
  BIDIRECTIONAL: 'bidirectional',
  REFLEXIVE: 'reflexive'
};

const RELATIONSHIP_TYPE_DESCRIPTIONS = {
  [RELATIONSHIP_TYPES.HIERARCHICAL]: 'Иерархическая связь',
  [RELATIONSHIP_TYPES.CAUSAL]: 'Причинно-следственная связь',
  [RELATIONSHIP_TYPES.DIALECTICAL]: 'Диалектическая связь',
  [RELATIONSHIP_TYPES.CORRELATIONAL]: 'Корреляционная связь',
  [RELATIONSHIP_TYPES.DISJUNCTIVE]: 'Дизъюнктивная связь',
  [RELATIONSHIP_TYPES.CONJUNCTIVE]: 'Конъюнктивная связь',
  [RELATIONSHIP_TYPES.CONTRADICTION]: 'Противоречие',
  [RELATIONSHIP_TYPES.COMPLEMENTARY]: 'Дополнительность',
  [RELATIONSHIP_TYPES.EMERGENCE]: 'Эмерджентность',
  [RELATIONSHIP_TYPES.NECESSARY_CONDITION]: 'Необходимое условие',
  [RELATIONSHIP_TYPES.SUFFICIENT_CONDITION]: 'Достаточное условие',
  [RELATIONSHIP_TYPES.IDENTITY]: 'Тождество',
  [RELATIONSHIP_TYPES.ANALOGY]: 'Аналогия',
  [RELATIONSHIP_TYPES.IMPLEMENTATION]: 'Реализация',
  [RELATIONSHIP_TYPES.INSTANTIATION]: 'Конкретизация',
  [RELATIONSHIP_TYPES.GENERALIZATION]: 'Обобщение',
  [RELATIONSHIP_TYPES.PART_WHOLE]: 'Часть-целое',
  [RELATIONSHIP_TYPES.MEANS_END]: 'Средство-цель',
  [RELATIONSHIP_TYPES.DEDUCTIVE]: 'Дедуктивная связь',
  [RELATIONSHIP_TYPES.INDUCTIVE]: 'Индуктивная связь',
  [RELATIONSHIP_TYPES.ABDUCTIVE]: 'Абдуктивная связь',
  [RELATIONSHIP_TYPES.TEMPORAL]: 'Временная связь',
  [RELATIONSHIP_TYPES.CONCEPTUAL]: 'Концептуальная связь',
  [RELATIONSHIP_TYPES.DEFINITIONAL]: 'Определяющая связь',
  [RELATIONSHIP_TYPES.MANIFESTATION]: 'Выражение',
  [RELATIONSHIP_TYPES.FOUNDATIONAL]: 'Основание',
  [RELATIONSHIP_TYPES.RECOGNITION]: 'Понимание',
  [RELATIONSHIP_TYPES.REFLEXION]: 'Мышление',
  [RELATIONSHIP_TYPES.DEVELOPMENT]: 'Развитие'
};

/**
 * Проверяет, является ли строка допустимым типом связи
 */
function isValidRelationshipType(type) {
  return Object.values(RELATIONSHIP_TYPES).includes(type);
}

/**
 * Проверяет, является ли строка допустимым направлением связи
 */
function isValidRelationshipDirection(direction) {
  return Object.values(RELATIONSHIP_DIRECTIONS).includes(direction);
}

/**
 * Получает описание типа связи
 */
function getRelationshipTypeDescription(type) {
  return RELATIONSHIP_TYPE_DESCRIPTIONS[type] || 'Неизвестный тип связи';
}

module.exports = {
  RELATIONSHIP_TYPES,
  RELATIONSHIP_DIRECTIONS,
  RELATIONSHIP_TYPE_DESCRIPTIONS,
  isValidRelationshipType,
  isValidRelationshipDirection,
  getRelationshipTypeDescription
};