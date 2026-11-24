// shared/lib/db/DataSynchronizer.js

const EventEmitter = require('events');
const { 
  CATEGORY_TYPES, 
  RELATIONSHIP_TYPES, 
  RELATIONSHIP_DIRECTIONS,
  CATEGORY_CHARACTERISTICS,
  RELATIONSHIP_CHARACTERISTICS,
  INNOVATION_LEVELS,
  THESIS_TYPES,
  THESIS_STYLES,
  PHILOSOPHICAL_TRADITIONS,
  PRACTICAL_DOMAINS,
  IMPLEMENTATION_METHODS,
  SYNTHESIS_TYPES,
  COMPATIBILITY_CRITERIA
} = require('../../constants/philosophy-constants');

class DataSynchronizer extends EventEmitter {
  constructor(databaseManager) {
    super();
    this.dbManager = databaseManager;
  }

  async syncConceptCreation(conceptData, graphData, thesesData, practicalApplicationData = null) {
    const transactionId = await this.dbManager.beginDistributedTransaction();
    
    try {
      // 1. Создание концепции в PostgreSQL
      const pgResult = await this.dbManager.executeInTransaction(transactionId, {
        postgres: {
          query: `
            INSERT INTO concepts (
              concept_id, creator_id, name, description, 
              is_synthesis, parent_concepts, synthesis_method, innovation_degree, focus
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9) 
            RETURNING *
          `,
          params: [
            conceptData.concept_id,
            conceptData.creator_id,
            conceptData.name,
            conceptData.description,
            conceptData.is_synthesis,
            conceptData.parent_concepts,
            conceptData.synthesis_method,
            conceptData.innovation_degree,
            conceptData.focus
          ]
        }
      });

      // 2. Создание графа в Neo4j
      const neo4jResult = await this.dbManager.executeInTransaction(transactionId, {
        neo4j: {
          query: `
            CREATE (c:Concept {
              concept_id: $conceptId,
              name: $name,
              description: $description,
              creation_date: datetime(),
              innovation_degree: $innovationDegree
            })
            WITH c
            UNWIND $categories AS category
            CREATE (cat:Category {
              category_id: category.category_id,
              concept_id: $conceptId,
              name: category.name,
              definition: category.definition,
              type: category.type,
              centrality: category.characteristics.centrality,
              certainty: category.characteristics.certainty,
              historical_significance: category.characteristics.historical_significance,
              innovation_degree: category.characteristics.innovation_degree,
              clarity: category.characteristics.clarity,
              breadth: category.characteristics.breadth,
              depth: category.characteristics.depth,
              applicability: category.characteristics.applicability
            })
            CREATE (c)-[:INCLUDES]->(cat)
            RETURN c, collect(cat) as categories
          `,
          params: {
            conceptId: conceptData.concept_id,
            name: conceptData.name,
            description: conceptData.description,
            innovationDegree: conceptData.innovation_degree,
            categories: graphData.categories
          }
        }
      });

      // 3. Создание связей между категориями в Neo4j
      for (const relationship of graphData.relationships) {
        await this.dbManager.executeInTransaction(transactionId, {
          neo4j: {
            query: `
              MATCH (source:Category {category_id: $sourceId})
              MATCH (target:Category {category_id: $targetId})
              CREATE (source)-[r:RELATED_TO {
                relationship_id: $relationshipId,
                type: $type,
                direction: $direction,
                strength: $strength,
                certainty: $certainty,
                innovation_degree: $innovationDegree,
                logical_necessity: $logicalNecessity,
                context_dependence: $contextDependence,
                historical_support: $historicalSupport
              }]->(target)
              RETURN r
            `,
            params: {
              sourceId: relationship.source_id,
              targetId: relationship.target_id,
              relationshipId: relationship.relationship_id,
              type: relationship.type,
              direction: relationship.direction,
              strength: relationship.characteristics[RELATIONSHIP_CHARACTERISTICS.STRENGTH] || 0.5,
              certainty: relationship.characteristics[RELATIONSHIP_CHARACTERISTICS.CERTAINTY] || 0.5,
              innovationDegree: relationship.characteristics[RELATIONSHIP_CHARACTERISTICS.INNOVATION_DEGREE] || INNOVATION_LEVELS.TRADITIONAL,
              logicalNecessity: relationship.characteristics[RELATIONSHIP_CHARACTERISTICS.LOGICAL_NECESSITY] || 0.5,
              contextDependence: relationship.characteristics[RELATIONSHIP_CHARACTERISTICS.CONTEXT_DEPENDENCE] || 0.5,
              historicalSupport: relationship.characteristics[RELATIONSHIP_CHARACTERISTICS.HISTORICAL_SUPPORT] || 0.5
            }
          }
        });
      }

      // 4. Создание тезисов в MongoDB
      if (thesesData && thesesData.length > 0) {
        await this.dbManager.executeInTransaction(transactionId, {
          mongodb: {
            collection: 'theses',
            method: 'insertMany',
            document: thesesData.map(thesis => ({
              ...thesis,
              concept_id: conceptData.concept_id,
              created_at: new Date(),
              updated_at: new Date()
            }))
          }
        });
      }

      // 5. Создание данных о практическом применении, если они предоставлены
      if (practicalApplicationData) {
        await this.dbManager.executeInTransaction(transactionId, {
          mongodb: {
            collection: 'practicalApplications',
            method: 'insertOne',
            document: {
              concept_id: conceptData.concept_id,
              domains: practicalApplicationData.domains,
              implementation_methods: practicalApplicationData.implementation_methods,
              application_analysis: 'Анализ практического применения концепции',
              created_at: new Date()
            }
          }
        });
      }

      // 6. Если это синтез, создаем запись синтеза
      if (conceptData.is_synthesis && conceptData.parent_concepts && conceptData.parent_concepts.length > 0) {
        await this.dbManager.executeInTransaction(transactionId, {
          mongodb: {
            collection: 'syntheses',
            method: 'insertOne',
            document: {
              concept_id: conceptData.concept_id,
              parent_concepts: conceptData.parent_concepts,
              synthesis_type: conceptData.synthesis_method || SYNTHESIS_TYPES.DIALECTICAL,
              compatibility_criteria: conceptData.compatibility_criteria || [COMPATIBILITY_CRITERIA.ONTOLOGICAL, COMPATIBILITY_CRITERIA.EPISTEMOLOGICAL],
              synthesis_description: `Синтез концепции "${conceptData.name}" на основе родительских концепций`,
              innovation_level: conceptData.innovation_degree || INNOVATION_LEVELS.EXTENDED,
              created_at: new Date()
            }
          }
        });
      }

      // 7. Коммит транзакции
      await this.dbManager.commitDistributedTransaction(transactionId);

      // 8. Инвалидация кэша
      await this.invalidateConceptCache(conceptData.concept_id);

      // 9. Отправка события
      this.emit('conceptCreated', {
        conceptId: conceptData.concept_id,
        conceptData,
        graphData,
        thesesData,
        practicalApplicationData
      });

      return {
        success: true,
        conceptId: conceptData.concept_id,
        message: 'Concept created successfully across all databases'
      };

    } catch (error) {
      await this.dbManager.rollbackDistributedTransaction(transactionId);
      this.emit('syncError', {
        operation: 'conceptCreation',
        conceptId: conceptData.concept_id,
        error
      });
      throw error;
    }
  }

