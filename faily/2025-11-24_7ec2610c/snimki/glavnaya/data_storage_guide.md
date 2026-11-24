# Руководство по организации внешнего хранения данных

## Архитектура решения

Я предлагаю **гибридное решение**:
1. **Начальные данные** загружаются из внешнего JSON файла
2. **Изменения** сохраняются в LocalStorage браузера
3. **Экспорт/импорт** для переноса данных между браузерами или резервного копирования

---

## Часть 1: Структура файлов

```
project/
├── index.html                    # Основная HTML страница
├── data/
│   └── philosophy_data.json     # Внешний файл с данными
└── js/
    └── data_manager.js          # (опционально) Менеджер данных
```

---

## Часть 2: Формат файла philosophy_data.json

Создайте файл `data/philosophy_data.json`:

```json
{
  "philosopherConcepts": {
    "Платон": {
      "name": "Платон",
      "color": "#FF6B6B",
      "birth": -428,
      "death": -348
    },
    "Аристотель": {
      "name": "Аристотель",
      "color": "#4ECDC4",
      "birth": -384,
      "death": -322
    },
    "Кант": {
      "name": "Кант",
      "color": "#45B7D1",
      "birth": 1724,
      "death": 1804
    }
  },
  "concepts": [
    {
      "id": "plato_ideas",
      "label": "Мир идей",
      "concept": "Платон",
      "description": "Мир вечных и неизменных идей",
      "extendedDescription": "Согласно Платону, существует трансцендентный мир идеальных форм..."
    },
    {
      "id": "aristotle_substance",
      "label": "Субстанция",
      "concept": "Аристотель",
      "description": "Первичная сущность, основа бытия"
    }
  ],
  "connections": [
    {
      "from": "plato_ideas",
      "to": "aristotle_substance",
      "type": "critique",
      "weight": 3,
      "bidirectional": false,
      "description": "Аристотель критикует теорию идей Платона"
    }
  ],
  "rubrics": [
    {
      "id": "metaphysics",
      "name": "Метафизика",
      "description": "Учение о первоначалах бытия"
    },
    {
      "id": "epistemology",
      "name": "Эпистемология",
      "description": "Теория познания"
    }
  ],
  "conceptToRubrics": {
    "plato_ideas": ["metaphysics", "epistemology"],
    "aristotle_substance": ["metaphysics"]
  },
  "relationTypes": [
    {
      "id": "influence",
      "label": "Влияние",
      "color": "#3498db"
    },
    {
      "id": "critique",
      "label": "Критика",
      "color": "#e74c3c"
    },
    {
      "id": "development",
      "label": "Развитие",
      "color": "#2ecc71"
    },
    {
      "id": "similarity",
      "label": "Сходство",
      "color": "#f39c12"
    },
    {
      "id": "opposition",
      "label": "Противопоставление",
      "color": "#9b59b6"
    }
  ]
}
```

---

## Часть 3: Модификация HTML файла

### 3.1 Удалить встроенные данные

В вашем HTML файле найдите и **удалите** секции с данными:
- `const philosopherConcepts = {...}`
- `const concepts = [...]`
- `const connections = [...]`
- `const rubrics = [...]`
- `const conceptToRubrics = {...}`
- `const relationTypes = [...]`

### 3.2 Добавить систему загрузки и сохранения данных

**Вставьте этот код в начало секции `<script>`** (сразу после `<script>`):

