// Часть 3: Генерация тезисов и синтез концепций

// === Функции для генерации тезисов ===

// Генерация тезисов на основе графа
async function generateTheses() {
    const conceptId = document.getElementById('conceptSelect').value;
    const thesisType = document.getElementById('thesisType').value;
    const count = document.getElementById('thesisCount').value;
    const detailLevel = document.getElementById('detailLevel').value;
    const style = document.getElementById('thesisStyle').value;
    const useMetrics = document.getElementById('useMetrics').checked;
    
    if (!conceptId) {
        alert('Пожалуйста, выберите концепцию');
        return;
    }
    
    const concept = concepts.find(c => c.id === conceptId);
    const conceptCategories = categories.filter(c => c.conceptId === conceptId);
    const conceptRelations = relations.filter(r => {
        const fromCategory = categories.find(c => c.id === r.from);
        return fromCategory && fromCategory.conceptId === conceptId;
    });
    
    const graphData = {
        concept: concept.name,
        categories: conceptCategories.map(c => ({
            name: c.name,
            definition: c.definition,
            traditions: c.traditions,
            philosophers: c.philosophers,
            metrics: useMetrics ? c.metrics : undefined
        })),
        relations: conceptRelations.map(r => ({
            from: categories.find(c => c.id === r.from)?.name,
            to: categories.find(c => c.id === r.to)?.name,
            type: relationTypes.find(t => t.id === r.type)?.name,
            bidirectional: r.bidirectional,
            strength: useMetrics ? r.strength : undefined,
            certainty: useMetrics ? r.certainty : undefined
        }))
    };
    
    let prompt;
    if (useMetrics) {
        prompt = `На основе следующего графа философской концепции "${concept.name}" с количественными характеристиками:
${JSON.stringify(graphData, null, 2)}
сформулируй ${count} ключевых тезисов в области ${getThesisTypeName(thesisType)}. 
Обрати особое внимание на категории с высокой центральностью и связи с высокой силой. 
Для категорий с низкой определённостью предложи альтернативные формулировки тезисов.
Уровень детализации: ${getDetailLevelName(detailLevel)}.
Стиль изложения: ${getStyleName(style)}.`;
    } else {
        prompt = `На основе следующего графа философской концепции "${concept.name}":
${JSON.stringify(graphData, null, 2)}
сформулируй ${count} ключевых тезисов в области ${getThesisTypeName(thesisType)}. 
Тезисы должны отражать структурные отношения между категориями.
Уровень детализации: ${getDetailLevelName(detailLevel)}.
Стиль изложения: ${getStyleName(style)}.
Для каждого тезиса укажи, из каких именно элементов графа он логически следует.`;
    }
    
    try {
        const response = await callClaudeAPI(prompt);
        document.getElementById('thesesContainer').innerHTML = response;
        saveGeneratedTheses(conceptId, response);
    } catch (error) {
        alert('Ошибка при генерации тезисов: ' + error.message);
    }
}

// Сравнение версий тезисов
async function compareThesesVersions() {
    const conceptId = document.getElementById('conceptSelect').value;
    if (!conceptId) {
        alert('Пожалуйста, выберите концепцию');
        return;
    }
    
    // Генерируем обе версии
    const thesesWithoutMetrics = await generateThesesVersion(conceptId, false);
    const thesesWithMetrics = await generateThesesVersion(conceptId, true);
    
    const prompt = `Сравни два набора тезисов, сгенерированных на основе одного графа концепции, 
но с разным учётом количественных характеристик:

ТЕЗИСЫ БЕЗ УЧЁТА ХАРАКТЕРИСТИК:
${thesesWithoutMetrics}

ТЕЗИСЫ С УЧЁТОМ ХАРАКТЕРИСТИК:
${thesesWithMetrics}

Выяви ключевые различия, их причины и оцени, какой набор лучше отражает суть концепции и почему.`;
    
    try {
        const response = await callClaudeAPI(prompt);
        showModal('Сравнение версий тезисов', response);
    } catch (error) {
        alert('Ошибка при сравнении версий: ' + error.message);
    }
}

