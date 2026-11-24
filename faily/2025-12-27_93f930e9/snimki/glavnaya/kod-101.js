/**
 * Инициализация MongoDB для платформы философских концепций
 */

// Подключение к базе данных
db = db.getSiblingDB('philos_concepts');

print('Создание коллекций MongoDB...');

// Создание коллекций с валидацией схемы

// Коллекция тезисов
db.createCollection('theses', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['concept_id', 'type', 'content', 'created_at'],
      properties: {
        thesis_id: {
          bsonType: 'objectId',
          description: 'Уникальный идентификатор тезиса'
        },
        concept_id: {
          bsonType: 'string',
          description: 'UUID концепции из PostgreSQL'
        },
        type: {
          bsonType: 'string',
          enum: ['ontological', 'epistemological', 'axiological', 'ethical', 'aesthetic', 'metaphysical', 'logical', 'practical', 'political'],
          description: 'Тип тезиса'
        },
        content: {
          bsonType: 'string',
          description: 'Текст тезиса'
        },
        related_categories: {
          bsonType: 'array',
          items: {
            bsonType: 'string'
          },
          description: 'Массив UUID связанных категорий'
        },
        style: {
          bsonType: 'string',
          enum: ['academic', 'popular', 'aphoristic'],
          description: 'Стиль тезиса'
        },
        generation_parameters: {
          bsonType: 'object',
          description: 'Параметры генерации тезиса'
        },
        created_at: {
          bsonType: 'date',
          description: 'Дата создания'
        },
        parent_theses: {
          bsonType: 'array',
          items: {
            bsonType: 'objectId'
          },
          description: 'Родительские тезисы для синтезированных'
        }
      }
    }
  }
});

// Индексы для theses
db.theses.createIndex({ concept_id: 1 });
db.theses.createIndex({ type: 1 });
db.theses.createIndex({ created_at: -1 });
db.theses.createIndex({ 'related_categories': 1 });

print('Коллекция theses создана');

// Коллекция описаний категорий
db.createCollection('category_descriptions', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['category_id', 'created_at'],
      properties: {
        category_id: {
          bsonType: 'string',
          description: 'UUID категории из Neo4j'
        },
        detailed_description: {
          bsonType: 'string',
          description: 'Детальное описание категории'
        },
        alternative_interpretations: {
          bsonType: 'array',
          items: {
            bsonType: 'string'
          }
        },
        historical_analogues: {
          bsonType: 'array',
          items: {
            bsonType: 'object',
            properties: {
              analogue_name: { bsonType: 'string' },
              philosopher: { bsonType: 'string' },
              tradition: { bsonType: 'string' },
              description: { bsonType: 'string' }
            }
          }
        },
        related_concepts: {
          bsonType: 'array'
        },
        claude_generation_id: {
          bsonType: 'string'
        },
        created_at: {
          bsonType: 'date'
        },
        last_modified: {
          bsonType: 'date'
        }
      }
    }
  }
});

db.category_descriptions.createIndex({ category_id: 1 });
db.category_descriptions.createIndex({ created_at: -1 });

print('Коллекция category_descriptions создана');

// Коллекция описаний связей
db.createCollection('relationship_descriptions', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['relationship_id', 'created_at'],
      properties: {
        relationship_id: {
          bsonType: 'string',
          description: 'UUID связи из Neo4j'
        },
        philosophical_foundation: {
          bsonType: 'string'
        },
        counterarguments: {
          bsonType: 'array',
          items: {
            bsonType: 'string'
          }
        },
        analogues: {
          bsonType: 'array'
        },
        claude_generation_id: {
          bsonType: 'string'
        },
        created_at: {
          bsonType: 'date'
        }
      }
    }
  }
});

db.relationship_descriptions.createIndex({ relationship_id: 1 });

print('Коллекция relationship_descriptions создана');

// Коллекция сгенерированных элементов (для валидации)
db.createCollection('generated_elements', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['concept_id', 'element_type', 'element_name', 'is_new', 'created_at'],
      properties: {
        concept_id: {
          bsonType: 'string'
        },
        generation_context: {
          bsonType: 'string',
          enum: ['thesis_to_graph', 'synthesis', 'evolution']
        },
        element_type: {
          bsonType: 'string',
          enum: ['category', 'relationship_type']
        },
        element_name: {
          bsonType: 'string'
        },
        element_definition: {
          bsonType: 'string'
        },
        is_new: {
          bsonType: 'bool'
        },
        is_approved: {
          bsonType: 'bool',
          description: 'Флаг одобрения пользователем'
        },
        claude_generation_id: {
          bsonType: 'string'
        },
        created_at: {
          bsonType: 'date'
        },
        approved_at: {
          bsonType: 'date'
        },
        approved_by: {
          bsonType: 'string'
        }
      }
    }
  }
});

db.generated_elements.createIndex({ concept_id: 1 });
db.generated_elements.createIndex({ is_new: 1, is_approved: 1 });
db.generated_elements.createIndex({ element_type: 1 });

