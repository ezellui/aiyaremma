/**
 * Модель связи между категориями
 */

const { v4: uuidv4 } = require('uuid');

class Relationship {
  constructor(data = {}) {
    this.relationshipId = data.relationship_id || data.relationshipId || uuidv4();
    this.conceptId = data.concept_id || data.conceptId;
    this.sourceCategoryId = data.source_category_id || data.sourceCategoryId;
    this.targetCategoryId = data.target_category_id || data.targetCategoryId;
    this.type = data.type;
    this.direction = data.direction || 'bidirectional';
    this.strength = data.strength !== undefined ? data.strength : 1.0;
    this.innovationDegree = data.innovation_degree || data.innovationDegree || 'традиционная';
    this.description = data.description || '';
    this.metadata = data.metadata || {};
    this.createdAt = data.created_at || data.createdAt || new Date();
  }

  toJSON() {
    return {
      relationshipId: this.relationshipId,
      conceptId: this.conceptId,
      sourceCategoryId: this.sourceCategoryId,
      targetCategoryId: this.targetCategoryId,
      type: this.type,
      direction: this.direction,
      strength: this.strength,
      innovationDegree: this.innovationDegree,
      description: this.description,
      metadata: this.metadata,
      createdAt: this.createdAt
    };
  }

  toNeo4j() {
    return {
      relationship_id: this.relationshipId,
      concept_id: this.conceptId,
      type: this.type,
      direction: this.direction,
      strength: this.strength,
      innovation_degree: this.innovationDegree,
      description: this.description,
      created_at: this.createdAt.toISOString()
    };
  }

  static fromNeo4j(relationship, startNode, endNode) {
    return new Relationship({
      relationship_id: relationship.relationship_id,
      concept_id: relationship.concept_id,
      source_category_id: startNode.category_id,
      target_category_id: endNode.category_id,
      type: relationship.type,
      direction: relationship.direction,
      strength: relationship.strength,
      innovation_degree: relationship.innovation_degree,
      description: relationship.description,
      created_at: new Date(relationship.created_at)
    });
  }
}

module.exports = Relationship;