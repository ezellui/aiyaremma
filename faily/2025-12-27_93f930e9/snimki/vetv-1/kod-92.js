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

// Индексы для коллекции HistoricalContexts
db.historical_contexts.createIndex({ concept_id: 1 });
db.historical_contexts.createIndex({ created_at: -1 });

// Индексы для коллекции PracticalApplications
db.practical_applications.createIndex({ concept_id: 1 });
db.practical_applications.createIndex({ 'domains.name': 1 });
db.practical_applications.createIndex({ created_at: -1 });

// Индексы для коллекции ConceptEvolutions
db.concept_evolutions.createIndex({ concept_id: 1 });
db.concept_evolutions.createIndex({ created_at: -1 });

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
        created_at: {
          bsonType: 'date',
          description: 'Дата создания'
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
        element_type: {
          enum: ['category', 'relationship_type'],
          description: 'Тип элемента'
        },
        element_name: {
          bsonType: 'string',
          description: 'Название элемента'
        },
        is_new: {
          bsonType: 'bool',
          description: 'Флаг нового элемента'
        },
        is_approved: {
          bsonType: 'bool',
          description: 'Флаг одобрения'
        }
      }
    }
  }
});

print('MongoDB инициализация завершена успешно');