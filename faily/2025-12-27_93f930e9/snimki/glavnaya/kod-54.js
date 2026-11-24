/**
 * Базовая модель для всех моделей сервиса
 */

const { v4: uuidv4 } = require('uuid');

class BaseModel {
  constructor(data = {}) {
    this.id = data.id || uuidv4();
    this.createdAt = data.created_at || new Date();
    this.updatedAt = data.updated_at || new Date();
  }

  /**
   * Преобразует модель в JSON
   */
  toJSON() {
    return {
      id: this.id,
      createdAt: this.createdAt,
      updatedAt: this.updatedAt
    };
  }

  /**
   * Создает модель из данных БД
   */
  static fromDB(data) {
    return new this(data);
  }

  /**
   * Преобразует модель для сохранения в БД
   */
  toDB() {
    return {
      id: this.id,
      created_at: this.createdAt,
      updated_at: this.updatedAt
    };
  }
}

module.exports = BaseModel;