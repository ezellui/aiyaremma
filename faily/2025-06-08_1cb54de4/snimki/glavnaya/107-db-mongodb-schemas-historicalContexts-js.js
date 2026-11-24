/**
 * MongoDB Schema: Historical Contexts
 * Коллекция для хранения исторических контекстов философских концепций
 * 
 * Коллекция: historicalContexts
 */

module.exports = {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      title: 'Historical Context Schema',
      required: [
        'context_id',
        'concept_id',
        'time_period',
        'historical_analysis',
        'created_at',
        'claude_generation_id'
      ],
      properties: {
        _id: {
          bsonType: 'objectId',
          description: 'MongoDB ID документа'
        },
        context_id: {
          bsonType: 'string',
          pattern: '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$',
          description: 'UUID исторического контекста'
        },
        concept_id: {
          bsonType: 'string',
          pattern: '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$',
          description: 'UUID связанной концепции'
        },
        time_period: {
          bsonType: 'object',
          required: ['era', 'start_year', 'end_year'],
          properties: {
            era: {
              bsonType: 'string',
              enum: [
                'ancient',
                'classical',
                'medieval',
                'renaissance',
                'early_modern',
                'modern',
                'contemporary',
                'postmodern'
              ],
              description: 'Историческая эпоха'
            },
            start_year: {
              bsonType: 'int',
              description: 'Начальный год периода'
            },
            end_year: {
              bsonType: 'int',
              description: 'Конечный год периода'
            },
            specific_period: {
              bsonType: 'string',
              description: 'Более точное определение периода'
            }
          },
          description: 'Временной период'
        },
        historical_analysis: {
          bsonType: 'string',
          minLength: 200,
          description: 'Развернутый исторический анализ концепции'
        },
        influences: {
          bsonType: 'array',
          items: {
            bsonType: 'object',
            required: ['source', 'type', 'strength', 'description'],
            properties: {
              source: {
                bsonType: 'object',
                required: ['name', 'type'],
                properties: {
                  name: {
                    bsonType: 'string',
                    description: 'Название источника влияния'
                  },
                  type: {
                    bsonType: 'string',
                    enum: [
                      'philosopher',
                      'school',
                      'movement',
                      'event',
                      'cultural_context',
                      'scientific_discovery',
                      'political_context',
                      'religious_tradition'
                    ],
                    description: 'Тип источника влияния'
                  },
                  philosopher_id: {
                    bsonType: 'string',
                    pattern: '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$',
                    description: 'ID философа (если применимо)'
                  },
                  tradition_id: {
                    bsonType: 'string',
                    pattern: '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$',
                    description: 'ID традиции (если применимо)'
                  }
                }
              },
              type: {
                bsonType: 'string',
                enum: [
                  'direct',
                  'indirect',
                  'reactive',
                  'synthetic',
                  'critical',
                  'transformative'
                ],
                description: 'Тип влияния'
              },
              strength: {
                bsonType: 'double',
                minimum: 0,
                maximum: 1,
                description: 'Сила влияния'
              },
              description: {
                bsonType: 'string',
                description: 'Описание влияния'
              },
              specific_concepts: {
                bsonType: 'array',
                items: {
                  bsonType: 'string'
                },
                description: 'Конкретные концепции или идеи, которые были заимствованы'
              }
            }
          },
          description: 'Источники влияния на концепцию'
        },
        contemporaries: {
          bsonType: 'array',
          items: {
            bsonType: 'object',
            required: ['name', 'relationship', 'interaction_type'],
            properties: {
              name: {
                bsonType: 'string',
                description: 'Имя современника'
              },
              philosopher_id: {
                bsonType: 'string',
                pattern: '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$',
                description: 'ID философа (если есть в базе)'
              },
              relationship: {
                bsonType: 'string',
                enum: [
                  'colleague',
                  'student',
                  'teacher',
                  'correspondent',
                  'critic',
                  'rival',
                  'collaborator',
                  'influenced_by',
                  'influenced'
                ],
                description: 'Тип отношений'
              },
              interaction_type: {
                bsonType: 'string',
                enum: [
                  'direct_personal',
                  'correspondence',
                  'debate',
                  'collaboration',
                  'criticism',
                  'indirect_through_works'
                ],
                description: 'Тип взаимодействия'
              },
              shared_concepts: {
                bsonType: 'array',
                items: {
                  bsonType: 'string'
                },
                description: 'Общие концепции или темы'
              },
              divergent_views: {
                bsonType: 'array',
                items: {
                  bsonType: 'string'
                },
                description: 'Различающиеся взгляды'
              }
            }
          },
          description: 'Современники и их взаимоотношения'
        },
        subsequent_influence: {
          bsonType: 'array',
          items: {
            bsonType: 'object',
            required: ['target', 'period', 'type', 'description'],
            properties: {
              target: {
                bsonType: 'object',
                required: ['name', 'type'],
                properties: {
                  name: {
                    bsonType: 'string',
                    description: 'Название объекта влияния'
                  },
                  type: {
                    bsonType: 'string',
                    enum: [
                      'philosopher',
                      'school',
                      'movement',
                      'discipline',
                      'cultural_phenomenon',
                      'political_ideology',
                      'scientific_paradigm'
                    ],
                    description: 'Тип объекта влияния'
                  }
                }
              },
              period: {
                bsonType: 'object',
                properties: {
                  start_year: {
                    bsonType: 'int'
                  },
                  end_year: {
                    bsonType: 'int'
                  },
                  description: {
                    bsonType: 'string'
                  }
                },
                description: 'Период влияния'
              },
              type: {
                bsonType: 'string',
                enum: [
                  'foundational',
                  'transformative',
                  'critical',
                  'synthetic',
                  'inspirational',
                  'methodological'
                ],
                description: 'Тип последующего влияния'
              },
              description: {
                bsonType: 'string',
                description: 'Описание влияния'
              },
              specific_developments: {
                bsonType: 'array',
                items: {
                  bsonType: 'string'
                },
                description: 'Конкретные развития идей'
              }
            }
          },
          description: 'Последующее влияние концепции'
        },
        cultural_context: {
          bsonType: 'object',
          properties: {
            geographical_location: {
              bsonType: 'string',
              description: 'Географическое расположение'
            },
            political_system: {
              bsonType: 'string',
              description: 'Политическая система'
            },
            economic_conditions: {
              bsonType: 'string',
              description: 'Экономические условия'
            },
            social_structure: {
              bsonType: 'string',
              description: 'Социальная структура'
            },
            religious_context: {
              bsonType: 'string',
              description: 'Религиозный контекст'
            },
            intellectual_climate: {
              bsonType: 'string',
              description: 'Интеллектуальный климат эпохи'
            },
            major_events: {
              bsonType: 'array',
              items: {
                bsonType: 'object',
                properties: {
                  event: {
                    bsonType: 'string',
                    description: 'Название события'
                  },
                  year: {
                    bsonType: 'int',
                    description: 'Год события'
                  },
                  impact: {
                    bsonType: 'string',
                    description: 'Влияние на развитие концепции'
                  }
                }
              },
              description: 'Важные исторические события'
            }
          },
          description: 'Культурный контекст эпохи'
        },
        evolution_timeline: {
          bsonType: 'array',
          items: {
            bsonType: 'object',
            required: ['period', 'description', 'key_developments'],
            properties: {
              period: {
                bsonType: 'string',
                description: 'Период развития'
              },
              description: {
                bsonType: 'string',
                description: 'Описание этапа эволюции'
              },
              key_developments: {
                bsonType: 'array',
                items: {
                  bsonType: 'string'
                },
                description: 'Ключевые развития в этот период'
              },
              key_figures: {
                bsonType: 'array',
                items: {
                  bsonType: 'string'
                },
                description: 'Ключевые фигуры периода'
              }
            }
          },
          description: 'Временная линия эволюции концепции'
        },
        historical_significance: {
          bsonType: 'object',
          properties: {
            paradigm_shift: {
              bsonType: 'bool',
              description: 'Представляла ли концепция смену парадигмы'
            },
            lasting_impact: {
              bsonType: 'string',
              enum: ['minimal', 'moderate', 'significant', 'revolutionary'],
              description: 'Долгосрочное влияние'
            },
            contemporary_relevance: {
              bsonType: 'string',
              description: 'Современная релевантность'
            },
            key_contributions: {
              bsonType: 'array',
              items: {
                bsonType: 'string'
              },
              description: 'Ключевые вклады в философию'
            }
          },
          description: 'Историческая значимость концепции'
        },
        claude_generation_id: {
          bsonType: 'string',
          pattern: '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$',
          description: 'ID взаимодействия с Claude API'
        },
        generation_parameters: {
          bsonType: 'object',
          properties: {
            historical_depth: {
              bsonType: 'string',
              enum: ['surface', 'moderate', 'deep', 'comprehensive'],
              description: 'Глубина исторического анализа'
            },
            focus_areas: {
              bsonType: 'array',
              items: {
                bsonType: 'string'
              },
              description: 'Области фокуса анализа'
            },
            sources_consulted: {
              bsonType: 'array',
              items: {
                bsonType: 'string'
              },
              description: 'Консультированные источники'
            }
          },
          description: 'Параметры генерации исторического контекста'
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
      name: 'context_id_unique',
      key: { context_id: 1 },
      unique: true
    },
    {
      name: 'concept_id_index',
      key: { concept_id: 1 }
    },
    {
      name: 'time_period_index',
      key: { 'time_period.era': 1, 'time_period.start_year': 1 }
    },
    {
      name: 'influences_source_index',
      key: { 'influences.source.name': 1 }
    },
    {
      name: 'contemporaries_name_index',
      key: { 'contemporaries.name': 1 }
    },
    {
      name: 'historical_significance_index',
      key: { 'historical_significance.lasting_impact': 1 }
    },
    {
      name: 'created_at_index',
      key: { created_at: -1 }
    },
    {
      name: 'claude_generation_id_index',
      key: { claude_generation_id: 1 }
    }
  ]
};