  async syncConceptUpdate(conceptId, updates) {
    const transactionId = await this.dbManager.beginDistributedTransaction();
    
    try {
      // 1. Обновление в PostgreSQL
      if (updates.metadata) {
        await this.dbManager.executeInTransaction(transactionId, {
          postgres: {
            query: `
              UPDATE concepts 
              SET name = COALESCE($2, name),
                  description = COALESCE($3, description),
                  last_modified = CURRENT_TIMESTAMP
              WHERE concept_id = $1
              RETURNING *
            `,
            params: [conceptId, updates.metadata.name, updates.metadata.description]
          }
        });
      }

      // 2. Обновление в Neo4j
      if (updates.graph) {
        for (const categoryUpdate of updates.graph.categoryUpdates || []) {
          let updateParams = { categoryId: categoryUpdate.category_id };
          let setClauses = [];
          let paramCount = 2;

          // Обновление основных свойств
          if (categoryUpdate.updates.definition) {
            setClauses.push(`cat.definition = $${paramCount}`);
            updateParams[`param${paramCount}`] = categoryUpdate.updates.definition;
            paramCount++;
          }

          // Обновление характеристик категории
          if (categoryUpdate.updates.characteristics) {
            for (const [characteristic, value] of Object.entries(categoryUpdate.updates.characteristics)) {
              setClauses.push(`cat.${characteristic} = $${paramCount}`);
              updateParams[`param${paramCount}`] = value;
              paramCount++;
            }
          }

          // Обновление типа категории
          if (categoryUpdate.updates.type) {
            setClauses.push(`cat.type = $${paramCount}`);
            updateParams[`param${paramCount}`] = categoryUpdate.updates.type;
            paramCount++;
          }

          // Обновление времени изменения
          setClauses.push(`cat.updated_at = datetime()`);

          if (setClauses.length > 0) {
            await this.dbManager.executeInTransaction(transactionId, {
              neo4j: {
                query: `
                  MATCH (cat:Category {category_id: $categoryId})
                  SET ${setClauses.join(', ')}
                  RETURN cat
                `,
                params: updateParams
              }
            });
          }
        }

        // Обновление отношений
        if (updates.graph.relationshipUpdates) {
          for (const relationshipUpdate of updates.graph.relationshipUpdates) {
            let updateParams = { relationshipId: relationshipUpdate.relationship_id };
            let setClauses = [];
            let paramCount = 2;

            if (relationshipUpdate.updates.type) {
              setClauses.push(`r.type = $${paramCount}`);
              updateParams[`param${paramCount}`] = relationshipUpdate.updates.type;
              paramCount++;
            }

            if (relationshipUpdate.updates.direction) {
              setClauses.push(`r.direction = $${paramCount}`);
              updateParams[`param${paramCount}`] = relationshipUpdate.updates.direction;
              paramCount++;
            }

            // Обновление характеристик отношения
            if (relationshipUpdate.updates.characteristics) {
              for (const [characteristic, value] of Object.entries(relationshipUpdate.updates.characteristics)) {
                setClauses.push(`r.${characteristic} = $${paramCount}`);
                updateParams[`param${paramCount}`] = value;
                paramCount++;
              }
            }

            setClauses.push(`r.updated_at = datetime()`);

            if (setClauses.length > 0) {
              await this.dbManager.executeInTransaction(transactionId, {
                neo4j: {
                  query: `
                    MATCH ()-[r:RELATED_TO {relationship_id: $relationshipId}]->()
                    SET ${setClauses.join(', ')}
                    RETURN r
                  `,
                  params: updateParams
                }
              });
            }
          }
        }
      }

      // 3. Обновление в MongoDB
      if (updates.theses) {
        for (const thesisUpdate of updates.theses) {
          await this.dbManager.executeInTransaction(transactionId, {
            mongodb: {
              collection: 'theses',
              method: 'updateOne',
              filter: { _id: thesisUpdate.thesis_id },
              update: { 
                $set: {
                  ...thesisUpdate.updates,
                  updated_at: new Date()
                }
              }
            }
          });
        }
      }

      // 4. Обновление практического применения
      if (updates.practicalApplication) {
        await this.dbManager.executeInTransaction(transactionId, {
          mongodb: {
            collection: 'practicalApplications',
            method: 'updateOne',
            filter: { concept_id: conceptId },
            update: { 
              $set: {
                ...updates.practicalApplication,
                updated_at: new Date()
              }
            },
            options: { upsert: true }
          }
        });
      }

      // 5. Обновление данных синтеза
      if (updates.synthesis) {
        await this.dbManager.executeInTransaction(transactionId, {
          mongodb: {
            collection: 'syntheses',
            method: 'updateOne',
            filter: { concept_id: conceptId },
            update: { 
              $set: {
                ...updates.synthesis,
                updated_at: new Date()
              }
            },
            options: { upsert: true }
          }
        });
      }

      // 6. Коммит транзакции
      await this.dbManager.commitDistributedTransaction(transactionId);

      // 7. Обновление кэша
      await this.updateConceptCache(conceptId);

      this.emit('conceptUpdated', {
        conceptId,
        updates
      });

      return {
        success: true,
        conceptId,
        message: 'Concept updated successfully across all databases'
      };

    } catch (error) {
      await this.dbManager.rollbackDistributedTransaction(transactionId);
      this.emit('syncError', {
        operation: 'conceptUpdate',
        conceptId,
        error
      });
      throw error;
    }
  }

