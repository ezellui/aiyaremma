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
    this.creationDate = data.creation_date || new Date();
    this.lastModified = data.last_modified || new Date();
    this.isSynthesis = data.is_synthesis || false;
    this.isPublic = data.is_public || false;
    this.isArchived = data.is_archived || false;
    this.parentConcepts = data.parent_concepts || [];
    this.synthesisMethod = data.synthesis_method;
    this.focus = data.focus;
    this.innovationDegree = data.innovation_degree;
    this.historicalContext = data.historical_context;
    this.tags = data.tags || [];
    this.viewsCount = data.views_count || 0;
    this.likesCount = data.likes_count || 0;
  }

  toJSON() {
    return {
      conceptId: this.conceptId,
      creatorId: this.creatorId,
      name: this.name,
      description: this.description,
      creationDate: this.creationDate,
      lastModified: this.lastModified,
      isSynthesis: this.isSynthesis,
      isPublic: this.isPublic,
      isArchived: this.isArchived,
      parentConcepts: this.parentConcepts,
      synthesisMethod: this.synthesisMethod,
      focus: this.focus,
      innovationDegree: this.innovationDegree,
      historicalContext: this.historicalContext,
      tags: this.tags,
      viewsCount: this.viewsCount,
      likesCount: this.likesCount
    };
  }

  toDB() {
    return {
      concept_id: this.conceptId,
      creator_id: this.creatorId,
      name: this.name,
      description: this.description,
      creation_date: this.creationDate,
      last_modified: this.lastModified,
      is_synthesis: this.isSynthesis,
      is_public: this.isPublic,
      is_archived: this.isArchived,
      parent_concepts: JSON.stringify(this.parentConcepts),
      synthesis_method: this.synthesisMethod,
      focus: this.focus,
      innovation_degree: this.innovationDegree,
      historical_context: this.historicalContext,
      tags: JSON.stringify(this.tags),
      views_count: this.viewsCount,
      likes_count: this.likesCount
    };
  }

  static fromDB(data) {
    if (!data) return null;
    
    return new Concept({
      ...data,
      parent_concepts: typeof data.parent_concepts === 'string' 
        ? JSON.parse(data.parent_concepts) 
        : data.parent_concepts,
      tags: typeof data.tags === 'string'
        ? JSON.parse(data.tags)
        : data.tags
    });
  }
}

module.exports = Concept;