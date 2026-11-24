// Часть 2: Работа с базой данных и API Claude

// === Функции для работы с базой данных ===

// Сохранение базы данных в localStorage и возможность экспорта в файл
function saveDatabase() {
    const database = {
        concepts,
        categories,
        relations,
        relationTypes,
        apiKey: localStorage.getItem('claudeApiKey')
    };
    localStorage.setItem('philosophicalConceptsDB', JSON.stringify(database));
}

// Загрузка базы данных из localStorage
function loadDatabase() {
    const savedData = localStorage.getItem('philosophicalConceptsDB');
    if (savedData) {
        const database = JSON.parse(savedData);
        concepts = database.concepts || [];
        categories = database.categories || [];
        relations = database.relations || [];
        relationTypes = database.relationTypes || relationTypes;
        
        const apiKey = database.apiKey;
        if (apiKey) {
            document.getElementById('apiKey').value = apiKey;
        }
    }
}

// Экспорт базы данных в файл
function exportDatabase() {
    const database = {
        concepts,
        categories,
        relations,
        relationTypes,
        apiKey: localStorage.getItem('claudeApiKey'),
        exportDate: new Date().toISOString()
    };
    
    const dataStr = JSON.stringify(database, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `philosophical_concepts_db_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Импорт базы данных из файла
function importDatabase() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    
    input.onchange = function(event) {
        const file = event.target.files[0];
        const reader = new FileReader();
        
        reader.onload = function(e) {
            try {
                const database = JSON.parse(e.target.result);
                concepts = database.concepts || [];
                categories = database.categories || [];
                relations = database.relations || [];
                relationTypes = database.relationTypes || relationTypes;
                
                if (database.apiKey) {
                    localStorage.setItem('claudeApiKey', database.apiKey);
                    document.getElementById('apiKey').value = database.apiKey;
                }
                
                saveDatabase();
                updateUI();
                alert('База данных успешно импортирована!');
            } catch (error) {
                alert('Ошибка при импорте базы данных: ' + error.message);
            }
        };
        
        reader.readAsText(file);
    };
    
    input.click();
}

// === Функции для работы с API Claude ===

// Сохранение API ключа
function saveApiKey() {
    const apiKey = document.getElementById('apiKey').value;
    if (apiKey) {
        localStorage.setItem('claudeApiKey', apiKey);
        saveDatabase();
        alert('API ключ сохранён');
    } else {
        alert('Пожалуйста, введите API ключ');
    }
}

// Тестирование соединения с API
async function testApiConnection() {
    const apiKey = document.getElementById('apiKey').value;
    if (!apiKey) {
        alert('Пожалуйста, введите API ключ');
        return;
    }
    
    try {
        const response = await callClaudeAPI('Скажи "привет"');
        showModal('Тест соединения', 'Соединение успешно установлено! Ответ Claude: ' + response);
    } catch (error) {
        alert('Ошибка соединения: ' + error.message);
    }
}

// Вызов Claude API
async function callClaudeAPI(prompt) {
    const apiKey = localStorage.getItem('claudeApiKey');
    if (!apiKey) {
        throw new Error('API ключ не найден');
    }
    
    const response = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01',
            'x-api-key': apiKey
        },
        body: JSON.stringify({
            model: 'claude-3-7-sonnet-20250219',
            max_tokens: 2000,
            messages: [{
                role: 'user',
                content: prompt
            }]
        })
    });
    
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data.content[0].text;
}

// === Функции для взаимодействия с Claude по конкретным задачам ===

// Валидация графа
async function validateGraph() {
    if (categories.length === 0) {
        alert('Граф пуст. Добавьте категории.');
        return;
    }
    
    const graphData = {
        categories: categories.map(c => ({
            name: c.name,
            definition: c.definition,
            traditions: c.traditions,
            philosophers: c.philosophers
        })),
        relations: relations.map(r => ({
            from: categories.find(c => c.id === r.from)?.name,
            to: categories.find(c => c.id === r.to)?.name,
            type: relationTypes.find(t => t.id === r.type)?.name,
            bidirectional: r.bidirectional
        }))
    };
    
    const prompt = `Проанализируй следующий граф категорий философской концепции:
${JSON.stringify(graphData, null, 2)}
Выяви возможные логические противоречия, пропущенные важные категории или 
связи, необычные отношения между категориями. Предложи возможные улучшения.`;
    
    try {
        const response = await callClaudeAPI(prompt);
        showModal('Валидация графа', response);
    } catch (error) {
        alert('Ошибка при валидации: ' + error.message);
    }
}

// Предложение описания категории через Claude
async function requestCategoryDescription() {
    const name = document.getElementById('categoryName').value;
    if (!name) {
        alert('Пожалуйста, введите название категории');
        return;
    }
    
    const prompt = `Для категории "${name}" в контексте философской концепции, 
предложи краткое определение и возможные традиции/философов, связанных с этой категорией.`;
    
    try {
        const response = await callClaudeAPI(prompt);
        showModal('Предложение описания', response);
    } catch (error) {
        alert('Ошибка при запросе описания: ' + error.message);
    }
}

// Анализ связи через Claude
async function requestRelationAnalysis() {
    const fromId = document.getElementById('relationFrom').value;
    const toId = document.getElementById('relationTo').value;
    const typeId = document.getElementById('relationType').value;
    
    if (!fromId || !toId || !typeId) {
        alert('Пожалуйста, заполните все поля связи');
        return;
    }
    
    const fromCategory = categories.find(c => c.id === fromId);
    const toCategory = categories.find(c => c.id === toId);
    const relationType = relationTypes.find(t => t.id === typeId);
    
    const prompt = `Проанализируй связь типа "${relationType.name}" между категориями 
"${fromCategory.name}" и "${toCategory.name}". Предложи философское обоснование 
этой связи, возможные контраргументы и примеры аналогичных связей в других философских системах.`;
    
    try {
        const response = await callClaudeAPI(prompt);
        showModal('Анализ связи', response);
    } catch (error) {
        alert('Ошибка при анализе связи: ' + error.message);
    }
}

// Обогащение категории через Claude
async function enrichCategory(categoryId) {
    const category = categories.find(c => c.id === categoryId);
    if (!category) return;
    
    const prompt = `Для следующей категории "${category.name}" с определением "${category.definition}"
в контексте философской концепции, предложи расширенное описание, возможные альтернативные 
трактовки, исторические аналоги и связанные концепты.
Категория используется в традициях: ${category.traditions.join(', ')}
Категория связана с философами: ${category.philosophers.join(', ')}
При обогащении учитывай указанные традиции и философов.`;
    
    try {
        const response = await callClaudeAPI(prompt);
        showModal(`Обогащение категории "${category.name}"`, response);
    } catch (error) {
        alert('Ошибка при обогащении категории: ' + error.message);
    }
}

// Анализ количественных характеристик через Claude
async function requestMetricsAnalysis() {
    const categoryId = document.getElementById('selectedCategory').value;
    const category = categories.find(c => c.id === categoryId);
    if (!category) return;
    
    const prompt = `Я определил для категории "${category.name}" следующие характеристики:
- Центральность: ${category.metrics.centrality}
- Определённость: ${category.metrics.definition}
- Историческая значимость: ${category.metrics.historical}
Предложи философские и методологические основания для такой оценки, её возможные 
ограничения и альтернативные подходы к оценке.`;
    
    try {
        const response = await callClaudeAPI(prompt);
        showModal('Анализ характеристик', response);
    } catch (error) {
        alert('Ошибка при анализе характеристик: ' + error.message);
    }
}

// Обновление количественных метрик категории
function updateMetric(metricType) {
    const categoryId = document.getElementById('selectedCategory').value;
    const category = categories.find(c => c.id === categoryId);
    if (!category) return;
    
    const value = document.getElementById(metricType).value;
    category.metrics[metricType] = parseInt(value);
    document.getElementById(metricType + 'Value').textContent = value;
    
    saveDatabase();
}

// Отображение метрик выбранной категории
function updateMetricsDisplay() {
    const categoryId = document.getElementById('selectedCategory').value;
    const category = categories.find(c => c.id === categoryId);
    if (!category) return;
    
    document.getElementById('centrality').value = category.metrics.centrality;
    document.getElementById('centralityValue').textContent = category.metrics.centrality;
    
    document.getElementById('definition').value = category.metrics.definition;
    document.getElementById('definitionValue').textContent = category.metrics.definition;
    
    document.getElementById('historical').value = category.metrics.historical;
    document.getElementById('historicalValue').textContent = category.metrics.historical;
}

// Экспорт графа в JSON
function exportGraph() {
    if (!currentConcept) {
        alert('Сначала создайте или выберите концепцию');
        return;
    }
    
    const graphData = {
        conceptId: currentConcept.id,
        conceptName: currentConcept.name,
        categories: categories.filter(c => c.conceptId === currentConcept.id),
        relations: relations.filter(r => {
            const fromCategory = categories.find(c => c.id === r.from);
            return fromCategory && fromCategory.conceptId === currentConcept.id;
        }),
        exportDate: new Date().toISOString()
    };
    
    const dataStr = JSON.stringify(graphData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `concept_${currentConcept.name.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Импорт графа из JSON
function importGraph() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    
    input.onchange = function(event) {
        const file = event.target.files[0];
        const reader = new FileReader();
        
        reader.onload = function(e) {
            try {
                const graphData = JSON.parse(e.target.result);
                
                // Создаем новую концепцию или обновляем существующую
                let concept = concepts.find(c => c.id === graphData.conceptId);
                if (!concept) {
                    concept = {
                        id: graphData.conceptId,
                        name: graphData.conceptName,
                        createdAt: new Date().toISOString()
                    };
                    concepts.push(concept);
                }
                
                // Импортируем категории
                graphData.categories.forEach(importedCategory => {
                    if (!categories.find(c => c.id === importedCategory.id)) {
                        categories.push({
                            ...importedCategory,
                            conceptId: concept.id
                        });
                    }
                });
                
                // Импортируем связи
                graphData.relations.forEach(importedRelation => {
                    if (!relations.find(r => r.id === importedRelation.id)) {
                        relations.push(importedRelation);
                    }
                });
                
                currentConcept = concept;
                saveDatabase();
                updateUI();
                alert('Граф успешно импортирован!');
            } catch (error) {
                alert('Ошибка при импорте графа: ' + error.message);
            }
        };
        
        reader.readAsText(file);
    };
    
    input.click();
}