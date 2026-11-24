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
    
    // Стоп-слова, которые часто встречаются в тексте и мог

// Запуск сервера
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
