// migrations/00002_create_indexes.js

// Индексы для коллекции theses
db.theses.createIndex({ concept_id: 1 }, { name: "idx_theses_concept_id" });
db.theses.createIndex({ type: 1 }, { name: "idx_theses_type" });
db.theses.createIndex({ style: 1 }, { name: "idx_theses_style" });
db.theses.createIndex({ created_at: -1 }, { name: "idx_theses_created_at" });
db.theses.createIndex({ tags: 1 }, { name: "idx_theses_tags" });
db.theses.createIndex({ parent_theses: 1 }, { name: "idx_theses_parent_theses" });

// Составной индекс для частых запросов
db.theses.createIndex(
  { concept_id: 1, type: 1 },
  { name: "idx_theses_concept_type" }
);

// Составной индекс для поиска тезисов по стилю и типу
db.theses.createIndex(
  { concept_id: 1, style: 1, type: 1 },
  { name: "idx_theses_concept_style_type" }
);

// Текстовый индекс для поиска по содержанию
db.theses.createIndex(
  { content: "text", tags: "text" },
  { 
    name: "idx_theses_text_search",
    weights: { content: 10, tags: 5 },
    default_language: "russian"
  }
);

// Индексы для коллекции categoryDescriptions
db.categoryDescriptions.createIndex({ category_id: 1 }, { name: "idx_category_desc_category_id" });
db.categoryDescriptions.createIndex({ claude_generation_id: 1 }, { name: "idx_category_desc_claude_id" });
db.categoryDescriptions.createIndex({ created_at: -1 }, { name: "idx_category_desc_created_at" });

// Индекс для поиска описаний по характеристикам категорий
db.categoryDescriptions.createIndex(
  { "category_characteristics.centrality": -1 },
  { name: "idx_category_desc_centrality" }
);

// Текстовый индекс для поиска по описаниям категорий
db.categoryDescriptions.createIndex(
  { detailed_description: "text" },
  { 
    name: "idx_category_desc_text_search",
    default_language: "russian"
  }
);

// Индексы для коллекции relationshipDescriptions
db.relationshipDescriptions.createIndex({ relationship_id: 1 }, { name: "idx_rel_desc_relationship_id" });
db.relationshipDescriptions.createIndex({ relationship_type: 1 }, { name: "idx_rel_desc_type" });
db.relationshipDescriptions.createIndex({ relationship_direction: 1 }, { name: "idx_rel_desc_direction" });
db.relationshipDescriptions.createIndex({ claude_generation_id: 1 }, { name: "idx_rel_desc_claude_id" });

// Индекс для поиска по силе связи
db.relationshipDescriptions.createIndex(
  { "relationship_characteristics.strength": -1 },
  { name: "idx_rel_desc_strength" }
);

// Индексы для коллекции conceptAnalyses
db.conceptAnalyses.createIndex({ concept_id: 1 }, { name: "idx_concept_analyses_concept_id" });
db.conceptAnalyses.createIndex({ analysis_type: 1 }, { name: "idx_concept_analyses_type" });
db.conceptAnalyses.createIndex({ created_at: -1 }, { name: "idx_concept_analyses_created_at" });

// Составной индекс для частых запросов
db.conceptAnalyses.createIndex(
  { concept_id: 1, analysis_type: 1 },
  { name: "idx_concept_analyses_concept_type" }
);

// Индексы для коллекции dialogues
db.dialogues.createIndex({ concept_ids: 1 }, { name: "idx_dialogues_concept_ids" });
db.dialogues.createIndex({ philosophical_question_type: 1 }, { name: "idx_dialogues_question_type" });
db.dialogues.createIndex({ topic: 1 }, { name: "idx_dialogues_topic" });
db.dialogues.createIndex({ generated_at: -1 }, { name: "idx_dialogues_generated_at" });

// Индекс для поиска диалогов по типам аргументации
db.dialogues.createIndex(
  { "dialogue_structure.argument_type": 1 },
  { name: "idx_dialogues_argument_type" }
);

// Текстовый индекс для поиска по диалогам
db.dialogues.createIndex(
  { topic: "text", content: "text" },
  { 
    name: "idx_dialogues_text_search",
    weights: { topic: 10, content: 5 },
    default_language: "russian"
  }
);

// Индексы для коллекции historicalContexts
db.historicalContexts.createIndex({ concept_id: 1 }, { name: "idx_historical_concept_id" });
db.historicalContexts.createIndex({ time_period: 1 }, { name: "idx_historical_time_period" });
db.historicalContexts.createIndex({ created_at: -1 }, { name: "idx_historical_created_at" });

