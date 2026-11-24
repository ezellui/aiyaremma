// synthesis-service/services/synthesisService.js
async handleNewGraphElements(synthesisResult) {
  // Извлечь новые категории из результата синтеза
  const newCategories = extractNewCategories(synthesisResult);
  
  // Добавить их в базу через Graph Service
  for (const category of newCategories) {
    await graphServiceClient.createCategory(category);
  }
}