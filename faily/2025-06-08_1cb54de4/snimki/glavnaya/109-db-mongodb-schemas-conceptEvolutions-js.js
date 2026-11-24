/**
 * MongoDB Schema: Concept Evolutions
 * Коллекция для хранения анализа эволюции философских концепций
 * 
 * Коллекция: conceptEvolutions
 */

module.exports = {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      title: 'Concept Evolution Schema',
      required: [
        'evolution_id',
        'concept_id',
        'evolution_analysis',
        'directions',
        'created_at',
        'claude_generation_id'
      ],
      properties: {
        _id: {
          bsonType: 'objectId',
          description: 'MongoDB ID документа'
        },
        evolution_id: {
          bsonType: 'string',
          pattern: '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$',
          description: 'UUID эволюции концепции'
        },
        concept_id: {
          bsonType: 'string',
          pattern: '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$',
          description: 'UUID исходной концепции'
        },
        target_concept_id: {
          bsonType: 'string',
          pattern: '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$',
          description: 'UUID целевой концепции (если создана)'
        },
        evolution_analysis: {
          bsonType: 'string',
          minLength: 200,
          description: 'Общий анализ возможной эволюции концепции'
        },
        evolution_context: {
          bsonType: 'object',
          properties: {
            contemporary_challenges: {
              bsonType: 'array',
              items: {
                bsonType: 'string'
              },
              description: 'Современные вызовы, требующие эволюции'
            },
            scientific_developments: {
              bsonType: 'array',
              items: {
                bsonType: 'object',
                properties: {
                  field: {
                    bsonType: 'string',
                    description: 'Область науки'
                  },
                  development: {
                    bsonType: 'string',
                    description: 'Научное развитие'
                  },
                  impact: {
                    bsonType: 'string',
                    description: 'Влияние на концепцию'
                  }
                }
              },
              description: 'Научные открытия, влияющие на эволюцию'
            },
            social_changes: {
              bsonType: 'array',
              items: {
                bsonType: 'string'
              },
              description: 'Социальные изменения, влияющие на эволюцию'
            },
            technological_advances: {
              bsonType: 'array',
              items: {
                bsonType: 'object',
                properties: {
                  technology: {
                    bsonType: 'string',
                    description: 'Технология'
                  },
                  relevance: {
                    bsonType: 'string',
                    description: 'Релевантность для концепции'
                  }
                }
              },
              description: 'Технологические достижения'
            }
          },
          description: 'Контекст, в котором происходит эволюция'
        },
        directions: {
          bsonType: 'array',
          minItems: 1,
          items: {
            bsonType: 'object',
            required: ['direction_id', 'name', 'description', 'probability', 'changes'],
            properties: {
              direction_id: {
                bsonType: 'string',
                description: 'ID направления эволюции'
              },
              name: {
                bsonType: 'string',
                description: 'Название направления'
              },
              description: {
                bsonType: 'string',
                description: 'Описание направления эволюции'
              },
              type: {
                bsonType: 'string',
                enum: [
                  'conservative',
                  'progressive',
                  'radical',
                  'synthetic',
                  'deconstructive',
                  'reconstructive',
                  'transformative'
                ],
                description: 'Тип направления эволюции'
              },
              probability: {
                bsonType: 'double',
                minimum: 0,
                maximum: 1,
                description: 'Вероятность данного направления'
              },
              timeframe: {
                bsonType: 'string',
                enum: [
                  'immediate',
                  'short_term',
                  'medium_term',
                  'long_term',
                  'generational'
                ],
                description: 'Временные рамки'
              },
              changes: {
                bsonType: 'object',
                required: ['categories', 'relationships', 'theses'],
                properties: {
                  categories: {
                    bsonType: 'object',
                    properties: {
                      added: {
                        bsonType: 'array',
                        items: {
                          bsonType: 'object',
                          properties: {
                            name: {
                              bsonType: 'string',
                              description: 'Название новой категории'
                            },
                            definition: {
                              bsonType: 'string',
                              description: 'Определение категории'
                            },
                            rationale: {
                              bsonType: 'string',
                              description: 'Обоснование добавления'
                            }
                          }
                        }
                      },
                      modified: {
                        bsonType: 'array',
                        items: {
                          bsonType: 'object',
                          properties: {
                            category_id: {
                              bsonType: 'string',
                              description: 'ID изменяемой категории'
                            },
                            changes: {
                              bsonType: 'object',
                              description: 'Изменения в категории'
                            },
                            rationale: {
                              bsonType: 'string',
                              description: 'Обоснование изменений'
                            }
                          }
                        }
                      },
                      removed: {
                        bsonType: 'array',
                        items: {
                          bsonType: 'object',
                          properties: {
                            category_id: {
                              bsonType: 'string',
                              description: 'ID удаляемой категории'
                            },
                            rationale: {
                              bsonType: 'string',
                              description: 'Обоснование удаления'
                            }
                          }
                        }
                      }
                    },
                    description: 'Изменения в категориях'
                  },
                  relationships: {
                    bsonType: 'object',
                    properties: {
                      added: {
                        bsonType: 'array',
                        items: {
                          bsonType: 'object',
                          properties: {
                            from_category: {
                              bsonType: 'string',
                              description: 'Исходная категория'
                            },
                            to_category: {
                              bsonType: 'string',
                              description: 'Целевая категория'
                            },
                            type: {
                              bsonType: 'string',
                              description: 'Тип связи'
                            },
                            rationale: {
                              bsonType: 'string',
                              description: 'Обоснование добавления'
                            }
                          }
                        }
                      },
                      modified: {
                        bsonType: 'array',
                        items: {
                          bsonType: 'object',
                          properties: {
                            relationship_id: {
                              bsonType: 'string',
                              description: 'ID изменяемой связи'
                            },
                            changes: {
                              bsonType: 'object',
                              description: 'Изменения в связи'
                            },
                            rationale: {
                              bsonType: 'string',
                              description: 'Обоснование изменений'
                            }
                          }
                        }
                      },
                      removed: {
                        bsonType: 'array',
                        items: {
                          bsonType: 'object',
                          properties: {
                            relationship_id: {
                              bsonType: 'string',
                              description: 'ID удаляемой связи'
                            },
                            rationale: {
                              bsonType: 'string',
                              description: 'Обоснование удаления'
                            }
                          }
                        }
                      }
                    },
                    description: 'Изменения в связях'
                  },
                  theses: {
                    bsonType: 'object',
                    properties: {
                      new_emphases: {
                        bsonType: 'array',
                        items: {
                          bsonType: 'string'
                        },
                        description: 'Новые акценты в тезисах'
                      },
                      reinterpretations: {
                        bsonType: 'array',
                        items: {
                          bsonType: 'object',
                          properties: {
                            original_thesis: {
                              bsonType: 'string',
                              description: 'Оригинальный тезис'
                            },
                            new_interpretation: {
                              bsonType: 'string',
                              description: 'Новая интерпретация'
                            }
                          }
                        },
                        description: 'Переинтерпретации тезисов'
                      },
                      abandoned_ideas: {
                        bsonType: 'array',
                        items: {
                          bsonType: 'string'
                        },
                        description: 'Отброшенные идеи'
                      }
                    },
                    description: 'Изменения в тезисах'
                  },
                  quantitative_characteristics: {
                    bsonType: 'object',
                    properties: {
                      centrality_shifts: {
                        bsonType: 'array',
                        items: {
                          bsonType: 'object',
                          properties: {
                            category_id: {
                              bsonType: 'string'
                            },
                            old_centrality: {
                              bsonType: 'double'
                            },
                            new_centrality: {
                              bsonType: 'double'
                            }
                          }
                        },
                        description: 'Изменения в центральности категорий'
                      },
                      new_characteristics: {
                        bsonType: 'object',
                        description: 'Новые количественные характеристики'
                      }
                    },
                    description: 'Изменения в количественных характеристиках'
                  }
                },
                description: 'Предлагаемые изменения'
              },
              philosophical_justification: {
                bsonType: 'string',
                description: 'Философское обоснование направления'
              },
              potential_impact: {
                bsonType: 'object',
                properties: {
                  theoretical: {
                    bsonType: 'string',
                    description: 'Теоретическое влияние'
                  },
                  practical: {
                    bsonType: 'string',
                    description: 'Практическое влияние'
                  },
                  cultural: {
                    bsonType: 'string',
                    description: 'Культурное влияние'
                  }
                },
                description: 'Потенциальное влияние'
              },
              prerequisites: {
                bsonType: 'array',
                items: {
                  bsonType: 'string'
                },
                description: 'Предпосылки для данного направления'
              },
              obstacles: {
                bsonType: 'array',
                items: {
                  bsonType: 'string'
                },
                description: 'Препятствия для реализации'
              }
            }
          },
          description: 'Возможные направления эволюции'
        },
        name_evolution: {
          bsonType: 'object',
          properties: {
            current_name_assessment: {
              bsonType: 'string',
              description: 'Оценка текущего названия'
            },
            suggested_names: {
              bsonType: 'array',
              items: {
                bsonType: 'object',
                properties: {
                  name: {
                    bsonType: 'string',
                    description: 'Предлагаемое название'
                  },
                  rationale: {
                    bsonType: 'string',
                    description: 'Обоснование названия'
                  },
                  alignment_with_direction: {
                    bsonType: 'string',
                    description: 'Соответствие направлению эволюции'
                  }
                }
              },
              description: 'Предлагаемые новые названия'
            }
          },
          description: 'Эволюция названия концепции'
        },
        integration_possibilities: {
          bsonType: 'array',
          items: {
            bsonType: 'object',
            properties: {
              field: {
                bsonType: 'string',
                description: 'Область интеграции'
              },
              concepts: {
                bsonType: 'array',
                items: {
                  bsonType: 'string'
                },
                description: 'Концепции для интеграции'
              },
              approach: {
                bsonType: 'string',
                description: 'Подход к интеграции'
              },
              expected_outcome: {
                bsonType: 'string',
                description: 'Ожидаемый результат'
              }
            }
          },
          description: 'Возможности интеграции с другими областями'
        },
        contemporary_relevance: {
          bsonType: 'object',
          properties: {
            current_issues_addressed: {
              bsonType: 'array',
              items: {
                bsonType: 'string'
              },
              description: 'Текущие проблемы, к которым применима концепция'
            },
            emerging_applications: {
              bsonType: 'array',
              items: {
                bsonType: 'object',
                properties: {
                  domain: {
                    bsonType: 'string',
                    description: 'Область применения'
                  },
                  application: {
                    bsonType: 'string',
                    description: 'Применение'
                  },
                  novelty: {
                    bsonType: 'string',
                    enum: ['incremental', 'substantial', 'breakthrough'],
                    description: 'Уровень новизны'
                  }
                }
              },
              description: 'Появляющиеся применения'
            },
            future_potential: {
              bsonType: 'string',
              description: 'Потенциал на будущее'
            }
          },
          description: 'Современная релевантность'
        },
        paradigm_shifts: {
          bsonType: 'array',
          items: {
            bsonType: 'object',
            properties: {
              shift_description: {
                bsonType: 'string',
                description: 'Описание сдвига парадигмы'
              },
              from_paradigm: {
                bsonType: 'string',
                description: 'Исходная парадигма'
              },
              to_paradigm: {
                bsonType: 'string',
                description: 'Новая парадигма'
              },
              catalysts: {
                bsonType: 'array',
                items: {
                  bsonType: 'string'
                },
                description: 'Катализаторы изменения'
              },
              resistance_points: {
                bsonType: 'array',
                items: {
                  bsonType: 'string'
                },
                description: 'Точки сопротивления'
              }
            }
          },
          description: 'Потенциальные сдвиги парадигмы'
        },
        implementation_roadmap: {
          bsonType: 'object',
          properties: {
            phases: {
              bsonType: 'array',
              items: {
                bsonType: 'object',
                properties: {
                  phase_name: {
                    bsonType: 'string',
                    description: 'Название фазы'
                  },
                  duration: {
                    bsonType: 'string',
                    description: 'Продолжительность'
                  },
                  key_actions: {
                    bsonType: 'array',
                    items: {
                      bsonType: 'string'
                    },
                    description: 'Ключевые действия'
                  },
                  milestones: {
                    bsonType: 'array',
                    items: {
                      bsonType: 'string'
                    },
                    description: 'Вехи'
                  },
                  success_criteria: {
                    bsonType: 'array',
                    items: {
                      bsonType: 'string'
                    },
                    description: 'Критерии успеха'
                  }
                }
              },
              description: 'Фазы внедрения эволюции'
            },
            resources_required: {
              bsonType: 'array',
              items: {
                bsonType: 'string'
              },
              description: 'Необходимые ресурсы'
            },
            stakeholders: {
              bsonType: 'array',
              items: {
                bsonType: 'string'
              },
              description: 'Заинтересованные стороны'
            }
          },
          description: 'Дорожная карта внедрения эволюции'
        },
        claude_generation_id: {
          bsonType: 'string',
          pattern: '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$',
          description: 'ID взаимодействия с Claude API'
        },
        generation_parameters: {
          bsonType: 'object',
          properties: {
            evolution_depth: {
              bsonType: 'string',
              enum: ['surface', 'moderate', 'deep', 'revolutionary'],
              description: 'Глубина эволюционного анализа'
            },
            time_horizon: {
              bsonType: 'string',
              description: 'Временной горизонт анализа'
            },
            focus_areas: {
              bsonType: 'array',
              items: {
                bsonType: 'string'
              },
              description: 'Области фокуса анализа'
            },
            constraint_level: {
              bsonType: 'string',
              enum: ['conservative', 'moderate', 'progressive', 'unconstrained'],
              description: 'Уровень ограничений'
            }
          },
          description: 'Параметры генерации эволюции'
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
      name: 'evolution_id_unique',
      key: { evolution_id: 1 },
      unique: true
    },
    {
      name: 'concept_id_index',
      key: { concept_id: 1 }
    },
    {
      name: 'target_concept_id_index',
      key: { target_concept_id: 1 }
    },
    {
      name: 'direction_type_index',
      key: { 'directions.type': 1 }
    },
    {
      name: 'timeframe_index',
      key: { 'directions.timeframe': 1 }
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
