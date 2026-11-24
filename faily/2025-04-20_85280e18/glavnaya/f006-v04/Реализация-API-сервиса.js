// Главный алгоритм генерации новой концепции
async function generateCombinedConcept(requestId) {
  try {
    // Создаем контекст для логирования процесса
    const context = { requestId };
    logger.info(context, 'Starting concept generation process');
    
    // Получаем запрос из базы данных
    const request = await Request.findOne({ id: requestId });
    if (!request) {
      throw new Error('Request not found');
    }
    
    logger.info(context, `Processing request with ${request.selectedConcepts.length} selected concepts`);
    
    // Получаем выбранные концепции
    const conceptIds = request.selectedConcepts;
    const concepts = await Concept.find({ id: { $in: conceptIds } });
    
    if (concepts.length < conceptIds.length) {
      const missingIds = conceptIds.filter(id => !concepts.some(c => c.id === id));
      logger.warn(context, `Some concepts were not found: ${missingIds.join(', ')}`);
      throw new Error(`Some concepts not found: ${missingIds.join(', ')}`);
    }
    
    // Начинаем процесс обработки с извлечения и группировки тезисов
    logger.info(context, 'Extracting and grouping theses');
    const startTime = Date.now();
    
    const groupedTheses = await extractAndGroupTheses(concepts);
    
    logger.info(context, `Extracted theses grouped into ${Object.keys(groupedTheses).length} topics. Processing took ${Date.now() - startTime}ms`);
    
    // Находим конфликты между тезисами
    logger.info(context, 'Detecting conflicts between theses');
    const conflictDetectionStart = Date.now();
    
    const conflicts = await findConflicts(groupedTheses);
    
    logger.info(context, `Found ${conflicts.length} conflicts. Detection took ${Date.now() - conflictDetectionStart}ms`);
    
    // Анализируем конфликты для формирования более точного промпта
    const conflictAnalysis = analyzeConflicts(conflicts);
    logger.info(context, `Conflict analysis: ${JSON.stringify(conflictAnalysis)}`);
    
    // Обогащаем параметры генерации на основе анализа конфликтов
    const enhancedParams = enhanceGenerationParams(request.generationParams, conflictAnalysis);
    
    // Формируем запрос к Claude
    logger.info(context, 'Formatting prompt for Claude');
    const promptFormattingStart = Date.now();
    
    const prompt = await formatPromptForClaude(groupedTheses, conflicts, enhancedParams);
    
    logger.info(context, `Prompt formatting completed. Took ${Date.now() - promptFormattingStart}ms. Prompt length: ${prompt.length} characters`);
    
    // Проверяем длину промпта и при необходимости сокращаем
    const maxPromptLength = 100000; // Примерное ограничение для Claude API
    
    let finalPrompt = prompt;
    if (prompt.length > maxPromptLength) {
      logger.warn(context, `Prompt exceeds maximum length. Trimming from ${prompt.length} to ~${maxPromptLength} characters`);
      finalPrompt = await trimPrompt(prompt, maxPromptLength);
    }
    
    // Сохраняем копию промпта для отладки и анализа
    await savePromptForAnalysis(requestId, finalPrompt);
    
    // Отправляем запрос к Claude с мониторингом и обработкой ошибок
    logger.info(context, 'Sending request to Claude API');
    const claudeRequestStart = Date.now();
    
    let claudeResponse;
    try {
      // Настраиваем параметры запроса к Claude
      const claudeRequestParams = {
        prompt: finalPrompt,
        max_tokens: 4000,  // Достаточно для хорошего ответа
        temperature: 0.7   // Баланс между креативностью и согласованностью
      };
      
      // Добавляем пользовательские настройки, если они указаны
      if (enhancedParams.temperature) {
        claudeRequestParams.temperature = parseFloat(enhancedParams.temperature);
      }
      
      claudeResponse = await claude.sendMessage(claudeRequestParams);
      
      logger.info(context, `Claude response received. Took ${Date.now() - claudeRequestStart}ms. Response length: ${claudeResponse.completion?.length || 0} characters`);
    } catch (error) {
      logger.error(context, `Error calling Claude API: ${error.message}`);
      
      // Обновляем статус запроса в случае ошибки
      await Request.updateOne(
        { id: requestId },
        { 
          status: 'error',
          error: `Error calling Claude API: ${error.message}`
        }
      );
      
      throw new Error(`Failed to get response from Claude: ${error.message}`);
    }
    
    // Проверяем ответ Claude
    if (!claudeResponse || !claudeResponse.completion) {
      const errorMsg = 'Received invalid or empty response from Claude API';
      logger.error(context, errorMsg);
      
      // Обновляем статус запроса
      await Request.updateOne(
        { id: requestId },
        { 
          status: 'error',
          error: errorMsg
        }
      );
      
      throw new Error(errorMsg);
    }
    
    // Обрабатываем ответ и создаем новую концепцию
    logger.info(context, 'Processing Claude response and creating new concept');
    const processingStart = Date.now();
    
    const newConcept = await processClaudeResponse(claudeResponse, concepts);
    
    logger.info(context, `Response processing completed. Took ${Date.now() - processingStart}ms. Created concept "${newConcept.name}" with ${newConcept.theses.length} theses`);
    
    // Сохраняем новую концепцию в базу данных
    logger.info(context, 'Saving new concept to database');
    const conceptModel = new Concept(newConcept);
    const savedConcept = await conceptModel.save();
    
    // Добавляем ссылки на родительские концепции
    await createConceptRelations(savedConcept.id, conceptIds);
    
    // Обновляем статус запроса
    await Request.updateOne(
      { id: requestId },
      { 
        status: 'completed',
        result: savedConcept.id,
        completionTime: new Date()
      }
    );
    
    logger.info(context, `Concept generation completed successfully. Total time: ${Date.now() - startTime}ms`);
    
    return savedConcept;
  } catch (error) {
    logger.error({ requestId }, `Error generating concept: ${error.message}`);
    logger.error({ requestId, stack: error.stack }, 'Error stack trace');
    
    // Обновляем статус запроса в случае ошибки
    await Request.updateOne(
      { id: requestId },
      { 
        status: 'error',
        error: error.message
      }
    );
    
    throw error;
  }
}

// Вспомогательная функция для анализа конфликтов
function analyzeConflicts(conflicts) {
  // Инициализируем результат анализа
  const analysis = {
    totalConflicts: conflicts.length,
    severeConflicts: 0,
    topicDistribution: {},
    dominantConflictTypes: {},
    keyContradictions: []
  };
  
  // Подсчитываем количество серьезных конфликтов
  conflicts.forEach(conflict => {
    // Считаем конфликты по степени серьезности
    if (conflict.severity === 'high') {
      analysis.severeConflicts++;
    }
    
    // Распределение по темам
    const topic = conflict.topic || 'Общая философия';
    analysis.topicDistribution[topic] = (analysis.topicDistribution[topic] || 0) + 1;
    
    // Типы конфликтов
    const type = conflict.conflictType || 'Неопределенный';
    analysis.dominantConflictTypes[type] = (analysis.dominantConflictTypes[type] || 0) + 1;
    
    // Собираем ключевые противоречия (термины)
    if (conflict.terms && conflict.terms.length > 0) {
      analysis.keyContradictions.push(conflict.terms);
    }
  });
  
  // Преобразуем объекты в отсортированные массивы для более удобного использования
  analysis.topicDistribution = Object.entries(analysis.topicDistribution)
    .sort((a, b) => b[1] - a[1]);
  
  analysis.dominantConflictTypes = Object.entries(analysis.dominantConflictTypes)
    .sort((a, b) => b[1] - a[1]);
  
  return analysis;
}