print('Коллекция generated_elements создана');

// Коллекция анализов концепций
db.createCollection('concept_analyses', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['concept_id', 'analysis_type', 'content', 'created_at'],
      properties: {
        concept_id: {
          bsonType: 'string'
        },
        analysis_type: {
          bsonType: 'string',
          enum: ['critical', 'historical', 'practical', 'comparative', 'origin', 'evolution', 'name']
        },
        content: {
          bsonType: 'string'
        },
        generation_parameters: {
          bsonType: 'object'
        },
        claude_generation_id: {
          bsonType: 'string'
        },
        created_at: {
          bsonType: 'date'
        }
      }
    }
  }
});

db.concept_analyses.createIndex({ concept_id: 1 });
db.concept_analyses.createIndex({ analysis_type: 1 });
db.concept_analyses.createIndex({ created_at: -1 });

print('Коллекция concept_analyses создана');

// Коллекция диалогов
db.createCollection('dialogues', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['concept_ids', 'topic', 'content', 'generated_at'],
      properties: {
        concept_ids: {
          bsonType: 'array',
          items: {
            bsonType: 'string'
          },
          minItems: 2
        },
        topic: {
          bsonType: 'string'
        },
        content: {
          bsonType: 'string'
        },
        parameters: {
          bsonType: 'object',
          properties: {
            style: { bsonType: 'string' },
            format: { bsonType: 'string' },
            focus: { bsonType: 'string' }
          }
        },
        discussion_points: {
          bsonType: 'array'
        },
        arguments: {
          bsonType: 'array'
        },
        convergence_points: {
          bsonType: 'array'
        },
        irreconcilable_differences: {
          bsonType: 'array'
        },
        claude_generation_id: {
          bsonType: 'string'
        },
        generated_at: {
          bsonType: 'date'
        }
      }
    }
  }
});

db.dialogues.createIndex({ concept_ids: 1 });
db.dialogues.createIndex({ topic: 1 });
db.dialogues.createIndex({ generated_at: -1 });

print('Коллекция dialogues создана');

// Коллекция исторических контекстов
db.createCollection('historical_contexts', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['concept_id', 'created_at'],
      properties: {
        concept_id: {
          bsonType: 'string'
        },
        time_period: {
          bsonType: 'string'
        },
        historical_analysis: {
          bsonType: 'string'
        },
        influences: {
          bsonType: 'array'
        },
        contemporaries: {
          bsonType: 'array'
        },
        subsequent_influence: {
          bsonType: 'array'
        },
        name_context_analysis: {
          bsonType: 'string'
        },
        claude_generation_id: {
          bsonType: 'string'
        },
        created_at: {
          bsonType: 'date'
        },
        updated_at: {
          bsonType: 'date'
        }
      }
    }
  }
});

db.historical_contexts.createIndex({ concept_id: 1 });
db.historical_contexts.createIndex({ created_at: -1 });

print('Коллекция historical_contexts создана');

// Коллекция практических применений
db.createCollection('practical_applications', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['concept_id', 'created_at'],
      properties: {
        concept_id: {
          bsonType: 'string'
        },
        domains: {
          bsonType: 'array'
        },
        application_analysis: {
          bsonType: 'string'
        },
        implementation_methods: {
          bsonType: 'array'
        },
        relevance_mappings: {
          bsonType: 'array'
        },
        challenges: {
          bsonType: 'array'
        },
        claude_generation_id: {
          bsonType: 'string'
        },
        created_at: {
          bsonType: 'date'
        },
        updated_at: {
          bsonType: 'date'
        }
      }
    }
  }
});

db.practical_applications.createIndex({ concept_id: 1 });
db.practical_applications.createIndex({ 'domains.name': 1 });

print('Коллекция practical_applications создана');

// Коллекция эволюции концепций
db.createCollection('concept_evolutions', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['concept_id', 'created_at'],
      properties: {
        concept_id: {
          bsonType: 'string'
        },
        directions: {
          bsonType: 'array'
        },
        suggested_changes: {
          bsonType: 'array'
        },
        name_evolution: {
          bsonType: 'object'
        },
        timeframe: {
          bsonType: 'string'
        },
        scientific_areas: {
          bsonType: 'array'
        },
        social_contexts: {
          bsonType: 'array'
        },
        claude_generation_id: {
          bsonType: 'string'
        },
        created_at: {
          bsonType: 'date'
        },
        updated_at: {
          bsonType: 'date'
        }
      }
    }
  }
});

db.concept_evolutions.createIndex({ concept_id: 1 });
db.concept_evolutions.createIndex({ created_at: -1 });

print('Коллекция concept_evolutions создана');

// Создание пользователя БД
db.createUser({
  user: 'philos',
  pwd: 'password', // Изменить в продакшене!
  roles: [
    {
      role: 'readWrite',
      db: 'philos_concepts'
    }
  ]
});

print('Пользователь БД создан');

print('Инициализация MongoDB завершена успешно!');