// migrations/00001_create_collections.js

db.createCollection("theses", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["concept_id", "type", "content", "created_at"],
      properties: {
        thesis_id: {
          bsonType: "objectId",
          description: "Уникальный идентификатор тезиса"
        },
        concept_id: {
          bsonType: "string",
          pattern: "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
          description: "UUID концепции из PostgreSQL"
        },
        type: {
          enum: [
            "ontological", "epistemological", "axiological", "ethical", 
            "aesthetic", "metaphysical", "logical", "practical", 
            "political", "theological", "anthropological", "social", 
            "linguistic", "phenomenological", "existential", "analytical", 
            "hermeneutical", "cross_disciplinary"
          ],
          description: "Тип философского тезиса"
        },
        content: {
          bsonType: "string",
          minLength: 10,
          maxLength: 5000,
          description: "Содержание тезиса"
        },
        related_categories: {
          bsonType: "array",
          items: {
            bsonType: "string",
            pattern: "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
          },
          description: "UUID категорий из Neo4j"
        },
        style: {
          enum: [
            "academic", "popular", "aphoristic", "analytical", "continental", 
            "dialectical", "socratic", "hermeneutical", "phenomenological", 
            "existential", "pragmatic", "logical_positivist", "postmodern", 
            "structuralist", "deconstructionist"
          ],
          description: "Стиль изложения тезиса"
        },
        generation_parameters: {
          bsonType: "object",
          properties: {
            model: { bsonType: "string" },
            temperature: { bsonType: "number" },
            max_tokens: { bsonType: "int" },
            prompt_template: { bsonType: "string" }
          }
        },
        created_at: {
          bsonType: "date",
          description: "Дата создания"
        },
        updated_at: {
          bsonType: "date",
          description: "Дата последнего обновления"
        },
        parent_theses: {
          bsonType: "array",
          items: {
            bsonType: "objectId"
          },
          description: "ID родительских тезисов (для синтеза)"
        },
        version: {
          bsonType: "int",
          minimum: 1,
          description: "Версия тезиса"
        },
        tags: {
          bsonType: "array",
          items: {
            bsonType: "string"
          },
          description: "Теги для категоризации"
        },
        metadata: {
          bsonType: "object",
          description: "Дополнительные метаданные"
        }
      }
    }
  }
});

// Создание коллекции для описаний категорий
db.createCollection("categoryDescriptions", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["category_id", "detailed_description", "created_at"],
      properties: {
        description_id: {
          bsonType: "objectId"
        },
        category_id: {
          bsonType: "string",
          pattern: "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
          description: "UUID категории из Neo4j"
        },
        detailed_description: {
          bsonType: "string",
          minLength: 50,
          description: "Развернутое описание категории"
        },
        alternative_interpretations: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["interpretation", "tradition"],
            properties: {
              interpretation: { bsonType: "string" },
              tradition: { bsonType: "string" },
              source: { bsonType: "string" }
            }
          }
        },
        historical_analogues: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["name", "period", "similarity"],
            properties: {
              name: { bsonType: "string" },
              period: { bsonType: "string" },
              similarity: { bsonType: "string" },
              description: { bsonType: "string" }
            }
          }
        },
        related_concepts: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["concept_name", "relationship"],
            properties: {
              concept_name: { bsonType: "string" },
              relationship: { bsonType: "string" },
              description: { bsonType: "string" }
            }
          }
        },
        category_characteristics: {
          bsonType: "object",
          properties: {
            centrality: { bsonType: "number" },
            certainty: { bsonType: "number" },
            historical_significance: { bsonType: "number" },
            innovation_degree: { bsonType: "number" },
            clarity: { bsonType: "number" },
            breadth: { bsonType: "number" },
            depth: { bsonType: "number" },
            applicability: { bsonType: "number" }
          }
        },
        claude_generation_id: {
          bsonType: "string",
          pattern: "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        },
        created_at: {
          bsonType: "date"
        },
        last_modified: {
          bsonType: "date"
        }
      }
    }
  }
});

