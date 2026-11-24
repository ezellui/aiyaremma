// Часть 7: Продвинутый анализ и финальная интеграция

// === Продвинутый анализ графа ===

class GraphAnalyzer {
    constructor() {
        this.metrics = {};
    }

    analyzeGraph(conceptId) {
        const conceptCategories = categories.filter(c => c.conceptId === conceptId);
        const conceptRelations = relations.filter(r => {
            const fromCategory = categories.find(c => c.id === r.from);
            return fromCategory && fromCategory.conceptId === conceptId;
        });

        this.metrics = {
            density: this.calculateDensity(conceptCategories, conceptRelations),
            centralization: this.calculateCentralization(conceptCategories, conceptRelations),
            modularity: this.findCommunities(conceptCategories, conceptRelations),
            bridgingCategories: this.findBridgingCategories(conceptCategories, conceptRelations),
            corePeriphery: this.analyzeCorePeriphery(conceptCategories, conceptRelations)
        };

        return this.metrics;
    }

    calculateDensity(nodes, edges) {
        const n = nodes.length;
        const maxEdges = n * (n - 1); // Для направленного графа
        return edges.length / maxEdges;
    }

    calculateCentralization(nodes, edges) {
        const degreeCentrality = this.calculateDegreeCentrality(nodes, edges);
        const maxCentrality = Math.max(...Object.values(degreeCentrality));
        const sumDifferences = Object.values(degreeCentrality).reduce((sum, centrality) => 
            sum + (maxCentrality - centrality), 0);
        const maxPossibleSum = (nodes.length - 1) * (nodes.length - 2);
        
        return sumDifferences / maxPossibleSum;
    }

    calculateDegreeCentrality(nodes, edges) {
        const centrality = {};
        
        nodes.forEach(node => {
            const outDegree = edges.filter(e => e.from === node.id).length;
            const inDegree = edges.filter(e => e.to === node.id).length;
            centrality[node.id] = (outDegree + inDegree) / (2 * (nodes.length - 1));
        });
        
        return centrality;
    }

    findCommunities(nodes, edges) {
        // Упрощенный алгоритм поиска сообществ
        const communities = [];
        const visited = new Set();
        
        const dfs = (nodeId, community) => {
            if (visited.has(nodeId)) return;
            visited.add(nodeId);
            community.push(nodeId);
            
            edges.forEach(edge => {
                if (edge.from === nodeId) dfs(edge.to, community);
                if (edge.to === nodeId && edge.bidirectional) dfs(edge.from, community);
            });
        };
        
        nodes.forEach(node => {
            if (!visited.has(node.id)) {
                const community = [];
                dfs(node.id, community);
                communities.push(community);
            }
        });
        
        return communities;
    }

    findBridgingCategories(nodes, edges) {
        // Категории, которые связывают разные сообщества
        const bridging = [];
        const centrality = this.calculateDegreeCentrality(nodes, edges);
        
        nodes.forEach(node => {
            const connectedCommunities = new Set();
            edges.forEach(edge => {
                if (edge.from === node.id || edge.to === node.id) {
                    const otherNode = edge.from === node.id ? edge.to : edge.from;
                    // Здесь должна быть логика определения сообщества для otherNode
                    connectedCommunities.add(otherNode);
                }
            });
            
            if (connectedCommunities.size > 1 && centrality[node.id] > 0.5) {
                bridging.push(node.id);
            }
        });
        
        return bridging;
    }

    analyzeCorePeriphery(nodes, edges) {
        const centrality = this.calculateDegreeCentrality(nodes, edges);
        const sorted = Object.entries(centrality).sort((a, b) => b[1] - a[1]);
        const threshold = sorted[Math.floor(sorted.length / 3)][1];
        
        return {
            core: sorted.filter(([_, value]) => value >= threshold).map(([id]) => id),
            periphery: sorted.filter(([_, value]) => value < threshold).map(([id]) => id)
        };
    }
}

// === Визуализация метрик ===

