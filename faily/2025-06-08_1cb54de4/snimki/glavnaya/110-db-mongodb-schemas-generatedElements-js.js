/**
 * MongoDB Schema: Generated Elements
 * Коллекция для хранения новых элементов (категорий и типов связей),
 * сгенерированных Claude и требующих одобрения
 * 
 * Коллекция: generatedElements
 */

module.exports = {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      title: 'Generated Elements Schema',
      required: [
        'element_id',
        'concept_id',
        'element_type',
        'element_name',
        'is_new',
        'is_approved',
        'created_at',
        'generation_context'
      ],
      properties: {
        _id: {
          bsonType: 'objectId',
          description: 'MongoDB ID документа'
        },
        element_id: {
          bsonType: 'string',
          pattern: '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$',
          description: 'UUID сгенерированного элемента'
        },
        concept_id: {
          bsonType: 'string',
          pattern: '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$',
          description: 'UUID концепции, для которой генерировался элемент'
        },
        element_type: {
          bsonType: 'string',
          enum: ['category', 'relationship_type'],
          description: 'Тип элемента'
        },
        element_name: {
          bsonType: 'string',
          minLength: 2,
          maxLength: 100,
          description: 'Название элемента'
        },
        element_details: {
          bsonType: 'object',
          properties: {
            // Для категорий
            category_definition: {
              bsonType: 'string',
              description: 'Определение категории (для типа category)'
            },
            category_type: {
              bsonType: 'string',
              enum: [
                'ontological',
                'epistemological',
                'axiological',
                'ethical',
                'aesthetic',
                'metaphysical',
                'logical',
                'practical',
                'political',
                'theological',
                'anthropological',
                'social',
                'linguistic',
                'phenomenological',
                'existential',
                'analytical',
                'hermeneutical',
                'cross_disciplinary'
              ],
              description: 'Тип категории (для типа category)'
            },
            // Для типов связей
            relationship_direction: {
              bsonType: 'string',
              enum: ['unidirectional', 'bidirectional', 'reflexive'],
              description: 'Направленность связи (для типа relationship_type)'
            },
            relationship_description: {
              bsonType: 'string',
              description: 'Описание типа связи (для типа relationship_type)'
            },
            typical_usage: {
              bsonType: 'string',
              description: 'Типичное использование элемента'
            },
            examples: {
              bsonType: 'array',
              items: {
                bsonType: 'string'
              },
              description: 'Примеры использования'
            }
          },
          description: 'Детали элемента в зависимости от типа'
        },
        is_new: {
          bsonType: 'bool',
          description: 'Является ли элемент новым (не существовал в базе)'
        },
        is_approved: {
          bsonType: 'bool',
          description: 'Одобрен ли элемент для добавления в шаблоны'
        },
        is_rejected: {
          bsonType: 'bool',
          description: 'Отклонен ли элемент'
        },
        approval_details: {
          bsonType: 'object',
          properties: {
            approved_by: {
              bsonType: 'string',
              pattern: '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$',
              description: 'ID пользователя, одобрившего элемент'
            },
            approved_at: {
              bsonType: 'date',
              description: 'Дата одобрения'
            },
            rejection_reason: {
              bsonType: 'string',
              description: 'Причина отклонения (если отклонен)'
            },
            modified_before_approval: {
              bsonType: 'bool',
              description: 'Был ли элемент изменен перед одобрением'
            },
            modifications: {
              bsonType: 'object',
              properties: {
                original_name: {
                  bsonType: 'string',
                  description: 'Оригинальное название'
                },
                original_definition: {
                  bsonType: 'string',
                  description: 'Оригинальное определение'
                },
                modification_reason: {
                  bsonType: 'string',
                  description: 'Причина модификации'
                }
              },
              description: 'Внесенные изменения'
            }
          },
          description: 'Детали процесса одобрения'
        },
        generation_context: {
          bsonType: 'object',
          required: ['source_operation', 'claude_interaction_id'],
          properties: {
            source_operation: {
              bsonType: 'string',
              enum: [
                'graph_from_theses',
                'synthesis',
                'evolution',
                'graph_enrichment',
                'category_suggestion',
                'relationship_suggestion'
              ],
              description: 'Операция, в рамках которой был сгенерирован элемент'
            },
            claude_interaction_id: {
              bsonType: 'string',
              pattern: '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$',
              description: 'ID взаимодействия с Claude'
            },
            source_theses: {
              bsonType: 'array',
              items: {
                bsonType: 'string'
              },
              description: 'ID тезисов, из которых был извлечен элемент'
            },
            parent_concepts: {
              bsonType: 'array',
              items: {
                bsonType: 'string',
                pattern: '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$'
              },
              description: 'ID родительских концепций (для синтеза)'
            },
            generation_prompt: {
              bsonType: 'string',
              description: 'Промпт, использованный для генерации'
            }
          },
          description: 'Контекст генерации элемента'
        },
        usage_in_graph: {
          bsonType: 'object',
          properties: {
            // Для категорий
            used_in_categories: {
              bsonType: 'array',
              items: {
                bsonType: 'object',
                properties: {
                  category_id: {
                    bsonType: 'string',
                    description: 'ID категории в графе'
                  },
                  usage_context: {
                    bsonType: 'string',
                    description: 'Контекст использования'
                  }
                }
              },
              description: 'Где используется в графе (для категорий)'
            },
            // Для типов связей
            used_in_relationships: {
              bsonType: 'array',
              items: {
                bsonType: 'object',
                properties: {
                  relationship_id: {
                    bsonType: 'string',
                    description: 'ID связи в графе'
                  },
                  from_category: {
                    bsonType: 'string',
                    description: 'Исходная категория'
                  },
                  to_category: {
                    bsonType: 'string',
                    description: 'Целевая категория'
                  }
                }
              },
              description: 'Где используется в графе (для типов связей)'
            }
          },
          description: 'Информация об использовании в графе'
        },
        similarity_analysis: {
          bsonType: 'object',
          properties: {
            similar_existing_elements: {
              bsonType: 'array',
              items: {
                bsonType: 'object',
                properties: {
                  element_name: {
                    bsonType: 'string',
                    description: 'Название похожего элемента'
                  },
                  similarity_score: {
                    bsonType: 'double',
                    minimum: 0,
                    maximum: 1,
                    description: 'Оценка схожести'
                  },
                  difference_explanation: {
                    bsonType: 'string',
                    description: 'Объяснение различий'
                  }
                }
              },
              description: 'Похожие существующие элементы'
            },
            uniqueness_justification: {
              bsonType: 'string',
              description: 'Обоснование уникальности элемента'
            }
          },
          description: 'Анализ схожести с существующими элементами'
        },
        philosophical_justification: {
          bsonType: 'string',
          description: 'Философское обоснование необходимости элемента'
        },
        potential_applications: {
          bsonType: 'array',
          items: {
            bsonType: 'object',
            properties: {
              concept_area: {
                bsonType: 'string',
                description: 'Область концепций'
              },
              use_cases: {
                bsonType: 'array',
                items: {
                  bsonType: 'string'
                },
                description: 'Случаи использования'
              }
            }
          },
          description: 'Потенциальные применения элемента'
        },
        quality_assessment: {
          bsonType: 'object',
          properties: {
            clarity_score: {
              bsonType: 'double',
              minimum: 0,
              maximum: 1,
              description: 'Оценка ясности определения'
            },
            necessity_score: {
              bsonType: 'double',
              minimum: 0,
              maximum: 1,
              description: 'Оценка необходимости'
            },
            consistency_score: {
              bsonType: 'double',
              minimum: 0,
              maximum: 1,
              description: 'Оценка согласованности с существующими элементами'
            },
            overall_quality: {
              bsonType: 'string',
              enum: ['poor', 'fair', 'good', 'excellent'],
              description: 'Общая оценка качества'
            }
          },
          description: 'Оценка качества элемента'
        },
        review_notes: {
          bsonType: 'array',
          items: {
            bsonType: 'object',
            properties: {
              reviewer_id: {
                bsonType: 'string',
                pattern: '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$',
                description: 'ID рецензента'
              },
              note: {
                bsonType: 'string',
                description: 'Заметка рецензента'
              },
              created_at: {
                bsonType: 'date',
                description: 'Дата создания заметки'
              }
            }
          },
          description: 'Заметки рецензентов'
        },
        template_id: {
          bsonType: 'string',
          pattern: '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$',
          description: 'ID созданного шаблона (после одобрения)'
        },
        created_at: {
          bsonType: 'date',
          description: 'Дата создания'
        },
        updated_at: {
          bsonType: 'date',
          description: 'Дата последнего обновления'
        }
      }
    }
  },
  
  indexes: [
    {
      name: 'element_id_unique',
      key: { element_id: 1 },
      unique: true
    },
    {
      name: 'concept_id_index',
      key: { concept_id: 1 }
    },
    {
      name: 'element_type_index',
      key: { element_type: 1 }
    },
    {
      name: 'element_name_index',
      key: { element_name: 1 }
    },
    {
      name: 'is_new_is_approved_index',
      key: { is_new: 1, is_approved: 1 }
    },
    {
      name: 'source_operation_index',
      key: { 'generation_context.source_operation': 1 }
    },
    {
      name: 'claude_interaction_id_index',
      key: { 'generation_context.claude_interaction_id': 1 }
    },
    {
      name: 'created_at_index',
      key: { created_at: -1 }
    },
    {
      name: 'approval_status_index',
      key: { is_approved: 1, is_rejected: 1 }
    },
    {
      name: 'template_id_index',
      key: { template_id: 1 }
    }
  ]
};
