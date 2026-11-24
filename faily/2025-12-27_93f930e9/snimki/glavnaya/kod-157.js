/**
 * Модель философской традиции
 */

const { v4: uuidv4 } = require('uuid');

class Tradition {
  constructor(data = {}) {
    this.traditionId = data.tradition_id || uuidv4();
    this.name = data.name;
    this.timePeriod = data.time_period;
    this.keyFigures = data.key_figures || [];
    this.relatedTraditions = data.related_traditions || [];
    this.createdAt = data.created_at || new Date();
  }

  toJSON() {
    return {
      traditionId: this.traditionId,
      name: this.name,
      timePeriod: this.timePeriod,
      keyFigures: this.keyFigures,
      relatedTraditions: this.relatedTraditions,
      createdAt: this.createdAt
    };
  }

  toDB() {
    return {
      tradition_id: this.traditionId,
      name: this.name,
      time_period: this.timePeriod,
      key_figures: this.keyFigures,
      related_traditions: this.relatedTraditions,
      created_at: this.createdAt
    };
  }

  static fromDB(data) {
    return new Tradition(data);
  }
}

module.exports = Tradition;