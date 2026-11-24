# Исправленная функция generateConnectionViewContent

## Проблема

При двойном клике на связь открывается **пустая форма поиска** вместо отображения той связи, на которую кликнули.

## Причина

Функция `generateConnectionViewContent()` не проверяла, переданы ли ей данные о связи. Она всегда показывала пустую форму поиска.

## Решение

Функция должна работать в двух режимах:

1. **Если передан connectionData** (двойной клик на связь) → сразу показать визуализацию этой связи
2. **Если connectionData пуст** (создание новой связи) → показать форму поиска

---

## Исправленная функция generateConnectionViewContent

```javascript
/**
 * Генерация контента для просмотра связи
 * @param {object} connectionData - Данные связи (опционально)
 */
function generateConnectionViewContent(connectionData) {
    // Определяем, передана ли связь или это новый поиск
    const hasConnectionData = connectionData && 
                              (connectionData.source || connectionData.from) && 
                              (connectionData.target || connectionData.to);
    
    let html = `<h2>Просмотр связи</h2>`;
    
    // Если связь передана, сразу показываем её визуализацию
    if (hasConnectionData) {
        const sourceId = connectionData.source?.id || connectionData.source || connectionData.from;
        const targetId = connectionData.target?.id || connectionData.target || connectionData.to;
        const sourceNode = nodes.find(n => n.id === sourceId);
        const targetNode = nodes.find(n => n.id === targetId);
        
        if (!sourceNode || !targetNode) {
            return '<p>Ошибка: не удалось найти концепции связи</p>';
        }
        
        // Инициализируем состояние просмотра
        if (!ModalContext.editState.connectionView) {
            ModalContext.editState.connectionView = {};
        }
        ModalContext.editState.connectionView.selectedSource = sourceId;
        ModalContext.editState.connectionView.selectedTarget = targetId;
        
        // Генерируем визуализацию связи
        html += generateConnectionVisualization(sourceNode, targetNode, connectionData);
        
        // Добавляем сворачиваемую секцию поиска (на случай, если пользователь хочет посмотреть другую связь)
        html += `
            <div class="modal-section-title" style="margin-top: 25px; cursor: pointer;" onclick="toggleConnectionSearchSection()">
                🔍 Поиск другой связи
                <span id="toggleConnectionSearch" style="float: right;">▼</span>
            </div>
            <div id="connectionSearchSection" style="display: none;">
        `;
    } else {
        // Если связь не передана, показываем форму поиска развернутой
        html += `
            <div class="modal-section-title" style="margin-top: 0;">
                🔍 Поиск связи
            </div>
            <div id="connectionSearchSection">
        `;
        
        // Инициализируем пустое состояние
        if (!ModalContext.editState.connectionView) {
            ModalContext.editState.connectionView = {
                selectedSource: null,
                selectedTarget: null
            };
        }
    }
    
    // Форма поиска (всегда присутствует, но может быть свернута)
    html += `
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 25px; margin-top: 15px;">
            <!-- Поиск начальной концепции -->
            <div class="modal-form-group" style="margin-bottom: 0;">
                <label>Начальная концепция</label>
                <div class="modal-concept-search">
                    <input type="text" 
                           id="connViewSourceSearch" 
                           placeholder="Поиск концепции..."
                           oninput="handleConnectionViewSearch('source', this.value)"
                           onfocus="handleConnectionViewSearch('source', this.value)">
                    <div class="modal-concept-search-results" id="connViewSourceResults"></div>
                </div>
                <div id="connViewSourceSelected" style="margin-top: 10px; padding: 10px; background: rgba(162,155,254,0.1); border-radius: 6px; display: none;">
                    <strong id="connViewSourceLabel"></strong>
                    <div style="font-size: 11px; color: #b0b0b0; margin-top: 4px;" id="connViewSourcePhil"></div>
                </div>
            </div>
            
            <!-- Поиск конечной концепции -->
            <div class="modal-form-group" style="margin-bottom: 0;">
                <label>Конечная концепция</label>
                <div class="modal-concept-search">
                    <input type="text" 
                           id="connViewTargetSearch" 
                           placeholder="Поиск концепции..."
                           oninput="handleConnectionViewSearch('target', this.value)"
                           onfocus="handleConnectionViewSearch('target', this.value)">
                    <div class="modal-concept-search-results" id="connViewTargetResults"></div>
                </div>
                <div id="connViewTargetSelected" style="margin-top: 10px; padding: 10px; background: rgba(162,155,254,0.1); border-radius: 6px; display: none;">
                    <strong id="connViewTargetLabel"></strong>
                    <div style="font-size: 11px; color: #b0b0b0; margin-top: 4px;" id="connViewTargetPhil"></div>
                </div>
            </div>
        </div>
    </div>
    `;
    
    // Контейнер для визуализации (если связь не передана изначально)
    if (!hasConnectionData) {
        html += `
            <div id="connectionVisualization" style="min-height: 150px;">
                <div style="text-align: center; color: #95a5a6; padding: 40px; font-size: 13px;">
                    Выберите обе концепции для отображения связи
                </div>
            </div>
        `;
    }
    
    return html;
}

/**
 * Генерация визуализации связи между двумя концепциями
 */
function generateConnectionVisualization(sourceNode, targetNode, connectionData) {
    const sourceId = sourceNode.id;
    const targetId = targetNode.id;
    
    // Находим все связи между этими концепциями
    const connections = links.filter(l => {
        const srcId = l.source.id || l.source;
        const tgtId = l.target.id || l.target;
        
        return (srcId === sourceId && tgtId === targetId) || 
               (srcId === targetId && tgtId === sourceId);
    });
    
    let html = `
        <div id="connectionVisualization">
            <div class="modal-section-title" style="margin-bottom: 15px;">
                🔗 ${connections.length === 1 ? 'Связь' : `Найденные связи (${connections.length})`}
            </div>
    `;
    
    if (connections.length === 0) {
        html += `
            <div style="text-align: center; color: #e74c3c; padding: 40px; font-size: 13px;">
                ⚠️ Связь между выбранными концепциями не найдена
            </div>
        `;
    } else {
        // Генерируем визуализацию для каждой связи
        connections.forEach((conn, index) => {
            const srcId = conn.source.id || conn.source;
            const tgtId = conn.target.id || conn.target;
            
            // Определяем направление
            const isForward = srcId === sourceId;
            const displaySource = isForward ? sourceNode : targetNode;
            const displayTarget = isForward ? targetNode : sourceNode;
            
            const linkColor = relationTypesObj[conn.type].color;
            const linkLabel = relationTypesObj[conn.type].label;
            const sourceColor = philosopherConcepts[displaySource.concept].color;
            const targetColor = philosopherConcepts[displayTarget.concept].color;
            
            // Создаем SVG стрелку
            const svgWidth = 300;
            const svgHeight = 60;
            const arrowId = `arrow-viz-${index}`;
            
            let arrowSvg;
            if (conn.bidirectional) {
                arrowSvg = `
                    <svg width="${svgWidth}" height="${svgHeight}" style="display: block; margin: 0 auto;">
                        <defs>
                            <marker id="${arrowId}-start" markerWidth="10" markerHeight="10" refX="0" refY="5" orient="auto">
                                <polygon points="0,0 0,10 10,5" fill="${linkColor}" />
                            </marker>
                            <marker id="${arrowId}-end" markerWidth="10" markerHeight="10" refX="10" refY="5" orient="auto">
                                <polygon points="0,0 10,5 0,10" fill="${linkColor}" />
                            </marker>
                        </defs>
                        <line x1="20" y1="${svgHeight/2}" x2="${svgWidth-20}" y2="${svgHeight/2}" 
                              stroke="${linkColor}" stroke-width="3" 
                              marker-start="url(#${arrowId}-start)" 
                              marker-end="url(#${arrowId}-end)" />
                        <text x="${svgWidth/2}" y="${svgHeight/2 - 10}" 
                              text-anchor="middle" fill="${linkColor}" 
                              font-size="11px" font-weight="600">${linkLabel}</text>
                    </svg>
                `;
            } else {
                arrowSvg = `
                    <svg width="${svgWidth}" height="${svgHeight}" style="display: block; margin: 0 auto;">
                        <defs>
                            <marker id="${arrowId}" markerWidth="10" markerHeight="10" refX="10" refY="5" orient="auto">
                                <polygon points="0,0 10,5 0,10" fill="${linkColor}" />
                            </marker>
                        </defs>
                        <line x1="20" y1="${svgHeight/2}" x2="${svgWidth-20}" y2="${svgHeight/2}" 
                              stroke="${linkColor}" stroke-width="3" 
                              marker-end="url(#${arrowId})" />
                        <text x="${svgWidth/2}" y="${svgHeight/2 - 10}" 
                              text-anchor="middle" fill="${linkColor}" 
                              font-size="11px" font-weight="600">${linkLabel}</text>
                    </svg>
                `;
            }
            
            html += `
                <div style="background: rgba(255, 255, 255, 0.03); border-radius: 10px; padding: 20px; margin-bottom: 15px; border: 1px solid rgba(255, 255, 255, 0.1);">
                    <div style="display: flex; justify-content: space-around; align-items: flex-start; margin-bottom: 10px;">
                        <!-- Начальная концепция -->
                        <div style="text-align: center; flex: 1;">
                            <div style="width: 40px; height: 40px; border-radius: 50%; background: ${sourceColor}; margin: 0 auto 8px; box-shadow: 0 0 15px ${sourceColor};"></div>
                            <div style="font-weight: 600; color: #a29bfe; font-size: 13px; cursor: pointer; margin-bottom: 4px;"
                                 onclick="openUniversalModal('concept', nodes.find(n => n.id === '${displaySource.id}'), 'view');">
                                ${displaySource.label}
                            </div>
                            <div style="font-size: 11px; color: #7f8c8d; font-style: italic; cursor: pointer;"
                                 onclick="openUniversalModal('philosopher', '${displaySource.concept}', 'view');">
                                ${displaySource.concept}
                            </div>
                        </div>
                        
                        <!-- Стрелка -->
                        <div style="flex: 1.5; display: flex; align-items: center;">
                            ${arrowSvg}
                        </div>
                        
                        <!-- Конечная концепция -->
                        <div style="text-align: center; flex: 1;">
                            <div style="width: 40px; height: 40px; border-radius: 50%; background: ${targetColor}; margin: 0 auto 8px; box-shadow: 0 0 15px ${targetColor};"></div>
                            <div style="font-weight: 600; color: #a29bfe; font-size: 13px; cursor: pointer; margin-bottom: 4px;"
                                 onclick="openUniversalModal('concept', nodes.find(n => n.id === '${displayTarget.id}'), 'view');">
                                ${displayTarget.label}
                            </div>
                            <div style="font-size: 11px; color: #7f8c8d; font-style: italic; cursor: pointer;"
                                 onclick="openUniversalModal('philosopher', '${displayTarget.concept}', 'view');">
                                ${displayTarget.concept}
                            </div>
                        </div>
                    </div>
                    
                    <!-- Информация о связи -->
                    <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(255, 255, 255, 0.1);">
                        <div style="display: flex; gap: 20px; font-size: 12px; color: #b0b0b0;">
                            <div><strong>Тип:</strong> ${linkLabel}</div>
                            <div><strong>Вес:</strong> ${conn.weight === 1 ? 'Слабая' : conn.weight === 2 ? 'Средняя' : 'Сильная'}</div>
                            <div><strong>Направление:</strong> ${conn.bidirectional ? 'Двунаправленная' : 'Однонаправленная'}</div>
                        </div>
                        ${conn.description ? `
                            <div style="margin-top: 10px; padding: 10px; background: rgba(108, 92, 231, 0.1); border-radius: 6px; font-size: 12px; color: #e0e0e0; line-height: 1.5;">
                                ${conn.description}
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
        });
    }
    
    html += `</div>`;
    
    return html;
}

/**
 * Переключение видимости секции поиска связи
 */
function toggleConnectionSearchSection() {
    const section = document.getElementById('connectionSearchSection');
    const toggle = document.getElementById('toggleConnectionSearch');
    
    if (section.style.display === 'none') {
        section.style.display = 'block';
        toggle.textContent = '▲';
    } else {
        section.style.display = 'none';
        toggle.textContent = '▼';
    }
}
```

---

## Обновление функции updateConnectionVisualization

Эта функция теперь вызывается из `handleConnectionViewSearch` после выбора обеих концепций:

```javascript
/**
 * Обновление визуализации связи
 */
function updateConnectionVisualization() {
    const sourceId = ModalContext.editState.connectionView.selectedSource;
    const targetId = ModalContext.editState.connectionView.selectedTarget;
    
    if (!sourceId || !targetId) {
        return;
    }
    
    const sourceNode = nodes.find(n => n.id === sourceId);
    const targetNode = nodes.find(n => n.id === targetId);
    
    if (!sourceNode || !targetNode) return;
    
    // Генерируем визуализацию
    const vizHtml = generateConnectionVisualization(sourceNode, targetNode, null);
    
    // Вставляем визуализацию
    const vizContainer = document.getElementById('connectionVisualization');
    if (vizContainer) {
        vizContainer.outerHTML = vizHtml;
    }
}
```

---

## Ключевые изменения

### 1. Проверка наличия данных связи

```javascript
const hasConnectionData = connectionData && 
                          (connectionData.source || connectionData.from) && 
                          (connectionData.target || connectionData.to);
```

### 2. Два режима работы

**Режим А: Связь передана (двойной клик)**
- Сразу показывается визуализация связи
- Форма поиска свернута (но доступна по клику "🔍 Поиск другой связи")

**Режим Б: Связь не передана (новый поиск)**
- Форма поиска развернута
- Показывается заглушка "Выберите обе концепции"

### 3. Вынесена отдельная функция generateConnectionVisualization

Генерирует HTML визуализации связи - используется как:
- При первоначальной загрузке (если связь передана)
- При обновлении после выбора концепций в форме поиска

---

## Где объявить новые функции

```javascript
// После функции generateConnectionViewContent()
function generateConnectionVisualization(sourceNode, targetNode, connectionData) { ... }

function toggleConnectionSearchSection() { ... }
```

---

## Итого

**Исправлено:**
- ✅ При двойном клике на связь сразу показывается визуализация этой связи
- ✅ Форма поиска доступна, но свернута (можно раскрыть для поиска другой связи)
- ✅ При создании новой связи (без данных) форма поиска развернута

**Результат:** Окно просмотра связи теперь работает интуитивно - показывает ту связь, на которую кликнули!
