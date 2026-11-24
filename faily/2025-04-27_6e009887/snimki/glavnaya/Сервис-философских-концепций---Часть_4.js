// Часть 5: Продвинутая визуализация графа и история изменений

// === SVG визуализация графа ===

class GraphVisualizer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.width = this.container.clientWidth;
        this.height = 600;
        this.nodeRadius = 40;
        this.nodes = [];
        this.links = [];
        this.svg = null;
        this.simulation = null;
    }

    initialize() {
        // Очищаем контейнер
        this.container.innerHTML = '';
        
        // Создаем SVG элемент
        this.svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        this.svg.setAttribute("width", this.width);
        this.svg.setAttribute("height", this.height);
        this.svg.setAttribute("viewBox", `0 0 ${this.width} ${this.height}`);
        this.container.appendChild(this.svg);
        
        // Добавляем определения для стрелок
        const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
        const marker = this.createArrowMarker();
        defs.appendChild(marker);
        this.svg.appendChild(defs);
        
        // Создаем группы для слоев
        this.linkGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
        this.linkGroup.setAttribute("class", "links");
        this.svg.appendChild(this.linkGroup);
        
        this.nodeGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
        this.nodeGroup.setAttribute("class", "nodes");
        this.svg.appendChild(this.nodeGroup);
    }

    createArrowMarker() {
        const marker = document.createElementNS("http://www.w3.org/2000/svg", "marker");
        marker.setAttribute("id", "arrowhead");
        marker.setAttribute("markerWidth", "10");
        marker.setAttribute("markerHeight", "7");
        marker.setAttribute("refX", "10");
        marker.setAttribute("refY", "3.5");
        marker.setAttribute("orient", "auto");
        
        const polygon = document.createElementNS("http://www.w3.org/2000/svg", "polygon");
        polygon.setAttribute("points", "0 0, 10 3.5, 0 7");
        polygon.setAttribute("fill", "#999");
        
        marker.appendChild(polygon);
        return marker;
    }

    updateData(conceptId) {
        if (!conceptId) return;
        
        const conceptCategories = categories.filter(c => c.conceptId === conceptId);
        const conceptRelations = relations.filter(r => {
            const fromCategory = categories.find(c => c.id === r.from);
            return fromCategory && fromCategory.conceptId === conceptId;
        });
        
        // Преобразуем данные в формат для визуализации
        this.nodes = conceptCategories.map(category => ({
            id: category.id,
            name: category.name,
            definition: category.definition,
            metrics: category.metrics,
            x: Math.random() * this.width,
            y: Math.random() * this.height
        }));
        
        this.links = conceptRelations.map(relation => ({
            source: relation.from,
            target: relation.to,
            type: relation.type,
            bidirectional: relation.bidirectional,
            strength: relation.strength
        }));
    }

    render() {
        this.initialize();
        
        // Отрисовываем связи
        this.links.forEach(link => {
            const sourceNode = this.nodes.find(n => n.id === link.source);
            const targetNode = this.nodes.find(n => n.id === link.target);
            
            if (sourceNode && targetNode) {
                const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
                line.setAttribute("x1", sourceNode.x);
                line.setAttribute("y1", sourceNode.y);
                line.setAttribute("x2", targetNode.x);
                line.setAttribute("y2", targetNode.y);
                line.setAttribute("stroke", "#999");
                line.setAttribute("stroke-width", link.strength ? link.strength / 2 : 2);
                
                if (!link.bidirectional) {
                    line.setAttribute("marker-end", "url(#arrowhead)");
                }
                
                this.linkGroup.appendChild(line);
            }
        });
        
        // Отрисовываем узлы
        this.nodes.forEach(node => {
            const group = document.createElementNS("http://www.w3.org/2000/svg", "g");
            group.setAttribute("transform", `translate(${node.x}, ${node.y})`);
            
            // Круг узла
            const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            circle.setAttribute("r", this.nodeRadius);
            circle.setAttribute("fill", this.getNodeColor(node.metrics.centrality));
            circle.setAttribute("stroke", "#fff");
            circle.setAttribute("stroke-width", "2");
            
            // Текст узла
            const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
            text.setAttribute("text-anchor", "middle");
            text.setAttribute("dy", ".3em");
            text.setAttribute("fill", "#fff");
            text.textContent = node.name.substring(0, 10);
            
            group.appendChild(circle);
            group.appendChild(text);
            
            // Добавляем интерактивность
            this.addNodeInteraction(group, node);
            
            this.nodeGroup.appendChild(group);
        });
        
        // Запускаем симуляцию физики
        this.startForceSimulation();
    }

    getNodeColor(centrality) {
        const hue = 200 + (centrality * 16); // От синего к фиолетовому
        return `hsl(${hue}, 70%, 50%)`;
    }

    addNodeInteraction(element, node) {
        element.style.cursor = 'pointer';
        
        element.addEventListener('click', () => {
            showModal(node.name, `
                <p><strong>Определение:</strong> ${node.definition}</p>
                <p><strong>Центральность:</strong> ${node.metrics.centrality}</p>
                <p><strong>Определённость:</strong> ${node.metrics.definition}</p>
                <p><strong>Историческая значимость:</strong> ${node.metrics.historical}</p>
                <button onclick="enrichCategory('${node.id}')">Обогатить через Claude</button>
            `);
        });
        
        // Добавляем перетаскивание
        let isDragging = false;
        
        element.addEventListener('mousedown', (e) => {
            isDragging = true;
            e.stopPropagation();
        });
        
        document.addEventListener('mousemove', (e) => {
            if (isDragging) {
                const svgRect = this.svg.getBoundingClientRect();
                node.x = e.clientX - svgRect.left;
                node.y = e.clientY - svgRect.top;
                element.setAttribute('transform', `translate(${node.x}, ${node.y})`);
                this.updateLinks();
            }
        });
        
        document.addEventListener('mouseup', () => {
            isDragging = false;
        });
    }

    updateLinks() {
        const lines = this.linkGroup.getElementsByTagName('line');
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            const link = this.links[i];
            const sourceNode = this.nodes.find(n => n.id === link.source);
            const targetNode = this.nodes.find(n => n.id === link.target);
            
            if (sourceNode && targetNode) {
                line.setAttribute("x1", sourceNode.x);
                line.setAttribute("y1", sourceNode.y);
                line.setAttribute("x2", targetNode.x);
                line.setAttribute("y2", targetNode.y);
            }
        }
    }

    startForceSimulation() {
        // Простая физическая симуляция для начального расположения узлов
        const centerX = this.width / 2;
        const centerY = this.height / 2;
        
        this.nodes.forEach((node, i) => {
            const angle = (i / this.nodes.length) * 2 * Math.PI;
            const radius = Math.min(this.width, this.height) / 3;
            node.x = centerX + radius * Math.cos(angle);
            node.y = centerY + radius * Math.sin(angle);
        });
        
        this.render();
    }
}