class MetricsVisualizer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
    }

    visualizeMetrics(metrics) {
        if (!this.container) return;
        
        const html = `
            <div class="metrics-dashboard">
                <div class="metric-card">
                    <h4>Плотность графа</h4>
                    <div class="metric-value">${(metrics.density * 100).toFixed(1)}%</div>
                    <div class="metric-description">
                        Показывает насколько связана концепция
                    </div>
                </div>
                
                <div class="metric-card">
                    <h4>Централизация</h4>
                    <div class="metric-value">${(metrics.centralization * 100).toFixed(1)}%</div>
                    <div class="metric-description">
                        Степень иерархичности структуры
                    </div>
                </div>
                
                <div class="metric-card">
                    <h4>Количество сообществ</h4>
                    <div class="metric-value">${metrics.modularity.length}</div>
                    <div class="metric-description">
                        Число отдельных подструктур
                    </div>
                </div>
                
                <div class="metric-card">
                    <h4>Категории-мосты</h4>
                    <div class="metric-value">${metrics.bridgingCategories.length}</div>
                    <div class="metric-description">
                        Соединяют разные части концепции
                    </div>
                </div>
            </div>
            
            <div class="core-periphery-viz">
                <h4>Структура ядро-периферия</h4>
                <div class="core-nodes">
                    <h5>Ядро (${metrics.corePeriphery.core.length} категорий)</h5>
                    ${metrics.corePeriphery.core.map(id => {
                        const category = categories.find(c => c.id === id);
                        return `<span class="core-item">${category?.name}</span>`;
                    }).join('')}
                </div>
                <div class="periphery-nodes">
                    <h5>Периферия (${metrics.corePeriphery.periphery.length} категорий)</h5>
                    ${metrics.corePeriphery.periphery.map(id => {
                        const category = categories.find(c => c.id === id);
                        return `<span class="periphery-item">${category?.name}</span>`;
                    }).join('')}
                </div>
            </div>
        `;
        
        this.container.innerHTML = html;
    }
}

// === Автоматическая генерация рекомендаций ===

class ConceptAdvisor {
    constructor() {
        this.analyzer = new GraphAnalyzer();
    }

    generateRecommendations(conceptId) {
        const metrics = this.analyzer.analyzeGraph(conceptId);
        const recommendations = [];
        
        // Анализ плотности
        if (metrics.density < 0.1) {
            recommendations.push({
                type: 'structure',
                priority: 'high',
                message: 'Концепция слабо связана. Рекомендуется добавить больше связей между категориями.',
                action: () => showModal('Рекомендация', 'Добавьте связи между существующими категориями для улучшения структуры концепции.')
            });
        }
        
        // Анализ централизации
        if (metrics.centralization > 0.8) {
            recommendations.push({
                type: 'structure',
                priority: 'medium',
                message: 'Концепция слишком централизована. Рассмотрите возможность создания дополнительных связей между периферийными категориями.',
                action: () => showModal('Рекомендация', 'Создайте связи между периферийными категориями для более сбалансированной структуры.')
            });
        }
        
        // Анализ сообществ
        if (metrics.modularity.length > 1) {
            recommendations.push({
                type: 'cohesion',
                priority: 'high',
                message: `Обнаружено ${metrics.modularity.length} отдельных сообществ. Рекомендуется связать их через категории-мосты.`,
                action: () => this.suggestBridges(metrics.modularity)
            });
        }
        
        // Анализ категорий-мостов
        if (metrics.bridgingCategories.length === 0 && metrics.modularity.length > 1) {
            recommendations.push({
                type: 'connectivity',
                priority: 'high',
                message: 'Отсутствуют категории-мосты. Создайте категории, которые связывают разные части концепции.',
                action: () => this.suggestNewBridges()
            });
        }
        
        return recommendations;
    }

    suggestBridges(communities) {
        // Предложить создание связей между сообществами
        showModal('Предложение по улучшению', 
            'Рекомендуется создать связи между отдельными группами категорий для улучшения целостности концепции.');
    }

    suggestNewBridges() {
        // Предложить создание новых категорий-мостов
        showModal('Создание категорий-мостов', 
            'Рекомендуется создать новые категории, которые связывают разные части вашей концепции.');
    }
}

