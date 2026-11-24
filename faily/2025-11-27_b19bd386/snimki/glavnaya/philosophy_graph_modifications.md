# Модификации для разделения связей на внутренние и внешние

## 1. Добавить CSS стили для сворачиваемых секций

**Место вставки:** После строки 825 (после стилей `@keyframes slideDown`)

```css
/* Стили для сворачиваемых секций связей */
.connections-subsection {
    margin-top: 15px;
}

.subsection-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 15px;
    background: rgba(108, 92, 231, 0.15);
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.3s;
    margin-bottom: 10px;
}

.subsection-header:hover {
    background: rgba(108, 92, 231, 0.25);
}

.subsection-title {
    font-weight: 700;
    font-size: 13px;
    color: #a29bfe;
    display: flex;
    align-items: center;
    gap: 8px;
}

.subsection-toggle {
    font-size: 16px;
    color: #a29bfe;
    transition: transform 0.3s;
    user-select: none;
}

.subsection-toggle.collapsed {
    transform: rotate(-90deg);
}

.subsection-content {
    max-height: 2000px;
    overflow: hidden;
    transition: max-height 0.3s ease-out, opacity 0.3s ease-out;
    opacity: 1;
}

.subsection-content.collapsed {
    max-height: 0;
    opacity: 0;
}
```

---

## 2. Заменить функцию showDetailModal

**Место замены:** Строки 3785-3952 (вся функция `showDetailModal`)

