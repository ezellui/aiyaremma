// claude-service/utils/responseProcessors.js
function processGraphGenerationResponse(claudeResponse) {
  return {
    categories: extractCategories(claudeResponse),
    relationships: extractRelationships(claudeResponse),
    newElements: {
      categories: identifyNewCategories(claudeResponse),
      relationships: identifyNewRelationships(claudeResponse)
    }
  };
}