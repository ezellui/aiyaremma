// Часть 4: Дополнительные функции и завершение кода

// === Функции для работы с концепциями ===

// Создание новой концепции
function createConcept() {
    const name = prompt('Введите название концепции:');
    if (!name) return;
    
    const concept = {
        id: generateId(),
        name,
        createdAt: new Date().toISOString(),
        description: '',
        author: ''
    };
    
    concepts.push(concept);
    currentConcept = concept;
    saveDatabase();
    updateUI();
}

// Выбор текущей концепции
function selectConcept(conceptId) {
    currentConcept = concepts.find(c => c.id === conceptId);
    updateUI();
}

// === Вспомогательные функции для генерации тезисов ===

// Генерация версии тезисов (для сравнения)
async function generateThesesVersion(conceptId, useMetrics) {
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
    
    const prompt = useMetrics 
        ? `На основе графа концепции с учётом количественных характеристик:
${JSON.stringify(graphData, null, 2)}
сформулируй 5 ключевых тезисов.`
        : `На основе графа концепции без учёта количественных характеристик:
${JSON.stringify(graphData, null, 2)}
сформулируй 5 ключевых тезисов.`;
    
    try {
        return await callClaudeAPI(prompt);
    } catch (error) {
        console.error('Ошибка при генерации версии тезисов:', error);
        return null;
    }
}

// Сохранение сгенерированных тезисов
function saveGeneratedTheses(conceptId, theses) {
    const concept = concepts.find(c => c.id === conceptId);
    if (concept) {
        concept.generatedTheses = concept.generatedTheses || [];
        concept.generatedTheses.push({
            id: generateId(),
            content: theses,
            generatedAt: new Date().toISOString(),
            type: document.getElementById('thesisType').value,
            style: document.getElementById('thesisStyle').value,
            detailLevel: document.getElementById('detailLevel').value
        });
        saveDatabase();
    }
}

// Сохранение результата синтеза
function saveSynthesisResult(synthesis) {
    const concept1Id = document.getElementById('concept1').value;
    const concept2Id = document.getElementById('concept2').value;
    const concept1 = concepts.find(c => c.id === concept1Id);
    const concept2 = concepts.find(c => c.id === concept2Id);
    
    const synthesizedConcept = {
        id: generateId(),
        name: `Синтез: ${concept1.name} и ${concept2.name}`,
        sourceConceptIds: [concept1Id, concept2Id],
        synthesisMethod: document.getElementById('synthesisMethod').value,
        synthesisFocus: document.getElementById('synthesisFocus').value,
        innovationLevel: document.getElementById('innovationLevel').value,
        graph: synthesis,
        createdAt: new Date().toISOString()
    };
    
    concepts.push(synthesizedConcept);
    saveDatabase();
    updateUI();
}

// === Стилизация визуализации графа ===

// Добавим стили для визуализации графа
const graphStyles = `
.graph-vis {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    justify-content: center;
}

.graph-category {
    width: 250px;
    min-height: 150px;
    background: #f8f9fa;
    border: 2px solid #3498db;
    border-radius: 10px;
    padding: 15px;
    position: relative;
    transition: transform 0.3s ease;
}

.graph-category:hover {
    transform: scale(1.05);
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.graph-relation {
    width: 200px;
    background: #e8f0fe;
    border: 1px solid #3498db;
    border-radius: 8px;
    padding: 10px;
    margin-top: 20px;
}

.graph-relation::before {
    content: '↔';
    position: absolute;
    top: -15px;
    left: 50%;
    transform: translateX(-50%);
    background: white;
    padding: 2px 8px;
    border-radius: 10px;
    border: 1px solid #3498db;
}

.tags {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    margin-top: 10px;
}

.tag {
    background: #e8f0fe;
    color: #2c3e50;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 0.85em;
}

.metrics-badge {
    position: absolute;
    top: -10px;
    right: -10px;
    background: #3498db;
    color: white;
    border-radius: 50%;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
}

.loading {
    text-align: center;
    padding: 20px;
    color: #7f8c8d;
}

.error {
    color: #e74c3c;
    padding: 10px;
    background: #fadbd8;
    border-radius: 5px;
    margin: 10px 0;
}

.success {
    color: #27ae60;
    padding: 10px;
    background: #d5f5e3;
    border-radius: 5px;
    margin: 10px 0;
}
`;

// Добавляем стили в документ
const styleSheet = document.createElement('style');
styleSheet.textContent = graphStyles;
document.head.appendChild(styleSheet);

// === Инициализация приложения ===