```javascript
function showDetailModal(conceptData) {
    const modal = document.getElementById('detailModal');
    const overlay = document.getElementById('modalOverlay');
    const content = document.getElementById('modalContent');

    freezeSimulation();
    
    // Получаем рубрики этой концепции
    const conceptRubrics = conceptToRubrics[conceptData.id] || [];
    
    let html = `
        <div id="modalSearch">
            <div class="legend-search-header">
                <div class="legend-search-icon">🔍</div>
                <div class="legend-search-input-wrapper">
                    <input type="text" 
                           class="legend-search-input" 
                           id="modalSearchInput" 
                           placeholder="Поиск других концепций..."
                           oninput="handleModalSearch(this.value)"
                           onfocus="handleModalSearch(this.value)">
                    <span class="legend-search-clear" onclick="clearModalSearch()">×</span>
                    <div class="search-results" id="modalSearchResults"></div>
                </div>
            </div>
        </div>
        <h2>${conceptData.label}</h2>
        <div class="philosopher-tag" style="background: ${philosopherConcepts[conceptData.concept].color}">
            ${conceptData.concept}
        </div>
        <div class="description">${conceptData.extendedDescription}</div>
        <button class="goto-node-btn" onclick="gotoNodeFromModal('${conceptData.id}')">
            🎯 Перейти к узлу
        </button>
    `;
    
    // Секция связей узла - МОДИФИЦИРОВАННАЯ ВЕРСИЯ
    const nodeConnections = links.filter(l => {
        const src = l.source.id || l.source;
        const tgt = l.target.id || l.target;
        return src === conceptData.id || tgt === conceptData.id;
    });

    if (nodeConnections.length > 0) {
        // Разделяем связи на внутренние и внешние
        const internalConnections = [];
        const externalConnections = [];
        
        nodeConnections.forEach(conn => {
            const src = conn.source.id || conn.source;
            const tgt = conn.target.id || conn.target;
            const isSource = src === conceptData.id;
            const connectedNodeId = isSource ? tgt : src;
            const connectedNode = nodes.find(n => n.id === connectedNodeId);
            
            if (!connectedNode) return;
            
            // Проверяем, тот же философ или нет
            if (connectedNode.concept === conceptData.concept) {
                internalConnections.push({ conn, connectedNode, isSource });
            } else {
                externalConnections.push({ conn, connectedNode, isSource });
            }
        });
        
        // Проверяем, есть ли хотя бы одна связь с description
        const hasDescriptions = nodeConnections.some(conn => conn.description);
        
        html += `
            <div class="connections-section">
                <div class="connections-title">📊 Связи узла (${nodeConnections.length})</div>
        `;
        
        // Добавляем кнопку для раскрытия/свертывания всех описаний, если есть descriptions
        if (hasDescriptions) {
            html += `
                <button class="toggle-all-descriptions-btn" onclick="toggleAllConnectionDescriptions('${conceptData.id}')">
                    ▼ Развернуть все описания связей
                </button>
            `;
        }
        
        // ВНУТРЕННИЕ СВЯЗИ (того же философа)
        if (internalConnections.length > 0) {
            html += `
                <div class="connections-subsection">
                    <div class="subsection-header" onclick="toggleSubsection('internal-${conceptData.id}')">
                        <div class="subsection-title">
                            🔗 Связи внутри системы ${conceptData.concept}
                            <span style="font-weight: 400; font-size: 11px; color: #95a5a6;">(${internalConnections.length})</span>
                        </div>
                        <span class="subsection-toggle" id="toggle-internal-${conceptData.id}">▼</span>
                    </div>
                    <div class="subsection-content" id="content-internal-${conceptData.id}">
            `;
            
            internalConnections.forEach(({ conn, connectedNode, isSource }) => {
                const linkColor = relationTypesObj[conn.type].color;
                const linkLabel = relationTypesObj[conn.type].label;
                
                // Определяем направление стрелки
                let arrow = '';
                if (conn.bidirectional) {
                    arrow = '↔';
                } else if (isSource) {
                    arrow = '→';
                } else {
                    arrow = '←';
                }
                
                html += `
                    <div class="connection-item">
                        <div class="concept-color" style="background: ${philosopherConcepts[connectedNode.concept].color}"></div>
                        <div class="connection-arrow" style="color: ${linkColor};">
                            ${arrow}
                            <span class="connection-arrow-tooltip">${linkLabel}</span>
                        </div>
                        <div style="flex-grow: 1;" onclick="closeDetailModal(); setTimeout(() => showDetailModal(nodes.find(n => n.id === '${connectedNode.id}')), 100);">
                            <div class="concept-name">${connectedNode.label}</div>
                            <div class="concept-philosopher">${connectedNode.concept}</div>
                        </div>
                        ${conn.description ? `
                            <button class="connection-toggle" onclick="event.stopPropagation(); toggleConnectionDescription('${conceptData.id}-${connectedNode.id}')">
                                ▼
                            </button>
                        ` : ''}
                    </div>
                    ${conn.description ? `
                        <div class="connection-description" id="desc-${conceptData.id}-${connectedNode.id}">
                            ${conn.description}
                        </div>
                    ` : ''}
                `;
            });
            
            html += `
                    </div>
                </div>
            `;
        }
        
        // ВНЕШНИЕ СВЯЗИ (с другими философами)
        if (externalConnections.length > 0) {
            html += `
                <div class="connections-subsection">
                    <div class="subsection-header" onclick="toggleSubsection('external-${conceptData.id}')">
                        <div class="subsection-title">
                            🌐 Связи с концепциями других философов
                            <span style="font-weight: 400; font-size: 11px; color: #95a5a6;">(${externalConnections.length})</span>
                        </div>
                        <span class="subsection-toggle" id="toggle-external-${conceptData.id}">▼</span>
                    </div>
                    <div class="subsection-content" id="content-external-${conceptData.id}">
            `;
            
            externalConnections.forEach(({ conn, connectedNode, isSource }) => {
                const linkColor = relationTypesObj[conn.type].color;
                const linkLabel = relationTypesObj[conn.type].label;
                
                // Определяем направление стрелки
                let arrow = '';
                if (conn.bidirectional) {
                    arrow = '↔';
                } else if (isSource) {
                    arrow = '→';
                } else {
                    arrow = '←';
                }
                
                html += `
                    <div class="connection-item">
                        <div class="concept-color" style="background: ${philosopherConcepts[connectedNode.concept].color}"></div>
                        <div class="connection-arrow" style="color: ${linkColor};">
                            ${arrow}
                            <span class="connection-arrow-tooltip">${linkLabel}</span>
                        </div>
                        <div style="flex-grow: 1;" onclick="closeDetailModal(); setTimeout(() => showDetailModal(nodes.find(n => n.id === '${connectedNode.id}')), 100);">
                            <div class="concept-name">${connectedNode.label}</div>
                            <div class="concept-philosopher">${connectedNode.concept}</div>
                        </div>
                        ${conn.description ? `
                            <button class="connection-toggle" onclick="event.stopPropagation(); toggleConnectionDescription('${conceptData.id}-${connectedNode.id}')">
                                ▼
                            </button>
                        ` : ''}
                    </div>
                    ${conn.description ? `
                        <div class="connection-description" id="desc-${conceptData.id}-${connectedNode.id}">
                            ${conn.description}
                        </div>
                    ` : ''}
                `;
            });
            
            html += `
                    </div>
                </div>
            `;
        }
        
        html += `</div>`;
    }
    
    // Секция рубрик (без изменений)
    if (conceptRubrics.length > 0) {
        const rubricDataArray = conceptRubrics.map(rubricId => 
            rubrics.find(r => r.id === rubricId)
        ).filter(r => r !== undefined);
        
        rubricDataArray.forEach(rubricData => {
            const relatedConcepts = nodes.filter(n => {
                const nRubrics = conceptToRubrics[n.id] || [];
                return nRubrics.includes(rubricData.id) && n.id !== conceptData.id;
            });
            
            const showAllId = `show-all-${rubricData.id}`;
            const initialDisplay = 10;
            const hasMore = relatedConcepts.length > initialDisplay;
            
            html += `
                <div class="rubric-section">
                    <div class="rubric-title">📚 Рубрика: ${rubricData.name}</div>
                    <div class="rubric-description">${rubricData.description}</div>
                    
                    ${relatedConcepts.length > 0 ? `
                        <div class="related-concepts">
                            <div class="related-title">Также в этой рубрике (${relatedConcepts.length}):</div>
                            <div id="${showAllId}-container">
                                ${relatedConcepts.slice(0, initialDisplay).map(c => `
                                    <div class="concept-item" onclick="closeDetailModal(); setTimeout(() => showDetailModal(nodes.find(n => n.id === '${c.id}')), 100);">
                                        <div class="concept-color" style="background: ${philosopherConcepts[c.concept].color}"></div>
                                        <div class="concept-name">${c.label}</div>
                                        <div class="concept-philosopher">${c.concept}</div>
                                    </div>
                                `).join('')}
                            </div>
                            ${hasMore ? `
                                <button class="show-all-concepts-btn" id="${showAllId}" onclick="showAllConcepts('${rubricData.id}', '${conceptData.id}')">
                                    Показать все (${relatedConcepts.length})
                                </button>
                            ` : ''}
                        </div>
                    ` : ''}
                </div>
            `;
        });
    } else {
        html += `<div class="rubric-section">
            <div class="rubric-description" style="color: #95a5a6;">
                Эта концепция пока не отнесена к какой-либо рубрике.
            </div>
        </div>`;
    }
    
    content.innerHTML = html;
    modal.classList.add('show');
    overlay.classList.add('show');
}
```