// Функция для обогащения параметров генерации на основе анализа конфликтов
function enhanceGenerationParams(originalParams, conflictAnalysis) {
  const enhancedParams = { ...originalParams };
  
  // Если не указан подход к синтезу, предлагаем наиболее подходящий
  if (!enhancedParams.synthesisApproach) {
    if (conflictAnalysis.severeConflicts > 3) {
      // Для множества серьезных противоречий хорошо подходит диалектический подход
      enhancedParams.synthesisApproach = 'dialectical';
    } else if (conflictAnalysis.keyContradictions.length > 5) {
      // Для множества разнородных противоречий лучше интегративный подход
      enhancedParams.synthesisApproach = 'integrative';
    } else if (conflictAnalysis.topicDistribution.length > 3) {
      // Для разнообразия тем хорошо подходит прагматический подход
      enhancedParams.synthesisApproach = 'pragmatic';
    } else {
      // В остальных случаях можно предложить более творческий подход
      enhancedParams.synthesisApproach = 'revolutionary';
    }
  }
  
  // Предлагаем фокус на определенных темах, если он не указан явно
  if (!enhancedParams.focusTopics || enhancedParams.focusTopics.length === 0) {
    // Берем две наиболее конфликтные темы
    if (conflictAnalysis.topicDistribution.length > 0) {
      enhancedParams.focusTopics = conflictAnalysis.topicDistribution
        .slice(0, 2)
        .map(topic => topic[0]);
    }
  }
  
  return enhancedParams;
}

