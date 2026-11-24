class CategoryService {
  // Добавление категории в концепцию
  async addCategory(conceptId: string, data: CategoryCreateDTO): Promise<Category>;
  
  // ... остальные методы ...
  
  // Поиск категорий по традиции/концепции
  async searchCategoriesByTradition(tradition: string): Promise<Category[]>;
  
  // Поиск категорий по философу
  async searchCategoriesByPhilosopher(philosopher: string): Promise<Category[]>;
}