```javascript
// ============================================
// СИСТЕМА УПРАВЛЕНИЯ ДАННЫМИ
// ============================================

// Ключ для LocalStorage
const STORAGE_KEY = 'philosophyGraphData';
const DATA_VERSION = '1.0';

// Глобальные переменные для данных (будут инициализированы)
let philosopherConcepts = {};
let concepts = [];
let connections = [];
let rubrics = [];
let conceptToRubrics = {};
let relationTypes = [];

// Флаг, указывающий, загружены ли данные
let dataLoaded = false;

// Настройки приложения
const appSettings = {
    autoSaveEnabled: true,
    dataSource: 'localStorage', // 'localStorage' или 'json'
    jsonFilePath: './data/philosophy_data.json'
};

/**
 * Загрузка данных при старте приложения
 */
async function loadData() {
    try {
        // Сначала пытаемся загрузить из LocalStorage
        const savedData = loadFromLocalStorage();
        
        if (savedData && savedData.version === DATA_VERSION) {
            console.log('📦 Загрузка данных из LocalStorage');
            applyData(savedData.data);
            dataLoaded = true;
            initializeApp();
            return;
        }
        
        // Если нет сохраненных данных, загружаем из JSON
        console.log('📄 Загрузка начальных данных из JSON файла');
        const response = await fetch(appSettings.jsonFilePath);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const jsonData = await response.json();
        applyData(jsonData);
        
        // Сохраняем в LocalStorage для последующих запусков
        saveToLocalStorage();
        
        dataLoaded = true;
        initializeApp();
        
    } catch (error) {
        console.error('❌ Ошибка загрузки данных:', error);
        
        // Используем данные по умолчанию
        console.log('🔄 Использование данных по умолчанию');
        applyData(getDefaultData());
        dataLoaded = true;
        initializeApp();
    }
}

/**
 * Применение загруженных данных к глобальным переменным
 */
function applyData(data) {
    philosopherConcepts = data.philosopherConcepts || {};
    concepts = data.concepts || [];
    connections = data.connections || [];
    rubrics = data.rubrics || [];
    conceptToRubrics = data.conceptToRubrics || {};
    relationTypes = data.relationTypes || [];
    
    // Создаем производные структуры
    window.nodes = concepts.map(c => ({
        id: c.id,
        label: c.label,
        concept: c.concept,
        description: c.description,
        extendedDescription: c.extendedDescription
    }));
    
    window.links = connections.map(conn => ({
        source: conn.from,
        target: conn.to,
        type: conn.type,
        weight: conn.weight || 2,
        bidirectional: conn.bidirectional || false
    }));
    
    window.relationTypesObj = {};
    relationTypes.forEach(type => {
        window.relationTypesObj[type.id] = type;
    });
}

/**
 * Получение данных по умолчанию (минимальный набор)
 */
function getDefaultData() {
    return {
        philosopherConcepts: {
            "Платон": { name: "Платон", color: "#FF6B6B", birth: -428, death: -348 },
            "Аристотель": { name: "Аристотель", color: "#4ECDC4", birth: -384, death: -322 }
        },
        concepts: [
            {
                id: "plato_ideas",
                label: "Мир идей",
                concept: "Платон",
                description: "Мир вечных и неизменных идей"
            },
            {
                id: "aristotle_substance",
                label: "Субстанция",
                concept: "Аристотель",
                description: "Первичная сущность"
            }
        ],
        connections: [
            {
                from: "plato_ideas",
                to: "aristotle_substance",
                type: "critique",
                weight: 2,
                bidirectional: false
            }
        ],
        rubrics: [
            { id: "metaphysics", name: "Метафизика", description: "Учение о бытии" }
        ],
        conceptToRubrics: {
            "plato_ideas": ["metaphysics"],
            "aristotle_substance": ["metaphysics"]
        },
        relationTypes: [
            { id: "influence", label: "Влияние", color: "#3498db" },
            { id: "critique", label: "Критика", color: "#e74c3c" },
            { id: "development", label: "Развитие", color: "#2ecc71" },
            { id: "similarity", label: "Сходство", color: "#f39c12" },
            { id: "opposition", label: "Противопоставление", color: "#9b59b6" }
        ]
    };
}

/**
 * Сохранение в LocalStorage
 */
function saveToLocalStorage() {
    try {
        const dataToSave = {
            version: DATA_VERSION,
            timestamp: new Date().toISOString(),
            data: {
                philosopherConcepts: philosopherConcepts,
                concepts: concepts,
                connections: connections,
                rubrics: rubrics,
                conceptToRubrics: conceptToRubrics,
                relationTypes: relationTypes
            }
        };
        
        localStorage.setItem(STORAGE_KEY, JSON.stringify(dataToSave));
        console.log('💾 Данные сохранены в LocalStorage');
        showNotification('Изменения сохранены', 'success');
        
    } catch (error) {
        console.error('❌ Ошибка сохранения в LocalStorage:', error);
        showNotification('Ошибка сохранения данных', 'error');
    }
}

/**
 * Загрузка из LocalStorage
 */
function loadFromLocalStorage() {
    try {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
            return JSON.parse(stored);
        }
        return null;
    } catch (error) {
        console.error('❌ Ошибка загрузки из LocalStorage:', error);
        return null;
    }
}

/**
 * Автосохранение (вызывается после каждого изменения)
 */
function autoSave() {
    if (appSettings.autoSaveEnabled && dataLoaded) {
        saveToLocalStorage();
    }
}

/**
 * Экспорт данных в JSON файл
 */
function exportData() {
    const dataToExport = {
        philosopherConcepts: philosopherConcepts,
        concepts: concepts,
        connections: connections,
        rubrics: rubrics,
        conceptToRubrics: conceptToRubrics,
        relationTypes: relationTypes
    };
    
    const dataStr = JSON.stringify(dataToExport, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `philosophy_graph_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    showNotification('Данные экспортированы', 'success');
}

