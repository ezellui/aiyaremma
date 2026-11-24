// graph-service/services/graphService.js
async processClaudeGraphResponse(claudeResponse, conceptId) {
  const { categories, relationships } = parseClaudeResponse(claudeResponse);
  
  // Проверка и создание категорий
  for (const category of categories) {
    const exists = await categoryRepository.findByNameAndConcept(
      category.name, 
      conceptId
    );
    
    if (!exists) {
      await categoryRepository.create({
        concept_id: conceptId,
        name: category.name,
        definition: category.definition,
        // Установить начальные характеристики
        centrality: category.centrality || 0.5,
        certainty: category.certainty || 0.5
      });
    }
  }
  
  // Аналогично для связей
}