// === История изменений ===

class HistoryManager {
    constructor() {
        this.history = [];
        this.currentIndex = -1;
        this.maxHistoryLength = 50;
    }

    addState(state) {
        // Удаляем состояния после текущего индекса (если делаем новое действие после отмены)
        if (this.currentIndex < this.history.length - 1) {
            this.history = this.history.slice(0, this.currentIndex + 1);
        }
        
        // Добавляем новое состояние
        this.history.push({
            timestamp: new Date().toISOString(),
            data: JSON.parse(JSON.stringify(state))
        });
        
        // Ограничиваем размер истории
        if (this.history.length > this.maxHistoryLength) {
            this.history.shift();
        }
        
        this.currentIndex = this.history.length - 1;
        this.updateUI();
    }

    undo() {
        if (this.currentIndex > 0) {
            this.currentIndex--;
            return this.history[this.currentIndex].data;
        }
        return null;
    }

    redo() {
        if (this.currentIndex < this.history.length - 1) {
            this.currentIndex++;
            return this.history[this.currentIndex].data;
        }
        return null;
    }

    updateUI() {
        const undoButton = document.getElementById('undoButton');
        const redoButton = document.getElementById('redoButton');
        
        if (undoButton) undoButton.disabled = this.currentIndex <= 0;
        if (redoButton) redoButton.disabled = this.currentIndex >= this.history.length - 1;
    }

    getHistory() {
        return this.history.map((item, index) => ({
            ...item,
            isCurrent: index === this.currentIndex
        }));
    }
}

// === Управление версиями концепций ===

class ConceptVersionManager {
    constructor() {
        this.versions = {};
    }

    createVersion(conceptId, name, description) {
        if (!this.versions[conceptId]) {
            this.versions[conceptId] = [];
        }
        
        const version = {
            id: generateId(),
            name,
            description,
            timestamp: new Date().toISOString(),
            data: {
                categories: categories.filter(c => c.conceptId === conceptId),
                relations: relations.filter(r => {
                    const fromCategory = categories.find(c => c.id === r.from);
                    return fromCategory && fromCategory.conceptId === conceptId;
                })
            }
        };
        
        this.versions[conceptId].push(version);
        return version;
    }

    getVersions(conceptId) {
        return this.versions[conceptId] || [];
    }