/**
 * Импорт данных из JSON файла
 */
function importData() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    
    input.onchange = (event) => {
        const file = event.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const importedData = JSON.parse(e.target.result);
                
                // Проверяем структуру данных
                if (!importedData.philosopherConcepts || !importedData.concepts) {
                    throw new Error('Неверная структура данных');
                }
                
                if (confirm('Импортировать данные? Это заменит все текущие данные.')) {
                    applyData(importedData);
                    saveToLocalStorage();
                    
                    // Перезагружаем граф
                    updateGraphData();
                    initFilters();
                    
                    showNotification('Данные импортированы успешно', 'success');
                }
                
            } catch (error) {
                console.error('❌ Ошибка импорта:', error);
                showNotification('Ошибка импорта данных', 'error');
            }
        };
        reader.readAsText(file);
    };
    
    input.click();
}

/**
 * Сброс данных к начальному состоянию
 */
function resetData() {
    if (!confirm('Вы уверены? Это удалит все изменения и восстановит данные из JSON файла.')) {
        return;
    }
    
    // Очищаем LocalStorage
    localStorage.removeItem(STORAGE_KEY);
    
    // Перезагружаем страницу
    location.reload();
}

/**
 * Очистка всех данных
 */
function clearAllData() {
    if (!confirm('Вы уверены? Это удалит ВСЕ данные без возможности восстановления!')) {
        return;
    }
    
    if (!confirm('Последнее предупреждение! Все данные будут удалены. Продолжить?')) {
        return;
    }
    
    localStorage.removeItem(STORAGE_KEY);
    location.reload();
}

/**
 * Показ уведомлений
 */