// Развитие и обоснование тезиса
async function requestThesisDevelopment() {
    const thesesContent = document.getElementById('thesesContainer').innerHTML;
    if (!thesesContent || thesesContent === '<p>Здесь будут отображаться сгенерированные тезисы</p>') {
        alert('Сначала сгенерируйте тезисы');
        return;
    }
    
    const selectedThesis = prompt('Введите тезис для развития:');
    if (!selectedThesis) return;
    
    const conceptId = document.getElementById('conceptSelect').value;
    const concept = concepts.find(c => c.id === conceptId);
    
    const prompt = `Для следующего тезиса "${selectedThesis}", сформулированного на основе 
графа концепции "${concept.name}", предложи: 
1) философское обоснование, 
2) возможные контраргументы, 
3) исторические аналоги, 
4) практические следствия.`;
    
    try {
        const response = await callClaudeAPI(prompt);
        showModal('Развитие тезиса', response);
    } catch (error) {
        alert('Ошибка при развитии тезиса: ' + error.message);
    }
}

// === Функции для синтеза концепций ===

// Анализ совместимости концепций
async function analyzeCompatibility() {
    const concept1Id = document.getElementById('concept1').value;
    const concept2Id = document.getElementById('concept2').value;
    
    if (!concept1Id || !concept2Id || concept1Id === concept2Id) {
        alert('Пожалуйста, выберите две разные концепции');
        return;
    }
    
    const concept1 = concepts.find(c => c.id === concept1Id);
    const concept2 = concepts.find(c => c.id === concept2Id);
    
    const graph1Data = getConceptGraphData(concept1Id);
    const graph2Data = getConceptGraphData(concept2Id);
    
    const prompt = `Проанализируй графы следующих философских концепций:
КОНЦЕПЦИЯ 1: "${concept1.name}"
${JSON.stringify(graph1Data, null, 2)}

КОНЦЕПЦИЯ 2: "${concept2.name}"
${JSON.stringify(graph2Data, null, 2)}

Выяви: 
1) полностью совместимые элементы, 
2) потенциально совместимые при реинтерпретации, 
3) принципиально несовместимые элементы. 
Предложи возможные стратегии синтеза, учитывая выявленные особенности.`;
    
    try {
        const response = await callClaudeAPI(prompt);
        showModal('Анализ совместимости', response);
    } catch (error) {
        alert('Ошибка при анализе совместимости: ' + error.message);
    }
}

// Синтезирование концепций
async function synthesizeConcepts() {
    const concept1Id = document.getElementById('concept1').value;
    const concept2Id = document.getElementById('concept2').value;
    const method = document.getElementById('synthesisMethod').value;
    const focus = document.getElementById('synthesisFocus').value;
    const innovationLevel = document.getElementById('innovationLevel').value;
    
    if (!concept1Id || !concept2Id) {
        alert('Пожалуйста, выберите концепции для синтеза');
        return;
    }
    
    const concept1 = concepts.find(c => c.id === concept1Id);
    const concept2 = concepts.find(c => c.id === concept2Id);
    
    const graph1Data = getConceptGraphData(concept1Id);
    const graph2Data = getConceptGraphData(concept2Id);
    
    const prompt = `На основе графов философских концепций:
КОНЦЕПЦИЯ 1: "${concept1.name}"
${JSON.stringify(graph1Data, null, 2)}

КОНЦЕПЦИЯ 2: "${concept2.name}"
${JSON.stringify(graph2Data, null, 2)}

разработай граф синтетической концепции, используя метод ${getSynthesisMethodName(method)}. 
Фокус синтеза: ${getSynthesisFocusName(focus)}. 
Степень инновационности: ${getInnovationLevelName(innovationLevel)}. 
Для каждого элемента нового графа укажи его происхождение (из какой исходной 
концепции он взят или как трансформирован) и обоснование включения.`;
    
    try {
        const response = await callClaudeAPI(prompt);
        document.getElementById('synthesisResult').innerHTML = response;
        saveSynthesisResult(response);
    } catch (error) {
        alert('Ошибка при синтезе концепций: ' + error.message);
    }
}

// Генерация тезисов для синтезированной концепции
async function generateSynthesisTheses() {
    const synthesisContent = document.getElementById('synthesisResult').innerHTML;
    if (!synthesisContent || synthesisContent === '<p>Здесь будет отображаться синтезированная концепция</p>') {
        alert('Сначала синтезируйте концепцию');
        return;
    }
    
    const prompt = `На основе следующего графа синтезированной философской концепции:
${synthesisContent}

сформулируй ключевые тезисы. Особое внимание обрати на инновационные элементы, 
возникшие в процессе синтеза, и на то, как разрешены противоречия между исходными концепциями.`;
    
    try {
        const response = await callClaudeAPI(prompt);
        showModal('Тезисы синтезированной концепции', response);
    } catch (error) {
        alert('Ошибка при генерации тезисов: ' + error.message);
    }
}

