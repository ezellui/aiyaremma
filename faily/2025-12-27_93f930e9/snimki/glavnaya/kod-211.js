/**
 * Вспомогательные функции для работы с Neo4j
 */

/**
 * Преобразует Neo4j Integer в обычное число
 */
function toNumber(neo4jInt) {
  if (!neo4jInt) return 0;
  if (typeof neo4jInt === 'number') return neo4jInt;
  return typeof neo4jInt.toNumber === 'function' ? neo4jInt.toNumber() : neo4jInt;
}

/**
 * Преобразует Neo4j DateTime в JavaScript Date
 */
function toDate(neo4jDateTime) {
  if (!neo4jDateTime) return null;
  if (neo4jDateTime instanceof Date) return neo4jDateTime;
  return new Date(neo4jDateTime.toString());
}

/**
 * Преобразует результаты Neo4j в простой объект
 */
function recordToObject(record) {
  const obj = {};
  record.keys.forEach(key => {
    const value = record.get(key);
    
    // Обработка Neo4j типов
    if (value && typeof value === 'object') {
      if (value.constructor.name === 'Integer') {
        obj[key] = toNumber(value);
      } else if (value.constructor.name === 'DateTime') {
        obj[key] = toDate(value);
      } else if (value.properties) {
        // Neo4j Node
        obj[key] = value.properties;
      } else {
        obj[key] = value;
      }
    } else {
      obj[key] = value;
    }
  });
  return obj;
}

/**
 * Преобразует массив записей Neo4j
 */
function recordsToArray(records) {
  return records.map(recordToObject);
}

/**
 * Безопасное выполнение Cypher запроса
 */
async function safeExecute(session, cypher, params = {}) {
  try {
    const result = await session.run(cypher, params);
    return result.records;
  } catch (error) {
    throw new Error(`Neo4j query error: ${error.message}`);
  }
}

/**
 * Пакетная обработка данных для Neo4j
 */
function batchData(data, batchSize = 1000) {
  const batches = [];
  for (let i = 0; i < data.length; i += batchSize) {
    batches.push(data.slice(i, i + batchSize));
  }
  return batches;
}

module.exports = {
  toNumber,
  toDate,
  recordToObject,
  recordsToArray,
  safeExecute,
  batchData
};