function showNotification(message, type = 'info') {
    // Создаем элемент уведомления
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Добавляем стили, если их еще нет
    if (!document.getElementById('notificationStyles')) {
        const style = document.createElement('style');
        style.id = 'notificationStyles';
        style.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 15px 20px;
                border-radius: 8px;
                color: white;
                font-weight: 600;
                z-index: 10000;
                animation: slideIn 0.3s ease-out, slideOut 0.3s ease-in 2.7s;
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            }
            .notification-success { background: #27ae60; }
            .notification-error { background: #e74c3c; }
            .notification-info { background: #3498db; }
            @keyframes slideIn {
                from { transform: translateX(400px); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(400px); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

/**
 * Инициализация приложения после загрузки данных
 */
function initializeApp() {
    console.log('🚀 Инициализация приложения');
    console.log(`📊 Загружено: ${Object.keys(philosopherConcepts).length} философов, ${concepts.length} концепций, ${connections.length} связей`);
    
    // Здесь будет вызов существующей функции инициализации графа
    // Эта функция будет добавлена ниже
}

// Загружаем данные при загрузке страницы
window.addEventListener('DOMContentLoaded', loadData);
```

---

## Часть 4: Интеграция с существующим кодом

### 4.1 Обновление функций редактирования

В функциях `savePhilosopher()`, `saveConcept()`, `saveConnection()`, `deletePhilosopher()`, `deleteConcept()`, `deleteConnection()` добавьте в конец **перед** `closeEdit...Modal()`:

```javascript
// В конце каждой функции сохранения/удаления добавить:
autoSave();
```

Например:
```javascript
function savePhilosopher() {
    // ... существующий код ...
    
    // Обновляем граф и легенду
    updateGraphData();
    initFilters();
    
    // ДОБАВИТЬ ЭТУ СТРОКУ:
    autoSave();
    
    closeEditPhilosopherModal();
}
```

### 4.2 Обновление функции инициализации графа

Найдите код инициализации графа (обычно в конце скрипта) и **замените** его на:

```javascript
// ЗАМЕНИТЬ ЭТУ ЧАСТЬ:
// console.log("Инициализация графа:", nodes.length, "узлов,", links.length, "связей");
// initFilters();
// updateFilterStats();

// НА ЭТУ:
function initializeApp() {
    console.log("🎨 Инициализация графа:", nodes.length, "узлов,", links.length, "связей");
    
    // Создаем SVG и запускаем симуляцию
    createGraphVisualization();
    
    // Инициализируем фильтры
    initFilters();
    updateFilterStats();
    
    // Делаем легенду редактируемой
    setTimeout(makeLegendsEditable, 100);
    
    console.log("✅ Приложение готово к работе");
}

// Функция создания визуализации (если её еще нет)
function createGraphVisualization() {
    // Весь ваш существующий код создания SVG, simulation, node, link
    // Обычно это код, который был в глобальной области
}
```

---

## Часть 5: Панель управления данными

### 5.1 Добавить HTML для панели управления

В секции `<body>`, после `<div id="container">` добавить:

```html
<!-- Панель управления данными -->
<div id="dataManagementPanel" class="data-panel">
    <button class="data-panel-toggle" onclick="toggleDataPanel()">
        ⚙️ Управление данными
    </button>
    
    <div class="data-panel-content" id="dataPanelContent" style="display: none;">
        <h4>Управление данными</h4>
        
        <div class="data-panel-section">
            <h5>📊 Статистика</h5>
            <div class="data-stats">
                <div class="stat-item">
                    <span class="stat-label">Философов:</span>
                    <span class="stat-value" id="statPhilosophers">0</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Концепций:</span>
                    <span class="stat-value" id="statConcepts">0</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Связей:</span>
                    <span class="stat-value" id="statConnections">0</span>
                </div>
            </div>
        </div>
        
        <div class="data-panel-section">
            <h5>💾 Сохранение</h5>
            <div class="data-panel-checkbox">
                <input type="checkbox" id="autoSaveToggle" checked onchange="toggleAutoSave()">
                <label for="autoSaveToggle">Автосохранение</label>
            </div>
            <button class="data-panel-btn" onclick="saveToLocalStorage()">
                Сохранить вручную
            </button>
        </div>
        
        <div class="data-panel-section">
            <h5>📁 Экспорт/Импорт</h5>
            <button class="data-panel-btn" onclick="exportData()">
                📤 Экспортировать в JSON
            </button>
            <button class="data-panel-btn" onclick="importData()">
                📥 Импортировать из JSON
            </button>
        </div>
        
        <div class="data-panel-section">
            <h5>🔄 Сброс</h5>
            <button class="data-panel-btn data-panel-btn-warning" onclick="resetData()">
                Сбросить к исходным данным
            </button>
            <button class="data-panel-btn data-panel-btn-danger" onclick="clearAllData()">
                ⚠️ Очистить все данные
            </button>
        </div>
        
        <div class="data-panel-info">
            <small>
                Последнее сохранение: <span id="lastSaveTime">-</span>
            </small>
        </div>
    </div>
</div>
```

### 5.2 Добавить CSS для панели

В секцию `<style>` добавить:

```css
/* Панель управления данными */
.data-panel {
    position: fixed;
    bottom: 20px;
    left: 20px;
    z-index: 1000;
}

.data-panel-toggle {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 12px 20px;
    border-radius: 25px;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    transition: all 0.3s;
}

.data-panel-toggle:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.data-panel-content {
    position: absolute;
    bottom: 60px;
    left: 0;
    background: white;
    border-radius: 15px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    padding: 20px;
    min-width: 300px;
    max-height: 70vh;
    overflow-y: auto;
}

.data-panel-content h4 {
    margin: 0 0 20px 0;
    color: #2d3436;
    font-size: 18px;
    border-bottom: 2px solid #667eea;
    padding-bottom: 10px;
}

.data-panel-content h5 {
    margin: 15px 0 10px 0;
    color: #636e72;
    font-size: 14px;
    font-weight: 600;
}

.data-panel-section {
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px solid #e1e8ed;
}

.data-panel-section:last-of-type {
    border-bottom: none;
}

.data-stats {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.stat-item {
    display: flex;
    justify-content: space-between;
    padding: 8px;
    background: #f8f9fa;
    border-radius: 6px;
}

.stat-label {
    color: #636e72;
    font-size: 13px;
}

.stat-value {
    font-weight: 600;
    color: #2d3436;
}

.data-panel-checkbox {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
}

.data-panel-checkbox input {
    width: 18px;
    height: 18px;
    cursor: pointer;
    accent-color: #667eea;
}

.data-panel-checkbox label {
    cursor: pointer;
    font-size: 14px;
    color: #2d3436;
}

.data-panel-btn {
    width: 100%;
    padding: 10px;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
    margin-bottom: 8px;
    font-size: 13px;
}

.data-panel-btn {
    background: #3498db;
    color: white;
}

.data-panel-btn:hover {
    background: #2980b9;
    transform: translateY(-1px);
}

.data-panel-btn-warning {
    background: #f39c12;
}

.data-panel-btn-warning:hover {
    background: #e67e22;
}

.data-panel-btn-danger {
    background: #e74c3c;
}

.data-panel-btn-danger:hover {
    background: #c0392b;
}

.data-panel-info {
    margin-top: 15px;
    padding-top: 15px;
    border-top: 1px solid #e1e8ed;
    color: #95a5a6;
    font-size: 12px;
}
```

### 5.3 Добавить JavaScript функции панели

```javascript
// Функции для панели управления данными
function toggleDataPanel() {
    const content = document.getElementById('dataPanelContent');
    const isVisible = content.style.display !== 'none';
    content.style.display = isVisible ? 'none' : 'block';
    
    if (!isVisible) {
        updateDataStats();
    }
}

function updateDataStats() {
    document.getElementById('statPhilosophers').textContent = Object.keys(philosopherConcepts).length;
    document.getElementById('statConcepts').textContent = concepts.length;
    document.getElementById('statConnections').textContent = connections.length;
    
    const saved = loadFromLocalStorage();
    if (saved && saved.timestamp) {
        const date = new Date(saved.timestamp);
        document.getElementById('lastSaveTime').textContent = date.toLocaleString('ru-RU');
    }
}

function toggleAutoSave() {
    appSettings.autoSaveEnabled = document.getElementById('autoSaveToggle').checked;
    showNotification(
        appSettings.autoSaveEnabled ? 'Автосохранение включено' : 'Автосохранение выключено',
        'info'
    );
}
```

---

## Часть 6: Пример конвертации существующих данных

Если у вас уже есть данные в HTML файле, используйте этот скрипт для их извлечения:

```javascript
// ВРЕМЕННЫЙ КОД - выполните его в консоли браузера для извлечения данных
function extractCurrentData() {
    const data = {
        philosopherConcepts: philosopherConcepts,
        concepts: concepts,
        connections: connections,
        rubrics: rubrics,
        conceptToRubrics: conceptToRubrics,
        relationTypes: relationTypes
    };
    
    const dataStr = JSON.stringify(data, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = 'philosophy_data.json';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    console.log('✅ Данные экспортированы в philosophy_data.json');
}

// Вызовите эту функцию в консоли браузера
extractCurrentData();
```

---

## Часть 7: Инструкция по миграции

### Шаг 1: Извлечь текущие данные
1. Откройте ваш текущий HTML файл в браузере
2. Откройте консоль разработчика (F12)
3. Вставьте и выполните код из Части 6
4. Сохраните полученный файл как `data/philosophy_data.json`

### Шаг 2: Модифицировать HTML
1. Удалите встроенные данные из HTML (секции с const)
2. Добавьте код системы управления данными в начало `<script>`
3. Добавьте панель управления в HTML
4. Добавьте стили для панели
5. Обновите функции сохранения (добавьте `autoSave()`)

### Шаг 3: Создать структуру файлов
```
Создайте папку data/
Поместите туда philosophy_data.json
```

### Шаг 4: Тестирование
1. Откройте HTML файл в браузере
2. Проверьте, что данные загружаются
3. Попробуйте отредактировать элемент
4. Перезагрузите страницу - изменения должны сохраниться
5. Попробуйте экспорт/импорт

---

## Резюме: Что происходит

1. **При первом запуске:** Данные загружаются из `philosophy_data.json`
2. **При редактировании:** Изменения автоматически сохраняются в LocalStorage
3. **При последующих запусках:** Данные загружаются из LocalStorage (быстрее)
4. **Экспорт:** Можно выгрузить текущее состояние в JSON файл
5. **Импорт:** Можно загрузить данные из JSON файла
6. **Сброс:** Можно вернуться к начальным данным из JSON

### Преимущества этого подхода:
✅ Не требует сервера
✅ Данные сохраняются между сеансами
✅ Можно делиться данными (экспорт/импорт)
✅ Легко вернуться к исходному состоянию
✅ Прозрачная работа для пользователя

---

**Конец документа**
