/**
 * MongoDB Schema: Practical Applications
 * Коллекция для хранения практических применений философских концепций
 * 
 * Коллекция: practicalApplications
 */

module.exports = {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      title: 'Practical Application Schema',
      required: [
        'application_id',
        'concept_id',
        'domains',
        'application_analysis',
        'created_at',
        'claude_generation_id'
      ],
      properties: {
        _id: {
          bsonType: 'objectId',
          description: 'MongoDB ID документа'
        },
        application_id: {
          bsonType: 'string',
          pattern: '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$',
          description: 'UUID практического применения'
        },
        concept_id: {
          bsonType: 'string',
          pattern: '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$',
          description: 'UUID связанной концепции'
        },
        domains: {
          bsonType: 'array',
          minItems: 1,
          items: {
            bsonType: 'object',
            required: ['domain_type', 'name', 'relevance_score', 'applications'],
            properties: {
              domain_type: {
                bsonType: 'string',
                enum: [
                  'education',
                  'ethics',
                  'politics',
                  'business',
                  'psychology',
                  'healthcare',
                  'technology',
                  'law',
                  'social_work',
                  'environmental',
                  'arts',
                  'personal_development',
                  'community_development',
                  'conflict_resolution',
                  'leadership',
                  'science',
                  'religion'
                ],
                description: 'Тип области применения'
              },
              name: {
                bsonType: 'string',
                description: 'Название конкретной области'
              },
              relevance_score: {
                bsonType: 'double',
                minimum: 0,
                maximum: 1,
                description: 'Оценка релевантности для данной области'
              },
              applications: {
                bsonType: 'array',
                items: {
                  bsonType: 'object',
                  required: ['title', 'description', 'implementation_level'],
                  properties: {
                    title: {
                      bsonType: 'string',
                      description: 'Название применения'
                    },
                    description: {
                      bsonType: 'string',
                      description: 'Описание применения'
                    },
                    implementation_level: {
                      bsonType: 'string',
                      enum: [
                        'theoretical',
                        'experimental',
                        'pilot',
                        'limited_practice',
                        'widespread_practice',
                        'standard_practice'
                      ],
                      description: 'Уровень внедрения'
                    },
                    examples: {
                      bsonType: 'array',
                      items: {
                        bsonType: 'object',
                        properties: {
                          name: {
                            bsonType: 'string',
                            description: 'Название примера'
                          },
                          description: {
                            bsonType: 'string',
                            description: 'Описание примера'
                          },
                          outcome: {
                            bsonType: 'string',
                            description: 'Результат применения'
                          }
                        }
                      },
                      description: 'Примеры применения'
                    }
                  }
                },
                description: 'Конкретные применения в области'
              },
              challenges: {
                bsonType: 'array',
                items: {
                  bsonType: 'string'
                },
                description: 'Вызовы при применении в данной области'
              },
              opportunities: {
                bsonType: 'array',
                items: {
                  bsonType: 'string'
                },
                description: 'Возможности для расширения применения'
              }
            }
          },
          description: 'Области практического применения'
        },
        application_analysis: {
          bsonType: 'string',
          minLength: 200,
          description: 'Общий анализ практического применения концепции'
        },
        implementation_methods: {
          bsonType: 'array',
          items: {
            bsonType: 'object',
            required: ['method_name', 'description', 'steps', 'requirements'],
            properties: {
              method_name: {
                bsonType: 'string',
                description: 'Название метода реализации'
              },
              description: {
                bsonType: 'string',
                description: 'Описание метода'
              },
              steps: {
                bsonType: 'array',
                items: {
                  bsonType: 'object',
                  required: ['step_number', 'description'],
                  properties: {
                    step_number: {
                      bsonType: 'int',
                      minimum: 1,
                      description: 'Номер шага'
                    },
                    description: {
                      bsonType: 'string',
                      description: 'Описание шага'
                    },
                    tools_required: {
                      bsonType: 'array',
                      items: {
                        bsonType: 'string'
                      },
                      description: 'Необходимые инструменты'
                    },
                    estimated_duration: {
                      bsonType: 'string',
                      description: 'Оценочная продолжительность'
                    }
                  }
                },
                description: 'Шаги реализации'
              },
              requirements: {
                bsonType: 'object',
                properties: {
                  skills: {
                    bsonType: 'array',
                    items: {
                      bsonType: 'string'
                    },
                    description: 'Необходимые навыки'
                  },
                  resources: {
                    bsonType: 'array',
                    items: {
                      bsonType: 'string'
                    },
                    description: 'Необходимые ресурсы'
                  },
                  prerequisites: {
                    bsonType: 'array',
                    items: {
                      bsonType: 'string'
                    },
                    description: 'Предварительные условия'
                  }
                },
                description: 'Требования для реализации'
              },
              difficulty_level: {
                bsonType: 'string',
                enum: ['beginner', 'intermediate', 'advanced', 'expert'],
                description: 'Уровень сложности'
              },
              effectiveness_rating: {
                bsonType: 'double',
                minimum: 0,
                maximum: 5,
                description: 'Рейтинг эффективности'
              }
            }
          },
          description: 'Методы реализации концепции на практике'
        },
        relevance_mappings: {
          bsonType: 'array',
          items: {
            bsonType: 'object',
            required: ['thesis_id', 'domains', 'relevance_explanation'],
            properties: {
              thesis_id: {
                bsonType: 'string',
                description: 'ID тезиса концепции'
              },
              domains: {
                bsonType: 'array',
                items: {
                  bsonType: 'string'
                },
                description: 'Релевантные области для данного тезиса'
              },
              relevance_explanation: {
                bsonType: 'string',
                description: 'Объяснение релевантности'
              },
              practical_translation: {
                bsonType: 'string',
                description: 'Практическая интерпретация тезиса'
              }
            }
          },
          description: 'Сопоставление тезисов с областями применения'
        },
        case_studies: {
          bsonType: 'array',
          items: {
            bsonType: 'object',
            required: ['title', 'domain', 'description', 'outcome'],
            properties: {
              title: {
                bsonType: 'string',
                description: 'Название кейса'
              },
              domain: {
                bsonType: 'string',
                description: 'Область применения'
              },
              description: {
                bsonType: 'string',
                description: 'Описание кейса'
              },
              context: {
                bsonType: 'object',
                properties: {
                  organization: {
                    bsonType: 'string',
                    description: 'Организация'
                  },
                  location: {
                    bsonType: 'string',
                    description: 'Местоположение'
                  },
                  time_period: {
                    bsonType: 'string',
                    description: 'Временной период'
                  },
                  participants: {
                    bsonType: 'int',
                    description: 'Количество участников'
                  }
                },
                description: 'Контекст кейса'
              },
              implementation: {
                bsonType: 'object',
                properties: {
                  approach: {
                    bsonType: 'string',
                    description: 'Подход к реализации'
                  },
                  challenges_faced: {
                    bsonType: 'array',
                    items: {
                      bsonType: 'string'
                    },
                    description: 'Столкнувшиеся вызовы'
                  },
                  adaptations_made: {
                    bsonType: 'array',
                    items: {
                      bsonType: 'string'
                    },
                    description: 'Сделанные адаптации'
                  }
                },
                description: 'Детали реализации'
              },
              outcome: {
                bsonType: 'object',
                required: ['success_level', 'description'],
                properties: {
                  success_level: {
                    bsonType: 'string',
                    enum: ['failure', 'partial_success', 'success', 'exceptional_success'],
                    description: 'Уровень успеха'
                  },
                  description: {
                    bsonType: 'string',
                    description: 'Описание результатов'
                  },
                  metrics: {
                    bsonType: 'object',
                    description: 'Измеримые результаты'
                  },
                  lessons_learned: {
                    bsonType: 'array',
                    items: {
                      bsonType: 'string'
                    },
                    description: 'Извлеченные уроки'
                  }
                },
                description: 'Результаты кейса'
              }
            }
          },
          description: 'Кейс-стади практического применения'
        },
        operationalization_framework: {
          bsonType: 'object',
          properties: {
            key_principles: {
              bsonType: 'array',
              items: {
                bsonType: 'object',
                required: ['principle', 'operational_form'],
                properties: {
                  principle: {
                    bsonType: 'string',
                    description: 'Философский принцип'
                  },
                  operational_form: {
                    bsonType: 'string',
                    description: 'Операциональная форма'
                  },
                  measurement_criteria: {
                    bsonType: 'array',
                    items: {
                      bsonType: 'string'
                    },
                    description: 'Критерии измерения'
                  }
                }
              },
              description: 'Ключевые принципы и их операционализация'
            },
            implementation_phases: {
              bsonType: 'array',
              items: {
                bsonType: 'object',
                properties: {
                  phase: {
                    bsonType: 'string',
                    description: 'Название фазы'
                  },
                  duration: {
                    bsonType: 'string',
                    description: 'Продолжительность'
                  },
                  key_activities: {
                    bsonType: 'array',
                    items: {
                      bsonType: 'string'
                    },
                    description: 'Ключевые активности'
                  },
                  success_indicators: {
                    bsonType: 'array',
                    items: {
                      bsonType: 'string'
                    },
                    description: 'Индикаторы успеха'
                  }
                }
              },
              description: 'Фазы внедрения'
            },
            scalability_assessment: {
              bsonType: 'object',
              properties: {
                individual_level: {
                  bsonType: 'string',
                  description: 'Применимость на индивидуальном уровне'
                },
                group_level: {
                  bsonType: 'string',
                  description: 'Применимость на групповом уровне'
                },
                organizational_level: {
                  bsonType: 'string',
                  description: 'Применимость на организационном уровне'
                },
                societal_level: {
                  bsonType: 'string',
                  description: 'Применимость на социетальном уровне'
                }
              },
              description: 'Оценка масштабируемости'
            }
          },
          description: 'Фреймворк для операционализации концепции'
        },
        impact_assessment: {
          bsonType: 'object',
          properties: {
            potential_benefits: {
              bsonType: 'array',
              items: {
                bsonType: 'object',
                properties: {
                  benefit: {
                    bsonType: 'string',
                    description: 'Описание пользы'
                  },
                  beneficiaries: {
                    bsonType: 'array',
                    items: {
                      bsonType: 'string'
                    },
                    description: 'Бенефициары'
                  },
                  likelihood: {
                    bsonType: 'string',
                    enum: ['low', 'medium', 'high', 'certain'],
                    description: 'Вероятность реализации'
                  }
                }
              },
              description: 'Потенциальные выгоды'
            },
            potential_risks: {
              bsonType: 'array',
              items: {
                bsonType: 'object',
                properties: {
                  risk: {
                    bsonType: 'string',
                    description: 'Описание риска'
                  },
                  severity: {
                    bsonType: 'string',
                    enum: ['low', 'medium', 'high', 'critical'],
                    description: 'Серьезность риска'
                  },
                  mitigation_strategies: {
                    bsonType: 'array',
                    items: {
                      bsonType: 'string'
                    },
                    description: 'Стратегии митигации'
                  }
                }
              },
              description: 'Потенциальные риски'
            },
            ethical_considerations: {
              bsonType: 'array',
              items: {
                bsonType: 'string'
              },
              description: 'Этические соображения'
            }
          },
          description: 'Оценка воздействия практического применения'
        },
        claude_generation_id: {
          bsonType: 'string',
          pattern: '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$',
          description: 'ID взаимодействия с Claude API'
        },
        generation_parameters: {
          bsonType: 'object',
          properties: {
            focus_domains: {
              bsonType: 'array',
              items: {
                bsonType: 'string'
              },
              description: 'Фокусные области для анализа'
            },
            practicality_level: {
              bsonType: 'string',
              enum: ['high_level', 'detailed', 'step_by_step', 'implementation_ready'],
              description: 'Уровень практичности анализа'
            },
            include_case_studies: {
              bsonType: 'bool',
              description: 'Включать ли кейс-стади'
            }
          },
          description: 'Параметры генерации практического применения'
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
      name: 'application_id_unique',
      key: { application_id: 1 },
      unique: true
    },
    {
      name: 'concept_id_index',
      key: { concept_id: 1 }
    },
    {
      name: 'domains_type_index',
      key: { 'domains.domain_type': 1 }
    },
    {
      name: 'implementation_level_index',
      key: { 'domains.applications.implementation_level': 1 }
    },
    {
      name: 'case_studies_domain_index',
      key: { 'case_studies.domain': 1 }
    },
    {
      name: 'success_level_index',
      key: { 'case_studies.outcome.success_level': 1 }
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
