/**
 * Сервис форматирования запросов к Claude
 * На основе claude-requests.js из архитектуры
 */

class ClaudeRequestFormatter {
  /**
   * Вспомогательный метод для форматирования объекта в JSON-строку
   */
  _formatJSON(data) {
    if (!data) return '{}';
    return JSON.stringify(data, null, 2);
  }

  /**
   * Удаляет лишние пробелы из многострочных шаблонных строк
   */
  _removeExtraSpaces(str) {
    if (!str) return '';
    return str.replace(/\n\s+/g, '\n').trim();
  }

  //=============================================
  // МЕТОДЫ РАБОТЫ С ГРАФАМИ И КАТЕГОРИЯМИ
  //=============================================

  /**
   * Форматирует запрос для валидации графа
   */
  formatGraphValidationRequest(graphData) {
    if (!graphData) throw new Error('graphData is required');
    
    return this._removeExtraSpaces(`Проанализируй следующий граф категорий философской концепции ${this._formatJSON(graphData)}. 
Выяви возможные логические противоречия, пропущенные важные категории или 
связи, необычные отношения между категориями. Предложи возможные улучшения.`);
  }

  /**
   * Форматирует запрос для обогащения категории
   */
  formatCategoryEnrichmentRequest(categoryData, conceptName, traditions = [], philosophers = []) {
    if (!categoryData) throw new Error('categoryData is required');
    if (!conceptName) throw new Error('conceptName is required');
    
    return this._removeExtraSpaces(`Для следующей категории "${categoryData.name}" с определением "${categoryData.definition}"
в контексте философской концепции "${conceptName}", предложи расширенное
описание, возможные альтернативные трактовки, исторические аналоги и связанные концепты.
Категория используется в традициях: ${traditions.join(', ')}
Категория связана с философами: ${philosophers.join(', ')}
При обогащении учитывай указанные традиции и философов.`);
  }

  /**
   * Форматирует запрос для обогащения связи
   */
  formatRelationshipEnrichmentRequest(relationshipData, category1, category2, conceptName) {
    if (!relationshipData) throw new Error('relationshipData is required');
    if (!category1 || !category2) throw new Error('Both categories are required');
    if (!conceptName) throw new Error('conceptName is required');
    
    return this._removeExtraSpaces(`Проанализируй связь типа "${relationshipData.type}" между категориями "${category1}" 
и "${category2}" в контексте "${conceptName}". Предложи философское обоснование 
этой связи, возможные контраргументы и примеры аналогичных связей в других философских системах.`);
  }

  /**
   * Форматирует запрос для анализа графа для выявления происхождения
   */
  formatGraphOriginAnalysisRequest(graphData) {
    if (!graphData) throw new Error('graphData is required');
    
    return this._removeExtraSpaces(`Проанализируй следующий граф концепции ${this._formatJSON(graphData)}. 
Определи, является ли данная концепция синтезом существующих философских традиций. 
Если да, идентифицируй возможные 'родительские' концепции, элементы которых 
объединены в данной концепции. Укажи конкретные признаки, позволяющие сделать 
такой вывод, и оцени приблизительное соотношение влияния каждой родительской концепции.`);
  }

  //=============================================
  // МЕТОДЫ РАБОТЫ С ТЕЗИСАМИ
  //=============================================

  /**
   * Форматирует запрос для генерации тезисов
   */
  formatThesisGenerationRequest(graphData, quantity, thesisType, style) {
    if (!graphData) throw new Error('graphData is required');
    if (!quantity || quantity <= 0) throw new Error('quantity must be a positive number');
    if (!thesisType) throw new Error('thesisType is required');
    if (!style) throw new Error('style is required');
    
    return this._removeExtraSpaces(`На основе следующего графа философской концепции ${this._formatJSON(graphData)} 
сформулируй ${quantity} ключевых тезисов в области ${thesisType}. 
Тезисы должны отражать структурные отношения между категориями и быть 
выражены в ${style} стиле. Для каждого тезиса укажи, из каких именно 
элементов графа он логически следует.`);
  }

