// examples/create-concept-full-cycle.js

const { v4: uuidv4 } = require('uuid');
const DatabaseManager = require('../shared/lib/db/DatabaseManager');
const DataSynchronizer = require('../shared/lib/db/DataSynchronizer');
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
  SYNTHESIS_TYPES
} = require('../shared/constants/philosophy-constants');

async function createPhilosophicalConcept() {
  // Конфигурация подключения к БД
  const dbConfig = {
    postgres: {
      host: process.env.PG_HOST || 'localhost',
      port: process.env.PG_PORT || 5432,
      database: process.env.PG_DATABASE || 'philosophy_db',
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
      dbName: process.env.MONGODB_DB || 'philosophy_service'
    },
    redis: {
      host: process.env.REDIS_HOST || 'localhost',
      port: process.env.REDIS_PORT || 6379
    }
  };

  const dbManager = new DatabaseManager(dbConfig);
  const dataSynchronizer = new DataSynchronizer(dbManager);

  try {
    // 1. Инициализация подключений
    console.log('Initializing database connections...');
    await dbManager.initialize();

    // 2. Подготовка данных концепции
    const conceptId = uuidv4();
    const userId = '123e4567-e89b-12d3-a456-426614174000'; // Существующий пользователь

    const conceptData = {
      concept_id: conceptId,
      creator_id: userId,
      name: 'Диалектический материализм',
      description: 'Философское направление, синтезирующее диалектику и материализм',
      is_synthesis: true,
      parent_concepts: ['parent_id_1', 'parent_id_2'],
      synthesis_method: SYNTHESIS_TYPES.DIALECTICAL,
      innovation_degree: INNOVATION_LEVELS.EXTENDED,
      focus: 'методология познания'
    };

    // 3. Подготовка данных графа
    const graphData = {
      categories: [
        {
          category_id: uuidv4(),
          name: 'Материя',
          definition: 'Объективная реальность, существующая независимо от сознания',
          type: CATEGORY_TYPES.ONTOLOGICAL,
          characteristics: {
            [CATEGORY_CHARACTERISTICS.CENTRALITY]: 0.9,
            [CATEGORY_CHARACTERISTICS.CERTAINTY]: 0.95,
            [CATEGORY_CHARACTERISTICS.HISTORICAL_SIGNIFICANCE]: 0.88,
            [CATEGORY_CHARACTERISTICS.INNOVATION_DEGREE]: INNOVATION_LEVELS.TRADITIONAL,
            [CATEGORY_CHARACTERISTICS.CLARITY]: 0.85
          }
        },
        {
          category_id: uuidv4(),
          name: 'Сознание',
          definition: 'Свойство высокоорганизованной материи отражать объективный мир',
          type: CATEGORY_TYPES.EPISTEMOLOGICAL,
          characteristics: {
            [CATEGORY_CHARACTERISTICS.CENTRALITY]: 0.85,
            [CATEGORY_CHARACTERISTICS.CERTAINTY]: 0.9,
            [CATEGORY_CHARACTERISTICS.HISTORICAL_SIGNIFICANCE]: 0.82,
            [CATEGORY_CHARACTERISTICS.INNOVATION_DEGREE]: INNOVATION_LEVELS.REINTERPRETED,
            [CATEGORY_CHARACTERISTICS.BREADTH]: 0.8
          }
        },
        {
          category_id: uuidv4(),
          name: 'Диалектика',
          definition: 'Учение о всеобщих законах развития',
          type: CATEGORY_TYPES.METHODOLOGICAL,
          characteristics: {
            [CATEGORY_CHARACTERISTICS.CENTRALITY]: 0.95,
            [CATEGORY_CHARACTERISTICS.CERTAINTY]: 0.98,
            [CATEGORY_CHARACTERISTICS.HISTORICAL_SIGNIFICANCE]: 0.92,
            [CATEGORY_CHARACTERISTICS.INNOVATION_DEGREE]: INNOVATION_LEVELS.EXTENDED,
            [CATEGORY_CHARACTERISTICS.DEPTH]: 0.9
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
            [RELATIONSHIP_CHARACTERISTICS.STRENGTH]: 0.9,
            [RELATIONSHIP_CHARACTERISTICS.CERTAINTY]: 0.92,
            [RELATIONSHIP_CHARACTERISTICS.INNOVATION_DEGREE]: INNOVATION_LEVELS.REINTERPRETED,
            [RELATIONSHIP_CHARACTERISTICS.LOGICAL_NECESSITY]: 0.88
          }
        },
        {
          relationship_id: uuidv4(),
          source_id: graphData.categories[2].category_id,
          target_id: graphData.categories[0].category_id,
          type: RELATIONSHIP_TYPES.IMPLEMENTATION,
          direction: RELATIONSHIP_DIRECTIONS.UNIDIRECTIONAL,
          characteristics: {
            [RELATIONSHIP_CHARACTERISTICS.STRENGTH]: 0.88,
            [RELATIONSHIP_CHARACTERISTICS.CERTAINTY]: 0.9,
            [RELATIONSHIP_CHARACTERISTICS.INNOVATION_DEGREE]: INNOVATION_LEVELS.TRADITIONAL,
            [RELATIONSHIP_CHARACTERISTICS.CONTEXT_DEPENDENCE]: 0.7
          }
        }
      ]
    };

    // 4. Подготовка тезисов
    const thesesData = [
      {
        type: THESIS_TYPES.ONTOLOGICAL,
        content: 'Материя первична, сознание вторично',
        related_categories: [graphData.categories[0].category_id, graphData.categories[1].category_id],
        style: THESIS_STYLES.ACADEMIC,
        generation_parameters: { model: 'manual', template: 'ontological_thesis' }
      },
      {
        type: THESIS_TYPES.EPISTEMOLOGICAL,
        content: 'Познание есть отражение объективной реальности в сознании',
        related_categories: [graphData.categories[1].category_id],
        style: THESIS_STYLES.ANALYTICAL,
        generation_parameters: { model: 'manual', template: 'epistemological_thesis' }
      },
      {
        type: THESIS_TYPES.METHODOLOGICAL,
        content: 'Диалектический метод требует рассмотрения явлений в их развитии и взаимосвязи',
        related_categories: [graphData.categories[2].category_id],
        style: THESIS_STYLES.DIALECTICAL,
        generation_parameters: { model: 'manual', template: 'methodological_thesis' }
      }
    ];

    // 5. Практическое применение
    const practicalApplicationData = {
      domains: [
        {
          domain_name: PRACTICAL_DOMAINS.EDUCATION,
          relevance_score: 0.9,
          applications: [
            {
              description: "Применение диалектического подхода в образовательном процессе",
              example: "Рассмотрение противоречий и развития в изучаемых явлениях"
            }
          ]
        },
        {
          domain_name: PRACTICAL_DOMAINS.SCIENCE,
          relevance_score: 0.95,
          applications: [
            {
              description: "Использование материалистического подхода в научных исследованиях",
              example: "Учёт объективных закономерностей развития природы"
            }
          ]
        },
        {
          domain_name: PRACTICAL_DOMAINS.POLITICS,
          relevance_score: 0.85,
          applications: [
            {
              description: "Анализ социальных противоречий как движущей силы общественного развития",
              example: "Разработка политических стратегий на основе диалектических закономерностей"
            }
          ]
        }
      ],
      implementation_methods: [
        {
          method: "policy_change",
          description: "Реформирование политической системы на основе диалектического подхода",
          requirements: [
            "Анализ существующих противоречий",
            "Определение направления развития"
          ]
        },
        {
          method: "educational_curriculum",
          description: "Разработка учебных программ с учетом диалектико-материалистического подхода",
          requirements: [
            "Внедрение многоаспектного рассмотрения явлений",
            "Акцент на развитие критического мышления"
          ]
        }
      ]
    };

    // 5. Создание концепции с синхронизацией
    console.log('Creating concept with full synchronization...');
    const result = await dataSynchronizer.syncConceptCreation(
      conceptData,
      graphData,
      thesesData,
      practicalApplicationData
    );

    console.log('Concept created successfully:', result);

    // 6. Проверка данных в кэше
    const cachedData = await dataSynchronizer.getConceptFromCache(conceptId);
    console.log('Cached concept data:', cachedData);

    // 7. Демонстрация обновления данных
    console.log('Updating concept data...');
    const updateResult = await dataSynchronizer.syncConceptUpdate(conceptId, {
      metadata: {
        name: 'Диалектический материализм (обновленный)',
        description: 'Расширенное описание философского направления'
      },
      graph: {
        categoryUpdates: [
          {
            category_id: graphData.categories[0].category_id,
            updates: {
              characteristics: {
                [CATEGORY_CHARACTERISTICS.CENTRALITY]: 0.95,
                [CATEGORY_CHARACTERISTICS.CLARITY]: 0.9
              },
              definition: 'Обновленное определение материи как объективной реальности'
            }
          }
        ]
      },
      theses: [
        {
          thesis_id: 'thesis_id_1', // ID из MongoDB
          updates: {
            content: 'Обновленный тезис о первичности материи и вторичности сознания',
            style: THESIS_STYLES.DIALECTICAL
          }
        }
      ]
    });

    console.log('Update result:', updateResult);

    // 8. Демонстрация обработки ошибок и отката
    console.log('Demonstrating error handling...');
    try {
      await dataSynchronizer.syncConceptUpdate('non_existent_id', {
        metadata: { name: 'This will fail' }
      });
    } catch (error) {
      console.log('Expected error caught:', error.message);
    }

    // 9. Валидация целостности данных
    const DataIntegrityValidator = require('../shared/lib/db/DataIntegrityValidator');
    const validator = new DataIntegrityValidator(dbManager);
    
    console.log('Validating data integrity...');
    const validationResult = await validator.validateConcept(conceptId);
    console.log('Validation result:', validationResult);

    // 10. Получение полных данных концепции
    const completeData = await dataSynchronizer.getCompleteConceptData(conceptId);
    console.log('Complete concept data:', completeData);

  } catch (error) {
    console.error('Error in concept creation:', error);
    
    // Логирование ошибки для анализа
    await dbManager.postgresPool.query(
      `INSERT INTO error_logs (error_type, error_message, stack_trace, context)
       VALUES ($1, $2, $3, $4)`,
      ['concept_creation_error', error.message, error.stack, JSON.stringify({ conceptData })]
    );
    
    throw error;
  } finally {
    // 11. Закрытие соединений
    console.log('Closing database connections...');
    await dbManager.close();
  }
}

// Запуск примера
if (require.main === module) {
  createPhilosophicalConcept()
    .then(() => console.log('Example completed successfully'))
    .catch(error => {
      console.error('Example failed:', error);
      process.exit(1);
    });
}

module.exports = createPhilosophicalConcept;
