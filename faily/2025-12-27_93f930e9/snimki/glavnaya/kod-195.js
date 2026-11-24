/**
 * Модель графа концепции
 */

class Graph {
  constructor(data = {}) {
    this.conceptId = data.conceptId;
    this.conceptName = data.conceptName;
    this.categories = data.categories || [];
    this.relationships = data.relationships || [];
    this.metadata = data.metadata || {};
  }

  toJSON() {
    return {
      conceptId: this.conceptId,
      conceptName: this.conceptName,
      categories: this.categories.map(c => c.toJSON ? c.toJSON() : c),
      relationships: this.relationships.map(r => r.toJSON ? r.toJSON() : r),
      metadata: this.metadata
    };
  }

  /**
   * Получает категорию по ID
   */
  getCategoryById(categoryId) {
    return this.categories.find(c => 
      (c.categoryId || c.category_id) === categoryId
    );
  }

  /**
   * Получает связи категории
   */
  getCategoryRelationships(categoryId) {
    return this.relationships.filter(r => 
      (r.sourceCategoryId || r.source_category_id) === categoryId ||
      (r.targetCategoryId || r.target_category_id) === categoryId
    );
  }

  /**
   * Проверяет наличие категории
   */
  hasCategory(categoryId) {
    return this.categories.some(c => 
      (c.categoryId || c.category_id) === categoryId
    );
  }

  /**
   * Получает количество узлов и рёбер
   */
  getStats() {
    return {
      categoryCount: this.categories.length,
      relationshipCount: this.relationships.length,
      avgCentrality: this.categories.reduce((sum, c) => sum + (c.centrality || 0), 0) / this.categories.length || 0,
      avgStrength: this.relationships.reduce((sum, r) => sum + (r.strength || 0), 0) / this.relationships.length || 0
    };
  }
}

module.exports = Graph;