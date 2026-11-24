/**
 * Уровни инновационности концепций и их элементов
 */

const INNOVATION_LEVELS = {
  TRADITIONAL: 1,
  REINTERPRETED: 2,
  EXTENDED: 3,
  NOVEL: 4,
  REVOLUTIONARY: 5
};

const INNOVATION_LEVEL_DESCRIPTIONS = {
  [INNOVATION_LEVELS.TRADITIONAL]: 'Традиционное понимание',
  [INNOVATION_LEVELS.REINTERPRETED]: 'Переосмысленное понимание',
  [INNOVATION_LEVELS.EXTENDED]: 'Расширенное понимание',
  [INNOVATION_LEVELS.NOVEL]: 'Новое понимание',
  [INNOVATION_LEVELS.REVOLUTIONARY]: 'Революционное понимание'
};

/**
 * Проверяет, является ли значение допустимым уровнем инновационности
 */
function isValidInnovationLevel(level) {
  return Object.values(INNOVATION_LEVELS).includes(level);
}

/**
 * Получает описание уровня инновационности
 */
function getInnovationLevelDescription(level) {
  return INNOVATION_LEVEL_DESCRIPTIONS[level] || 'Неизвестный уровень инновационности';
}

module.exports = {
  INNOVATION_LEVELS,
  INNOVATION_LEVEL_DESCRIPTIONS,
  isValidInnovationLevel,
  getInnovationLevelDescription
};