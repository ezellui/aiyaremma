// API сервис (Node.js + Express)

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
    
    // Сортируем конфликты по степени

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
function formatPromptForClaude(groupedTheses, conflicts, params) {
  let prompt = `
  # Задача: создание новой философской концепции
  
  ## Имеющиеся тезисы по темам:
  `;
  
  // Форматируем тезисы по темам
  Object.keys(groupedTheses).forEach(topic => {
    prompt += `\n### ${topic}\n`;
    
    groupedTheses[topic].forEach((thesis, index) => {
      prompt += `${index + 1}. "${thesis.content}" (из концепции "${thesis.conceptName}")\n`;
    });
  });
  
  // Добавляем информацию о конфликтах
  if (conflicts.length > 0) {
    prompt += `\n## Обнаруженные противоречия:\n`;
    
    conflicts.forEach((conflict, index) => {
      prompt += `
      ${index + 1}. По теме "${conflict.topic}":
         - "${conflict.thesis1.content}" (из "${conflict.thesis1.conceptName}")
         - "${conflict.thesis2.content}" (из "${conflict.thesis2.conceptName}")
         - Тип противоречия: ${conflict.conflictType}
      `;
    });
  }
  
  // Добавляем инструкцию по генерации
  prompt += `
  ## Инструкция:
  Создай новую философскую концепцию, которая:
  1. Синтезирует предоставленные тезисы в единую систему
  2. Разрешает указанные противоречия
  3. Предлагает новую перспективу, объединяющую элементы исходных концепций
  
  ## Требуемый формат ответа:
  1. Название концепции
  2. Краткое описание (3-5 предложений)
  3. Список 5-10 ключевых тезисов, пронумерованных и четко сформулированных
  4. Отношение к исходным концепциям и как они были интегрированы
  `;
  
  // Добавляем дополнительные требования, если есть
  if (params && params.additionalRequirements) {
    prompt += `\n## Дополнительные требования:\n${params.additionalRequirements}\n`;
  }
  
  // Добавляем стилистические предпочтения, если есть
  if (params && params.style) {
    prompt += `\n## Стилистические предпочтения:\n${params.style}\n`;
  }
  
  return prompt;
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