// Создание коллекции для описаний связей
db.createCollection("relationshipDescriptions", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["relationship_id", "philosophical_foundation", "created_at"],
      properties: {
        description_id: {
          bsonType: "objectId"
        },
        relationship_id: {
          bsonType: "string",
          pattern: "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
          description: "UUID связи из Neo4j"
        },
        relationship_type: {
          enum: [
            "hierarchical", "causal", "dialectical", "correlational", 
            "disjunctive", "conjunctive", "contradiction", "complementary", 
            "emergence", "necessary_condition", "sufficient_condition", 
            "identity", "analogy", "implementation", "instantiation", 
            "generalization", "part_whole", "means_end", "deductive", 
            "inductive", "abductive", "temporal", "conceptual", "definitional"
          ],
          description: "Тип связи"
        },
        relationship_direction: {
          enum: ["unidirectional", "bidirectional", "circular", "reflexive"],
          description: "Направленность связи"
        },
        philosophical_foundation: {
          bsonType: "string",
          minLength: 50,
          description: "Философское обоснование связи"
        },
        relationship_characteristics: {
          bsonType: "object",
          properties: {
            strength: { bsonType: "number" },
            certainty: { bsonType: "number" },
            innovation_degree: { bsonType: "number" },
            historical_support: { bsonType: "number" },
            logical_necessity: { bsonType: "number" },
            context_dependence: { bsonType: "number" }
          }
        },
        counterarguments: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["argument", "source"],
            properties: {
              argument: { bsonType: "string" },
              source: { bsonType: "string" },
              response: { bsonType: "string" }
            }
          }
        },
        analogues: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["concept_pair", "description"],
            properties: {
              concept_pair: { bsonType: "string" },
              description: { bsonType: "string" },
              similarity_degree: { bsonType: "number" }
            }
          }
        },
        claude_generation_id: {
          bsonType: "string",
          pattern: "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        },
        created_at: {
          bsonType: "date"
        },
        last_modified: {
          bsonType: "date"
        }
      }
    }
  }
});

// Создание коллекции для анализов концепций
db.createCollection("conceptAnalyses", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["concept_id", "analysis_type", "content", "created_at"],
      properties: {
        analysis_id: {
          bsonType: "objectId"
        },
        concept_id: {
          bsonType: "string",
          pattern: "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        },
        analysis_type: {
          enum: [
            "critical", "historical", "comparative", "conceptual", "logical",
            "hermeneutical", "phenomenological", "linguistic", "pragmatic",
            "structural", "genealogical", "deconstructive", "psychoanalytical",
            "feminist", "postcolonial"
          ],
          description: "Тип анализа"
        },
        content: {
          bsonType: "string",
          minLength: 100
        },
        sections: {
          bsonType: "object",
          properties: {
            introduction: { bsonType: "string" },
            main_analysis: { bsonType: "string" },
            conclusions: { bsonType: "string" },
            recommendations: { bsonType: "string" }
          }
        },
        generation_parameters: {
          bsonType: "object"
        },
        claude_generation_id: {
          bsonType: "string",
          pattern: "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        },
        created_at: {
          bsonType: "date"
        }
      }
    }
  }
});

// Коллекция для диалогов между концепциями
db.createCollection("dialogues", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["concept_ids", "topic", "content", "generated_at"],
      properties: {
        dialogue_id: {
          bsonType: "objectId"
        },
        concept_ids: {
          bsonType: "array",
          minItems: 2,
          items: {
            bsonType: "string",
            pattern: "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
          },
          description: "UUID участвующих концепций"
        },
        philosophical_question_type: {
          enum: [
            "metaphysical", "epistemological", "ethical", "political", 
            "existential", "social", "logical", "aesthetic", "historical",
            "methodological", "comparative", "definitional", "conceptual", 
            "applicative"
          ],
          description: "Тип философского вопроса"
        },
        topic: {
          bsonType: "string",
          minLength: 5,
          description: "Тема диалога"
        },
        content: {
          bsonType: "string",
          minLength: 100,
          description: "Содержание диалога"
        },
        dialogue_structure: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["speaker", "statement", "response_to"],
            properties: {
              speaker: { bsonType: "string" },
              statement: { bsonType: "string" },
              response_to: { bsonType: ["string", "null"] },
              argument_type: { 
                enum: [
                  "deductive", "inductive", "abductive", "analogical", 
                  "pragmatic", "dialectical", "transcendental", 
                  "phenomenological", "hermeneutical", "rhetorical", 
                  "intuitive", "historical", "conceptual"
                ],
                description: "Тип аргументации"
              }
            }
          }
        },
        key_disagreements: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["issue", "positions"],
            properties: {
              issue: { bsonType: "string" },
              positions: { bsonType: "object" }
            }
          }
        },
        convergence_points: {
          bsonType: "array",
          items: {
            bsonType: "string"
          }
        },
        claude_generation_id: {
          bsonType: "string",
          pattern: "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        },
        generated_at: {
          bsonType: "date"
        },
        parameters: {
          bsonType: "object"
        }
      }
    }
  }
});