  /**
   * Форматирует запрос для генерации тезисов с учётом количественных характеристик
   */
  formatThesisGenerationWithCharacteristicsRequest(graphData, quantity, thesisType, characteristicsConfig = {}) {
    if (!graphData) throw new Error('graphData is required');
    if (!quantity || quantity <= 0) throw new Error('quantity must be a positive number');
    if (!thesisType) throw new Error('thesisType is required');
    
    const centralityThreshold = characteristicsConfig.centralityThreshold || 0.7;
    const strengthThreshold = characteristicsConfig.strengthThreshold || 0.7;
    const certaintyThreshold = characteristicsConfig.certaintyThreshold || 0.4;
    const additionalInstructions = characteristicsConfig.additionalInstructions || '';
    
    return this._removeExtraSpaces(`На основе следующего графа философской концепции ${this._formatJSON(graphData)} 
сформулируй ${quantity} ключевых тезисов в области ${thesisType}. 
Обрати особое внимание на категории с высокой центральностью (> ${centralityThreshold}) 
и связи с высокой силой (> ${strengthThreshold}). 
Для категорий с низкой определённостью (< ${certaintyThreshold}) 
предложи альтернативные формулировки тезисов.
${additionalInstructions}`);
  }

  /**
   * Форматирует запрос для генерации графа на основе тезисов
   */
  formatThesisToGraphRequest(theses) {
    if (!theses || !Array.isArray(theses)) throw new Error('theses must be an array');
    
    return this._removeExtraSpaces(`На основе следующих философских тезисов ${this._formatJSON(theses)} создай 
структурированный граф концепции. Выдели ключевые категории, установи связи 
между ними и предложи иерархию. Для каждого элемента графа укажи, из каких 
именно тезисов он логически следует.`);
  }

  /**
   * Форматирует запрос для анализа тезисов для выявления синтеза
   */
  formatThesisOriginAnalysisRequest(theses) {
    if (!theses || !Array.isArray(theses)) throw new Error('theses must be an array');
    
    return this._removeExtraSpaces(`Проанализируй следующие философские тезисы ${this._formatJSON(theses)}. 
Определи, представляют ли они единую философскую перспективу или являются 
синтезом различных философских традиций. Если это синтез, идентифицируй возможные 
'родительские' философские традиции или концепции, которые могли быть объединены. 
Предоставь детальное обоснование своего анализа.`);
  }

  //=============================================
  // МЕТОДЫ СИНТЕЗА И АНАЛИЗА СОВМЕСТИМОСТИ КОНЦЕПЦИЙ
  //=============================================

  /**
   * Форматирует запрос для синтеза концепций
   */
  formatConceptSynthesisRequest(concept1, concept2, method, focus, innovationDegree) {
    if (!concept1 || !concept2) throw new Error('Both concepts are required');
    if (!method) throw new Error('method is required');
    if (!focus) throw new Error('focus is required');
    if (!innovationDegree) throw new Error('innovationDegree is required');
    
    return this._removeExtraSpaces(`На основе графов философских концепций ${this._formatJSON(concept1)} и ${this._formatJSON(concept2)} 
разработай граф синтетической концепции, используя метод ${method}. 
Фокус синтеза: ${focus}. Степень инновационности: ${innovationDegree}. 
Для каждого элемента нового графа укажи его происхождение (из какой исходной 
концепции он взят или как трансформирован) и обоснование включения.`);
  }

  /**
   * Форматирует запрос для анализа совместимости концепций
   */
  formatConceptCompatibilityRequest(concept1, concept2) {
    if (!concept1 || !concept2) throw new Error('Both concepts are required');
    
    return this._removeExtraSpaces(`Проанализируй графы следующих философских концепций: ${this._formatJSON(concept1)} и ${this._formatJSON(concept2)}. 
Выяви: 1) полностью совместимые элементы, 2) потенциально совместимые при реинтерпретации, 
3) принципиально несовместимые элементы. Предложи возможные стратегии синтеза, учитывая 
выявленные особенности.`);
  }

