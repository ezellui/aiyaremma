/**
 * MongoDB Schema: Dialogues
 * Коллекция для хранения диалогов между философскими концепциями
 * 
 * Коллекция: dialogues
 */

module.exports = {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      title: 'Dialogue Schema',
      required: [
        'dialogue_id',
        'concept_ids',
        'philosophical_question',
        'dialogue_content',
        'created_at',
        'claude_generation_id'
      ],
      properties: {
        _id: {
          bsonType: 'objectId',
          description: 'MongoDB ID документа'
        },
        dialogue_id: {
          bsonType: 'string',
          pattern: '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$',
          description: 'UUID диалога'
        },
        concept_ids: {
          bsonType: 'array',
          minItems: 2,
          items: {
            bsonType: 'string',
            pattern: '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$',
            description: 'UUID концепции-участника'
          },
          description: 'Массив ID концепций, участвующих в диалоге'
        },
        philosophical_question: {
          bsonType: 'string',
          minLength: 10,
          maxLength: 500,
          description: 'Философский вопрос или тема диалога'
        },
        dialogue_content: {
          bsonType: 'string',
          minLength: 100,
          description: 'Полный текст диалога'
        },
        dialogue_structure: {
          bsonType: 'array',
          items: {
            bsonType: 'object',
            required: ['speaker_concept_id', 'text', 'argument_type'],
            properties: {
              speaker_concept_id: {
                bsonType: 'string',
                pattern: '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$',
                description: 'ID концепции-говорящего'
              },
              text: {
                bsonType: 'string',
                minLength: 10,
                description: 'Текст высказывания'
              },
              argument_type: {
                bsonType: 'string',
                enum: [
                  'thesis',
                  'argument',
                  'counterargument',
                  'question',
                  'clarification',
                  'agreement',
                  'disagreement',
                  'synthesis'
                ],
                description: 'Тип аргумента'
              },
              references_theses: {
                bsonType: 'array',
                items: {
                  bsonType: 'string',
                  description: 'ID тезиса, на который ссылается аргумент'
                },
                description: 'Ссылки на тезисы концепций'
              }
            }
          },
          description: 'Структурированное представление диалога'
        },
        discussion_points: {
          bsonType: 'array',
          items: {
            bsonType: 'object',
            required: ['point', 'raised_by', 'importance'],
            properties: {
              point: {
                bsonType: 'string',
                description: 'Ключевой пункт обсуждения'
              },
              raised_by: {
                bsonType: 'string',
                pattern: '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$',
                description: 'ID концепции, поднявшей вопрос'
              },
              importance: {
                bsonType: 'string',
                enum: ['low', 'medium', 'high', 'critical'],
                description: 'Важность пункта обсуждения'
              },
              resolution: {
                bsonType: 'string',
                enum: [
                  'agreed',
                  'disagreed',
                  'partially_agreed',
                  'unresolved',
                  'requires_further_discussion'
                ],
                description: 'Результат обсуждения пункта'
              }
            }
          },
          description: 'Ключевые пункты обсуждения'
        },
        arguments: {
          bsonType: 'array',
          items: {
            bsonType: 'object',
            required: ['argument_id', 'concept_id', 'type', 'content', 'strength'],
            properties: {
              argument_id: {
                bsonType: 'string',
                description: 'ID аргумента'
              },
              concept_id: {
                bsonType: 'string',
                pattern: '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$',
                description: 'ID концепции, выдвинувшей аргумент'
              },
              type: {
                bsonType: 'string',
                enum: [
                  'deductive',
                  'inductive',
                  'abductive',
                  'analogical',
                  'dialectical',
                  'transcendental',
                  'pragmatic',
                  'hermeneutical'
                ],
                description: 'Тип аргументации'
              },
              content: {
                bsonType: 'string',
                description: 'Содержание аргумента'
              },
              strength: {
                bsonType: 'double',
                minimum: 0,
                maximum: 1,
                description: 'Сила аргумента'
              },
              countered_by: {
                bsonType: 'array',
                items: {
                  bsonType: 'string',
                  description: 'ID контраргумента'
                },
                description: 'Массив ID контраргументов'
              }
            }
          },
          description: 'Детальный анализ аргументов'
        },
        convergence_points: {
          bsonType: 'array',
          items: {
            bsonType: 'object',
            required: ['description', 'concepts_agreed'],
            properties: {
              description: {
                bsonType: 'string',
                description: 'Описание точки схождения'
              },
              concepts_agreed: {
                bsonType: 'array',
                items: {
                  bsonType: 'string',
                  pattern: '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$'
                },
                description: 'ID концепций, согласных с этой точкой'
              },
              significance: {
                bsonType: 'string',
                description: 'Значимость точки схождения'
              }
            }
          },
          description: 'Точки согласия между концепциями'
        },
        divergence_points: {
          bsonType: 'array',
          items: {
            bsonType: 'object',
            required: ['description', 'concepts_positions'],
            properties: {
              description: {
                bsonType: 'string',
                description: 'Описание точки расхождения'
              },
              concepts_positions: {
                bsonType: 'object',
                description: 'Позиции концепций по данному вопросу'
              },
              irreconcilable: {
                bsonType: 'bool',
                description: 'Является ли расхождение непримиримым'
              }
            }
          },
          description: 'Точки непримиримых разногласий'
        },
        dialogue_metadata: {
          bsonType: 'object',
          properties: {
            dialogue_type: {
              bsonType: 'string',
              enum: [
                'debate',
                'dialectical',
                'maieutic',
                'collaborative',
                'critical',
                'exploratory'
              ],
              description: 'Тип диалога'
            },
            historical_period: {
              bsonType: 'string',
              description: 'Исторический период (если применимо)'
            },
            moderator_notes: {
              bsonType: 'string',
              description: 'Примечания модератора диалога'
            },
            outcome: {
              bsonType: 'string',
              enum: [
                'consensus_reached',
                'partial_agreement',
                'agree_to_disagree',
                'new_synthesis',
                'unresolved',
                'further_discussion_needed'
              ],
              description: 'Итог диалога'
            }
          },
          description: 'Метаданные диалога'
        },
        claude_generation_id: {
          bsonType: 'string',
          pattern: '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$',
          description: 'ID взаимодействия с Claude API'
        },
        generation_parameters: {
          bsonType: 'object',
          properties: {
            temperature: {
              bsonType: 'double',
              minimum: 0,
              maximum: 2,
              description: 'Параметр температуры для генерации'
            },
            max_tokens: {
              bsonType: 'int',
              minimum: 100,
              description: 'Максимальное количество токенов'
            },
            dialogue_style: {
              bsonType: 'string',
              description: 'Стиль диалога'
            },
            focus_areas: {
              bsonType: 'array',
              items: {
                bsonType: 'string'
              },
              description: 'Области фокуса диалога'
            }
          },
          description: 'Параметры генерации диалога'
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
      name: 'dialogue_id_unique',
      key: { dialogue_id: 1 },
      unique: true
    },
    {
      name: 'concept_ids_index',
      key: { concept_ids: 1 }
    },
    {
      name: 'philosophical_question_text',
      key: { philosophical_question: 'text' }
    },
    {
      name: 'created_at_index',
      key: { created_at: -1 }
    },
    {
      name: 'dialogue_type_index',
      key: { 'dialogue_metadata.dialogue_type': 1 }
    },
    {
      name: 'outcome_index',
      key: { 'dialogue_metadata.outcome': 1 }
    },
    {
      name: 'claude_generation_id_index',
      key: { claude_generation_id: 1 }
    }
  ]
};