  async syncConceptDeletion(conceptId) {
    const transactionId = await this.dbManager.beginDistributedTransaction();
    
    try {
      // 1. Удаление данных из MongoDB
      // Удаление тезисов
      await this.dbManager.executeInTransaction(transactionId, {
        mongodb: {
          collection: 'theses',
          method: 'deleteMany',
          filter: { concept_id: conceptId }
        }
      });

      // Удаление практического применения
      await this.dbManager.executeInTransaction(transactionId, {
        mongodb: {
          collection: 'practicalApplications',
          method: 'deleteMany',
          filter: { concept_id: conceptId }
        }
      });

      // Удаление данных синтеза
      await this.dbManager.executeInTransaction(transactionId, {
        mongodb: {
          collection: 'syntheses',
          method: 'deleteMany',
          filter: { concept_id: conceptId }
        }
      });

      // Удаление исторического контекста
      await this.dbManager.executeInTransaction(transactionId, {
        mongodb: {
          collection: 'historicalContexts',
          method: 'deleteMany',
          filter: { concept_id: conceptId }
        }
      });

      // Удаление анализов
      await this.dbManager.executeInTransaction(transactionId, {
        mongodb: {
          collection: 'conceptAnalyses',
          method: 'deleteMany',
          filter: { concept_id: conceptId }
        }
      });

      // Удаление данных эволюции
      await this.dbManager.executeInTransaction(transactionId, {
        mongodb: {
          collection: 'conceptEvolutions',
          method: 'deleteMany',
          filter: { concept_id: conceptId }
        }
      });

      // 2. Удаление графа из Neo4j
      await this.dbManager.executeInTransaction(transactionId, {
        neo4j: {
          query: `
            MATCH (c:Concept {concept_id: $conceptId})
            OPTIONAL MATCH (c)-[:INCLUDES]->(cat:Category)
            DETACH DELETE c, cat
          `,
          params: { conceptId }
        }
      });

      // 3. Удаление из PostgreSQL
      await this.dbManager.executeInTransaction(transactionId, {
        postgres: {
          query: 'DELETE FROM concepts WHERE concept_id = $1',
          params: [conceptId]
        }
      });

      // 4. Коммит транзакции
      await this.dbManager.commitDistributedTransaction(transactionId);

      // 5. Очистка кэша
      await this.invalidateConceptCache(conceptId);

      this.emit('conceptDeleted', { conceptId });

      return {
        success: true,
        conceptId,
        message: 'Concept deleted successfully from all databases'
      };

    } catch (error) {
      await this.dbManager.rollbackDistributedTransaction(transactionId);
      this.emit('syncError', {
        operation: 'conceptDeletion',
        conceptId,
        error
      });
      throw error;
    }
  }