  /**
   * Форматирует запрос для критического анализа синтезированной концепции
   */
  formatSynthesisCritiqueRequest(synthesizedConcept) {
    if (!synthesizedConcept) throw new Error('synthesizedConcept is required');
    
    return this._removeExtraSpaces(`Проведи критический анализ синтезированной концепции ${this._formatJSON(synthesizedConcept)}. 
Оцени: 1) внутреннюю согласованность, 2) философскую новизну, 3) сохранение ценных 
аспектов исходных концепций, 4) разрешение противоречий между ними, 5) потенциальные 
проблемы и слабые места.`);
  }

  /**
   * Форматирует запрос для создания диалога между концепциями
   */
  formatDialogueRequest(concept1, name1, concept2, name2, topic, options = {}) {
    if (!concept1 || !concept2) throw new Error('Both concepts are required');
    if (!name1 || !name2) throw new Error('Both concept names are required');
    if (!topic) throw new Error('topic is required');
    
    const { 
      format = 'классический', 
      length = 'средний', 
      focusPoints = [], 
      characterization = false 
    } = options;
    
    let additionalInstructions = "";
    
    if (focusPoints && focusPoints.length > 0) {
      additionalInstructions += `\nВ диалоге должны быть затронуты следующие аспекты: ${focusPoints.join(', ')}.`;
    }
    
    if (characterization) {
      additionalInstructions += "\nПридай участникам диалога характерные черты в соответствии с их философскими позициями.";
    }
    
    let formatInstruction = "";
    switch (format) {
      case 'платоновский':
        formatInstruction = "Диалог должен быть оформлен в стиле платоновских диалогов.";
        break;
      case 'современный':
        formatInstruction = "Диалог должен быть оформлен в стиле современной академической дискуссии.";
        break;
      case 'дебаты':
        formatInstruction = "Диалог должен быть оформлен в стиле структурированных дебатов с аргументами и контраргументами.";
        break;
      default:
        formatInstruction = "Диалог должен быть оформлен в классическом стиле философской беседы.";
    }
    
    let lengthInstruction = "";
    switch (length) {
      case 'краткий':
        lengthInstruction = "Диалог должен быть кратким, с фокусом на ключевых тезисах.";
        break;
      case 'развернутый':
        lengthInstruction = "Диалог должен быть развернутым, с подробным обсуждением всех аспектов вопроса.";
        break;
      default:
        lengthInstruction = "Диалог должен быть средней длины, охватывая основные аспекты вопроса.";
    }
    
    return this._removeExtraSpaces(`Создай философский диалог между представителями концепций ${this._formatJSON(concept1)} 
под названием "${name1}" и ${this._formatJSON(concept2)} под названием "${name2}" 
по вопросу "${topic}". Диалог должен отражать ключевые тезисы каждой концепции, 
логику аргументации и возможные точки соприкосновения или непреодолимых разногласий.
${formatInstruction}
${lengthInstruction}
${additionalInstructions}

Структура диалога должна включать:
1. Краткое введение, представляющее участников и контекст
2. Изложение позиций сторон по обсуждаемому вопросу
3. Развитие дискуссии с аргументами и контраргументами
4. Выявление точек соприкосновения и принципиальных разногласий
5. Заключение, подводящее итоги диалога`);
  }

  //=============================================
  // МЕТОДЫ ДЛЯ ИСТОРИЧЕСКОГО И ПРАКТИЧЕСКОГО АНАЛИЗА
  //=============================================

  /**
   * Форматирует запрос для исторической контекстуализации
   */
  formatHistoricalContextRequest(conceptData, conceptName, traditions = [], philosophers = [], timeContext = null) {
    if (!conceptData) throw new Error('conceptData is required');
    if (!conceptName) throw new Error('conceptName is required');
    
    let contextualizationScope = "";
    
    if (traditions && traditions.length > 0) {
      contextualizationScope += `\nОсобое внимание обрати на связь с традициями: ${traditions.join(', ')}.`;
    }
    
    if (philosophers && philosophers.length > 0) {
      contextualizationScope += `\nРассмотри влияние следующих философов: ${philosophers.join(', ')}.`;
    }
    
    if (timeContext) {
      contextualizationScope += `\nПоместить в контекст периода: ${timeContext.start || "древность"} - ${timeContext.end || "современность"}.`;
    }
    
    return this._removeExtraSpaces(`Помести философскую концепцию ${this._formatJSON(conceptData)} 
под названием "${conceptName}" в исторический контекст. 
Определи её возможные источники влияния, современников со схожими 
или противоположными идеями, а также потенциальное влияние на последующие 
философские направления. Объясни, насколько название концепции соответствует 
её историческому контексту.${contextualizationScope}

Представь результат в структурированном виде, включающем:
1. Общий исторический контекст
2. Ключевые источники влияния
3. Современные концепции (сходства и различия)
4. Потенциальное влияние на последующую философию
5. Соответствие названия историческому контексту`);
  }

