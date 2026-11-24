/**
 * Алгоритмы анализа графов
 */

/**
 * Вычисление степени централизации графа
 */
function calculateGraphCentralization(categories) {
  if (categories.length === 0) return 0;

  const maxCentrality = Math.max(...categories.map(c => c.centrality || 0));
  const sumDifferences = categories.reduce((sum, c) => 
    sum + (maxCentrality - (c.centrality || 0)), 0
  );

  const n = categories.length;
  const maxPossibleSum = (n - 1) * (n - 2);

  return maxPossibleSum > 0 ? sumDifferences / maxPossibleSum : 0;
}

/**
 * Вычисление плотности графа
 */
function calculateGraphDensity(categoryCount, relationshipCount) {
  if (categoryCount < 2) return 0;
  
  const maxEdges = (categoryCount * (categoryCount - 1)) / 2;
  return relationshipCount / maxEdges;
}

/**
 * Определение типа графа
 */
function determineGraphType(categoryCount, relationshipCount) {
  const density = calculateGraphDensity(categoryCount, relationshipCount);
  
  if (density > 0.7) return 'плотный';
  if (density > 0.3) return 'средний';
  return 'разреженный';
}

/**
 * Поиск ключевых узлов (по центральности)
 */
function findKeyNodes(categories, topN = 5) {
  return categories
    .sort((a, b) => (b.centrality || 0) - (a.centrality || 0))
    .slice(0, topN)
    .map(c => ({
      categoryId: c.categoryId,
      name: c.name,
      centrality: c.centrality
    }));
}

/**
 * Поиск мостов (связи с высокой важностью для связности)
 */
function findBridges(relationships) {
  // Упрощенная эвристика: связи с низкой силой но соединяющие разные части графа
  return relationships
    .filter(r => r.strength < 0.5)
    .map(r => ({
      relationshipId: r.relationshipId,
      source: r.sourceCategoryId,
      target: r.targetCategoryId,
      strength: r.strength
    }));
}

/**
 * Вычисление коэффициента кластеризации
 */
function calculateClusteringCoefficient(graph) {
  // Упрощенная версия
  let totalCoefficient = 0;
  let validNodes = 0;

  graph.categories.forEach(category => {
    const neighbors = new Set();
    const categoryRels = graph.relationships.filter(r => 
      r.sourceCategoryId === category.categoryId || 
      r.targetCategoryId === category.categoryId
    );

    categoryRels.forEach(rel => {
      const neighborId = rel.sourceCategoryId === category.categoryId 
        ? rel.targetCategoryId 
        : rel.sourceCategoryId;
      neighbors.add(neighborId);
    });

    const k = neighbors.size;
    if (k < 2) return;

    let actualEdges = 0;
    const neighborArray = Array.from(neighbors);
    
    for (let i = 0; i < neighborArray.length; i++) {
      for (let j = i + 1; j < neighborArray.length; j++) {
        const hasEdge = graph.relationships.some(r =>
          (r.sourceCategoryId === neighborArray[i] && r.targetCategoryId === neighborArray[j]) ||
          (r.sourceCategoryId === neighborArray[j] && r.targetCategoryId === neighborArray[i])
        );
        if (hasEdge) actualEdges++;
      }
    }

    const possibleEdges = (k * (k - 1)) / 2;
    if (possibleEdges > 0) {
      totalCoefficient += actualEdges / possibleEdges;
      validNodes++;
    }
  });

  return validNodes > 0 ? totalCoefficient / validNodes : 0;
}

module.exports = {
  calculateGraphCentralization,
  calculateGraphDensity,
  determineGraphType,
  findKeyNodes,
  findBridges,
  calculateClusteringCoefficient
};