// Функция для сокращения длинного промпта
async function trimPrompt(prompt, maxLength) {
  // Разбиваем промпт на секции
  const sections = prompt.split(/\n##\s+/);
  const header = sections[0];
  const remainingSections = sections.slice(1);
  
  // Помечаем каждую секцию префиксом
  const taggedSections = remainingSections.map(section => {
    const title = section.split('\n')[0];
    return { title, content: "## " + section, importance: getSectionImportance(title) };
  });
  
  // Сортируем секции по важности (от наиболее важных к наименее важным)
  taggedSections.sort((a, b) => b.importance - a.importance);
  
  // Начинаем с заголовка и добавляем секции, пока не достигнем максимальной длины
  let trimmedPrompt = header;
  
  for (const section of taggedSections) {
    // Если добавление секции превысит лимит, попробуем сократить ее
    if (trimmedPrompt.length + section.content.length > maxLength) {
      // Для секций с тезисами можно сократить количество тезисов
      if (section.title.includes('тезисы') || section.title.includes('Имеющиеся тезисы')) {
        const trimmedSection = trimThesesSection(section.content, maxLength - trimmedPrompt.length);
        trimmedPrompt += '\n' + trimmedSection;
      } else {
        // Для других секций просто добавляем, если поместится
        if (trimmedPrompt.length + section.content.length <= maxLength) {
          trimmedPrompt += '\n' + section.content;
        }
      }
    } else {
      trimmedPrompt += '\n' + section.content;
    }
    
    // Если достигли лимита, прекращаем добавление
    if (trimmedPrompt.length >= maxLength * 0.95) {
      break;
    }
  }
  
  // Добавляем примечание о сокращении, если были обрезаны секции
  if (trimmedPrompt.length < prompt.length) {
    trimmedPrompt += `\n\n## Примечание\nПромпт был сокращен из-за ограничений длины. Сфокусируйся на наиболее важных аспектах синтеза.`;
  }
  
  return trimmedPrompt;
}

// Функция для определения важности секции
function getSectionImportance(sectionTitle) {
  const importanceRanking = {
    'Инструкция': 100,
    'Требуемый формат ответа': 95,
    'Обнаруженные противоречия': 90,
    'Имеющиеся тезисы по темам': 85,
    'Напоминание': 80,
    'Философская традиция': 75,
    'Фокус концепции': 70,
    'Дополнительные требования': 65,
    'Стилистические предпочтения': 60,
    'Исторический контекст': 55
  };
  
  // Ищем наиболее подходящий ключ
  for (const [key, value] of Object.entries(importanceRanking)) {
    if (sectionTitle.includes(key)) {
      return value;
    }
  }
  
  return 50; // средняя важность по умолчанию
}

// Функция для сокращения секции с тезисами
function trimThesesSection(section, maxLength) {
  // Разбиваем секцию на заголовок и темы
  const lines = section.split('\n');
  const header = lines[0];
  
  // Находим все подзаголовки тем и их позиции
  const topicIndices = [];
  for (let i = 1; i < lines.length; i++) {
    if (lines[i].startsWith('### ')) {
      topicIndices.push(i);
    }
  }
  
  // Добавляем индекс конца для последней темы
  topicIndices.push(lines.length);
  
  // Разбиваем на темы с их содержимым
  const topics = [];
  for (let i = 0; i < topicIndices.length - 1; i++) {
    const topicStart = topicIndices[i];
    const topicEnd = topicIndices[i + 1];
    topics.push(lines.slice(topicStart, topicEnd).join('\n'));
  }
  
  // Определяем, сколько тезисов можно включить в каждую тему
  // Предполагаем, что у нас есть N тем и можем включить maxThesesPerTopic тезисов в каждую
  const approxLengthPerThesis = 100; // примерная длина одного тезиса
  const maxTotalTheses = Math.floor(maxLength / approxLengthPerThesis);
  const maxThesesPerTopic = Math.max(2, Math.floor(maxTotalTheses / topics.length));
  
  // Обрезаем каждую тему до указанного количества тезисов
  const trimmedTopics = topics.map(topic => {
    const topicLines = topic.split('\n');
    const topicHeader = topicLines[0];
    
    // Выбираем только первые maxThesesPerTopic тезисов
    const theses = topicLines.slice(1).filter(line => /^\d+\./.test(line)).slice(0, maxThesesPerTopic);
    
    // Собираем обратно с заголовком
    return [topicHeader, ...theses, `*Показаны ${theses.length} тезисов из этой темы.*`].// API сервис (Node.js + Express)

const express = require('express');
const cors = require('cors');
const { v4: uuidv4 } = require('uuid');
const mongoose = require('mongoose');
const ClaudeClient = require('./claude-client');

const app = express();
app.use(cors());
app.use(express.json());

// Подключение к MongoDB
mongoose.connect('mongodb://localhost:27017/philosophy-db');

// Схемы данных
const ThesisSchema = new mongoose.Schema({
  id: { type: String, default: () => uuidv4() },
  content: { type: String, required: true },
  keywords: [String],
  topics: [String],
  source: { type: String, required: true }
});

const ConceptSchema = new mongoose.Schema({
  id: { type: String, default: () => uuidv4() },
  name: { type: String, required: true },
  description: { type: String, required: true },
  source: { type: String, required: true },
  authors: [String],
  creationDate: { type: Date, default: Date.now },
  theses: [ThesisSchema],
  parentConcepts: [String]
});

const RequestSchema = new mongoose.Schema({
  id: { type: String, default: () => uuidv4() },
  user: { type: String, required: true },
  selectedConcepts: [String],
  generationParams: Object,
  result: String,
  status: { 
    type: String, 
    enum: ['processing', 'completed', 'error'],
    default: 'processing' 
  },
  creationDate: { type: Date, default: Date.now }
});

// Модели
const Concept = mongoose.model('Concept', ConceptSchema);
const Request = mongoose.model('Request', RequestSchema);

// Инициализация клиента Claude
const claude = new ClaudeClient({
  apiKey: process.env.CLAUDE_API_KEY,
  model: 'claude-3-7-sonnet-20250219'
});

// API эндпоинты
// 1. Получение списка всех концепций
app.get('/api/concepts', async (req, res) => {
  try {
    const concepts = await Concept.find({}).select('id name description authors source');
    res.json(concepts);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 2. Получение концепции по ID
app.get('/api/concepts/:id', async (req, res) => {
  try {
    const concept = await Concept.findOne({ id: req.params.id });
    if (!concept) {
      return res.status(404).json({ error: 'Concept not found' });
    }
    res.json(concept);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 3. Создание новой комбинированной концепции
app.post('/api/generate', async (req, res) => {
  try {
    const { selectedConcepts, generationParams, userId } = req.body;
    
    if (!selectedConcepts || selectedConcepts.length < 2) {
      return res.status(400).json({ error: 'At least two concepts are required' });
    }
    
    // Создаем запись о запросе
    const request = new Request({
      id: uuidv4(),
      user: userId,
      selectedConcepts,
      generationParams,
      status: 'processing'
    });
    
    await request.save();
    
    // Запускаем асинхронную обработку
    generateCombinedConcept(request.id);
    
    res.json({ 
      requestId: request.id,
      message: 'Generation started' 
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 4. Проверка статуса запроса
app.get('/api/requests/:id', async (req, res) => {
  try {
    const request = await Request.findOne({ id: req.params.id });
    if (!request) {
      return res.status(404).json({ error: 'Request not found' });
    }
    
    // Если запрос завершен, добавляем информацию о результате
    if (request.status === 'completed' && request.result) {
      const concept = await Concept.findOne({ id: request.result });
      return res.json({
        request,
        result: concept
      });
    }
    
    res.json({ request });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Алгоритм генерации новой концепции
async function generateCombinedConcept(requestId) {
  try {
    // Получаем запрос
    const request = await Request.findOne({ id: requestId });
    if (!request) throw new Error('Request not found');
    
    // Получаем выбранные концепции
    const conceptIds = request.selectedConcepts;
    const concepts = await Concept.find({ id: { $in: conceptIds } });
    
    if (concepts.length < conceptIds.length) {
      throw new Error('Some concepts not found');
    }
    
    // Извлекаем и группируем тезисы
    const groupedTheses = extractAndGroupTheses(concepts);
    
    // Находим конфликты между тезисами
    const conflicts = findConflicts(groupedTheses);
    
    // Формируем запрос к Claude
    const prompt = formatPromptForClaude(groupedTheses, conflicts, request.generationParams);
    
    // Отправляем запрос к Claude
    const claudeResponse = await claude.sendMessage({
      prompt: prompt,
      max_tokens: 4000
    });
    
    // Обрабатываем ответ и создаем новую концепцию
    const newConcept = processClaudeResponse(claudeResponse, concepts);
    
    // Сохраняем новую концепцию
    const conceptModel = new Concept(newConcept);
    await conceptModel.save();
    
    // Обновляем статус запроса
    request.status = 'completed';
    request.result = newConcept.id;
    await request.save();
    
  } catch (error) {
    console.error('Error generating concept:', error);
    
    // Обновляем статус запроса в случае ошибки
    await Request.updateOne(
      { id: requestId },
      { status: 'error', error: error.message }
    );
  }
}

// Функция извлечения и группировки тезисов
function extractAndGroupTheses(concepts) {
  // Собираем все тезисы из концепций
  let allTheses = [];
  
  concepts.forEach(concept => {
    const thesesWithSource = concept.theses.map(thesis => ({
      ...thesis,
      conceptName: concept.name,
      conceptId: concept.id
    }));
    
    allTheses = allTheses.concat(thesesWithSource);
  });
  
  // Группируем по темам
  const groupedByTopic = {};
  
  allTheses.forEach(thesis => {
    thesis.topics.forEach(topic => {
      if (!groupedByTopic[topic]) {
        groupedByTopic[topic] = [];
      }
      groupedByTopic[topic].push(thesis);
    });
  });
  
  return groupedByTopic;
}

// Функция поиска конфликтов между тезисами
async function findConflicts(groupedTheses) {
  try {
    const conflicts = [];
    
    // Анализируем тезисы в каждой тематической группе
    for (const [topic, theses] of Object.entries(groupedTheses)) {
      // Для оптимизации производительности ограничиваем количество сравнений
      // для очень больших групп тезисов
      const maxComparisons = 50;
      let comparisonCount = 0;
      
      // Сравниваем каждую пару тезисов
      for (let i = 0; i < theses.length; i++) {
        for (let j = i + 1; j < theses.length; j++) {
          // Проверяем лимит сравнений для большой группы тезисов
          if (theses.length > 10 && comparisonCount >= maxComparisons) break;
          
          const thesis1 = theses[i];
          const thesis2 = theses[j];
          
          // Проверяем, из разных ли они концепций
          if (thesis1.conceptId !== thesis2.conceptId) {
            // Используем расширенный алгоритм определения противоречий
            const conflict = await detectConflicts(thesis1, thesis2);
            
            if (conflict) {
              conflicts.push({
                thesis1: {
                  id: thesis1.id,
                  content: thesis1.content,
                  conceptName: thesis1.conceptName,
                  conceptId: thesis1.conceptId
                },
                thesis2: {
                  id: thesis2.id,
                  content: thesis2.content,
                  conceptName: thesis2.conceptName,
                  conceptId: thesis2.conceptId
                },
                conflictType: conflict.type,
                description: conflict.description,
                severity: conflict.severity,
                topic,
                terms: conflict.terms || []
              });
            }
            
            comparisonCount++;
          }
        }
      }
    }
    
    // Дополнительно ищем противоречия между тезисами из разных тематических групп,
    // которые могут иметь общие ключевые слова
    
    // Создаем плоский список всех тезисов с информацией о группе
    const allThesesWithTopics = [];
    Object.entries(groupedTheses).forEach(([topic, theses]) => {
      theses.forEach(thesis => {
        allThesesWithTopics.push({...thesis, groupTopic: topic});
      });
    });
    
    // Строим индекс тезисов по ключевым словам для быстрого поиска
    const keywordIndex = {};
    allThesesWithTopics.forEach(thesis => {
      thesis.keywords.forEach(keyword => {
        if (!keywordIndex[keyword]) {
          keywordIndex[keyword] = [];
        }
        keywordIndex[keyword].push(thesis);
      });
    });
    
    // Ищем потенциальные конфликты на основе общих ключевых слов
    const processedPairs = new Set(); // для отслеживания уже проверенных пар
    
    for (const [keyword, thesesWithKeyword] of Object.entries(keywordIndex)) {
      // Пропускаем слишком общие ключевые слова, которые могут давать много ложных срабатываний
      if (thesesWithKeyword.length > 10) continue;
      
      // Сравниваем тезисы с одинаковым ключевым словом, но из разных групп
      for (let i = 0; i < thesesWithKeyword.length; i++) {
        for (let j = i + 1; j < thesesWithKeyword.length; j++) {
          const thesis1 = thesesWithKeyword[i];
          const thesis2 = thesesWithKeyword[j];
          
          // Проверяем, из разных ли они концепций и не из одной ли они группы
          if (thesis1.conceptId !== thesis2.conceptId && 
              thesis1.groupTopic !== thesis2.groupTopic) {
            
            // Создаем уникальный идентификатор пары для проверки дубликатов
            const pairId = [thesis1.id, thesis2.id].sort().join('-');
            
            if (!processedPairs.has(pairId)) {
              processedPairs.add(pairId);
              
              // Проверяем на конфликт
              const conflict = await detectConflicts(thesis1, thesis2);
              
              if (conflict) {
                conflicts.push({
                  thesis1: {
                    id: thesis1.id,
                    content: thesis1.content,
                    conceptName: thesis1.conceptName,
                    conceptId: thesis1.conceptId
                  },
                  thesis2: {
                    id: thesis2.id,
                    content: thesis2.content,
                    conceptName: thesis2.conceptName,
                    conceptId: thesis2.conceptId
                  },
                  conflictType: conflict.type,
                  description: conflict.description,
                  severity: conflict.severity,
                  topic: 'Междисциплинарный конфликт',
                  crossTopics: [thesis1.groupTopic, thesis2.groupTopic],
                  terms: conflict.terms || []
                });
              }
            }
          }
        }
      }
    }
    
    // Сортируем конфликты по степени серьезности
    conflicts.sort((a, b) => {
      const severityRank = { 'high': 3, 'medium': 2, 'low': 1 };
      return severityRank[b.severity] - severityRank[a.severity];
    });
    
    // Ограничиваем количество возвращаемых конфликтов, чтобы не перегружать промпт
    const maxConflicts = 10;
    return conflicts.slice(0, maxConflicts);
  } catch (error) {
    console.error('Error in conflict detection:', error);
    return [];
  }
}

// Расширенная функция определения противоречий между тезисами
async function detectConflicts(thesis1, thesis2) {
  try {
    // Расширенный словарь противоположных понятий
    const opposites = {
      // Онтологические противоположности
      'объективный': ['субъективный'],
      'субъективный': ['объективный'],
      'материальный': ['идеальный', 'нематериальный', 'духовный'],
      'идеальный': ['материальный', 'вещественный'],
      'реальный': ['иллюзорный', 'фиктивный', 'воображаемый'],
      'конечный': ['бесконечный', 'безграничный'],
      'бесконечный': ['конечный', 'ограниченный'],
      'абсолютный': ['относительный'],
      'относительный': ['абсолютный'],
      'необходимый': ['случайный', 'произвольный'],
      'случайный': ['необходимый', 'закономерный'],
      
      // Гносеологические противоположности
      'рационализм': ['эмпиризм', 'сенсуализм', 'иррационализм'],
      'эмпиризм': ['рационализм', 'априоризм'],
      'истинный': ['ложный', 'ошибочный', 'заблуждение'],
      'достоверный': ['вероятностный', 'гипотетический'],
      'априорный': ['апостериорный'],
      'апостериорный': ['априорный'],
      'аналитический': ['синтетический'],
      'синтетический': ['аналитический'],
      
      // Онтологические системы
      'монизм': ['дуализм', 'плюрализм'],
      'дуализм': ['монизм', 'плюрализм'],
      'плюрализм': ['монизм'],
      'материализм': ['идеализм', 'солипсизм'],
      'идеализм': ['материализм', 'натурализм'],
      'реализм': ['номинализм', 'антиреализм', 'конструктивизм'],
      'номинализм': ['реализм', 'концептуализм'],
      'детерминизм': ['индетерминизм', 'свобода воли'],
      'фатализм': ['волюнтаризм'],
      
      // Этические противоположности
      'добро': ['зло'],
      'альтруизм': ['эгоизм'],
      'утилитаризм': ['деонтология'],
      'эвдемонизм': ['гедонизм'],
      'объективизм': ['субъективизм', 'релятивизм'],
      'релятивизм': ['абсолютизм', 'универсализм'],
      'коллективизм': ['индивидуализм'],
      
      // Социально-политические противоположности
      'свобода': ['необходимость', 'тоталитаризм'],
      'равенство': ['иерархия', 'неравенство'],
      'справедливость': ['несправедливость', 'произвол'],
      'либерализм': ['консерватизм', 'авторитаризм'],
      'капитализм': ['социализм', 'коммунизм'],
      'прогресс': ['регресс', 'деградация', 'консерватизм'],
      'революция': ['эволюция', 'традиция']
    };
    
    // Расширяем словарь, добавляя производные формы слов
    const expandedOpposites = {...opposites};
    Object.entries(opposites).forEach(([key, values]) => {
      // Добавляем производные прилагательных
      if (key.endsWith('ый') || key.endsWith('ий') || key.endsWith('ой')) {
        const stem = key.slice(0, -2);
        expandedOpposites[stem + 'ого'] = values;
        expandedOpposites[stem + 'ому'] = values;
        expandedOpposites[stem + 'ым'] = values;
        expandedOpposites[stem + 'ом'] = values;
        expandedOpposites[stem + 'ая'] = values;
        expandedOpposites[stem + 'ое'] = values;
        expandedOpposites[stem + 'ые'] = values;
      }
      // Добавляем существительные
      else if (key.endsWith('изм')) {
        expandedOpposites[key + 'а'] = values;
        expandedOpposites[key + 'у'] = values;
        expandedOpposites[key + 'ом'] = values;
        expandedOpposites[key + 'е'] = values;
      }
    });
    
    // Объединяем ключевые слова и содержание для более полного анализа
    const thesis1Words = [...thesis1.keywords, ...thesis1.content.toLowerCase().split(/\s+/)];
    const thesis2Words = [...thesis2.keywords, ...thesis2.content.toLowerCase().split(/\s+/)];
    
    // Проверка на прямые противоположности
    for (const word1 of thesis1Words) {
      if (expandedOpposites[word1]) {
        for (const word2 of thesis2Words) {
          if (expandedOpposites[word1].includes(word2)) {
            return {
              type: 'Противоположные понятия',
              description: `Противоположные концепции: "${word1}" и "${word2}"`,
              severity: 'high',
              terms: [word1, word2]
            };
          }
        }
      }
    }
    
    // Проверка на отрицание тезисов
    const negationPatterns = [
      /не [а-яА-Я]+/g,  // например, "не существует"
      /нет [а-яА-Я]+/g, // например, "нет бога"
      /отсутств[а-яА-Я]+ [а-яА-Я]+/g, // например, "отсутствует свобода"
      /невозможн[а-яА-Я]+ [а-яА-Я]+/g, // например, "невозможно познание"
      /отрица[а-яА-Я]+ [а-яА-Я]+/g  // например, "отрицание бытия"
    ];
    
    // Ищем негативные конструкции в тезисах
    const findNegations = (text) => {
      const results = [];
      negationPatterns.forEach(pattern => {
        const matches = text.toLowerCase().match(pattern);
        if (matches) results.push(...matches);
      });
      return results;
    };
    
    const negations1 = findNegations(thesis1.content);
    const negations2 = findNegations(thesis2.content);
    
    // Проверка, содержит ли один тезис отрицание утверждения из другого
    const checkNegationConflict = () => {
      // Извлекаем ключевые утверждения из каждого тезиса
      const statements1 = extractStatements(thesis1.content);
      const statements2 = extractStatements(thesis2.content);
      
      // Проверяем, есть ли в первом тезисе отрицание утверждения из второго
      for (const statement1 of statements1) {
        for (const statement2 of statements2) {
          if (isNegation(statement1, statement2)) {
            return {
              type: 'Противоречащие утверждения',
              description: `Утверждение "${statement1}" противоречит "${statement2}"`,
              severity: 'high',
              statements: [statement1, statement2]
            };
          }
        }
      }
      
      return null;
    };
    
    // Функция для извлечения ключевых утверждений из текста
    const extractStatements = (text) => {
      // Разбиваем текст на предложения
      const sentences = text.split(/(?<=\.|\?|\!)\s+/);
      
      // Извлекаем простые утверждения
      // В реальной реализации здесь был бы более сложный NLP-анализ
      return sentences.map(sentence => 
        sentence.replace(/[.,;:'"?!()]/g, '')
                .replace(/\s+/g, ' ')
                .trim()
      ).filter(s => s.length > 0);
    };
    
    // Функция для проверки, является ли одно утверждение отрицанием другого
    const isNegation = (statement1, statement2) => {
      // Упрощенная проверка: если удаление "не" из одного утверждения делает его похожим на другое
      const withoutNegation = statement1.replace(/\bне\s+/g, '');
      
      // Если после удаления отрицания утверждения становятся похожими
      if (similarityScore(withoutNegation, statement2) > 0.7) {
        return true;
      }
      
      return false;
    };
    
    // Функция для оценки похожести двух строк (простая метрика)
    const similarityScore = (str1, str2) => {
      const words1 = str1.toLowerCase().split(/\s+/).filter(w => w.length > 3);
      const words2 = str2.toLowerCase().split(/\s+/).filter(w => w.length > 3);
      
      let matches = 0;
      for (const word1 of words1) {
        if (words2.some(word2 => word2.includes(word1) || word1.includes(word2))) {
          matches++;
        }
      }
      
      // Коэффициент совпадения
      return words1.length > 0 ? matches / words1.length : 0;
    };
    
    // Проверяем наличие противоречивых утверждений
    const negationConflict = checkNegationConflict();
    if (negationConflict) {
      return negationConflict;
    }
    
    // Проверка на основе тематики
    // Если тезисы относятся к одной теме, но имеют противоположные ключевые слова
    const sharedTopics = thesis1.topics.filter(topic => thesis2.topics.includes(topic));
    
    if (sharedTopics.length > 0) {
      // Если у тезисов одинаковая тема, проверяем наличие характерных противоречий для этой темы
      const topic = sharedTopics[0];
      
      // Специфические противоречия для разных тем
      const topicSpecificConflicts = {
        'Онтология': {
          patterns: [
            { term1: 'существу', term2: 'не существу' },
            { term1: 'реаль', term2: 'иллюз' },
            { term1: 'множествен', term2: 'единств' }
          ]
        },
        'Гносеология': {
          patterns: [
            { term1: 'познава', term2: 'непознава' },
            { term1: 'истин', term2: 'ложн' },
            { term1: 'объектив', term2: 'субъектив' }
          ]
        },
        'Этика': {
          patterns: [
            { term1: 'добро', term2: 'зло' },
            { term1: 'должн', term2: 'недолжн' },
            { term1: 'универсал', term2: 'относитель' }
          ]
        }
        // Другие темы можно добавить по аналогии
      };
      
      if (topicSpecificConflicts[topic]) {
        for (const pattern of topicSpecificConflicts[topic].patterns) {
          if ((thesis1.content.includes(pattern.term1) && thesis2.content.includes(pattern.term2)) ||
              (thesis1.content.includes(pattern.term2) && thesis2.content.includes(pattern.term1))) {
            return {
              type: 'Тематическое противоречие',
              description: `Противоречие в рамках темы "${topic}": "${pattern.term1}" vs "${pattern.term2}"`,
              severity: 'medium',
              topic: topic,
              terms: [pattern.term1, pattern.term2]
            };
          }
        }
      }
    }
    
    // Проверка на логическую несовместимость (если оба тезиса не могут быть одновременно истинными)
    // Это более сложный анализ, который может потребовать NLP или даже вызов Claude
    // В данной реализации упрощенно ищем ключевые маркеры
    
    const logicalConflictMarkers = {
      exclusive: [
        { term1: 'только', term2: 'не только' },
        { term1: 'исключительно', term2: 'включительно' },
        { term1: 'всегда', term2: 'иногда' },
        { term1: 'никогда', term2: 'иногда' },
        { term1: 'все', term2: 'некоторые' },
        { term1: 'ни один', term2: 'некоторые' }
      ]
    };
    
    for (const marker of logicalConflictMarkers.exclusive) {
      if ((thesis1.content.includes(marker.term1) && thesis2.content.includes(marker.term2)) ||
          (thesis1.content.includes(marker.term2) && thesis2.content.includes(marker.term1))) {
        return {
          type: 'Логическое противоречие',
          description: `Логически несовместимые утверждения: "${marker.term1}" и "${marker.term2}"`,
          severity: 'medium',
          terms: [marker.term1, marker.term2]
        };
      }
    }
    
    // Если явных противоречий не нашли, проверяем более тонкие связи
    // В сложной реализации здесь мог бы быть вызов Claude для анализа
    
    // Проверяем конфликт философских традиций
    const philosophicalTraditions = {
      'материализм': ['идеализм', 'дуализм'],
      'эмпиризм': ['рационализм', 'априоризм'],
      'атеизм': ['теизм', 'деизм'],
      'детерминизм': ['индетерминизм']
    };
    
    for (const [tradition1, opposingTraditions] of Object.entries(philosophicalTraditions)) {
      if (thesis1.content.toLowerCase().includes(tradition1)) {
        for (const tradition2 of opposingTraditions) {
          if (thesis2.content.toLowerCase().includes(tradition2)) {
            return {
              type: 'Конфликт философских традиций',
              description: `Противоречие философских традиций: "${tradition1}" и "${tradition2}"`,
              severity: 'low',
              terms: [tradition1, tradition2]
            };
          }
        }
      }
    }
    
    // Если не нашли явных противоречий
    return null;
  } catch (error) {
    console.error('Error in conflict detection:', error);
    return null;
  }
}

// Функция форматирования запроса к Claude
async function formatPromptForClaude(groupedTheses, conflicts, params) {
  try {
    let prompt = `
# Задача: создание новой философской концепции

## Имеющиеся тезисы по темам:
`;
    
    // Форматируем тезисы по темам
    // Ограничиваем количество тезисов по каждой теме, чтобы не перегружать промпт
    const maxThesesPerTopic = 8;
    
    for (const [topic, theses] of Object.entries(groupedTheses)) {
      prompt += `\n### ${topic}\n`;
      
      // Если тезисов слишком много, выбираем самые важные
      const selectedTheses = theses.length > maxThesesPerTopic 
        ? selectMostImportantTheses(theses, maxThesesPerTopic)
        : theses;
      
      selectedTheses.forEach((thesis, index) => {
        prompt += `${index + 1}. "${thesis.content}" (из концепции "${thesis.conceptName}")\n`;
      });
      
      // Если были отфильтрованы тезисы, добавляем примечание
      if (theses.length > maxThesesPerTopic) {
        prompt += `*Примечание: показаны ${maxThesesPerTopic} из ${theses.length} тезисов по данной теме.*\n`;
      }
    }
    
    // Добавляем информацию о конфликтах
    if (conflicts.length > 0) {
      prompt += `\n## Обнаруженные противоречия:\n`;
      
      conflicts.forEach((conflict, index) => {
        prompt += `
${index + 1}. ${conflict.conflictType}${conflict.crossTopics ? ` (между темами ${conflict.crossTopics.join(' и ')})` : ` (в теме "${conflict.topic}")`}:
   - "${conflict.thesis1.content}" (из концепции "${conflict.thesis1.conceptName}")
   - "${conflict.thesis2.content}" (из концепции "${conflict.thesis2.conceptName}")
   - Описание противоречия: ${conflict.description}
`;
      });
    }
    
    // Добавляем инструкцию по генерации с учетом возможных предпочтений пользователя
    prompt += `
## Инструкция:
Создай новую философскую концепцию, которая:
1. Синтезирует предоставленные тезисы в единую систему
2. Разрешает указанные противоречия, предлагая новые подходы или переосмысление терминов
3. Предлагает новую перспективу, объединяющую элементы исходных концепций
4. Создает целостное философское видение, которое может стать основой для дальнейшего развития мысли
`;
    
    // Определяем предпочтительный подход к синтезу на основе параметров
    if (params && params.synthesisApproach) {
      switch (params.synthesisApproach) {
        case 'dialectical':
          prompt += `
Используй диалектический подход к синтезу (тезис-антитезис-синтез), находя более высокий уровень, на котором противоречия разрешаются.
`;
          break;
        case 'pragmatic':
          prompt += `
Используй прагматический подход, оценивая тезисы по их практической применимости и полезности для решения философских проблем.
`;
          break;
        case 'integrative':
          prompt += `
Используй интегративный подход, рассматривая разные тезисы как взаимодополняющие аспекты единой реальности или как описания различных уровней одного и того же явления.
`;
          break;
        case 'revolutionary':
          prompt += `
Используй революционный подход, предлагая радикально новый взгляд, который выходит за рамки существующих концепций, но при этом объясняет их ограниченную правоту.
`;
          break;
      }
    }
    
    prompt += `
## Требуемый формат ответа:
1. Название концепции (краткое и отражающее суть)
2. Краткое описание (3-5 предложений, поясняющих основную идею)
3. Список 5-10 ключевых тезисов, четко сформулированных и пронумерованных
4. Отношение к исходным концепциям (как они были интегрированы, преобразованы или преодолены)
5. Методологическое обоснование (какие принципы и подходы использовались для создания новой концепции)
`;
    
    // Обработка дополнительных требований пользователя
    if (params) {
      // Добавляем предпочтения по философской традиции
      if (params.philosophicalTradition) {
        prompt += `\n## Философская традиция:\nРазработай концепцию в русле ${params.philosophicalTradition} традиции.\n`;
      }
      
      // Добавляем предпочтения по историческому периоду
      if (params.historicalContext) {
        prompt += `\n## Исторический контекст:\nСоздай концепцию, которая могла бы возникнуть в контексте ${params.historicalContext}.\n`;
      }
      
      // Добавляем акцент на определенных темах
      if (params.focusTopics && params.focusTopics.length > 0) {
        prompt += `\n## Фокус концепции:\nУдели особое внимание следующим темам: ${params.focusTopics.join(', ')}.\n`;
      }
      
      // Добавляем дополнительные требования
      if (params.additionalRequirements) {
        prompt += `\n## Дополнительные требования:\n${params.additionalRequirements}\n`;
      }
      
      // Добавляем стилистические предпочтения
      if (params.style) {
        prompt += `\n## Стилистические предпочтения:\n${params.style}\n`;
      }
    }
    
    // Добавляем напоминание о задаче и ограничениях
    prompt += `
## Напоминание:
- Обеспечь внутреннюю согласованность концепции
- Стремись к оригинальности, но сохраняй связь с исходными концепциями
- Используй точные философские термины, но избегай излишней терминологической сложности
- Концепция должна предлагать новый взгляд, а не просто обобщать существующие идеи
- Обрати особое внимание на разрешение выявленных противоречий
`;
    
    return prompt;
  } catch (error) {
    console.error('Error formatting prompt for Claude:', error);
    // Возвращаем базовый промпт в случае ошибки
    return `
# Задача: создание новой философской концепции

Синтезируй новую философскую концепцию на основе предоставленных тезисов, 
разрешая обнаруженные противоречия и предлагая новую перспективу.

Формат ответа:
1. Название концепции
2. Краткое описание
3. 5-7 ключевых тезисов
4. Отношение к исходным концепциям
`;
  }
}

// Вспомогательная функция для выбора наиболее важных тезисов из большого набора
function selectMostImportantTheses(theses, maxCount) {
  // Создаем систему оценки важности тезисов
  const scoredTheses = theses.map(thesis => {
    let score = 0;
    
    // Длина тезиса (в разумных пределах)
    const contentLength = thesis.content.length;
    if (contentLength > 30 && contentLength < 300) {
      score += contentLength / 100; // Больший вес для тезисов средней длины
    } else if (contentLength >= 300) {
      score += 3;
    } else {
      score += 0.3;
    }
    
    // Количество ключевых слов
    score += thesis.keywords.length * 0.5;
    
    // Наличие философских терминов (упрощенно)
    const philosophicalTerms = [
      'бытие', 'сознание', 'познание', 'истина', 'материя', 'идея',
      'субстанция', 'метод', 'система', 'диалектика', 'категория'
    ];
    
    for (const term of philosophicalTerms) {
      if (thesis.content.toLowerCase().includes(term)) {
        score += 0.7;
      }
    }
    
    return { thesis, score };
  });
  
  // Сортируем по убыванию оценки и берем maxCount тезисов
  return scoredTheses
    .sort((a, b) => b.score - a.score)
    .slice(0, maxCount)
    .map(item => item.thesis);
}

// Функция обработки ответа Claude
function processClaudeResponse(response, sourceConcepts) {
  // Парсинг ответа
  // В реальной реализации требуется более сложный парсинг
  
  const lines = response.content.split('\n');
  
  // Извлекаем название (первая строка)
  const name = lines[0].replace('#', '').trim();
  
  // Извлекаем описание (следующие несколько строк до списка тезисов)
  let description = '';
  let currentLine = 1;
  
  while (currentLine < lines.length && !lines[currentLine].includes('Тезис')) {
    if (lines[currentLine].trim() !== '') {
      description += lines[currentLine].trim() + ' ';
    }
    currentLine++;
  }
  
  // Извлекаем тезисы
  const theses = [];
  let thesisMode = false;
  
  for (let i = currentLine; i < lines.length; i++) {
    const line = lines[i].trim();
    
    if (line.match(/^\d+\.\s/) && (line.includes('Тезис') || thesisMode)) {
      thesisMode = true;
      const thesisContent = line.replace(/^\d+\.\s/, '').trim();
      
      theses.push({
        id: uuidv4(),
        content: thesisContent,
        keywords: extractKeywords(thesisContent),
        topics: determineTopics(thesisContent),
        source: 'generated'
      });
    } else if (thesisMode && line === '') {
      // Пустая строка после тезисов означает конец списка
      thesisMode = false;
    }
  }
  
  // Создаем новую концепцию
  const newConcept = {
    id: uuidv4(),
    name,
    description: description.trim(),
    source: 'generated',
    authors: ['Claude 3.7'],
    creationDate: new Date(),
    theses,
    parentConcepts: sourceConcepts.map(c => c.id)
  };
  
  return newConcept;
}

// Функция извлечения ключевых слов из тезиса с использованием NLP
async function extractKeywords(thesisContent) {
  try {
    // Расширенный словарь философских терминов
    const commonPhilosophicalTerms = [
      // Онтология
      'бытие', 'сущность', 'существование', 'реальность', 'материя', 
      'субстанция', 'форма', 'идея', 'ничто', 'пустота', 'вечность',
      'время', 'пространство', 'движение', 'покой', 'изменение',
      'становление', 'возможность', 'действительность', 'потенциальность',
      'актуальность', 'универсалии', 'монада', 'атом', 'континуум',
      
      // Гносеология/Эпистемология
      'познание', 'знание', 'истина', 'ложь', 'мнение', 'вера',
      'достоверность', 'сомнение', 'скепсис', 'эмпиризм', 'рационализм',
      'априори', 'апостериори', 'феномен', 'ноумен', 'интуиция',
      'восприятие', 'ощущение', 'представление', 'понятие', 'суждение',
      'умозаключение', 'метод', 'индукция', 'дедукция', 'абдукция',
      'верификация', 'фальсификация', 'парадигма', 'референция',
      
      // Философия сознания
      'сознание', 'разум', 'интеллект', 'мышление', 'рассудок',
      'рефлексия', 'самосознание', 'психика', 'душа', 'дух',
      'ментальное', 'квалиа', 'интенциональность', 'эмерджентность',
      
      // Этика
      'мораль', 'этика', 'добро', 'зло', 'благо', 'должное',
      'добродетель', 'порок', 'ценность', 'норма', 'долг',
      'справедливость', 'честность', 'свобода', 'ответственность',
      'совесть', 'счастье', 'эвдемония', 'утилитаризм', 'деонтология',
      'консеквенциализм', 'гедонизм', 'аскетизм', 'альтруизм', 'эгоизм',
      
      // Социальная философия и политическая философия
      'общество', 'государство', 'власть', 'право', 'закон',
      'свобода', 'равенство', 'справедливость', 'правосудие', 'личность',
      'индивид', 'класс', 'группа', 'народ', 'нация', 'цивилизация',
      'культура', 'традиция', 'прогресс', 'регресс', 'революция',
      'эволюция', 'идеология', 'утопия', 'дистопия', 'анархия',
      'демократия', 'тоталитаризм', 'либерализм', 'консерватизм',
      'социализм', 'коммунизм', 'капитализм', 'глобализация',
      
      // Метафилософские термины
      'философия', 'метафизика', 'онтология', 'гносеология', 'эпистемология',
      'эстетика', 'аксиология', 'телеология', 'натурфилософия', 'феноменология',
      'герменевтика', 'диалектика', 'логика', 'софистика', 'майевтика',
      'эклектика', 'догматизм', 'скептицизм', 'материализм', 'идеализм',
      'реализм', 'номинализм', 'эмпиризм', 'рационализм', 'иррационализм',
      'экзистенциализм', 'позитивизм', 'структурализм', 'постмодернизм',
      'аналитическая философия', 'континентальная философия'
    ];

    // Словари словоформ для учета морфологии русского языка
    const wordForms = {
      'бытие': ['бытия', 'бытию', 'бытием', 'бытии'],
      'сознание': ['сознания', 'сознанию', 'сознанием', 'сознании'],
      'познание': ['познания', 'познанию', 'познанием', 'познании'],
      // Добавляем словоформы для других ключевых терминов
    };
    
    // Создаем обратный словарь словоформ для быстрого поиска
    const formToRoot = {};
    for (const [root, forms] of Object.entries(wordForms)) {
      for (const form of forms) {
        formToRoot[form] = root;
      }
    }
    
    // Предобработка текста
    const text = thesisContent.toLowerCase()
      .replace(/[.,;:'"`?!()]/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();
    
    // Разбиение на слова и фразы
    const words = text.split(' ');
    const bigrams = [];
    const trigrams = [];
    
    // Формируем биграммы и триграммы для поиска составных терминов
    for (let i = 0; i < words.length - 1; i++) {
      bigrams.push(words[i] + ' ' + words[i + 1]);
      if (i < words.length - 2) {
        trigrams.push(words[i] + ' ' + words[i + 1] + ' ' + words[i + 2]);
      }
    }
    
    // Найденные ключевые слова
    const foundKeywords = new Set();
    
    // Поиск ключевых слов среди триграмм
    for (const trigram of trigrams) {
      if (commonPhilosophicalTerms.includes(trigram)) {
        foundKeywords.add(trigram);
      }
    }
    
    // Поиск ключевых слов среди биграмм
    for (const bigram of bigrams) {
      if (commonPhilosophicalTerms.includes(bigram)) {
        foundKeywords.add(bigram);
      }
    }
    
    // Поиск ключевых слов среди отдельных слов
    for (const word of words) {
      // Проверяем само слово
      if (commonPhilosophicalTerms.includes(word)) {
        foundKeywords.add(word);
      } 
      // Проверяем, является ли слово формой известного корня
      else if (formToRoot[word]) {
        foundKeywords.add(formToRoot[word]);
      }
      // Применяем простую стемминг-эвристику для русского языка
      else {
        // Отбрасываем окончания и проверяем основу слова
        for (const term of commonPhilosophicalTerms) {
          if (word.length > 4 && term.length > 4 && word.startsWith(term.substring(0, term.length - 1))) {
            foundKeywords.add(term);
            break;
          }
        }
      }
    }
    
    // Если не нашли ни одного ключевого слова, используем
    // частотный анализ, чтобы выделить наиболее важные слова
    if (foundKeywords.size === 0) {
      const wordCount = {};
      for (const word of words) {
        if (word.length > 3) { // Игнорируем короткие слова
          wordCount[word] = (wordCount[word] || 0) + 1;
        }
      }
      
      // Сортируем слова по частоте и берем топ-3
      const sortedWords = Object.entries(wordCount)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 3)
        .map(entry => entry[0]);
      
      for (const word of sortedWords) {
        foundKeywords.add(word);
      }
    }
    
    // Используем Claude для проверки и дополнения ключевых слов
    // для особо сложных или важных тезисов (опционально)
    if (thesisContent.length > 200 && foundKeywords.size < 3) {
      try {
        // Здесь может быть код для запроса к Claude для определения ключевых слов
        // В данном примере просто дополняем результаты
        foundKeywords.add('философия');
      } catch (error) {
        console.warn('Failed to use Claude for keyword extraction:', error);
      }
    }
    
    return Array.from(foundKeywords);
  } catch (error) {
    console.error('Error in keyword extraction:', error);
    // Возвращаем базовые ключевые слова при ошибке
    return ['философия'];
  }
}

// Расширенная функция определения тем тезиса
async function determineTopics(thesisContent) {
  try {
    // Расширенный словарь тематических категорий
    const topicKeywords = {
      'Онтология': [
        'бытие', 'реальность', 'существование', 'сущее', 'материя', 'идея',
        'субстанция', 'форма', 'время', 'пространство', 'ничто', 'пустота',
        'движение', 'покой', 'изменение', 'становление', 'бесконечность', 
        'вечность', 'универсалии', 'монада', 'атом', 'континуум'
      ],
      'Гносеология': [
        'познание', 'истина', 'знание', 'опыт', 'разум', 'рассудок',
        'восприятие', 'ощущение', 'представление', 'достоверность',
        'сомнение', 'скепсис', 'эмпиризм', 'рационализм', 'априори',
        'апостериори', 'феномен', 'ноумен', 'интуиция', 'метод',
        'индукция', 'дедукция', 'абдукция', 'верификация', 'фальсификация'
      ],
      'Эпистемология': [
        'знание', 'теория познания', 'эпистема', 'парадигма', 'структура знания',
        'обоснование', 'объяснение', 'понимание', 'научное знание', 'референция',
        'истинность', 'заблуждение', 'когнитивный', 'релятивизм', 'абсолютизм'
      ],
      'Философия сознания': [
        'сознание', 'разум', 'психика', 'душа', 'дух', 'мышление',
        'интеллект', 'самосознание', 'рефлексия', 'ментальное',
        'психофизическая проблема', 'квалиа', 'интенциональность',
        'эмерджентность', 'тождество', 'дуализм', 'функционализм'
      ],
      'Этика': [
        'мораль', 'добро', 'зло', 'должное', 'ценность', 'благо',
        'добродетель', 'порок', 'норма', 'долг', 'справедливость',
        'честность', 'совесть', 'счастье', 'эвдемония', 'утилитаризм',
        'деонтология', 'консеквенциализм', 'гедонизм', 'аскетизм',
        'альтруизм', 'эгоизм', 'моральный', 'нравственный'
      ],
      'Эстетика': [
        'красота', 'искусство', 'прекрасное', 'восприятие', 'вкус',
        'возвышенное', 'гармония', 'мимесис', 'катарсис', 'творчество',
        'эстетический', 'художественный', 'искусство', 'поэзия',
        'живопись', 'музыка', 'литература', 'стиль', 'форма'
      ],
      'Логика': [
        'мышление', 'понятие', 'суждение', 'умозаключение', 'закон',
        'доказательство', 'опровержение', 'дедукция', 'индукция',
        'силлогизм', 'аналогия', 'категория', 'противоречие', 'тождество',
        'аналитическое', 'синтетическое', 'логический', 'формальный'
      ],
      'Антропология': [
        'человек', 'личность', 'индивид', 'сознание', 'самосознание',
        'идентичность', 'пол', 'гендер', 'тело', 'телесность',
        'природа человека', 'сущность человека', 'душа', 'психика',
        'антропогенез', 'происхождение', 'эволюция', 'смысл жизни'
      ],
      'Социальная философия': [
        'общество', 'государство', 'право', 'социальный', 'культура',
        'власть', 'закон', 'свобода', 'равенство', 'справедливость',
        'класс', 'группа', 'народ', 'нация', 'цивилизация',
        'идеология', 'утопия', 'дистопия', 'анархия', 'демократия',
        'тоталитаризм', 'либерализм', 'консерватизм', 'социализм',
        'коммунизм', 'капитализм', 'глобализация', 'политический'
      ],
      'Историософия': [
        'история', 'прогресс', 'развитие', 'цивилизация', 'эпоха',
        'историчность', 'формация', 'эволюция', 'революция',
        'традиция', 'современность', 'постсовременность', 'модерн',
        'постмодерн', 'исторический', 'временной', 'период', 'эра'
      ],
      'Метафизика': [
        'метафизика', 'трансцендентное', 'трансцендентальное', 'имманентное',
        'абсолют', 'бесконечность', 'первопричина', 'первоначало',
        'сверхчувственное', 'ноумен', 'вещь в себе', 'идеал', 'универсалия'
      ],
      'Аксиология': [
        'ценность', 'оценка', 'цель', 'значимость', 'благо', 'иерархия ценностей',
        'ценностная ориентация', 'предпочтение', 'идеал', 'аксиологический'
      ],
      'Философия языка': [
        'язык', 'значение', 'смысл', 'референция', 'семантика', 'синтаксис',
        'прагматика', 'речевой акт', 'дискурс', 'текст', 'интерпретация',
        'герменевтика', 'понимание', 'перевод', 'лингвистический'
      ],
      'Философия науки': [
        'наука', 'научный метод', 'теория', 'гипотеза', 'парадигма',
        'исследовательская программа', 'верификация', 'фальсификация',
        'эксперимент', 'наблюдение', 'объяснение', 'предсказание'
      ],
      'Философия религии': [
        'религия', 'вера', 'бог', 'божественное', 'священное', 'профанное',
        'откровение', 'трансцендентное', 'мистическое', 'теодицея',
        'атеизм', 'агностицизм', 'теизм', 'пантеизм', 'деизм'
      ]
    };
    
    // Стоп-слова, которые часто встречаются в тексте и могут привести к неверной классификации
    const stopWords = ['также', 'более', 'менее', 'весьма', 'очень', 'крайне', 
                      'однако', 'причем', 'таким', 'образом', 'можно', 'нужно', 
                      'следует', 'если', 'либо', 'или', 'когда', 'другой', 'такой'];
    
    // Предобработка текста
    const text = thesisContent.toLowerCase()
      .replace(/[.,;:'"`?!()]/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();
    
    // Разбиение на слова
    const words = text.split(' ').filter(word => 
      !stopWords.includes(word) && word.length > 2);
    
    // Подсчет "очков" для каждой темы
    const topicScores = {};
    
    // Инициализация счетчиков для всех тем
    Object.keys(topicKeywords).forEach(topic => {
      topicScores[topic] = 0;
    });
    
    // Функция для проверки вхождения ключевых слов с учетом морфологии
    const containsKeyword = (word, keywords) => {
      // Прямое совпадение
      if (keywords.includes(word)) return true;
      
      // Проверка на вхождение основы слова (для русского языка)
      for (const keyword of keywords) {
        // Если слово и ключевое слово достаточно длинные, проверяем совпадение основы
        if (keyword.length > 4 && word.length > 4) {
          // Проверяем, содержит ли слово основу ключевого слова
          const stem = keyword.substring(0, keyword.length - 2); // приблизительная основа
          if (word.startsWith(stem)) return true;
        }
      }
      
      return false;
    };
    
    // Анализ слов и добавление очков для каждой темы
    words.forEach(word => {
      Object.entries(topicKeywords).forEach(([topic, keywords]) => {
        if (containsKeyword(word, keywords)) {
          topicScores[topic] += 1;
        }
      });
    });
    
    // Проверка на наличие фраз (n-граммы)
    const checkPhrases = (text, topicScores) => {
      Object.entries(topicKeywords).forEach(([topic, keywords]) => {
        keywords.forEach(keyword => {
          // Проверяем только многословные ключевые слова
          if (keyword.includes(' ')) {
            if (text.includes(keyword)) {
              // Многословные фразы имеют больший вес
              topicScores[topic] += 2;
            }
          }
        });
      });
    };
    
    checkPhrases(text, topicScores);
    
    // Определение контекстуальных связей между темами
    // Например, если тезис относится к "метафизике" и содержит слова о "бытии",
    // повышаем вероятность "онтологии"
    const contextualBoost = (topicScores) => {
      // Связи между темами
      const relatedTopics = {
        'Метафизика': ['Онтология', 'Философия религии'],
        'Онтология': ['Метафизика', 'Философия науки'],
        'Гносеология': ['Эпистемология', 'Философия науки', 'Логика'],
        'Эпистемология': ['Гносеология', 'Философия науки', 'Логика'],
        'Этика': ['Аксиология', 'Социальная философия'],
        'Социальная философия': ['Этика', 'Историософия', 'Антропология'],
        'Философия сознания': ['Антропология', 'Гносеология'],
        'Философия языка': ['Логика', 'Гносеология', 'Эпистемология']
      };
      
      Object.entries(relatedTopics).forEach(([topic, related]) => {
        if (topicScores[topic] > 0) {
          related.forEach(relatedTopic => {
            topicScores[relatedTopic] += topicScores[topic] * 0.3; // 30% от основного счета
          });
        }
      });
    };
    
    contextualBoost(topicScores);
    
    // Сортируем темы по их очкам и выбираем лучшие
    const sortedTopics = Object.entries(topicScores)
      .filter(([_, score]) => score > 0) // отбрасываем темы с нулевыми очками
      .sort((a, b) => b[1] - a[1]); // сортируем по убыванию очков
    
    // Выбираем до 3 тем с наивысшими очками
    const topTopics = sortedTopics.slice(0, 3).map(([topic, _]) => topic);
    
    // Если не нашли ни одной темы, возвращаем "Общая философия"
    if (topTopics.length === 0) {
      return ['Общая философия'];
    }
    
    return topTopics;
  } catch (error) {
    console.error('Error in topic detection:', error);
    return ['Общая философия'];
  }
}

// Запуск сервера
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