// Критический анализ синтезированной концепции
async function criticalAnalysis() {
    const synthesisContent = document.getElementById('synthesisResult').innerHTML;
    if (!synthesisContent || synthesisContent === '<p>Здесь будет отображаться синтезированная концепция</p>') {
        alert('Сначала синтезируйте концепцию');
        return;
    }
    
    const prompt = `Проведи критический анализ синтезированной концепции:
${synthesisContent}

Оцени: 
1) внутреннюю согласованность, 
2) философскую новизну, 
3) сохранение ценных аспектов исходных концепций, 
4) разрешение противоречий между ними, 
5) потенциальные проблемы и слабые места.`;
    
    try {
        const response = await callClaudeAPI(prompt);
        showModal('Критический анализ', response);
    } catch (error) {
        alert('Ошибка при критическом анализе: ' + error.message);
    }
}

// === Функции для дополнительного анализа ===

// Выполнение анализа выбранного типа
async function performAnalysis() {
    const conceptId = document.getElementById('analysisConceptSelect').value;
    const analysisType = document.getElementById('analysisType').value;
    
    if (!conceptId) {
        alert('Пожалуйста, выберите концепцию');
        return;
    }
    
    const concept = concepts.find(c => c.id === conceptId);
    const graphData = getConceptGraphData(conceptId);
    
    let prompt;
    
    switch (analysisType) {
        case 'historical':
            prompt = `Помести философскую концепцию "${concept.name}" в исторический контекст. 
Определи её возможные источники влияния, современников со схожими или 
противоположными идеями, а также потенциальное влияние на последующие 
философские направления.

ГРАФ КОНЦЕПЦИИ:
${JSON.stringify(graphData, null, 2)}`;
            break;
            
        case 'practical':
            prompt = `Предложи возможные практические применения философской концепции "${concept.name}" 
в следующих областях: образование, этика, политика, личностное развитие, 
социальные институты. Для каждой области укажи, какие именно тезисы или 
категории концепции наиболее релевантны и как они могут быть операционализированы.

ГРАФ КОНЦЕПЦИИ:
${JSON.stringify(graphData, null, 2)}`;
            break;
            
        case 'dialogical':
            const partnerId = document.getElementById('dialoguePartner').value;
            const topic = document.getElementById('dialogueTopic').value;
            
            if (!partnerId || !topic) {
                alert('Пожалуйста, выберите концепцию для диалога и тему');
                return;
            }
            
            const partner = concepts.find(c => c.id === partnerId);
            const partnerGraphData = getConceptGraphData(partnerId);
            
            prompt = `Создай философский диалог между представителями концепций 
"${concept.name}" и "${partner.name}" по вопросу "${topic}". 
Диалог должен отражать ключевые тезисы каждой концепции, логику аргументации 
и возможные точки соприкосновения или непреодолимых разногласий.

КОНЦЕПЦИЯ 1:
${JSON.stringify(graphData, null, 2)}

КОНЦЕПЦИЯ 2:
${JSON.stringify(partnerGraphData, null, 2)}`;
            break;
            
        case 'evolution':
            prompt = `Предложи возможные направления эволюции философской концепции "${concept.name}" 
в свете современных научных открытий, социальных изменений и философских тенденций. 
Какие категории могли бы измениться, какие связи переосмыслены, какие новые 
элементы добавлены?

ГРАФ КОНЦЕПЦИИ:
${JSON.stringify(graphData, null, 2)}`;
            break;
    }
    
    try {
        const response = await callClaudeAPI(prompt);
        document.getElementById('analysisResult').innerHTML = response;
    } catch (error) {
        alert('Ошибка при выполнении анализа: ' + error.message);
    }
}

// === Вспомогательные функции ===

// Получение данных графа концепции
function getConceptGraphData(conceptId) {
    const conceptCategories = categories.filter(c => c.conceptId === conceptId);
    const conceptRelations = relations.filter(r => {
        const fromCategory = categories.find(c => c.id === r.from);
        return fromCategory && fromCategory.conceptId === conceptId;
    });
    
    return {
        categories: conceptCategories.map(c => ({
            name: c.name,
            definition: c.definition,
            traditions: c.traditions,
            philosophers: c.philosophers,
            metrics: c.metrics
        })),
        relations: conceptRelations.map(r => ({
            from: categories.find(c => c.id === r.from)?.name,
            to: categories.find(c => c.id === r.to)?.name,
            type: relationTypes.find(t => t.id === r.type)?.name,
            bidirectional: r.bidirectional,
            strength: r.strength,
            certainty: r.certainty
        }))
    };
}

