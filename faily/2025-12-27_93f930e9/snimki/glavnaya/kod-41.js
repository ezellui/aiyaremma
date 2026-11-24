/**
 * Конфигурация сервиса
 */

module.exports = {
  env: process.env.NODE_ENV || 'development',
  port: parseInt(process.env.PORT, 10) || 3000,
  serviceName: process.env.SERVICE_NAME || 'service-template',
  
  // CORS
  cors: {
    origin: process.env.CORS_ORIGIN || '*',
    credentials: true
  },
  
  // База данных
  database: {
    postgres: {
      host: process.env.POSTGRES_HOST || 'localhost',
      port: parseInt(process.env.POSTGRES_PORT, 10) || 5432,
      database: process.env.POSTGRES_DB || 'philos_concepts',
      user: process.env.POSTGRES_USER || 'philos',
      password: process.env.POSTGRES_PASSWORD || 'password',
      max: 20,
      idleTimeoutMillis: 30000,
      connectionTimeoutMillis: 2000
    },
    
    mongodb: {
      url: process.env.MONGO_URL || 'mongodb://philos:password@localhost:27017/philos_concepts'
    },
    
    neo4j: {
      url: process.env.NEO4J_URL || 'bolt://localhost:7687',
      user: process.env.NEO4J_USER || 'neo4j',
      password: process.env.NEO4J_PASSWORD || 'password'
    }
  },
  
  // Redis
  redis: {
    url: process.env.REDIS_URL || 'redis://localhost:6379',
    keyPrefix: `${process.env.SERVICE_NAME || 'service'}:`
  },
  
  // Внешние сервисы
  services: {
    concept: process.env.CONCEPT_SERVICE_URL || 'http://localhost:4002',
    graph: process.env.GRAPH_SERVICE_URL || 'http://localhost:4003',
    thesis: process.env.THESIS_SERVICE_URL || 'http://localhost:4004',
    claude: process.env.CLAUDE_SERVICE_URL || 'http://localhost:4006'
  },
  
  // Логирование
  logging: {
    level: process.env.LOG_LEVEL || 'debug'
  }
};