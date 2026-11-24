/**
 * Маршруты Claude запросов
 */

const express = require('express');
const router = express.Router();
const Joi = require('joi');
const { asyncHandler } = require('@philos/shared');
const claudeController = require('../controllers/claude.controller');
const { extractUserFromHeaders } = require('../middleware/auth.middleware');

// Middleware для извлечения данных пользователя из заголовков
router.use(extractUserFromHeaders);

//=============================================
// СХЕМЫ ВАЛИДАЦИИ
//=============================================

const graphDataSchema = Joi.object({
  graphData: Joi.object().required()
});

const categoryEnrichmentSchema = Joi.object({
  categoryData: Joi.object().required(),
  conceptName: Joi.string().required(),
  traditions: Joi.array().items(Joi.string()),
  philosophers: Joi.array().items(Joi.string())
});

const relationshipEnrichmentSchema = Joi.object({
  relationshipData: Joi.object().required(),
  category1: Joi.string().required(),
  category2: Joi.string().required(),
  conceptName: Joi.string().required()
});

const thesisGenerationSchema = Joi.object({
  graphData: Joi.object().required(),
  quantity: Joi.number().integer().min(1).max(20).required(),
  thesisType: Joi.string().required(),
  style: Joi.string().required()
});

const graphFromThesesSchema = Joi.object({
  theses: Joi.array().items(Joi.object()).min(1).required()
});

const conceptSynthesisSchema = Joi.object({
  concept1: Joi.object().required(),
  concept2: Joi.object().required(),
  method: Joi.string().required(),
  focus: Joi.string().required(),
  innovationDegree: Joi.string().required()
});

const compatibilitySchema = Joi.object({
  concept1: Joi.object().required(),
  concept2: Joi.object().required()
});

const dialogueSchema = Joi.object({
  concept1: Joi.object().required(),
  name1: Joi.string().required(),
  concept2: Joi.object().required(),
  name2: Joi.string().required(),
  topic: Joi.string().required(),
  options: Joi.object({
    format: Joi.string().valid('классический', 'платоновский', 'современный', 'дебаты'),
    length: Joi.string().valid('краткий', 'средний', 'развернутый'),
    focusPoints: Joi.array().items(Joi.string()),
    characterization: Joi.boolean()
  })
});

const historicalContextSchema = Joi.object({
  conceptData: Joi.object().required(),
  conceptName: Joi.string().required(),
  traditions: Joi.array().items(Joi.string()),
  philosophers: Joi.array().items(Joi.string()),
  timeContext: Joi.object({
    start: Joi.string(),
    end: Joi.string()
  })
});

const practicalApplicationSchema = Joi.object({
  conceptData: Joi.object().required(),
  conceptName: Joi.string().required(),
  domains: Joi.array().items(Joi.string()),
  detailed: Joi.boolean()
});

const conceptEvolutionSchema = Joi.object({
  conceptData: Joi.object().required(),
  conceptName: Joi.string().required()
});

const nameGenerationSchema = Joi.object({
  graphData: Joi.object(),
  theses: Joi.array().items(Joi.object())
}).or('graphData', 'theses');

const nameAnalysisSchema = Joi.object({
  name: Joi.string().required(),
  conceptData: Joi.object()
});

const synthesizedConceptSchema = Joi.object({
  synthesizedConcept: Joi.object().required()
});

// Middleware валидации
function validate(schema) {
  return (req, res, next) => {
    const { error, value } = schema.validate(req.body);
    
    if (error) {
      return res.status(400).json({
        success: false,
        error: {
          message: 'Ошибка валидации',
          details: error.details.map(d => ({
            field: d.path.join('.'),
            message: d.message
          }))
        }
      });
    }
    
    req.body = value;
    next();
  };
}

//=============================================
// МАРШРУТЫ - РАБОТА С ГРАФАМИ
//=============================================

// Валидация графа
router.post('/validate-graph',
  validate(graphDataSchema),
  asyncHandler(claudeController.validateGraph.bind(claudeController))
);

