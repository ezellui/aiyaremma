/**
 * Направления связей между категориями
 */

const RELATIONSHIP_DIRECTIONS = {
  UNIDIRECTIONAL: 'unidirectional',    // Однонаправленная
  BIDIRECTIONAL: 'bidirectional',      // Двунаправленная
  REFLEXIVE: 'reflexive'               // Рефлексивная (на себя)
};

// Массив всех направлений
const RELATIONSHIP_DIRECTION_VALUES = Object.values(RELATIONSHIP_DIRECTIONS);

module.exports = {
  RELATIONSHIP_DIRECTIONS,
  RELATIONSHIP_DIRECTION_VALUES
};