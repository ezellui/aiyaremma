/**
 * Тесты для validators
 */

const {
  validate,
  conceptSchema,
  categorySchema,
  relationshipSchema,
  thesisSchema,
  userRegistrationSchema,
  paginationSchema
} = require('../validators');
const { ValidationError } = require('../errors');

describe('Validators', () => {
  describe('conceptSchema', () => {
    it('должен валидировать корректную концепцию', () => {
      const validConcept = {
        name: 'Тестовая концепция',
        description: 'Описание тестовой концепции для проверки валидации',
        focus: 'Фокус концепции',
        is_synthesis: false
      };
      
      const result = validate(conceptSchema, validConcept);
      expect(result).toHaveProperty('name', validConcept.name);
    });
    
    it('должен выбросить ошибку для короткого названия', () => {
      const invalidConcept = {
        name: 'А',
        description: 'Описание'
      };
      
      expect(() => validate(conceptSchema, invalidConcept))
        .toThrow(ValidationError);
    });
  });
  
  describe('categorySchema', () => {
    it('должен валидировать корректную категорию', () => {
      const validCategory = {
        name: 'Бытие',
        type: 'ontological',
        definition: 'Определение категории бытия',
        concept_id: '123e4567-e89b-12d3-a456-426614174000',
        innovation_degree: 3
      };
      
      const result = validate(categorySchema, validCategory);
      expect(result).toHaveProperty('type', 'ontological');
    });
    
    it('должен выбросить ошибку для неверного типа', () => {
      const invalidCategory = {
        name: 'Бытие',
        type: 'invalid_type',
        concept_id: '123e4567-e89b-12d3-a456-426614174000'
      };
      
      expect(() => validate(categorySchema, invalidCategory))
        .toThrow(ValidationError);
    });
  });
  
  describe('paginationSchema', () => {
    it('должен использовать значения по умолчанию', () => {
      const result = validate(paginationSchema, {});
      expect(result).toHaveProperty('page', 1);
      expect(result).toHaveProperty('limit', 20);
    });
    
    it('должен ограничить максимальное значение limit', () => {
      const data = { limit: 500 };
      
      expect(() => validate(paginationSchema, data))
        .toThrow(ValidationError);
    });
  });
});