  /**
   * Форматирует запрос для анализа практического применения
   */
  formatPracticalApplicationRequest(conceptData, conceptName, domains = null, detailed = false) {
    if (!conceptData) throw new Error('conceptData is required');
    if (!conceptName) throw new Error('conceptName is required');
    
    let domainsStr = "образование, этика, политика, личностное развитие, социальные институты";
    
    if (domains && domains.length > 0) {
      domainsStr = domains.join(', ');
    }
    
    let detailLevel = detailed 
      ? "Для каждой области предоставь подробный анализ способов операционализации с конкретными примерами и методиками внедрения."
      : "Для каждой области укажи, какие именно тезисы или категории концепции наиболее релевантны и как они могут быть операционализированы.";
    
    return this._removeExtraSpaces(`Предложи возможные практические применения философской концепции ${this._formatJSON(conceptData)} 
под названием "${conceptName}" в следующих областях: ${domainsStr}. 
${detailLevel}

Представь результат в структурированном виде для каждой области:
1. Краткое описание применимости концепции в данной области
2. Релевантные тезисы/категории концепции
3. Конкретные способы операционализации
4. Потенциальные трудности и ограничения
5. Критерии оценки эффективности применения`);
  }

  /**
   * Форматирует запрос для возможных направлений эволюции концепции
   */
  formatConceptEvolutionRequest(conceptData, conceptName) {
    if (!conceptData) throw new Error('conceptData is required');
    if (!conceptName) throw new Error('conceptName is required');
    
    return this._removeExtraSpaces(`Предложи возможные направления эволюции философской концепции ${this._formatJSON(conceptData)} 
под названием "${conceptName}" в свете современных научных открытий, социальных 
изменений и философских тенденций. Какие категории могли бы измениться, какие связи 
переосмыслены, какие новые элементы добавлены? Как может измениться или должно ли 
сохраниться название концепции при её эволюции?`);
  }

  //=============================================
  // МЕТОДЫ ДЛЯ РАБОТЫ С МЕТАДАННЫМИ И ИМЕНАМИ КОНЦЕПЦИЙ
  //=============================================

  /**
   * Форматирует запрос для генерации названия концепции
   */
  formatConceptNameGenerationRequest(graphData, theses) {
    if (!graphData && (!theses || !Array.isArray(theses))) {
      throw new Error('Either graphData or theses must be provided');
    }
    
    return this._removeExtraSpaces(`На основе следующего графа концепции ${this._formatJSON(graphData)} 
или списка тезисов ${this._formatJSON(theses)},
предложи лаконичное и содержательное название для этой философской концепции. 
Название должно отражать сущность концепции и быть узнаваемым в философской традиции. 
Предоставь обоснование своего предложения.`);
  }

  /**
   * Форматирует запрос для анализа названия концепции
   */
  formatConceptNameAnalysisRequest(name, conceptData = null) {
    if (!name) throw new Error('name is required');
    
    let conceptDataStr = conceptData ? `в контексте её содержания ${this._formatJSON(conceptData)}` : '';
    
    return this._removeExtraSpaces(`Проанализируй название философской концепции "${name}" ${conceptDataStr}. 
Насколько точно название отражает суть концепции? Какие аспекты концепции 
подчеркиваются в названии, а какие остаются в тени? Предложи возможные 
альтернативные названия, которые могли бы лучше отразить различные аспекты концепции.`);
  }
}

module.exports = new ClaudeRequestFormatter();