---

## 3. Добавить функцию для сворачивания/разворачивания подсекций

**Место вставки:** После строки 3998 (после функции `toggleAllConnectionDescriptions`)

```javascript
// Функция для сворачивания/разворачивания подсекций связей
function toggleSubsection(sectionId) {
    const content = document.getElementById(`content-${sectionId}`);
    const toggle = document.getElementById(`toggle-${sectionId}`);
    
    if (!content || !toggle) return;
    
    if (content.classList.contains('collapsed')) {
        content.classList.remove('collapsed');
        toggle.classList.remove('collapsed');
    } else {
        content.classList.add('collapsed');
        toggle.classList.add('collapsed');
    }
}
```

---

## Инструкция по применению изменений:

1. **CSS стили:** Вставьте блок CSS после строки 825 (после `@keyframes slideDown`)

2. **Функция showDetailModal:** Замените всю функцию `showDetailModal` (строки 3785-3952) на новую версию

3. **Функция toggleSubsection:** Добавьте новую функцию после строки 3998 (после функции `toggleAllConnectionDescriptions`)

## Что изменится:

- ✅ Связи будут разделены на две категории: внутренние (того же философа) и внешние (других философов)
- ✅ Каждая категория будет иметь заголовок с количеством связей
- ✅ Обе секции можно сворачивать/разворачивать независимо друг от друга
- ✅ Добавлены иконки для улучшения визуального восприятия (🔗 для внутренних, 🌐 для внешних связей)
- ✅ Анимация сворачивания/разворачивания для плавности
- ✅ Сохранена вся существующая функциональность (описания связей, переход к узлам и т.д.)
