/**
 * Вспомогательный класс для построения SQL запросов
 */

class QueryBuilder {
  constructor(baseQuery) {
    this.query = baseQuery;
    this.params = [];
    this.paramCount = 0;
  }

  /**
   * Добавляет WHERE условие
   */
  where(condition, value) {
    this.paramCount++;
    
    if (this.query.includes('WHERE')) {
      this.query += ' AND ';
    } else {
      this.query += ' WHERE ';
    }
    
    this.query += condition.replace('?', `$${this.paramCount}`);
    this.params.push(value);
    
    return this;
  }

  /**
   * Добавляет LIKE условие
   */
  whereLike(field, value) {
    return this.where(`${field} ILIKE ?`, `%${value}%`);
  }

  /**
   * Добавляет IN условие
   */
  whereIn(field, values) {
    if (!values || values.length === 0) {
      return this;
    }

    this.paramCount++;
    
    if (this.query.includes('WHERE')) {
      this.query += ' AND ';
    } else {
      this.query += ' WHERE ';
    }
    
    this.query += `${field} = ANY($${this.paramCount})`;
    this.params.push(values);
    
    return this;
  }

  /**
   * Добавляет JSONB contains условие
   */
  whereJsonbContains(field, value) {
    this.paramCount++;
    
    if (this.query.includes('WHERE')) {
      this.query += ' AND ';
    } else {
      this.query += ' WHERE ';
    }
    
    this.query += `${field} @> $${this.paramCount}::jsonb`;
    this.params.push(JSON.stringify(value));
    
    return this;
  }

  /**
   * Добавляет ORDER BY
   */
  orderBy(field, direction = 'ASC') {
    this.query += ` ORDER BY ${field} ${direction}`;
    return this;
  }

  /**
   * Добавляет LIMIT
   */
  limit(value) {
    this.paramCount++;
    this.query += ` LIMIT $${this.paramCount}`;
    this.params.push(value);
    return this;
  }

  /**
   * Добавляет OFFSET
   */
  offset(value) {
    this.paramCount++;
    this.query += ` OFFSET $${this.paramCount}`;
    this.params.push(value);
    return this;
  }

  /**
   * Возвращает готовый запрос и параметры
   */
  build() {
    return {
      text: this.query,
      values: this.params
    };
  }
}

module.exports = QueryBuilder;