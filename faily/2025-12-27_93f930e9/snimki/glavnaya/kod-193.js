/**
 * Модель категории
 */

const { v4: uuidv4 } = require('uuid');

class Category {
  constructor(data = {}) {
    this.categoryId = data.category_id || data.categoryId || uuidv4();
    this.conceptId = data.concept_id || data.conceptId;
    this.name = data.name;
    this.definition = data.definition;
    this.type = data.type;
    this.innovationDegree = data.innovation_degree || data.innovationDegree || 'традиционная';
    this.certainty = data.certainty !== undefined ? data.certainty : 1.0;
    this.centrality = data.centrality || 0;
    this.metadata = data.metadata || {};
    this.createdAt = data.created_at || data.createdAt || new Date();
    this.lastModified = data.last_modified || data.lastModified || new Date();
  }

  toJSON() {
    return {
      categoryId: this.categoryId,
      conceptId: this.conceptId,
      name: this.name,
      definition: this.definition,
      type: this.type,
      innovationDegree: this.innovationDegree,
      certainty: this.certainty,
      centrality: this.centrality,
      metadata: this.metadata,
      createdAt: this.createdAt,
      lastModified: this.lastModified
    };
  }

  toNeo4j() {
    return {
      category_id: this.categoryId,
      concept_id: this.conceptId,
      name: this.name,
      definition: this.definition,
      type: this.type,
      innovation_degree: this.innovationDegree,
      certainty: this.certainty,
      centrality: this.centrality,
      created_at: this.createdAt.toISOString()
    };
  }

  static fromNeo4j(node) {
    return new Category({
      category_id: node.category_id,
      concept_id: node.concept_id,
      name: node.name,
      definition: node.definition,
      type: node.type,
      innovation_degree: node.innovation_degree,
      certainty: node.certainty,
      centrality: node.centrality,
      created_at: new Date(node.created_at)
    });
  }
}

module.exports = Category;