  // Методы для работы с кэшем
  async cacheConceptData(conceptId, data) {
    const key = `concept:${conceptId}`;
    await this.dbManager.redisClient.set(
      key, 
      JSON.stringify(data),
      'EX',
      3600 // TTL 1 час
    );
  }

  async getConceptFromCache(conceptId) {
    const key = `concept:${conceptId}`;
    const data = await this.dbManager.redisClient.get(key);
    return data ? JSON.parse(data) : null;
  }

  async invalidateConceptCache(conceptId) {
    const key = `concept:${conceptId}`;
    await this.dbManager.redisClient.del(key);
  }

  async updateConceptCache(conceptId) {
    // Получение свежих данных из всех БД
    const conceptData = await this.getCompleteConceptData(conceptId);
    await this.cacheConceptData(conceptId, conceptData);
  }

  async getCompleteConceptData(conceptId) {
    // Параллельное получение данных из всех БД
    const [pgData, neo4jData, mongoData] = await Promise.all([
      // PostgreSQL
      this.dbManager.postgresPool.query(
        'SELECT * FROM concepts WHERE concept_id = $1',
        [conceptId]
      ),
      
      // Neo4j
      this.dbManager.neo4jDriver.session().run(`
        MATCH (c:Concept {concept_id: $conceptId})
        OPTIONAL MATCH (c)-[:INCLUDES]->(cat:Category)
        OPTIONAL MATCH (cat)-[r:RELATED_TO]-(related:Category)
        RETURN c, collect(DISTINCT cat) as categories, 
               collect(DISTINCT r) as relationships
      `, { conceptId }),
      
      // MongoDB - собираем данные из всех коллекций
      Promise.all([
        this.dbManager.mongodb.collection('theses')
          .find({ concept_id: conceptId })
          .toArray(),
        this.dbManager.mongodb.collection('practicalApplications')
          .findOne({ concept_id: conceptId }),
        this.dbManager.mongodb.collection('syntheses')
          .findOne({ concept_id: conceptId }),
        this.dbManager.mongodb.collection('historicalContexts')
          .findOne({ concept_id: conceptId }),
        this.dbManager.mongodb.collection('conceptAnalyses')
          .find({ concept_id: conceptId })
          .toArray(),
        this.dbManager.mongodb.collection('conceptEvolutions')
          .findOne({ concept_id: conceptId }),
        this.dbManager.mongodb.collection('dialogues')
          .find({ concept_ids: conceptId })
          .toArray()
      ])
    ]);

    const [theses, practicalApplication, synthesis, historicalContext, analyses, evolution, dialogues] = mongoData;

    return {
      metadata: pgData.rows[0],
      graph: neo4jData.records[0]?.toObject(),
      theses,
      practicalApplication,
      synthesis,
      historicalContext,
      analyses,
      evolution,
      dialogues
    };
  }
}

module.exports = DataSynchronizer;