// === Интеллектуальный помощник ===

class SmartAssistant {
    constructor() {
        this.advisor = new ConceptAdvisor();
        this.analyzer = new GraphAnalyzer();
    }

    async analyzeAndSuggest() {
        if (!currentConcept) {
            alert('Выберите концепцию для анализа');
            return;
        }
        
        showProgress('Анализ концепции...', 0);
        
        try {
            // Анализ структуры
            showProgress('Анализ структуры...', 25);
            const recommendations = this.advisor.generateRecommendations(currentConcept.id);
            
            // Запрос рекомендаций от Claude
            showProgress('Получение рекомендаций от Claude...', 50);
            const claudeRecommendations = await this.getClaudeRecommendations();
            
            // Объединение рекомендаций
            showProgress('Формирование отчета...', 75);
            const report = this.generateReport(recommendations, claudeRecommendations);
            
            showProgress('Готово!', 100);
            setTimeout(() => {
                hideProgress();
                showModal('Анализ и рекомендации', report);
            }, 500);
            
        } catch (error) {
            hideProgress();
            showError('Ошибка при анализе: ' + error.message);
        }
    }

    async getClaudeRecommendations() {
        const graphData = getConceptGraphData(currentConcept.id);
        const metrics = this.analyzer.analyzeGraph(currentConcept.id);
        
        const prompt = `Проанализируй философскую концепцию "${currentConcept.name}" со следующей структурой:
${JSON.stringify(graphData, null, 2)}

Метрики графа:
- Плотность: ${(metrics.density * 100).toFixed(1)}%
- Централизация: ${(metrics.centralization * 100).toFixed(1)}%
- Количество сообществ: ${metrics.modularity.length}
- Категории-мосты: ${metrics.bridgingCategories.length}

Предложи:
1. Какие важные категории могут отсутствовать
2. Какие дополнительные связи улучшат концепцию
3. Как можно развить и углубить существующие категории
4. Философские традиции или концепции для сравнения`;

        return await callClaudeAPI(prompt);
    }

    generateReport(recommendations, claudeRecommendations) {
        let html = `
            <div class="analysis-report">
                <h2>Структурный анализ</h2>
                <div class="recommendations-list">
        `;
        
        recommendations.forEach(rec => {
            html += `
                <div class="recommendation ${rec.priority}-priority">
                    <h4>${this.getPriorityIcon(rec.priority)} ${rec.message}</h4>
                    <button onclick="(${rec.action.toString()})()">Применить рекомендацию</button>
                </div>
            `;
        });
        
        html += `
                </div>
                
                <h2>Рекомендации Claude</h2>
                <div class="claude-recommendations">
                    ${claudeRecommendations}
                </div>
                
                <h2>Действия</h2>
                <div class="action-buttons">
                    <button onclick="exportAnalysisReport()">Экспорт отчета</button>
                    <button onclick="implementRecommendations()" class="primary">Применить рекомендации</button>
                </div>
            </div>
        `;
        
        return html;
    }

    getPriorityIcon(priority) {
        const icons = {
            high: '🔴',
            medium: '🟡',
            low: '🟢'
        };
        return icons[priority] || '⚪';
    }
}

// === Финальная интеграция и инициализация ===

// Глобальные экземпляры
let graphAnalyzer = new GraphAnalyzer();
let metricsVisualizer = null;
let smartAssistant = new SmartAssistant();

// Дополнительные функции для интерфейса
function showGraphMetrics() {
    if (!currentConcept) {
        alert('Выберите концепцию для анализа');
        return;
    }
    
    const metrics = graphAnalyzer.analyzeGraph(currentConcept.id);
    
    const metricsModal = `
        <div id="metricsViz" style="min-height: 400px;"></div>
    `;
    
    showModal('Метрики графа', metricsModal);
    
    metricsVisualizer = new MetricsVisualizer('metricsViz');
    metricsVisualizer.visualizeMetrics(metrics);
}

function startSmartAnalysis() {
    smartAssistant.analyzeAndSuggest();
}