// Коллекция для исторического контекста
db.createCollection("historicalContexts", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["concept_id", "time_period", "historical_analysis", "created_at"],
      properties: {
        context_id: {
          bsonType: "objectId"
        },
        concept_id: {
          bsonType: "string",
          pattern: "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        },
        time_period: {
          enum: [
            "ancient", "medieval", "renaissance", "early_modern", 
            "modern", "contemporary"
          ],
          description: "Исторический период"
        },
        historical_analysis: {
          bsonType: "string",
          minLength: 200
        },
        influences: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["source", "description", "impact_level"],
            properties: {
              source: { bsonType: "string" },
              description: { bsonType: "string" },
              impact_level: { 
                bsonType: "string",
                enum: ["major", "moderate", "minor"]
              },
              evidence: { bsonType: "array", items: { bsonType: "string" } }
            }
          }
        },
        contemporaries: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["name", "relationship", "description"],
            properties: {
              name: { bsonType: "string" },
              relationship: { bsonType: "string" },
              description: { bsonType: "string" },
              similarities: { bsonType: "array", items: { bsonType: "string" } },
              differences: { bsonType: "array", items: { bsonType: "string" } }
            }
          }
        },
        subsequent_influence: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["target", "description", "period"],
            properties: {
              target: { bsonType: "string" },
              description: { bsonType: "string" },
              period: { bsonType: "string" },
              manifestations: { bsonType: "array", items: { bsonType: "string" } }
            }
          }
        },
        cultural_context: {
          bsonType: "object",
          properties: {
            social_conditions: { bsonType: "string" },
            political_climate: { bsonType: "string" },
            intellectual_trends: { bsonType: "array", items: { bsonType: "string" } }
          }
        },
        claude_generation_id: {
          bsonType: "string",
          pattern: "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        },
        created_at: {
          bsonType: "date"
        }
      }
    }
  }
});

// Коллекция для практического применения
db.createCollection("practicalApplications", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["concept_id", "domains", "application_analysis", "created_at"],
      properties: {
        application_id: {
          bsonType: "objectId"
        },
        concept_id: {
          bsonType: "string",
          pattern: "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        },
        domains: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["domain_name", "relevance_score", "applications"],
            properties: {
              domain_name: {
                bsonType: "string",
                enum: [
                  "education", "ethics", "politics", "law", "economics",
                  "medicine", "psychology", "environmental", "technology",
                  "business", "social_policy", "personal_development",
                  "science", "art", "conflict_resolution", "culture",
                  "religion", "communication"
                ]
              },
              relevance_score: {
                bsonType: "number",
                minimum: 0,
                maximum: 1
              },
              applications: {
                bsonType: "array",
                items: {
                  bsonType: "object",
                  required: ["description", "example"],
                  properties: {
                    description: { bsonType: "string" },
                    example: { bsonType: "string" },
                    implementation_level: {
                      bsonType: "string",
                      enum: ["theoretical", "experimental", "practical"]
                    }
                  }
                }
              }
            }
          }
        },
        application_analysis: {
          bsonType: "string",
          minLength: 200
        },
        implementation_methods: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["method", "description", "requirements"],
            properties: {
              method: { 
                bsonType: "string", 
                enum: [
                  "policy_change", "educational_curriculum", "legal_reform",
                  "social_movement", "institutional_design", "personal_practice",
                  "community_initiative", "professional_ethics", 
                  "technological_innovation", "artistic_expression",
                  "therapeutic_approach", "dialogical_practice"
                ]
              },
              description: { bsonType: "string" },
              requirements: { bsonType: "array", items: { bsonType: "string" } },
              challenges: { bsonType: "array", items: { bsonType: "string" } }
            }
          }
        },
        relevance_mappings: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["thesis_id", "domain", "relevance_explanation"],
            properties: {
              thesis_id: { bsonType: "objectId" },
              domain: { bsonType: "string" },
              relevance_explanation: { bsonType: "string" }
            }
          }
        },
        case_studies: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["title", "description", "outcome"],
            properties: {
              title: { bsonType: "string" },
              description: { bsonType: "string" },
              outcome: { bsonType: "string" },
              lessons_learned: { bsonType: "array", items: { bsonType: "string" } }
            }
          }
        },
        claude_generation_id: {
          bsonType: "string",
          pattern: "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        },
        created_at: {
          bsonType: "date"
        }
      }
    }
  }
});