// Получение читаемых названий для значений
function getThesisTypeName(type) {
    const types = {
        'ontological': 'онтологии',
        'epistemological': 'эпистемологии',
        'ethical': 'этики',
        'aesthetic': 'эстетики',
        'political': 'политической философии',
        'metaphysical': 'метафизики'
    };
    return types[type] || type;
}

function getDetailLevelName(level) {
    const levels = {
        'concise': 'краткий',
        'moderate': 'умеренный',
        'detailed': 'подробный'
    };
    return levels[level] || level;
}

function getStyleName(style) {
    const styles = {
        'academic': 'академический',
        'popular': 'популярный',
        'aphoristic': 'афористичный'
    };
    return styles[style] || style;
}

function getSynthesisMethodName(method) {
    const methods = {
        'dialectical': 'диалектический',
        'integrative': 'интегративный',
        'transformational': 'трансформационный',
        'complementary': 'дополнительный'
    };
    return methods[method] || method;
}

function getSynthesisFocusName(focus) {
    const focuses = {
        'ontological': 'онтологический',
        'ethical': 'этический',
        'political': 'политический',
        'epistemological': 'эпистемологический'
    };
    return focuses[focus] || focus;
}

function getInnovationLevelName(level) {
    const levels = {
        'conservative': 'консервативная',
        'moderate': 'умеренная',
        'radical': 'радикальная'
    };
    return levels[level] || level;
}

// Функции экспорта
function exportTheses() {
    const thesesContent = document.getElementById('thesesContainer').innerHTML;
    if (!thesesContent || thesesContent === '<p>Здесь будут отображаться сгенерированные тезисы</p>') {
        alert('Нет тезисов для экспорта');
        return;
    }
    
    const dataBlob = new Blob([thesesContent], { type: 'text/html' });
    const url = URL.createObjectURL(dataBlob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `theses_${new Date().toISOString().split('T')[0]}.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function exportSynthesis() {
    const synthesisContent = document.getElementById('synthesisResult').innerHTML;
    if (!synthesisContent || synthesisContent === '<p>Здесь будет отображаться синтезированная концепция</p>') {
        alert('Нет синтеза для экспорта');
        return;
    }
    
    const dataBlob = new Blob([synthesisContent], { type: 'text/html' });
    const url = URL.createObjectURL(dataBlob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `synthesis_${new Date().toISOString().split('T')[0]}.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function exportAnalysis() {
    const analysisContent = document.getElementById('analysisResult').innerHTML;
    if (!analysisContent || analysisContent === '<p>Здесь будут отображаться результаты анализа</p>') {
        alert('Нет анализа для экспорта');
        return;
    }
    
    const dataBlob = new Blob([analysisContent], { type: 'text/html' });
    const url = URL.createObjectURL(dataBlob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `analysis_${new Date().toISOString().split('T')[0]}.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Визуализация графа (базовая реализация)
function updateGraphVisualization() {
    const container = document.getElementById('graphContainer');
    if (!container) return;
    
    let html = '<div class="graph-vis">';
    
    if (currentConcept) {
        const conceptCategories = categories.filter(c => c.conceptId === currentConcept.id);
        const conceptRelations = relations.filter(r => {
            const fromCategory = categories.find(c => c.id === r.from);
            return fromCategory && fromCategory.conceptId === currentConcept.id;
        });
        
        // Отображаем категории
        conceptCategories.forEach(category => {
            html += `<div class="graph-category card">
                <div class="card-header">${category.name}</div>
                <div>${category.definition}</div>
                <div class="traditions-list">
                    ${category.traditions.map(t => `<span class="tag">${t}</span>`).join('')}
                </div>
                <div class="philosophers-list">
                    ${category.philosophers.map(p => `<span class="tag">${p}</span>`).join('')}
                </div>
                <button onclick="enrichCategory('${category.id}')" class="secondary">Обогатить</button>
            </div>`;
        });
        
        // Отображаем связи
        html += '<div class="graph-relations">';
        conceptRelations.forEach(relation => {
            const fromCategory = categories.find(c => c.id === relation.from);
            const toCategory = categories.find(c => c.id === relation.to);
            const relationType = relationTypes.find(t => t.id === relation.type);
            
            html += `<div class="graph-relation card">
                <div class="card-header">${fromCategory?.name} → ${toCategory?.name}</div>
                <div>Тип: ${relationType?.name}</div>
                <div>${relation.bidirectional ? 'Двунаправленная' : 'Однонаправленная'}</div>
            </div>`;
        });
        html += '</div>';
    } else {
        html += '<p>Выберите или создайте концепцию для отображения графа</p>';
    }
    
    html += '</div>';
    container.innerHTML = html;
}