/**
 * Модель философа
 */

const { v4: uuidv4 } = require('uuid');

class Philosopher {
  constructor(data = {}) {
    this.philosopherId = data.philosopher_id || uuidv4();
    this.name = data.name;
    this.birthYear = data.birth_year;
    this.deathYear = data.death_year;
    this.description = data.description;
    this.traditions = data.traditions || [];
    this.keyWorks = data.key_works || [];
    this.createdAt = data.created_at || new Date();
  }

  toJSON() {
    return {
      philosopherId: this.philosopherId,
      name: this.name,
      birthYear: this.birthYear,
      deathYear: this.deathYear,
      description: this.description,
      traditions: this.traditions,
      keyWorks: this.keyWorks,
      createdAt: this.createdAt
    };
  }

  toDB() {
    return {
      philosopher_id: this.philosopherId,
      name: this.name,
      birth_year: this.birthYear,
      death_year: this.deathYear,
      description: this.description,
      traditions: JSON.stringify(this.traditions),
      key_works: JSON.stringify(this.keyWorks),
      created_at: this.createdAt
    };
  }

  static fromDB(data) {
    if (!data) return null;
    
    return new Philosopher({
      ...data,
      traditions: typeof data.traditions === 'string'
        ? JSON.parse(data.traditions)
        : data.traditions,
      key_works: typeof data.key_works === 'string'
        ? JSON.parse(data.key_works)
        : data.key_works
    });
  }
}

module.exports = Philosopher;