// Коллекция для эволюции концепций
db.createCollection("conceptEvolutions", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["concept_id", "evolution_analysis", "created_at"],
      properties: {
        evolution_id: {
          bsonType: "objectId"
        },
        concept_id: {
          bsonType: "string",
          pattern: "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        },
        evolution_analysis: {
          bsonType: "string",
          minLength: 200
        },
        evolution_directions: {
          bsonType: "array",
          items: {
            bsonType: "string",
            enum: [
              "specialization", "generalization", "integration", "differentiation",
              "reinterpretation", "extension", "reduction", "formalization",
              "contextualization", "historicization", "critique", "synthesis",
              "application", "transdisciplinary"
            ] 
          }
        },
        potential_directions: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["direction", "description", "probability", "impact"],
            properties: {
              direction: { bsonType: "string" },
              description: { bsonType: "string" },
              probability: {
                bsonType: "string",
                enum: ["high", "medium", "low"]
              },
              impact: {
                bsonType: "string",
                enum: ["transformative", "significant", "moderate", "minor"]
              },
              prerequisites: { bsonType: "array", items: { bsonType: "string" } }
            }
          }
        },
        suggested_modifications: {
          bsonType: "object",
          properties: {
            categories_to_add: {
              bsonType: "array",
              items: {
                bsonType: "object",
                required: ["name", "rationale"],
                properties: {
                  name: { bsonType: "string" },
                  rationale: { bsonType: "string" },
                  connections: { bsonType: "array", items: { bsonType: "string" } }
                }
              }
            },
            categories_to_modify: {
              bsonType: "array",
              items: {
                bsonType: "object",
                required: ["category_id", "changes", "rationale"],
                properties: {
                  category_id: { bsonType: "string" },
                  changes: { bsonType: "object" },
                  rationale: { bsonType: "string" }
                }
              }
            },
            relationships_to_add: {
              bsonType: "array",
              items: {
                bsonType: "object",
                required: ["source", "target", "type", "rationale"],
                properties: {
                  source: { bsonType: "string" },
                  target: { bsonType: "string" },
                  type: { bsonType: "string" },
                  rationale: { bsonType: "string" }
                }
              }
            }
          }
        },
        change_types: {
          bsonType: "array",
          items: {
            bsonType: "string",
            enum: [
              "add_category", "remove_category", "modify_category",
              "add_relationship", "remove_relationship", "modify_relationship",
              "redefine_concept", "rename_concept", "merge_categories",
              "split_category", "refocus", "recontextualize", "add_perspective",
              "change_methodology", "update_terminology"
            ]
          }
        },
        scientific_context: {
          bsonType: "object",
          properties: {
            relevant_discoveries: {
              bsonType: "array",
              items: {
                bsonType: "object",
                required: ["discovery", "field", "impact_on_concept"],
                properties: {
                  discovery: { bsonType: "string" },
                  field: { bsonType: "string" },
                  year: { bsonType: "int" },
                  impact_on_concept: { bsonType: "string" }
                }
              }
            },
            emerging_fields: {
              bsonType: "array",
              items: {
                bsonType: "object",
                required: ["field", "relevance"],
                properties: {
                  field: { bsonType: "string" },
                  relevance: { bsonType: "string" }
                }
              }
            }
          }
        },
        name_evolution: {
          bsonType: "object",
          properties: {
            current_name_assessment: { bsonType: "string" },
            suggested_alternatives: {
              bsonType: "array",
              items: {
                bsonType: "object",
                required: ["name", "rationale"],
                properties: {
                  name: { bsonType: "string" },
                  rationale: { bsonType: "string" }
                }
              }
            }
          }
        },
        claude_generation_id: {
          bsonType: "string",
          pattern: "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        },
        created_at: {
          bsonType: "date"
        }
      }
    }
  }
});

// Коллекция для синтеза концепций
db.createCollection("syntheses", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["concept_id", "parent_concepts", "synthesis_type", "created_at"],
      properties: {
        synthesis_id: {
          bsonType: "objectId"
        },
        concept_id: {
          bsonType: "string",
          pattern: "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        },
        parent_concepts: {
          bsonType: "array",
          items: {
            bsonType: "string",
            pattern: "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
          },
          description: "ID родительских концепций"
        },
        synthesis_type: {
          bsonType: "string",
          enum: [
            "dialectical", "integrative", "creative", "comparative",
            "historical", "conceptual", "pragmatic", "methodological",
            "hermeneutical", "cross_cultural"
          ],
          description: "Тип синтеза"
        },
        compatibility_criteria: {
          bsonType: "array",
          items: {
            bsonType: "string",
            enum: [
              "ontological", "epistemological", "axiological", "methodological",
              "linguistic", "logical", "historical", "cultural", "pragmatic", 
              "conceptual"
            ]
          },
          description: "Критерии совместимости"
        },
        synthesis_description: {
          bsonType: "string",
          minLength: 200,
          description: "Описание процесса синтеза"
        },
        innovation_level: {
          bsonType: "number",
          minimum: 1,
          maximum: 5,
          description: "Уровень инновационности"
        },
        claude_generation_id: {
          bsonType: "string",
          pattern: "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        },
        created_at: {
          bsonType: "date"
        }
      }
    }
  }
});
