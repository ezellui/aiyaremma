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
function findConflicts(groupedTheses) {
  // Для полноценной реализации требуется NLP анализ
  // Здесь представлена упрощенная версия
  
  const conflicts = [];
  
  // Анализируем тезисы в каждой тематической группе
  Object.keys(groupedTheses).forEach(topic => {
    const theses = groupedTheses[topic];
    
    // Сравниваем каждую пару тезисов
    for (let i = 0; i < theses.length; i++) {
      for (let j = i + 1; j < theses.length; j++) {
        const thesis1 = theses[i];
        const thesis2 = theses[j];
        
        // Проверяем, из разных ли они концепций
        if (thesis1.conceptId !== thesis2.conceptId) {
          // Здесь должен быть сложный алгоритм определения противоречий
          // Упрощенная версия: ищем противоположные ключевые слова
          const potentialConflict = simpleConflictDetection(thesis1, thesis2);
          
          if (potentialConflict) {
            conflicts.push({
              thesis1,
              thesis2,
              conflictType: potentialConflict,
              topic
            });
          }
        }
      }
    }
  });
  
  return conflicts;
}

// Упрощенный алгоритм определения противоречий
function simpleConflictDetection(thesis1, thesis2) {
  // Набор противоположных понятий для проверки
  const opposites = {
    'объективный': 'субъективный',
    'материальный': 'идеальный',
    'детерминизм': 'свобода воли',
    'рационализм': 'эмпиризм',
    'монизм': 'дуализм',
    // Можно дополнить список
  };
  
  // Проверяем ключевые слова на противоположности
  for (const word1 of thesis1.keywords) {
    for (const word2 of thesis2.keywords) {
      if (opposites[word1] === word2 || opposites[word2] === word1) {
        return `Противоположные концепции: ${word1} vs ${word2}`;
      }
    }
  }
  
  // Проверка на отрицания (упрощенно)
  if (thesis1.content.includes('не') && thesis2.content.includes(thesis1.content.replace('не ', ''))) {
    return 'Возможное отрицание';
  }
  
  return null;
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

// Функция извлечения ключевых слов из тезиса
function extractKeywords(thesisContent) {
  // Упрощенная версия - в реальной реализации нужен NLP
  const commonPhilosophicalTerms = [
    'бытие', 'сознание', 'познание', 'истина', 'субъект',
    'объект', 'материя', 'идея', 'опыт', 'разум', 'мышление',
    'воля', 'свобода', 'необходимость', 'причинность', 'этика',
    'мораль', 'добро', 'зло', 'красота', 'эстетика', 'логика',
    'онтология', 'гносеология', 'эпистемология', 'метафизика',
    'интуиция', 'относительность', 'абсолют', 'системность'
  ];
  
  const words = thesisContent.toLowerCase()
    .replace(/[.,;:'"`?!()]/g, '')
    .split(' ');
  
  const keywords = words.filter(word => 
    commonPhilosophicalTerms.includes(word) && 
    word.length > 3
  );
  
  return [...new Set(keywords)]; // Удаляем дубликаты
}

// Функция определения тем тезиса
function determineTopics(thesisContent) {
  // Упрощенная версия - в реальной реализации нужен NLP
  const topicKeywords = {
    'Онтология': ['бытие', 'реальность', 'существование', 'материя', 'идея'],
    'Гносеология': ['познание', 'истина', 'знание', 'опыт', 'разум', 'рассудок'],
    'Этика': ['мораль', 'добро', 'зло', 'должное', 'ценность'],
    'Эстетика': ['красота', 'искусство', 'прекрасное', 'восприятие', 'вкус'],
    'Логика': ['мышление', 'понятие', 'суждение', 'умозаключение', 'закон'],
    'Антропология': ['человек', 'личность', 'индивид', 'сознание', 'самосознание'],
    'Социальная философия': ['общество', 'государство', 'право', 'социальный', 'культура'],
    'Историософия': ['история', 'прогресс', 'развитие', 'цивилизация', 'эпоха']
  };
  
  const content = thesisContent.toLowerCase();
  const detectedTopics = [];
  
  Object.keys(topicKeywords).forEach(topic => {
    for (const keyword of topicKeywords[topic]) {
      if (content.includes(keyword)) {
        detectedTopics.push(topic);
        break;
      }
    }
  });
  
  // Если не определили ни одной темы, добавляем "Общая философия"
  if (detectedTopics.length === 0) {
    detectedTopics.push('Общая философия');
  }
  
  return detectedTopics;
}

// Запуск сервера
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
