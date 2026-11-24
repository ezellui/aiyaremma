/**
 * Инициализация MongoDB
 */

// Переключаемся на базу данных приложения
db = db.getSiblingDB('philos_concepts');

// Создаем коллекции
db.createCollection('theses');
db.createCollection('category_descriptions');
db.createCollection('relationship_descriptions');
db.createCollection('generated_elements');
db.createCollection('concept_analyses');
db.createCollection('dialogues');
db.createCollection('historical_contexts');
db.createCollection('practical_applications');
db.createCollection('concept_evolutions');

// Индексы для коллекции Theses
db.theses.createIndex({ concept_id: 1 });
db.theses.createIndex({ type: 1 });
db.theses.createIndex({ created_at: -1 });
db.theses.createIndex({ 'related_categories': 1 });

// Индексы для коллекции CategoryDescriptions
db.category_descriptions.createIndex({ category_id: 1 });
db.category_descriptions.createIndex({ created_at: -1 });
db.category_descriptions.createIndex({ claude_generation_id: 1 });

// Индексы для коллекции RelationshipDescriptions
db.relationship_descriptions.createIndex({ relationship_id: 1 });
db.relationship_descriptions.createIndex({ created_at: -1 });
db.relationship_descriptions.createIndex({ claude_generation_id: 1 });

// Индексы для коллекции GeneratedElements
db.generated_elements.createIndex({ concept_id: 1 });
db.generated_elements.createIndex({ is_new: 1, is_approved: 1 });
db.generated_elements.createIndex({ element_type: 1 });
db.generated_elements.createIndex({ created_at: -1 });

// Индексы для коллекции ConceptAnalyses
db.concept_analyses.createIndex({ concept_id: 1 });
db.concept_analyses.createIndex({ analysis_type: 1 });
db.concept_analyses.createIndex({ created_at: -1 });

// Индексы для коллекции Dialogues
db.dialogues.createIndex({ concept_ids: 1 });
db.dialogues.createIndex({ topic: 1 });
db.dialogues.createIndex({ generated_at: -1 });

// Индексы для коллекции HistoricalContexts (расширенные данные)
db.historical_contexts.createIndex({ concept_id: 1 });
db.historical_contexts.createIndex({ created_at: -1 });
db.historical_contexts.createIndex({ 'influences.source': 1 });

// Индексы для коллекции PracticalApplications (расширенные данные)
db.practical_applications.createIndex({ concept_id: 1 });
db.practical_applications.createIndex({ 'domains.name': 1 });
db.practical_applications.createIndex({ created_at: -1 });

// Индексы для коллекции ConceptEvolutions (расширенные данные)
db.concept_evolutions.createIndex({ concept_id: 1 });
db.concept_evolutions.createIndex({ created_at: -1 });
db.concept_evolutions.createIndex({ timeframe: 1 });

// Валидация схем
db.runCommand({
  collMod: 'theses',
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['concept_id', 'type', 'content'],
      properties: {
        concept_id: {
          bsonType: 'string',
          description: 'UUID связи с Concepts в PostgreSQL - обязательное поле'
        },
        type: {
          bsonType: 'string',
          description: 'Тип тезиса - обязательное поле'
        },
        content: {
          bsonType: 'string',
          description: 'Текст тезиса - обязательное поле'
        },
        related_categories: {
          bsonType: 'array',
          description: 'Массив идентификаторов связанных категорий'
        },
        style: {
          bsonType: 'string',
          description: 'Стиль тезиса'
        },
        generation_parameters: {
          bsonType: 'object',
          description: 'Параметры генерации'
        },
        created_at: {
          bsonType: 'date',
          description: 'Дата создания'
        },
        parent_theses: {
          bsonType: 'array',
          description: 'Родительские тезисы'
        }
      }
    }
  }
});

db.runCommand({
  collMod: 'generated_elements',
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['concept_id', 'element_type', 'element_name'],
      properties: {
        concept_id: {
          bsonType: 'string',
          description: 'UUID связи с Concepts'
        },
        generation_context: {
          bsonType: 'string',
          enum: ['thesis_to_graph', 'synthesis', 'evolution'],
          description: 'Контекст генерации'
        },
        element_type: {
          enum: ['category', 'relationship_type'],
          description: 'Тип элемента'
        },
        element_name: {
          bsonType: 'string',
          description: 'Название элемента'
        },
        element_definition: {
          bsonType: 'string',
          description: 'Определение элемента'
        },
        is_new: {
          bsonType: 'bool',
          description: 'Флаг нового элемента'
        },
        is_approved: {
          bsonType: 'bool',
          description: 'Флаг одобрения'
        },
        approved_by: {
          bsonType: 'string',
          description: 'UUID пользователя'
        },
        approved_at: {
          bsonType: 'date',
          description: 'Дата одобрения'
        }
      }
    }
  }
});

// Валидация для historical_contexts (расширенные данные из architecture/document-db-schema.json)
db.runCommand({
  collMod: 'historical_contexts',
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['concept_id'],
      properties: {
        concept_id: {
          bsonType: 'string',
          description: 'UUID связи с Concepts'
        },
        time_period: {
          bsonType: 'string',
          description: 'Временной период'
        },
        historical_analysis: {
          bsonType: 'string',
          description: 'Текст исторического анализа'
        },
        influences: {
          bsonType: 'array',
          description: 'Массив влияний'
        },
        contemporaries: {
          bsonType: 'array',
          description: 'Массив современников'
        },
        subsequent_influence: {
          bsonType: 'array',
          description: 'Массив последующих влияний'
        },
        name_context_analysis: {
          bsonType: 'string',
          description: 'Анализ названия в историческом контексте'
        }
      }
    }
  }
});

print('MongoDB инициализация завершена успешно');
print('Созданы коллекции: theses, category_descriptions, relationship_descriptions, generated_elements, concept_analyses, dialogues, historical_contexts, practical_applications, concept_evolutions');
print('Созданы индексы и валидации схем');