// Обогащение категории
router.post('/enrich-category',
  validate(categoryEnrichmentSchema),
  asyncHandler(claudeController.enrichCategory.bind(claudeController))
);

// Обогащение связи
router.post('/enrich-relationship',
  validate(relationshipEnrichmentSchema),
  asyncHandler(claudeController.enrichRelationship.bind(claudeController))
);

// Анализ происхождения графа
router.post('/analyze-graph-origin',
  validate(graphDataSchema),
  asyncHandler(claudeController.analyzeGraphOrigin.bind(claudeController))
);

//=============================================
// МАРШРУТЫ - РАБОТА С ТЕЗИСАМИ
//=============================================

// Генерация тезисов
router.post('/generate-theses',
  validate(thesisGenerationSchema),
  asyncHandler(claudeController.generateTheses.bind(claudeController))
);

// Генерация графа из тезисов
router.post('/generate-graph',
  validate(graphFromThesesSchema),
  asyncHandler(claudeController.generateGraphFromTheses.bind(claudeController))
);

// Анализ происхождения тезисов
router.post('/analyze-thesis-origin',
  validate(graphFromThesesSchema),
  asyncHandler(claudeController.analyzeThesisOrigin.bind(claudeController))
);

//=============================================
// МАРШРУТЫ - СИНТЕЗ И СОВМЕСТИМОСТЬ
//=============================================

// Синтез концепций
router.post('/synthesize',
  validate(conceptSynthesisSchema),
  asyncHandler(claudeController.synthesizeConcepts.bind(claudeController))
);

// Анализ совместимости
router.post('/analyze-compatibility',
  validate(compatibilitySchema),
  asyncHandler(claudeController.analyzeCompatibility.bind(claudeController))
);

// Критика синтеза
router.post('/critique-synthesis',
  validate(synthesizedConceptSchema),
  asyncHandler(claudeController.critiqueSynthesis.bind(claudeController))
);

//=============================================
// МАРШРУТЫ - ДИАЛОГИ
//=============================================

// Создание диалога
router.post('/create-dialogue',
  validate(dialogueSchema),
  asyncHandler(claudeController.createDialogue.bind(claudeController))
);

//=============================================
// МАРШРУТЫ - ИСТОРИЧЕСКИЙ И ПРАКТИЧЕСКИЙ АНАЛИЗ
//=============================================

// Историческая контекстуализация
router.post('/contextualize-historically',
  validate(historicalContextSchema),
  asyncHandler(claudeController.contextualizeHistorically.bind(claudeController))
);

// Практическое применение
router.post('/analyze-practical',
  validate(practicalApplicationSchema),
  asyncHandler(claudeController.analyzePracticalApplication.bind(claudeController))
);

// Эволюция концепции
router.post('/analyze-evolution',
  validate(conceptEvolutionSchema),
  asyncHandler(claudeController.analyzeConceptEvolution.bind(claudeController))
);

//=============================================
// МАРШРУТЫ - РАБОТА С НАЗВАНИЯМИ
//=============================================

// Генерация названия
router.post('/generate-name',
  validate(nameGenerationSchema),
  asyncHandler(claudeController.generateConceptName.bind(claudeController))
);

// Анализ названия
router.post('/analyze-name',
  validate(nameAnalysisSchema),
  asyncHandler(claudeController.analyzeConceptName.bind(claudeController))
);

//=============================================
// МАРШРУТЫ - ИСТОРИЯ И СТАТИСТИКА
//=============================================

// История взаимодействий
router.get('/interactions',
  asyncHandler(claudeController.getInteractionHistory.bind(claudeController))
);

// Детали взаимодействия
router.get('/interactions/:id',
  asyncHandler(claudeController.getInteractionDetails.bind(claudeController))
);

// Статистика пользователя
router.get('/stats',
  asyncHandler(claudeController.getUserStats.bind(claudeController))
);

module.exports = router;