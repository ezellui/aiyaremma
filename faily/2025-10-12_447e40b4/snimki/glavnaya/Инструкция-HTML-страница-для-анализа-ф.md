# Инструкция по созданию HTML-страницы для анализа философского графа

## Содержание
1. [Структура файлов](#структура-файлов)
2. [Шаг 1: Создание HTML-каркаса](#шаг-1-создание-html-каркаса)
3. [Шаг 2: Подключение данных](#шаг-2-подключение-данных)
4. [Шаг 3: Добавление классов анализа](#шаг-3-добавление-классов-анализа)
5. [Шаг 4: Создание UI и запуск](#шаг-4-создание-ui-и-запуск)
6. [Проверка работоспособности](#проверка-работоспособности)

---

## Структура файлов

Создайте следующую структуру папок и файлов:

```
philosophy-graph-analysis/
│
├── index.html                    (основной файл)
├── data/
│   └── philo_data_refactored.js (данные из документа)
├── js/
│   ├── analyzer.js              (классы анализа)
│   └── ui.js                    (интерфейс и запуск)
└── css/
    └── styles.css               (стили)
```

---

## Шаг 1: Создание HTML-каркаса

### 1.1. Создайте файл `index.html`

Скопируйте следующий код полностью:

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Анализ философского графа знаний</title>
    <link rel="stylesheet" href="css/styles.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>🧠 Количественный анализ философского графа знаний</h1>
            <p class="subtitle">Интерактивная платформа для исследования связей между философскими концепциями</p>
        </header>

        <nav class="controls">
            <button id="runBasicStats" class="btn btn-primary">📊 Базовая статистика</button>
            <button id="runCentrality" class="btn btn-primary">🎯 Центральность</button>
            <button id="runCommunities" class="btn btn-primary">👥 Сообщества</button>
            <button id="runPaths" class="btn btn-primary">🔗 Пути и расстояния</button>
            <button id="runClustering" class="btn btn-primary">🔷 Кластеризация</button>
            <button id="runTemporal" class="btn btn-primary">⏱️ Временной анализ</button>
            <button id="runAll" class="btn btn-success">▶️ Запустить всё</button>
            <button id="clearResults" class="btn btn-secondary">🗑️ Очистить</button>
        </nav>

        <div id="loading" class="loading" style="display: none;">
            <div class="spinner"></div>
            <p>Выполняется анализ...</p>
        </div>

        <main id="results" class="results">
            <div class="placeholder">
                <h2>👆 Выберите метод анализа</h2>
                <p>Нажмите на одну из кнопок выше, чтобы начать анализ</p>
            </div>
        </main>

        <footer>
            <p>Данные: 25 философов | 198 концепций | 389 связей | Период: 469 до н.э. - 1995 н.э.</p>
        </footer>
    </div>

    <!-- Подключение скриптов -->
    <script src="data/philo_data_refactored.js"></script>
    <script src="js/analyzer.js"></script>
    <script src="js/ui.js"></script>
</body>
</html>
```

---

## Шаг 2: Подключение данных

### 2.1. Создайте папку `data` и файл `data/philo_data_refactored.js`

**ВАЖНО:** Скопируйте **ВЕСЬ** код из документа `philo_data_refactored.js` (который вы предоставили в начале) в этот файл.

Файл должен начинаться так:
```javascript
// ============================================
// 1. ФИЛОСОФЫ (единый источник истины)
// ============================================
const philosophers = [
    { id: "socrates", name: "Сократ", nameRu: "Сократ", ...
```

И заканчиваться так:
```javascript
    ...
    { source: "property_theory", target: "objective_spirit", type: "influence", weight: 2 }
];
```

**Проверьте:** Файл должен содержать 4 основных массива:
- `philosophers`
- `rubrics`
- `concepts`
- `relations`

---

## Шаг 3: Добавление классов анализа

### 3.1. Создайте папку `js` и файл `js/analyzer.js`

Этот файл будет содержать **ВСЕ** классы анализа. Скопируйте код по частям из второго документа (с количественными методами).

#### Часть 1: PhilosophyGraphAnalyzer

Скопируйте из документа "Количественные методы анализа философского графа" → Раздел 1 → весь класс `PhilosophyGraphAnalyzer`:

```javascript
/**
 * Класс для анализа философского графа
 */
class PhilosophyGraphAnalyzer {
    constructor(philosophers, concepts, relations, rubrics) {
        this.philosophers = philosophers;
        this.concepts = concepts;
        this.relations = relations;
        this.rubrics = rubrics;
        
        // Построение графа
        this.graph = this.buildGraph();
        this.adjacencyMatrix = this.buildAdjacencyMatrix();
    }
    
    // ... весь код класса ...
}
```

#### Часть 2: Классы центральности

Добавьте после `PhilosophyGraphAnalyzer` следующие классы из Раздела 2:

```javascript
/**
 * Вычисление Degree Centrality
 */
class DegreeCentrality {
    // ... весь код из раздела 2.1 ...
}

/**
 * Вычисление Betweenness Centrality
 */
class BetweennessCentrality {
    // ... весь код из раздела 2.2 ...
}

/**
 * Вычисление Closeness Centrality
 */
class ClosenessCentrality {
    // ... весь код из раздела 2.3 ...
}

/**
 * Вычисление PageRank
 */
class PageRank {
    // ... весь код из раздела 2.4 ...
}

/**
 * Вычисление Eigenvector Centrality
 */
class EigenvectorCentrality {
    // ... весь код из раздела 2.5 ...
}
```

#### Часть 3: Обнаружение сообществ

Добавьте из Раздела 3:

```javascript
/**
 * Алгоритм Лувена
 */
class LouvainCommunityDetection {
    // ... весь код из раздела 3.1 ...
}

/**
 * Алгоритм распространения меток
 */
class LabelPropagation {
    // ... весь код из раздела 3.2 ...
}
```

#### Часть 4: Временной анализ

Добавьте из Раздела 4:

```javascript
/**
 * Анализ эволюции философского графа
 */
class TemporalAnalysis {
    // ... весь код из раздела 4 ...
}
```

#### Часть 5: PCA анализ

Добавьте из Раздела 5:

```javascript
/**
 * Анализ главных компонент
 */
class PCAAnalysis {
    // ... весь код из раздела 5 ...
}
```

#### Часть 6: Анализ путей

Добавьте из Раздела 6:

```javascript
/**
 * Анализ путей в графе
 */
class PathAnalysis {
    // ... весь код из раздела 6 ...
}
```

#### Часть 7: Кластерный анализ

Добавьте из Раздела 7:

```javascript
/**
 * Коэффициент кластеризации
 */
class ClusteringAnalysis {
    // ... весь код из раздела 7 ...
}
```

**Итого:** Файл `js/analyzer.js` должен содержать 11 классов в следующем порядке:
1. PhilosophyGraphAnalyzer
2. DegreeCentrality
3. BetweennessCentrality
4. ClosenessCentrality
5. PageRank
6. EigenvectorCentrality
7. LouvainCommunityDetection
8. LabelPropagation
9. TemporalAnalysis
10. PCAAnalysis
11. PathAnalysis
12. ClusteringAnalysis

---

## Шаг 4: Создание UI и запуск

### 4.1. Создайте файл `js/ui.js`

Скопируйте следующий полный код:

```javascript
// Глобальный анализатор
let analyzer = null;

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Инициализация анализатора...');
    
    try {
        analyzer = new PhilosophyGraphAnalyzer(
            philosophers, 
            concepts, 
            relations, 
            rubrics
        );
        console.log('✅ Анализатор успешно создан');
        console.log(`📊 Узлов: ${analyzer.graph.size}, Рёбер: ${relations.length}`);
    } catch (error) {
        console.error('❌ Ошибка при создании анализатора:', error);
        showError('Не удалось загрузить данные. Проверьте файл philo_data_refactored.js');
        return;
    }
    
    // Привязка событий к кнопкам
    document.getElementById('runBasicStats').addEventListener('click', runBasicStats);
    document.getElementById('runCentrality').addEventListener('click', runCentrality);
    document.getElementById('runCommunities').addEventListener('click', runCommunities);
    document.getElementById('runPaths').addEventListener('click', runPaths);
    document.getElementById('runClustering').addEventListener('click', runClustering);
    document.getElementById('runTemporal').addEventListener('click', runTemporal);
    document.getElementById('runAll').addEventListener('click', runAll);
    document.getElementById('clearResults').addEventListener('click', clearResults);
});

// Вспомогательные функции
function showLoading() {
    document.getElementById('loading').style.display = 'block';
    document.getElementById('results').style.opacity = '0.5';
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('results').style.opacity = '1';
}

function clearResults() {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = `
        <div class="placeholder">
            <h2>👆 Выберите метод анализа</h2>
            <p>Нажмите на одну из кнопок выше, чтобы начать анализ</p>
        </div>
    `;
}

function showError(message) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = `
        <div class="error-box">
            <h3>❌ Ошибка</h3>
            <p>${message}</p>
        </div>
    `;
}

function appendSection(title, content) {
    const resultsDiv = document.getElementById('results');
    
    // Удаляем placeholder при первом добавлении
    const placeholder = resultsDiv.querySelector('.placeholder');
    if (placeholder) {
        resultsDiv.innerHTML = '';
    }
    
    const section = document.createElement('div');
    section.className = 'result-section';
    section.innerHTML = `
        <h2>${title}</h2>
        ${content}
    `;
    resultsDiv.appendChild(section);
}

function createTable(data, maxRows = 20) {
    if (!data || data.length === 0) {
        return '<p>Нет данных для отображения</p>';
    }
    
    const displayData = data.slice(0, maxRows);
    const keys = Object.keys(displayData[0]);
    
    let html = '<div class="table-container"><table>';
    
    // Заголовок
    html += '<thead><tr>';
    keys.forEach(key => {
        html += `<th>${key}</th>`;
    });
    html += '</tr></thead>';
    
    // Данные
    html += '<tbody>';
    displayData.forEach(row => {
        html += '<tr>';
        keys.forEach(key => {
            const value = row[key];
            html += `<td>${value !== null && value !== undefined ? value : '-'}</td>`;
        });
        html += '</tr>';
    });
    html += '</tbody></table></div>';
    
    if (data.length > maxRows) {
        html += `<p class="table-note">Показано ${maxRows} из ${data.length} записей</p>`;
    }
    
    return html;
}

// 1. Базовая статистика
function runBasicStats() {
    showLoading();
    
    setTimeout(() => {
        try {
            clearResults();
            
            const stats = analyzer.getBasicStats();
            const relationStats = analyzer.getRelationTypeStats();
            const rubricStats = analyzer.getRubricStats();
            const philoStats = analyzer.getPhilosopherStats();
            
            appendSection('📊 Общая статистика графа', `
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">${stats.numNodes}</div>
                        <div class="stat-label">Концепций</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${stats.numEdges}</div>
                        <div class="stat-label">Связей</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${stats.avgDegree}</div>
                        <div class="stat-label">Средняя степень</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${stats.density}</div>
                        <div class="stat-label">Плотность</div>
                    </div>
                </div>
            `);
            
            appendSection('🔗 Распределение по типам связей', createTable(relationStats));
            appendSection('📚 Распределение по рубрикам', createTable(rubricStats));
            appendSection('👤 Топ-15 философов по количеству концепций', createTable(philoStats.slice(0, 15)));
            
            console.log('✅ Базовая статистика выполнена');
        } catch (error) {
            console.error('❌ Ошибка при выполнении базовой статистики:', error);
            showError('Ошибка при расчёте базовой статистики: ' + error.message);
        } finally {
            hideLoading();
        }
    }, 100);
}

// 2. Центральность
function runCentrality() {
    showLoading();
    
    setTimeout(() => {
        try {
            clearResults();
            
            console.log('🎯 Вычисление Degree Centrality...');
            const degree = new DegreeCentrality(analyzer.graph);
            const degreeResults = degree.compute();
            appendSection('🎯 Degree Centrality (Топ-20)', createTable(degreeResults.slice(0, 20)));
            
            console.log('🎯 Вычисление PageRank...');
            const pagerank = new PageRank(analyzer.graph);
            const pagerankResults = pagerank.compute();
            appendSection('📈 PageRank (Топ-20)', createTable(pagerankResults.slice(0, 20)));
            
            console.log('🎯 Вычисление Closeness Centrality...');
            const closeness = new ClosenessCentrality(analyzer.graph);
            const closenessResults = closeness.compute();
            appendSection('🔍 Closeness Centrality (Топ-20)', createTable(closenessResults.slice(0, 20)));
            
            console.log('🎯 Вычисление Betweenness Centrality...');
            const betweenness = new BetweennessCentrality(analyzer.graph);
            const betweennessResults = betweenness.compute();
            appendSection('🌉 Betweenness Centrality (Топ-20)', createTable(betweennessResults.slice(0, 20)));
            
            console.log('🎯 Вычисление Eigenvector Centrality...');
            const eigenvector = new EigenvectorCentrality(analyzer.graph);
            const eigenvectorResults = eigenvector.compute();
            appendSection('⚡ Eigenvector Centrality (Топ-20)', createTable(eigenvectorResults.slice(0, 20)));
            
            console.log('✅ Все метрики центральности вычислены');
        } catch (error) {
            console.error('❌ Ошибка при вычислении центральности:', error);
            showError('Ошибка при расчёте центральности: ' + error.message);
        } finally {
            hideLoading();
        }
    }, 100);
}

// 3. Сообщества
function runCommunities() {
    showLoading();
    
    setTimeout(() => {
        try {
            clearResults();
            
            console.log('👥 Обнаружение сообществ (Louvain)...');
            const louvain = new LouvainCommunityDetection(analyzer.graph);
            const louvainResults = louvain.detect();
            
            appendSection(`👥 Сообщества Louvain (${louvainResults.numCommunities} сообществ, модулярность: ${louvainResults.modularity})`, 
                createTable(louvainResults.communities, 50)
            );
            
            console.log('👥 Обнаружение сообществ (Label Propagation)...');
            const labelProp = new LabelPropagation(analyzer.graph);
            const labelResults = labelProp.detect();
            
            appendSection(`🏷️ Label Propagation (${labelResults.numCommunities} сообществ)`, 
                createTable(labelResults.communities, 50)
            );
            
            console.log('✅ Обнаружение сообществ завершено');
        } catch (error) {
            console.error('❌ Ошибка при обнаружении сообществ:', error);
            showError('Ошибка при обнаружении сообществ: ' + error.message);
        } finally {
            hideLoading();
        }
    }, 100);
}

// 4. Пути и расстояния
function runPaths() {
    showLoading();
    
    setTimeout(() => {
        try {
            clearResults();
            
            console.log('🔗 Анализ путей...');
            const paths = new PathAnalysis(analyzer.graph);
            
            console.log('🔗 Вычисление диаметра...');
            const diameter = paths.analyzeDiameter();
            
            appendSection('📏 Диаметр и расстояния в графе', `
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">${diameter.diameter}</div>
                        <div class="stat-label">Диаметр графа</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${diameter.averagePathLength}</div>
                        <div class="stat-label">Средняя длина пути</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${diameter.reachablePairs}</div>
                        <div class="stat-label">Достижимых пар</div>
                    </div>
                </div>
                <p><strong>Самый длинный путь:</strong> от "${diameter.longestPath.from}" до "${diameter.longestPath.to}" (расстояние: ${diameter.longestPath.distance})</p>
            `);
            
            console.log('🔗 Вычисление эксцентриситета...');
            const eccentricity = paths.computeEccentricity();
            appendSection('🎯 Эксцентриситет узлов (Топ-20)', createTable(eccentricity.slice(0, 20)));
            
            console.log('🔗 Поиск длинных цепочек влияния...');
            const chains = paths.findLongestInfluenceChains();
            appendSection('⛓️ Самые длинные цепочки влияния (Топ-20)', createTable(chains));
            
            console.log('✅ Анализ путей завершён');
        } catch (error) {
            console.error('❌ Ошибка при анализе путей:', error);
            showError('Ошибка при анализе путей: ' + error.message);
        } finally {
            hideLoading();
        }
    }, 100);
}

// 5. Кластеризация
function runClustering() {
    showLoading();
    
    setTimeout(() => {
        try {
            clearResults();
            
            console.log('🔷 Анализ кластеризации...');
            const clustering = new ClusteringAnalysis(analyzer.graph);
            
            const globalCC = clustering.globalClusteringCoefficient();
            const transitivity = clustering.transitivity();
            const localCC = clustering.analyzeAll();
            
            appendSection('🔷 Глобальные метрики кластеризации', `
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">${globalCC.toFixed(4)}</div>
                        <div class="stat-label">Глобальный коэффициент</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${transitivity.toFixed(4)}</div>
                        <div class="stat-label">Транзитивность</div>
                    </div>
                </div>
            `);
            
            appendSection('🔷 Локальные коэффициенты кластеризации (Топ-20)', createTable(localCC.slice(0, 20)));
            
            console.log('✅ Анализ кластеризации завершён');
        } catch (error) {
            console.error('❌ Ошибка при анализе кластеризации:', error);
            showError('Ошибка при анализе кластеризации: ' + error.message);
        } finally {
            hideLoading();
        }
    }, 100);
}

// 6. Временной анализ
function runTemporal() {
    showLoading();
    
    setTimeout(() => {
        try {
            clearResults();
            
            console.log('⏱️ Временной анализ...');
            const temporal = new TemporalAnalysis(philosophers, concepts, relations);
            
            const productivity = temporal.analyzeProductivityByEpoch();
            appendSection('📈 Продуктивность по эпохам', createTable(productivity));
            
            const evolution = temporal.analyzeRelationTypeEvolution();
            appendSection('🔄 Эволюция типов связей', createTable(evolution));
            
            const influence = temporal.buildTemporalInfluenceNetwork();
            const influenceTable = Object.keys(influence).map(from => ({
                'От эпохи': from,
                ...influence[from]
            }));
            appendSection('🌐 Матрица межэпохальных влияний', createTable(influenceTable));
            
            const growth = temporal.analyzeCumulativeGrowth();
            appendSection('📊 Кумулятивный рост графа (первые 15 философов)', createTable(growth.slice(0, 15)));
            
            console.log('✅ Временной анализ завершён');
        } catch (error) {
            console.error('❌ Ошибка при временном анализе:', error);
            showError('Ошибка при временном анализе: ' + error.message);
        } finally {
            hideLoading();
        }
    }, 100);
}

// 7. Запустить всё
function runAll() {
    if (!confirm('Выполнить все виды анализа? Это может занять несколько секунд.')) {
        return;
    }
    
    clearResults();
    
    // Последовательно запускаем все анализы
    runBasicStats();
    setTimeout(() => runCentrality(), 1000);
    setTimeout(() => runCommunities(), 2000);
    setTimeout(() => runPaths(), 3000);
    setTimeout(() => runClustering(), 4000);
    setTimeout(() => runTemporal(), 5000);
}
```

---

## Шаг 5: Добавление стилей

### 5.1. Создайте папку `css` и файл `css/styles.css`

Скопируйте следующий код полностью:

```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 20px;
    color: #333;
}

.container {
    max-width: 1400px;
    margin: 0 auto;
    background: white;
    border-radius: 16px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    overflow: hidden;
}

header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 40px;
    text-align: center;
}

header h1 {
    font-size: 2.5rem;
    margin-bottom: 10px;
    font-weight: 700;
}

.subtitle {
    font-size: 1.1rem;
    opacity: 0.9;
}

.controls {
    padding: 20px;
    background: #f8f9fa;
    border-bottom: 2px solid #e9ecef;
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    justify-content: center;
}

.btn {
    padding: 12px 24px;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.btn-primary {
    background: #667eea;
    color: white;
}

.btn-primary:hover {
    background: #5568d3;
}

.btn-success {
    background: #10b981;
    color: white;
    font-size: 16px;
    padding: 14px 32px;
}

.btn-success:hover {
    background: #059669;
}

.btn-secondary {
    background: #6c757d;
    color: white;
}

.btn-secondary:hover {
    background: #5a6268;
}

.loading {
    text-align: center;
    padding: 40px;
    background: #f8f9fa;
}

.spinner {
    width: 50px;
    height: 50px;
    margin: 0 auto 20px;
    border: 5px solid #e9ecef;
    border-top: 5px solid #667eea;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.results {
    padding: 30px;
    min-height: 400px;
    transition: opacity 0.3s;
}

.placeholder {
    text-align: center;
    padding: 80px 20px;
    color: #6c757d;
}

.placeholder h2 {
    font-size: 1.8rem;
    margin-bottom: 10px;
}

.result-section {
    margin-bottom: 40px;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 12px;
    border-left: 4px solid #667eea;
}

.result-section h2 {
    color: #667eea;
    margin-bottom: 20px;
    font-size: 1.5rem;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin: 20px 0;
}

.stat-card {
    background: white;
    padding: 25px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s;
}

.stat-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.stat-value {
    font-size: 2.5rem;
    font-weight: 700;
    color: #667eea;
    margin-bottom: 5px;
}

.stat-label {
    font-size: 0.9rem;
    color: #6c757d;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.table-container {
    overflow-x: auto;
    margin: 20px 0;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

table {
    width: 100%;
    border-collapse: collapse;
    background: white;
}

thead {
    background: #667eea;
    color: white;
}

th, td {
    padding: 12px 16px;
    text-align: left;
    border-bottom: 1px solid #e9ecef;
}

th {
    font-weight: 600;
    text-transform: uppercase;
    font-size: 0.85rem;
    letter-spacing: 0.5px;
}

tbody tr:hover {
    background: #f8f9fa;
}

tbody tr:nth-child(even) {
    background: #fafbfc;
}

.table-note {
    margin-top: 10px;
    color: #6c757d;
    font-style: italic;
    font-size: 0.9rem;
}

.error-box {
    background: #fee;
    border: 2px solid #fcc;
    border-radius: 8px;
    padding: 20px;
    color: #c33;
}

.error-box h3 {
    margin-bottom: 10px;
}

footer {
    background: #2c3e50;
    color: white;
    padding: 20px;
    text-align: center;
    font-size: 0.9rem;
}

@media (max-width: 768px) {
    header h1 {
        font-size: 1.8rem;
    }
    
    .controls {
        flex-direction: column;
    }
    
    .btn {
        width: 100%;
    }
    
    .stats-grid {
        grid-template-columns: 1fr;
    }
    
    table {
        font-size: 0.85rem;
    }
    
    th, td {
        padding: 8px;
    }
}
```

---

## Проверка работоспособности

### Шаг 1: Проверка структуры

Убедитесь, что структура папок выглядит так:

```
philosophy-graph-analysis/
│
├── index.html
├── data/
│   └── philo_data_refactored.js   (≈35 КБ)
├── js/
│   ├── analyzer.js                 (≈30 КБ)
│   └── ui.js                       (≈10 КБ)
└── css/
    └── styles.css                  (≈5 КБ)
```

### Шаг 2: Открытие страницы

1. Откройте файл `index.html` в браузере (Chrome, Firefox, Safari, Edge)
2. Откройте консоль разработчика (F12 или Cmd+Option+I)

### Шаг 3: Проверка загрузки

В консоли должны появиться сообщения:
```
🚀 Инициализация анализатора...
✅ Анализатор успешно создан
📊 Узлов: 198, Рёбер: 389
```

Если появились ошибки:

**Ошибка: "philosophers is not defined"**
- Проблема: файл `philo_data_refactored.js` не загружен или неправильный путь
- Решение: проверьте, что файл существует в папке `data/` и содержит данные

**Ошибка: "PhilosophyGraphAnalyzer is not defined"**
- Проблема: файл `analyzer.js` не загружен
- Решение: проверьте путь к файлу

**Ошибка: "Cannot read property 'addEventListener' of null"**
- Проблема: элементы HTML не найдены
- Решение: убедитесь, что `index.html` содержит все элементы с правильными id

### Шаг 4: Тестирование функций

1. Нажмите кнопку **"📊 Базовая статистика"**
   - Должны появиться карточки со статистикой и таблицы
   
2. Нажмите кнопку **"🎯 Центральность"**
   - Должны появиться 5 таблиц с метриками центральности
   - В консоли будут логи: "Вычисление Degree Centrality...", "PageRank converged after X iterations" и т.д.

3. Нажмите кнопку **"👥 Сообщества"**
   - Должны появиться результаты Louvain и Label Propagation

4. Нажмите **"▶️ Запустить всё"**
   - Подтвердите в диалоговом окне
   - Все анализы запустятся последовательно

### Шаг 5: Проверка производительности

Типичное время выполнения (на современном компьютере):
- Базовая статистика: < 100 мс
- Центральность (все метрики): 2-5 секунд
- Сообщества: 1-3 секунды
- Пути и расстояния: 3-7 секунд (Floyd-Warshall - O(n³))
- Кластеризация: < 1 секунда
- Временной анализ: < 500 мс

**Если анализ зависает:**
- Откройте консоль и проверьте, где остановился процесс
- Betweenness и Floyd-Warshall - самые медленные алгоритмы (это нормально)

---

## Частые проблемы и решения

### Проблема 1: Белый экран

**Причина:** JavaScript файлы не загрузились

**Решение:**
1. Откройте консоль (F12)
2. Перейдите на вкладку Network
3. Обновите страницу (Ctrl+R)
4. Проверьте, что все файлы загрузились без ошибок 404

### Проблема 2: "Uncaught ReferenceError: philosophers is not defined"

**Причина:** Файл с данными не загружен первым

**Решение:**
Убедитесь, что в `index.html` скрипты подключены в правильном порядке:
```html
<script src="data/philo_data_refactored.js"></script>  <!-- ПЕРВЫЙ -->
<script src="js/analyzer.js"></script>                 <!-- ВТОРОЙ -->
<script src="js/ui.js"></script>                       <!-- ТРЕТИЙ -->
```

### Проблема 3: Кнопки не работают

**Причина:** События не привязаны

**Решение:**
1. Проверьте консоль на ошибки
2. Убедитесь, что все id элементов совпадают с кодом в `ui.js`
3. Проверьте, что `DOMContentLoaded` срабатывает

### Проблема 4: Медленная работа

**Причина:** Большой граф и сложные алгоритмы

**Решение:**
- Это нормально для алгоритмов O(n³)
- Можно закомментировать самые медленные части (Betweenness, Floyd-Warshall)
- Или уменьшить размер данных для тестирования

---

## Дополнительные возможности

### Экспорт результатов в CSV

Добавьте в `ui.js` после функции `createTable`:

```javascript
function exportToCSV(data, filename) {
    if (!data || data.length === 0) return;
    
    const keys = Object.keys(data[0]);
    let csv = keys.join(',') + '\n';
    
    data.forEach(row => {
        const values = keys.map(key => {
            const value = row[key];
            return typeof value === 'string' ? `"${value}"` : value;
        });
        csv += values.join(',') + '\n';
    });
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
}
```

И добавьте кнопку экспорта после каждой таблицы.

### Сохранение результатов в localStorage

Добавьте в конец `ui.js`:

```javascript
function saveResults() {
    const results = document.getElementById('results').innerHTML;
    localStorage.setItem('philoResults', results);
    alert('Результаты сохранены!');
}

function loadResults() {
    const results = localStorage.getItem('philoResults');
    if (results) {
        document.getElementById('results').innerHTML = results;
        alert('Результаты загружены!');
    } else {
        alert('Нет сохранённых результатов');
    }
}
```

---

## Финальная проверка

✅ **Контрольный список:**

- [ ] Файл `index.html` создан и содержит полную структуру
- [ ] Файл `data/philo_data_refactored.js` содержит все данные
- [ ] Файл `js/analyzer.js` содержит все 12 классов
- [ ] Файл `js/ui.js` содержит все функции UI
- [ ] Файл `css/styles.css` содержит все стили
- [ ] Страница открывается без ошибок
- [ ] В консоли появляется сообщение "✅ Анализатор успешно создан"
- [ ] Все кнопки работают и показывают результаты
- [ ] Таблицы отображаются корректно
- [ ] Нет ошибок в консоли

**Если все пункты выполнены - поздравляем, страница работает! 🎉**

---

## Контакты и поддержка

Если возникли проблемы:
1. Проверьте консоль браузера (F12)
2. Убедитесь, что все файлы на месте
3. Проверьте, что данные загружены корректно
4. Попробуйте открыть страницу в другом браузере

Для отладки используйте `console.log()` в ключевых местах кода.