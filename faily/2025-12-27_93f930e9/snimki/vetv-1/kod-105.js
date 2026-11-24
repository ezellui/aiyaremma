/**
 * Правила валидации для различных полей
 */

const VALIDATION_RULES = {
  // Концепции
  concept: {
    name: {
      minLength: 2,
      maxLength: 200
    },
    description: {
      minLength: 10,
      maxLength: 5000
    },
    focus: {
      minLength: 10,
      maxLength: 1000
    }
  },
  
  // Категории
  category: {
    name: {
      minLength: 2,
      maxLength: 100
    },
    definition: {
      minLength: 10,
      maxLength: 2000
    }
  },
  
  // Связи
  relationship: {
    description: {
      minLength: 10,
      maxLength: 2000
    }
  },
  
  // Тезисы
  thesis: {
    content: {
      minLength: 20,
      maxLength: 3000
    }
  },
  
  // Пользователи
  user: {
    username: {
      minLength: 3,
      maxLength: 50,
      pattern: /^[a-zA-Z0-9_-]+$/
    },
    email: {
      pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    },
    password: {
      minLength: 8,
      maxLength: 128,
      requireUppercase: true,
      requireLowercase: true,
      requireNumber: true,
      requireSpecial: false
    }
  },
  
  // UUID
  uuid: {
    pattern: /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i
  },
  
  // Пагинация
  pagination: {
    page: {
      min: 1,
      default: 1
    },
    limit: {
      min: 1,
      max: 100,
      default: 20
    }
  }
};

module.exports = VALIDATION_RULES;