    loadVersion(conceptId, versionId) {
        const versions = this.getVersions(conceptId);
        const version = versions.find(v => v.id === versionId);
        
        if (version) {
            // Удаляем текущие категории и связи концепции
            categories = categories.filter(c => c.conceptId !== conceptId);
            relations = relations.filter(r => {
                const fromCategory = categories.find(c => c.id === r.from);
                return !fromCategory || fromCategory.conceptId !== conceptId;
            });
            
            // Добавляем данные из версии
            categories.push(...version.data.categories);
            relations.push(...version.data.relations);
            
            saveDatabase();
            updateUI();
            return true;
        }
        
        return false;
    }

    compareVersions(conceptId, version1Id, version2Id) {
        const versions = this.getVersions(conceptId);
        const v1 = versions.find(v => v.id === version1Id);
        const v2 = versions.find(v => v.id === version2Id);
        
        if (!v1 || !v2) return null;
        
        const comparison = {
            categoriesAdded: v2.data.categories.filter(c2 => 
                !v1.data.categories.find(c1 => c1.id === c2.id)
            ),
            categoriesRemoved: v1.data.categories.filter(c1 => 
                !v2.data.categories.find(c2 => c2.id === c1.id)
            ),
            categoriesModified: v2.data.categories.filter(c2 => {
                const c1 = v1.data.categories.find(c => c.id === c2.id);
                return c1 && JSON.stringify(c1) !== JSON.stringify(c2);
            }),
            relationsAdded: v2.data.relations.filter(r2 => 
                !v1.data.relations.find(r1 => r1.id === r2.id)
            ),
            relationsRemoved: v1.data.relations.filter(r1 => 
                !v2.data.relations.find(r2 => r2.id === r1.id)
            )
        };
        
        return comparison;
    }
}

// === Инициализация новых компонентов ===

let graphVisualizer = null;
let historyManager = new HistoryManager();
let versionManager = new ConceptVersionManager();

// Добавляем функции для работы с историей
function handleUndo() {
    const previousState = historyManager.undo();
    if (previousState) {
        concepts = previousState.concepts;
        categories = previousState.categories;
        relations = previousState.relations;
        updateUI();
    }
}

function handleRedo() {
    const nextState = historyManager.redo();
    if (nextState) {
        concepts = nextState.concepts;
        categories = nextState.categories;
        relations = nextState.relations;
        updateUI();
    }
}

// Сохраняем состояние в историю при изменениях
function saveToHistory() {
    historyManager.addState({
        concepts,
        categories,
        relations
    });
}

// Обновляем функцию создания категории для работы с историей
const originalCreateCategory = createCategory;
createCategory = function() {
    originalCreateCategory();
    saveToHistory();
};

// Аналогично для других функций изменения данных
const originalCreateRelation = createRelation;
createRelation = function() {
    originalCreateRelation();
    saveToHistory();
};

// Функции для управления версиями
function createConceptVersion() {
    if (!currentConcept) {
        alert('Выберите концепцию для создания версии');
        return;
    }
    
    const name = prompt('Введите название версии:');
    const description = prompt('Введите описание версии:');
    
    if (name) {
        const version = versionManager.createVersion(currentConcept.id, name, description);
        showSuccess(`Версия "${name}" создана`);
    }
}

function showVersions() {
    if (!currentConcept) {
        alert('Выберите концепцию');
        return;
    }
    
    const versions = versionManager.getVersions(currentConcept.id);
    if (versions.length === 0) {
        alert('Нет сохраненных версий');
        return;
    }
    
    let html = '<div class="versions-list">';
    versions.forEach(version => {
        html += `
            <div class="version-item card">
                <h4>${version.name}</h4>
                <p>${version.description}</p>
                <p><small>Создано: ${new Date(version.timestamp).toLocaleString()}</small></p>
                <button onclick="loadConceptVersion('${version.id}')">Загрузить</button>
                <button onclick="compareWithVersion('${version.id}')" class="secondary">Сравнить</button>
            </div>
        `;
    });
    html += '</div>';
    
    showModal('Версии концепции', html);
}

function loadConceptVersion(versionId) {
    if (versionManager.loadVersion(currentConcept.id, versionId)) {
        showSuccess('Версия загружена');
        closeModal();
    } else {
        showError('Ошибка загрузки версии');
    }
}

// Обновляем функцию визуализации графа
function updateGraphVisualization() {
    const container = document.getElementById('graphContainer');
    if (!container) return;
    
    if (!graphVisualizer) {
        graphVisualizer = new GraphVisualizer('graphContainer');
    }
    
    if (currentConcept) {
        graphVisualizer.updateData(currentConcept.id);
        graphVisualizer.render();
    } else {
        container.innerHTML = '<p>Выберите или создайте концепцию для отображения графа</p>';
    }
}