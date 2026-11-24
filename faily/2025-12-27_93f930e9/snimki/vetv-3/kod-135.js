/**
 * Модель философской традиции
 */

const { v4: uuidv4 } = require('uuid');

class Tradition {
  constructor(data = {}) {
    this.traditionId = data.tradition_id || uuidv4();
    this.name = data.name;
    this.timePeriod = data.time_period;
    this.description = data.description;
    this.keyFigures = data.key_figures || [];
    this.relatedTraditions = data.related_traditions || [];
    this.createdAt = data.created_at || new Date();
  }

  toJSON() {
    return {
      traditionId: this.traditionId,
      name: this.name,
      timePeriod: this.timePeriod,
      description: this.description,
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
      description: this.description,
      key_figures: JSON.stringify(this.keyFigures),
      related_traditions: JSON.stringify(this.relatedTraditions),
      created_at: this.createdAt
    };
  }

  static fromDB(data) {
    if (!data) return null;
    
    return new Tradition({
      ...data,
      key_figures: typeof data.key_figures === 'string'
        ? JSON.parse(data.key_figures)
        : data.key_figures,
      related_traditions: typeof data.related_traditions === 'string'
        ? JSON.parse(data.related_traditions)
        : data.related_traditions
    });
  }
}

module.exports = Tradition;