// tests/integration/concept-sync.test.js

const DatabaseManager = require('../../shared/lib/db/DatabaseManager');
const DataSynchronizer = require('../../shared/lib/db/DataSynchronizer');
const { 
  CATEGORY_TYPES, 
  RELATIONSHIP_TYPES, 
  RELATIONSHIP_DIRECTIONS,
  CATEGORY_CHARACTERISTICS,
  RELATIONSHIP_CHARACTERISTICS,
  INNOVATION_LEVELS,
  THESIS_TYPES,
  THESIS_STYLES,
  PRACTICAL_DOMAINS,
  IMPLEMENTATION_METHODS,
  SYNTHESIS_TYPES,
  COMPATIBILITY_CRITERIA
} = require('../../shared/constants/philosophy-constants');
const { v4: uuidv4 } = require('uuid');

describe('Concept Synchronization', () => {
  let dbManager;
  let dataSynchronizer;

  beforeAll(async () => {
    const testConfig = {
      postgres: {
        host: process.env.PG_HOST || 'localhost',
        port: process.env.PG_PORT || 5432,
        database: process.env.PG_DATABASE || 'philosophy_test',
        user: process.env.PG_USER || 'postgres',
        password: process.env.PG_PASSWORD || 'password'
      },
      neo4j: {
        uri: process.env.NEO4J_URI || 'bolt://localhost:7687',
        user: process.env.NEO4J_USER || 'neo4j',
        password: process.env.NEO4J_PASSWORD || 'password'
      },
      mongodb: {
        uri: process.env.MONGODB_URI || 'mongodb://localhost:27017',
        dbName: process.env.MONGODB_DB || 'philosophy_test'
      },
      redis: {
        host: process.env.REDIS_HOST || 'localhost',
        port: process.env.REDIS_PORT || 6379,
        db: 1 // Используем отдельную БД для тестов
      }
    };

    dbManager = new DatabaseManager(testConfig);
    await dbManager.initialize();
    dataSynchronizer = new DataSynchronizer(dbManager);
  });

  afterAll(async () => {
    await dbManager.close();
  });

  test('should synchronize concept creation across all databases with proper constants', async () => {
    const conceptId = uuidv4();
    const conceptData = {
      concept_id: conceptId,
      creator_id: uuidv4(),
      name: 'Integration Test Concept',
      description: 'Test concept for integration testing',
      is_synthesis: true,
      parent_concepts: [uuidv4(), uuidv4()],
      synthesis_method: SYNTHESIS_TYPES.INTEGRATIVE,
      innovation_degree: INNOVATION_LEVELS.EXTENDED,
      focus: 'Testing philosophy service'
    };

    const graphData = {
      categories: [
        {
          category_id: uuidv4(),
          name: 'Test Ontological Category',
          definition: 'A test category for ontological aspects',
          type: CATEGORY_TYPES.ONTOLOGICAL,
          characteristics: {
            [CATEGORY_CHARACTERISTICS.CENTRALITY]: 0.8,
            [CATEGORY_CHARACTERISTICS.CERTAINTY]: 0.9,
            [CATEGORY_CHARACTERISTICS.HISTORICAL_SIGNIFICANCE]: 0.7,
            [CATEGORY_CHARACTERISTICS.INNOVATION_DEGREE]: INNOVATION_LEVELS.NOVEL,
            [CATEGORY_CHARACTERISTICS.CLARITY]: 0.85,
            [CATEGORY_CHARACTERISTICS.BREADTH]: 0.75,
            [CATEGORY_CHARACTERISTICS.DEPTH]: 0.8,
            [CATEGORY_CHARACTERISTICS.APPLICABILITY]: 0.6
          }
        },
        {
          category_id: uuidv4(),
          name: 'Test Epistemological Category',
          definition: 'A test category for epistemological aspects',
          type: CATEGORY_TYPES.EPISTEMOLOGICAL,
          characteristics: {
            [CATEGORY_CHARACTERISTICS.CENTRALITY]: 0.7,
            [CATEGORY_CHARACTERISTICS.CERTAINTY]: 0.8,
            [CATEGORY_CHARACTERISTICS.HISTORICAL_SIGNIFICANCE]: 0.6,
            [CATEGORY_CHARACTERISTICS.INNOVATION_DEGREE]: INNOVATION_LEVELS.EXTENDED,
            [CATEGORY_CHARACTERISTICS.CLARITY]: 0.9,
            [CATEGORY_CHARACTERISTICS.BREADTH]: 0.7,
            [CATEGORY_CHARACTERISTICS.DEPTH]: 0.85,
            [CATEGORY_CHARACTERISTICS.APPLICABILITY]: 0.75
          }
        }
      ],
      relationships: [
        {
          relationship_id: uuidv4(),
          source_id: graphData.categories[0].category_id,
          target_id: graphData.categories[1].category_id,
          type: RELATIONSHIP_TYPES.DIALECTICAL,
          direction: RELATIONSHIP_DIRECTIONS.BIDIRECTIONAL,
          characteristics: {
            [RELATIONSHIP_CHARACTERISTICS.STRENGTH]: 0.85,
            [RELATIONSHIP_CHARACTERISTICS.CERTAINTY]: 0.8,
            [RELATIONSHIP_CHARACTERISTICS.INNOVATION_DEGREE]: INNOVATION_LEVELS.EXTENDED,
            [RELATIONSHIP_CHARACTERISTICS.HISTORICAL_SUPPORT]: 0.7,
            [RELATIONSHIP_CHARACTERISTICS.LOGICAL_NECESSITY]: 0.9,
            [RELATIONSHIP_CHARACTERISTICS.CONTEXT_DEPENDENCE]: 0.6
          }
        }
      ]
    };

    const thesesData = [
      {
        type: THESIS_TYPES.ONTOLOGICAL,
        content: 'This is a test ontological thesis',
        related_categories: [graphData.categories[0].category_id],
        style: THESIS_STYLES.ACADEMIC
      },
      {
        type: THESIS_TYPES.EPISTEMOLOGICAL,
        content: 'This is a test epistemological thesis',
        related_categories: [graphData.categories[1].category_id],
        style: THESIS_STYLES.ANALYTICAL
      },
      {
        type: THESIS_TYPES.SYNTHETIC,
        content: 'This is a test synthetic thesis combining ontology and epistemology',
        related_categories: [graphData.categories[0].category_id, graphData.categories[1].category_id],
        style: THESIS_STYLES.DIALECTICAL
      }
    ];

    const practicalApplicationData = {
      domains: [
        {
          domain_name: PRACTICAL_DOMAINS.EDUCATION,
          relevance_score: 0.9,
          applications: [
            {
              description: 'Application in educational theory',
              example: 'Testing philosophical frameworks in educational contexts'
            }
          ]
        },
        {
          domain_name: PRACTICAL_DOMAINS.SCIENCE,
          relevance_score: 0.85,
          applications: [
            {
              description: 'Application in scientific methodology',
              example: 'Using the concept to structure research approaches'
            }
          ]
        }
      ],
      implementation_methods: [
        {
          method: IMPLEMENTATION_METHODS.EDUCATIONAL_CURRICULUM,
          description: 'Integration into curriculum design',
          requirements: ['Understanding of basic philosophical concepts', 'Pedagogical training']
        },
        {
          method: IMPLEMENTATION_METHODS.DIALOGICAL_PRACTICE,
          description: 'Use in philosophical dialogue sessions',
          requirements: ['Group facilitation skills', 'Knowledge of dialectical methods']
        }
      ]
    };

    const result = await dataSynchronizer.syncConceptCreation(
      conceptData,
      graphData,
      thesesData,
      practicalApplicationData
    );

    expect(result.success).toBe(true);
    expect(result.conceptId).toBe(conceptId);

    // Проверка данных в PostgreSQL
    const pgResult = await dbManager.postgresPool.query(
      'SELECT * FROM concepts WHERE concept_id = $1',
      [conceptId]
    );
    expect(pgResult.rows).toHaveLength(1);
    expect(pgResult.rows[0].synthesis_method).toBe(SYNTHESIS_TYPES.INTEGRATIVE);
    expect(pgResult.rows[0].innovation_degree).toBe(INNOVATION_LEVELS.EXTENDED);

    // Проверка данных в Neo4j
    const neo4jSession = dbManager.neo4jDriver.session();
    
    // Проверка категорий
    const categoryResult = await neo4jSession.run(
      'MATCH (c:Concept {concept_id: $conceptId})-[:INCLUDES]->(cat:Category) RETURN cat',
      { conceptId }
    );
    expect(categoryResult.records).toHaveLength(2);
    
    // Проверка, что типы категорий соответствуют константам
    const categoryTypes = categoryResult.records.map(record => record.get('cat').properties.type);
    expect(categoryTypes).toContain(CATEGORY_TYPES.ONTOLOGICAL);
    expect(categoryTypes).toContain(CATEGORY_TYPES.EPISTEMOLOGICAL);
    
    // Проверка отношений между категориями
    const relationshipResult = await neo4jSession.run(
      'MATCH (c:Concept {concept_id: $conceptId})-[:INCLUDES]->(cat:Category)-[r:RELATED_TO]->(:Category) RETURN r',
      { conceptId }
    );
    expect(relationshipResult.records).toHaveLength(1);
    expect(relationshipResult.records[0].get('r').properties.type).toBe(RELATIONSHIP_TYPES.DIALECTICAL);
    expect(relationshipResult.records[0].get('r').properties.direction).toBe(RELATIONSHIP_DIRECTIONS.BIDIRECTIONAL);
    
    await neo4jSession.close();

    // Проверка данных в MongoDB
    // Проверка тезисов
    const theses = await dbManager.mongodb
      .collection('theses')
      .find({ concept_id: conceptId })
      .toArray();
    expect(theses).toHaveLength(3);
    
    // Проверка типов тезисов
    const thesisTypes = theses.map(thesis => thesis.type);
    expect(thesisTypes).toContain(THESIS_TYPES.ONTOLOGICAL);
    expect(thesisTypes).toContain(THESIS_TYPES.EPISTEMOLOGICAL);
    expect(thesisTypes).toContain(THESIS_TYPES.SYNTHETIC);
    
    // Проверка стилей тезисов
    const thesisStyles = theses.map(thesis => thesis.style);
    expect(thesisStyles).toContain(THESIS_STYLES.ACADEMIC);
    expect(thesisStyles).toContain(THESIS_STYLES.ANALYTICAL);
    expect(thesisStyles).toContain(THESIS_STYLES.DIALECTICAL);
    
    // Проверка практического применения
    const practicalApplication = await dbManager.mongodb
      .collection('practicalApplications')
      .findOne({ concept_id: conceptId });
    expect(practicalApplication).toBeDefined();
    expect(practicalApplication.domains[0].domain_name).toBe(PRACTICAL_DOMAINS.EDUCATION);
    expect(practicalApplication.implementation_methods[0].method).toBe(IMPLEMENTATION_METHODS.EDUCATIONAL_CURRICULUM);
    
    // Проверка данных синтеза
    const synthesis = await dbManager.mongodb
      .collection('syntheses')
      .findOne({ concept_id: conceptId });
    expect(synthesis).toBeDefined();
    expect(synthesis.synthesis_type).toBe(SYNTHESIS_TYPES.INTEGRATIVE);
    
    // Очистка после теста
    await dataSynchronizer.syncConceptDeletion(conceptId);
  });

  test('should handle updates with proper constants', async () => {
    // Создаем концепцию для тестирования обновления
    const conceptId = uuidv4();
    const initialData = {
      concept_id: conceptId,
      creator_id: uuidv4(),
      name: 'Update Test Concept',
      description: 'Test concept for update testing',
      is_synthesis: false
    };

    const initialGraphData = {
      categories: [
        {
          category_id: uuidv4(),
          name: 'Initial Category',
          definition: 'Initial definition',
          type: CATEGORY_TYPES.LOGICAL,
          characteristics: {
            [CATEGORY_CHARACTERISTICS.CENTRALITY]: 0.5,
            [CATEGORY_CHARACTERISTICS.CERTAINTY]: 0.5
          }
        }
      ],
      relationships: []
    };

    const initialThesesData = [
      {
        type: THESIS_TYPES.LOGICAL,
        content: 'Initial logical thesis',
        related_categories: [initialGraphData.categories[0].category_id],
        style: THESIS_STYLES.ACADEMIC
      }
    ];

    // Создаем исходную концепцию
    await dataSynchronizer.syncConceptCreation(
      initialData,
      initialGraphData,
      initialThesesData
    );

    // Обновляем концепцию с использованием констант
    const updateResult = await dataSynchronizer.syncConceptUpdate(conceptId, {
      metadata: {
        name: 'Updated Concept Name',
        description: 'Updated concept description'
      },
      graph: {
        categoryUpdates: [
          {
            category_id: initialGraphData.categories[0].category_id,
            updates: {
              definition: 'Updated definition',
              type: CATEGORY_TYPES.ANALYTICAL,
              characteristics: {
                [CATEGORY_CHARACTERISTICS.CENTRALITY]: 0.8,
                [CATEGORY_CHARACTERISTICS.INNOVATION_DEGREE]: INNOVATION_LEVELS.NOVEL
              }
            }
          }
        ]
      },
      theses: [
        {
          thesis_id: initialThesesData[0]._id,
          updates: {
            content: 'Updated thesis content',
            type: THESIS_TYPES.ANALYTICAL,
            style: THESIS_STYLES.CONTINENTAL
          }
        }
      ]
    });

    expect(updateResult.success).toBe(true);

    // Проверка обновленных данных
    const neo4jSession = dbManager.neo4jDriver.session();
    const categoryResult = await neo4jSession.run(
      'MATCH (c:Concept {concept_id: $conceptId})-[:INCLUDES]->(cat:Category) RETURN cat',
      { conceptId }
    );
    await neo4jSession.close();

    // Проверка обновленного типа категории
    expect(categoryResult.records[0].get('cat').properties.type).toBe(CATEGORY_TYPES.ANALYTICAL);

    // Проверка обновленного тезиса
    const updatedThesis = await dbManager.mongodb
      .collection('theses')
      .findOne({ concept_id: conceptId });
    
    expect(updatedThesis).toBeDefined();
    expect(updatedThesis.type).toBe(THESIS_TYPES.ANALYTICAL);
    expect(updatedThesis.style).toBe(THESIS_STYLES.CONTINENTAL);

    // Очистка после теста
    await dataSynchronizer.syncConceptDeletion(conceptId);
  });

  test('should handle concept deletion across all databases', async () => {
    // Создаем временную концепцию для удаления
    const conceptId = uuidv4();
    const tempData = {
      concept_id: conceptId,
      creator_id: uuidv4(),
      name: 'Temporary Concept',
      description: 'This concept will be deleted'
    };

    const tempGraphData = {
      categories: [
        {
          category_id: uuidv4(),
          name: 'Temp Category',
          definition: 'Temporary definition',
          type: CATEGORY_TYPES.SOCIAL,
          characteristics: {
            [CATEGORY_CHARACTERISTICS.CENTRALITY]: 0.5,
            [CATEGORY_CHARACTERISTICS.CERTAINTY]: 0.5
          }
        }
      ],
      relationships: []
    };

    // Создаем временную концепцию
    await dataSynchronizer.syncConceptCreation(
      tempData,
      tempGraphData,
      [] // без тезисов
    );

    // Удаляем концепцию
    const deleteResult = await dataSynchronizer.syncConceptDeletion(conceptId);
    expect(deleteResult.success).toBe(true);

    // Проверяем, что концепция удалена из всех БД
    const pgResult = await dbManager.postgresPool.query(
      'SELECT * FROM concepts WHERE concept_id = $1',
      [conceptId]
    );
    expect(pgResult.rows).toHaveLength(0);

    const neo4jSession = dbManager.neo4jDriver.session();
    const neo4jResult = await neo4jSession.run(
      'MATCH (c:Concept {concept_id: $conceptId}) RETURN c',
      { conceptId }
    );
    await neo4jSession.close();
    expect(neo4jResult.records).toHaveLength(0);

    const mongoResult = await dbManager.mongodb
      .collection('theses')
      .findOne({ concept_id: conceptId });
    expect(mongoResult).toBeNull();
  });
});