// Индекс для поиска по историческим влияниям
db.historicalContexts.createIndex(
  { "influences.source": 1 },
  { name: "idx_historical_influences" }
);

// Индексы для коллекции practicalApplications
db.practicalApplications.createIndex({ concept_id: 1 }, { name: "idx_practical_concept_id" });
db.practicalApplications.createIndex({ "domains.domain_name": 1 }, { name: "idx_practical_domains" });
db.practicalApplications.createIndex({ created_at: -1 }, { name: "idx_practical_created_at" });

// Индекс для поиска по методам реализации
db.practicalApplications.createIndex(
  { "implementation_methods.method": 1 },
  { name: "idx_practical_implementation_methods" }
);

// Составной индекс для поиска по доменам и релевантности
db.practicalApplications.createIndex(
  { "domains.domain_name": 1, "domains.relevance_score": -1 },
  { name: "idx_practical_domain_relevance" }
);

// Индексы для коллекции conceptEvolutions
db.conceptEvolutions.createIndex({ concept_id: 1 }, { name: "idx_evolution_concept_id" });
db.conceptEvolutions.createIndex({ evolution_directions: 1 }, { name: "idx_evolution_directions" });
db.conceptEvolutions.createIndex({ change_types: 1 }, { name: "idx_evolution_change_types" });
db.conceptEvolutions.createIndex({ created_at: -1 }, { name: "idx_evolution_created_at" });

// Индексы для коллекции syntheses
db.syntheses.createIndex({ concept_id: 1 }, { name: "idx_syntheses_concept_id" });
db.syntheses.createIndex({ parent_concepts: 1 }, { name: "idx_syntheses_parent_concepts" });
db.syntheses.createIndex({ synthesis_type: 1 }, { name: "idx_syntheses_type" });
db.syntheses.createIndex({ compatibility_criteria: 1 }, { name: "idx_syntheses_criteria" });
db.syntheses.createIndex({ innovation_level: -1 }, { name: "idx_syntheses_innovation_level" });
db.syntheses.createIndex({ created_at: -1 }, { name: "idx_syntheses_created_at" });

// Составной индекс для поиска по типу синтеза и уровню инновационности
db.syntheses.createIndex(
  { synthesis_type: 1, innovation_level: -1 },
  { name: "idx_syntheses_type_innovation" }
);

// Создание представлений (views) для часто используемых запросов
db.createView(
  "recentTheses",
  "theses",
  [
    { $sort: { created_at: -1 } },
    { $limit: 100 },
    { $project: { 
      concept_id: 1, 
      type: 1, 
      style: 1,
      content: 1, 
      created_at: 1 
    }}
  ]
);

db.createView(
  "innovativeCategories",
  "categoryDescriptions",
  [
    { $match: { "category_characteristics.innovation_degree": { $gte: 3 } } },
    { $sort: { "category_characteristics.innovation_degree": -1 } },
    { $project: {
      category_id: 1,
      detailed_description: 1,
      innovation_degree: "$category_characteristics.innovation_degree"
    }}
  ]
);

db.createView(
  "practicalApplicationsByDomain",
  "practicalApplications",
  [
    { $unwind: "$domains" },
    { $group: {
      _id: "$domains.domain_name",
      concepts: { $addToSet: "$concept_id" },
      average_relevance: { $avg: "$domains.relevance_score" }
    }},
    { $sort: { average_relevance: -1 } }
  ]
);

db.createView(
  "conceptsBySynthesisType",
  "syntheses",
  [
    { $group: {
      _id: "$synthesis_type",
      count: { $sum: 1 },
      concepts: { $addToSet: "$concept_id" },
      avg_innovation: { $avg: "$innovation_level" }
    }},
    { $sort: { count: -1 } }
  ]
);

// Комментарии к индексам
/*
Индексы спроектированы с учетом следующих паттернов использования:

1. Частые запросы по concept_id - основной способ связи с PostgreSQL
2. Фильтрация по типам (type, style, analysis_type, synthesis_type) - для категоризации контента
3. Сортировка по датам (created_at) - для отображения последних изменений
4. Текстовый поиск - для поиска по содержанию тезисов и диалогов
5. Составные индексы - для оптимизации частых комбинаций фильтров
6. Индексы для поиска по количественным характеристикам - для аналитических запросов

Рекомендации:
- Использовать explain() для анализа планов выполнения запросов
- Мониторить использование индексов через db.collection.stats()
- Периодически пересматривать индексы на основе реальных паттернов использования
*/
