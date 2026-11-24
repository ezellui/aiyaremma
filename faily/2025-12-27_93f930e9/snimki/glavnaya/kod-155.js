/**
 * Модель концепции
 */

const { v4: uuidv4 } = require('uuid');

class Concept {
  constructor(data = {}) {
    this.conceptId = data.concept_id || uuidv4();
    this.creatorId = data.creator_id;
    this.name = data.name;
    this.description = data.description;
    this.isSynthesis = data.is_synthesis || false;
    this.parentConcepts = data.parent_concepts || [];
    this.synthesisMethod = data.synthesis_method || null;
    this.innovationDegree = data.innovation_degree || null;
    this.tags = data.tags || [];
    this.createdAt = data.created_at || new Date();
    this.lastModified = data.last_modified || new Date();
    this.isPublic = data.is_public !== undefined ? data.is_public : true;
  }

  toJSON() {
    return {
      conceptId: this.conceptId,
      creatorId: this.creatorId,
      name: this.name,
      description: this.description,
      isSynthesis: this.isSynthesis,
      parentConcepts: this.parentConcepts,
      synthesisMethod: this.synthesisMethod,
      innovationDegree: this.innovationDegree,
      tags: this.tags,
      createdAt: this.createdAt,
      lastModified: this.lastModified,
      isPublic: this.isPublic
    };
  }

  toDB() {
    return {
      concept_id: this.conceptId,
      creator_id: this.creatorId,
      name: this.name,
      description: this.description,
      is_synthesis: this.isSynthesis,
      parent_concepts: this.parentConcepts,
      synthesis_method: this.synthesisMethod,
      innovation_degree: this.innovationDegree,
      tags: this.tags,
      created_at: this.createdAt,
      last_modified: this.lastModified,
      is_public: this.isPublic
    };
  }

  static fromDB(data) {
    return new Concept(data);
  }
}

module.exports = Concept;