// Экспорт отчета анализа
function exportAnalysisReport() {
    if (!currentConcept) return;
    
    const metrics = graphAnalyzer.analyzeGraph(currentConcept.id);
    const recommendations = smartAssistant.advisor.generateRecommendations(currentConcept.id);
    
    const report = {
        concept: currentConcept.name,
        date: new Date().toISOString(),
        metrics,
        recommendations: recommendations.map(r => ({
            type: r.type,
            priority: r.priority,
            message: r.message
        }))
    };
    
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `analysis_report_${currentConcept.name.replace(/\s+/g, '_')}.json`;
    a.click();
    URL.revokeObjectURL(url);
}

// Применение рекомендаций
function implementRecommendations() {
    // Здесь может быть логика для автоматического применения рекомендаций
    showModal('Применение рекомендаций', 
        'Функция в разработке. Пока вы можете применять рекомендации вручную.');
}

// Обновление основного UI
const originalUpdateUI = updateUI;
updateUI = function() {
    originalUpdateUI();
    
    // Обновляем селектор текущей концепции
    const conceptSelect = document.getElementById('currentConceptSelect');
    if (conceptSelect) {
        conceptSelect.innerHTML = '<option value="">Выберите концепцию</option>';
        concepts.forEach(concept => {
            const option = document.createElement('option');
            option.value = concept.id;
            option.textContent = concept.name;
            if (currentConcept && concept.id === currentConcept.id) {
                option.selected = true;
            }
            conceptSelect.appendChild(option);
        });
    }
    
    // Обновляем информацию о концепции
    updateConceptInfo();
    
    // Обновляем визуализацию графа
    updateGraphVisualization();
};

// Финальные CSS стили
const finalStyles = `
.metrics-dashboard {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.metric-card {
    background: white;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 15px;
    text-align: center;
}

.metric-value {
    font-size: 24px;
    font-weight: bold;
    color: var(--secondary-color);
    margin: 10px 0;
}

.metric-description {
    font-size: 14px;
    color: #666;
}

.core-periphery-viz {
    margin-top: 30px;
}

.core-nodes, .periphery-nodes {
    margin: 15px 0;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;
}

.core-item, .periphery-item {
    display: inline-block;
    margin: 5px;
    padding: 5px 10px;
    border-radius: 20px;
    font-size: 14px;
}

.core-item {
    background: var(--secondary-color);
    color: white;
}

.periphery-item {
    background: #e9ecef;
    color: #495057;
}

.analysis-report {
    max-height: 70vh;
    overflow-y: auto;
}

.recommendations-list {
    margin: 20px 0;
}

.recommendation {
    margin: 10px 0;
    padding: 15px;
    border-radius: 8px;
    border-left: 4px solid;
}

.high-priority {
    border-left-color: #e74c3c;
    background: #fdf2f2;
}

.medium-priority {
    border-left-color: #f39c12;
    background: #fef9e7;
}

.low-priority {
    border-left-color: #27ae60;
    background: #eafaf1;
}

.claude-recommendations {
    background: #f8f9fa;
    padding: 20px;
    border-radius: 8px;
    margin: 20px 0;
    white-space: pre-wrap;
}

.action-buttons {
    display: flex;
    gap: 15px;
    justify-content: flex-end;
    margin-top: 20px;
}
`;

// Добавляем финальные стили
document.addEventListener('DOMContentLoaded', function() {
    const styleSheet = document.createElement('style');
    styleSheet.textContent = finalStyles;
    document.head.appendChild(styleSheet);
});

// Добавляем кнопки анализа в интерфейс
function addAnalysisButtons() {
    const analysisButtons = `
        <div class="analysis-buttons">
            <button onclick="showGraphMetrics()" title="Показать метрики графа">📊 Метрики</button>
            <button onclick="startSmartAnalysis()" title="Запустить умный анализ">🤖 Анализ</button>
        </div>
    `;
    
    const graphSection = document.querySelector('#graph .section:first-child');
    if (graphSection) {
        graphSection.insertAdjacentHTML('beforeend', analysisButtons);
    }
}

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', function() {
    addAnalysisButtons();
});

// Конец приложения "Сервис философских концепций"