// Дополнительные функции для инициализации
function initializeApp() {
    // Проверяем наличие сохраненного API ключа
    const savedApiKey = localStorage.getItem('claudeApiKey');
    if (savedApiKey) {
        document.getElementById('apiKey').value = savedApiKey;
    }
    
    // Загружаем данные из базы
    loadDatabase();
    
    // Настраиваем обработчики событий
    setupEventListeners();
    
    // Обновляем интерфейс
    updateUI();
    
    // Проверяем наличие концепций
    if (concepts.length === 0) {
        showWelcomeMessage();
    }
}

// Приветственное сообщение для новых пользователей
function showWelcomeMessage() {
    const welcomeHTML = `
        <div class="welcome-message card">
            <h3>Добро пожаловать в сервис философских концепций!</h3>
            <p>Для начала работы:</p>
            <ol>
                <li>Введите ваш API ключ Claude в поле выше</li>
                <li>Создайте новую концепцию или загрузите существующую</li>
                <li>Начните добавлять категории и связи между ними</li>
            </ol>
            <button onclick="createConcept()" class="button primary">Создать первую концепцию</button>
        </div>
    `;
    
    const graphContainer = document.getElementById('graphContainer');
    if (graphContainer) {
        graphContainer.innerHTML = welcomeHTML;
    }
}

// Добавляем обработчик ошибок для API запросов
function handleApiError(error) {
    console.error('API Error:', error);
    let errorMessage = 'Произошла ошибка при обращении к API Claude.';
    
    if (error.message.includes('401')) {
        errorMessage = 'Неверный API ключ. Пожалуйста, проверьте и обновите ключ.';
    } else if (error.message.includes('429')) {
        errorMessage = 'Превышен лимит запросов к API. Пожалуйста, подождите немного.';
    }
    
    showError(errorMessage);
}

// Показ сообщения об ошибке
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error';
    errorDiv.textContent = message;
    
    const container = document.querySelector('.container');
    container.insertBefore(errorDiv, container.firstChild);
    
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

// Показ сообщения об успехе
function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'success';
    successDiv.textContent = message;
    
    const container = document.querySelector('.container');
    container.insertBefore(successDiv, container.firstChild);
    
    setTimeout(() => {
        successDiv.remove();
    }, 3000);
}

// Показ индикатора загрузки
function showLoading(element) {
    element.innerHTML = '<div class="loading">Загрузка...</div>';
}

// Автосохранение
function setupAutoSave() {
    setInterval(() => {
        saveDatabase();
    }, 30000); // Сохранение каждые 30 секунд
}

// === Дополнительные утилиты ===

// Экспорт всех данных в CSV
function exportToCSV() {
    const data = {
        concepts: concepts.map(c => ({
            id: c.id,
            name: c.name,
            createdAt: c.createdAt
        })),
        categories: categories.map(c => ({
            id: c.id,
            conceptId: c.conceptId,
            name: c.name,
            definition: c.definition,
            traditions: c.traditions.join(';'),
            philosophers: c.philosophers.join(';')
        })),
        relations: relations.map(r => ({
            id: r.id,
            from: r.from,
            to: r.to,
            type: r.type,
            bidirectional: r.bidirectional
        }))
    };
    
    // Создаем CSV для каждой сущности
    Object.keys(data).forEach(entityName => {
        const csvContent = convertToCSV(data[entityName]);
        downloadCSV(csvContent, `${entityName}_${new Date().toISOString().split('T')[0]}.csv`);
    });
}

// Конвертация данных в CSV формат
function convertToCSV(data) {
    if (data.length === 0) return '';
    
    const headers = Object.keys(data[0]);
    const csvRows = [headers.join(',')];
    
    data.forEach(item => {
        const values = headers.map(header => {
            const value = item[header];
            return typeof value === 'string' ? `"${value.replace(/"/g, '""')}"` : value;
        });
        csvRows.push(values.join(','));
    });
    
    return csvRows.join('\n');
}

// Скачивание CSV файла
function downloadCSV(content, filename) {
    const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// === Завершающая инициализация ===

// Запускаем инициализацию при полной загрузке DOM
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupAutoSave();
    
    // Добавляем обработчик для закрытия модального окна по Escape
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            closeModal();
        }
    });
    
    // Обработчик для изменения размера окна
    window.addEventListener('resize', function() {
        // Перерисовываем граф при изменении размера окна
        updateGraphVisualization();
    });
});

// Предупреждение при закрытии страницы с несохраненными изменениями
window.addEventListener('beforeunload', function(e) {
    const unsavedChanges = checkForUnsavedChanges();
    if (unsavedChanges) {
        e.preventDefault();
        e.returnValue = '';
    }
});

// Проверка наличия несохраненных изменений
function checkForUnsavedChanges() {
    // Здесь можно добавить более сложную логику проверки
    return false;
}

// Экспорт функций для тестирования (если необходимо)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        createCategory,
        createRelation,
        generateTheses,
        synthesizeConcepts,
        performAnalysis
    };
}