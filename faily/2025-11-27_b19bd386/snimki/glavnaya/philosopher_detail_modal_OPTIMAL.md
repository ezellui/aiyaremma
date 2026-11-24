# Добавление окна детальной информации о философе (ОПТИМИЗИРОВАННАЯ ВЕРСИЯ)

## Обзор изменений

Эта версия создает общие CSS классы для обоих модальных окон (концепции и философа), избегая дублирования кода.

---

## 1. Модифицировать HTML окна концепции - добавить классы

**Место изменения:** Строка 1634-1637

**Было:**
```html
<div id="detailModal">
    <button class="close-btn" onclick="closeDetailModal()">×</button>
    <div id="modalContent"></div>
</div>
```

**Заменить на:**
```html
<div id="detailModal" class="detail-modal">
    <button class="close-btn" onclick="closeDetailModal()">×</button>
    <div id="modalContent" class="modal-content"></div>
</div>
```

---

## 2. Добавить HTML разметку окна философа

**Место вставки:** Сразу после окна концепции (после строки 1637, перед `<div id="legend">`)

```html
<div id="philosopherDetailModal" class="detail-modal">
    <button class="close-btn" onclick="closePhilosopherDetailModal()">×</button>
    <div id="philosopherModalContent" class="modal-content"></div>
</div>
```

---

## 3. Рефакторинг CSS - заменить ID селекторы на классы

**Место замены:** Строки 489-659 (весь блок стилей `#detailModal`)

**Заменить весь блок на:**

```css
/* ============================================ */
/* ОБЩИЕ СТИЛИ ДЛЯ МОДАЛЬНЫХ ОКОН ДЕТАЛЬНОЙ ИНФОРМАЦИИ */
/* ============================================ */

.detail-modal {
    display: none;
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: rgba(0, 0, 0, 0.92);
    color: white;
    padding: 25px 30px;
    border-radius: 15px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.7);
    max-width: 550px;
    max-height: 80vh;
    overflow-y: auto;
    z-index: 2000;
    border: 1px solid rgba(255,255,255,0.2);
}

/* Окно философа чуть шире из-за большего количества информации */
#philosopherDetailModal.detail-modal {
    max-width: 650px;
    max-height: 85vh;
}

.detail-modal.show {
    display: block;
}

#modalOverlay {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.7);
    z-index: 1999;
}

#modalOverlay.show {
    display: block;
}

.detail-modal h2 {
    margin: 0 0 8px 0;
    color: #a29bfe;
    font-size: 22px;
    font-weight: 600;
}

.detail-modal .philosopher-tag {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 600;
    color: white;
    margin-bottom: 12px;
    opacity: 0.9;
}

.detail-modal .description {
    color: #e0e0e0;
    margin-bottom: 18px;
    line-height: 1.6;
    font-size: 13px;
}

.detail-modal .rubric-section {
    background: rgba(255, 255, 255, 0.08);
    padding: 18px;
    border-radius: 10px;
    border-left: 3px solid #a29bfe;
}

.detail-modal .rubric-title {
    font-size: 15px;
    font-weight: 700;
    color: #a29bfe;
    margin-bottom: 6px;
}

.detail-modal .rubric-description {
    font-size: 12px;
    color: #b0b0b0;
    margin-bottom: 14px;
    font-style: italic;
}

.detail-modal .related-concepts {
    margin-top: 12px;
}

.detail-modal .related-title {
    font-size: 13px;
    font-weight: 700;
    color: #e0e0e0;
    margin-bottom: 8px;
}

.detail-modal .concept-item {
    display: flex;
    align-items: center;
    padding: 7px 10px;
    margin: 4px 0;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.detail-modal .concept-item:hover {
    background: rgba(255, 255, 255, 0.15);
    transform: translateX(5px);
    border-color: rgba(162, 155, 254, 0.4);
}

.detail-modal .concept-color {
    width: 11px;
    height: 11px;
    border-radius: 50%;
    margin-right: 10px;
    flex-shrink: 0;
    box-shadow: 0 0 8px currentColor;
}

.detail-modal .concept-name {
    font-size: 13px;
    color: #e0e0e0;
    flex-grow: 1;
}

.detail-modal .concept-philosopher {
    font-size: 10px;
    color: #a0a0a0;
    font-style: italic;
}

.detail-modal .close-btn {
    position: absolute;
    top: 12px;
    right: 12px;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.15);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: white;
    cursor: pointer;
    font-size: 18px;
    line-height: 1;
    transition: all 0.2s;
}

.detail-modal .close-btn:hover {
    background: rgba(255, 255, 255, 0.25);
    transform: rotate(90deg);
}

.detail-modal::-webkit-scrollbar {
    width: 6px;
}

.detail-modal::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 10px;
}

.detail-modal::-webkit-scrollbar-thumb {
    background: #a29bfe;
    border-radius: 10px;
}

.detail-modal::-webkit-scrollbar-thumb:hover {
    background: #8b7fe6;
}
```

---

## 4. Добавить специфичные стили для окна философа

**Место вставки:** Сразу после общих стилей модальных окон (после предыдущего блока)

```css
/* ============================================ */
/* СПЕЦИФИЧНЫЕ СТИЛИ ДЛЯ ОКНА ФИЛОСОФА */
/* ============================================ */

/* Стили для подсказок рубрик */
.rubric-name-tooltip {
    position: relative;
    cursor: help;
    border-bottom: 1px dotted #a29bfe;
    display: inline-block;
}

.rubric-tooltip-text {
    visibility: hidden;
    background-color: rgba(0, 0, 0, 0.95);
    color: #fff;
    text-align: left;
    border-radius: 6px;
    padding: 8px 12px;
    position: absolute;
    z-index: 2001;
    bottom: 125%;
    left: 50%;
    transform: translateX(-50%);
    white-space: normal;
    max-width: 300px;
    font-size: 11px;
    line-height: 1.4;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
}

.rubric-name-tooltip:hover .rubric-tooltip-text {
    visibility: visible;
}

/* Стиль для кликабельных философов */
.philosopher-link {
    cursor: pointer;
    color: #a29bfe;
    font-weight: 600;
    text-decoration: none;
    transition: color 0.2s;
}

.philosopher-link:hover {
    color: #6c5ce7;
    text-decoration: underline;
}

/* Стили для секций взаимодействия философов */
.interaction-section {
    margin-bottom: 15px;
    padding: 12px;
    background: rgba(108, 92, 231, 0.08);
    border-radius: 8px;
    border-left: 3px solid #a29bfe;
}

.interaction-type {
    font-weight: 700;
    color: #a29bfe;
    margin-bottom: 8px;
    font-size: 13px;
}

.interaction-direction {
    margin: 6px 0;
    padding-left: 10px;
    font-size: 12px;
    color: #e0e0e0;
}

.interaction-direction-label {
    font-weight: 600;
    color: #b0b0b0;
    font-size: 11px;
    text-transform: uppercase;
}

.philosopher-list {
    display: inline;
    margin-left: 5px;
}

/* Стили для разделов концепций философа */
.philosopher-concepts-section {
    margin-top: 20px;
}

.concept-details-item {
    background: rgba(255, 255, 255, 0.03);
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 10px;
    border-left: 3px solid #a29bfe;
    cursor: pointer;
    transition: all 0.2s;
}

.concept-details-item:hover {
    background: rgba(162, 155, 254, 0.1);
    border-left-color: #6c5ce7;
}

.concept-details-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 8px;
}

.concept-details-name {
    font-weight: 700;
    font-size: 14px;
    color: #a29bfe;
}

.concept-short-desc {
    font-size: 12px;
    color: #b0b0b0;
    line-height: 1.5;
    margin: 8px 0;
}

.concept-extended-desc {
    font-size: 12px;
    color: #e0e0e0;
    line-height: 1.6;
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease-out, opacity 0.3s ease-out;
    opacity: 0;
}

.concept-extended-desc.show {
    max-height: 1000px;
    opacity: 1;
}

.toggle-concept-desc-btn {
    background: none;
    border: none;
    color: #a29bfe;
    cursor: pointer;
    font-size: 16px;
    padding: 4px 8px;
    transition: transform 0.3s;
}

.toggle-concept-desc-btn.expanded {
    transform: rotate(180deg);
}

/* Заголовки секций в модальном окне философа */
.philosopher-section-title {
    font-size: 15px;
    font-weight: 700;
    color: #a29bfe;
    margin: 20px 0 12px 0;
    padding-bottom: 8px;
    border-bottom: 2px solid rgba(162, 155, 254, 0.3);
    display: flex;
    align-items: center;
    gap: 8px;
}
```

---

## 5. Создать функцию showPhilosopherDetailModal

**Место вставки:** После строки 4070 (после функции `closeDetailModal`)

**ВАЖНО:** Функция остается такой же, как в исправленной версии, но теперь она работает с общими классами.

```javascript
// ============================================
// ФУНКЦИИ ДЕТАЛЬНОГО МОДАЛЬНОГО ОКНА ФИЛОСОФА
// ============================================

function showPhilosopherDetailModal(philosopherName) {
    const modal = document.getElementById('philosopherDetailModal');
    const overlay = document.getElementById('modalOverlay');
    const content = document.getElementById('philosopherModalContent');

    freezeSimulation();
    
    // Находим данные философа
    const philosopherData = philosophers.find(p => p.nameRu === philosopherName);
    if (!philosopherData) {
        console.error('Философ не найден:', philosopherName);
        return;
    }
    
    const philColor = philosopherConcepts[philosopherName].color;
    
    // Формируем описание с переносами строк
    const formattedDescription = philosopherData.description.replace(/\n\n/g, '<br><br>');
    
    let html = `
        <h2>${philosopherName}</h2>
        <div class="philosopher-tag" style="background: ${philColor}">
            ${philosopherData.years}
        </div>
        <div class="description">${formattedDescription}</div>
    `;
    
    // ========================================
    // РАЗДЕЛ ВЗАИМОДЕЙСТВИЯ С ДРУГИМИ ФИЛОСОФАМИ
    // ========================================
    
    const philosopherConcepts_ids = nodes.filter(n => n.concept === philosopherName).map(n => n.id);
    
    const externalLinks = links.filter(l => {
        const srcId = l.source.id || l.source;
        const tgtId = l.target.id || l.target;
        const srcNode = nodes.find(n => n.id === srcId);
        const tgtNode = nodes.find(n => n.id === tgtId);
        
        if (!srcNode || !tgtNode) return false;
        
        return (srcNode.concept === philosopherName && tgtNode.concept !== philosopherName) ||
               (tgtNode.concept === philosopherName && srcNode.concept !== philosopherName);
    });
    
    if (externalLinks.length > 0) {
        const interactionsByType = {};
        
        externalLinks.forEach(link => {
            const srcId = link.source.id || link.source;
            const tgtId = link.target.id || link.target;
            const srcNode = nodes.find(n => n.id === srcId);
            const tgtNode = nodes.find(n => n.id === tgtId);
            
            const linkType = link.type;
            const isOutgoing = srcNode.concept === philosopherName;
            const otherPhilosopher = isOutgoing ? tgtNode.concept : srcNode.concept;
            
            if (!interactionsByType[linkType]) {
                interactionsByType[linkType] = {
                    incoming: new Set(),
                    outgoing: new Set()
                };
            }
            
            if (link.bidirectional) {
                interactionsByType[linkType].incoming.add(otherPhilosopher);
                interactionsByType[linkType].outgoing.add(otherPhilosopher);
            } else if (isOutgoing) {
                interactionsByType[linkType].outgoing.add(otherPhilosopher);
            } else {
                interactionsByType[linkType].incoming.add(otherPhilosopher);
            }
        });
        
        html += `
            <div class="philosopher-section-title">
                🔗 Взаимодействие с другими философами
            </div>
        `;
        
        const interactionLabels = {
            'influence': { incoming: 'Испытал влияние от', outgoing: 'Оказал влияние на' },
            'develop': { incoming: 'Развивал концепции', outgoing: 'Его концепции развивали' },
            'oppose': { incoming: 'Ему противостояли', outgoing: 'Противостоял' },
            'critique': { incoming: 'Его критиковали', outgoing: 'Критиковал' },
            'dialogue': { incoming: 'С ним полемизировали', outgoing: 'Полемизировал' },
            'synthesize': { incoming: 'Его концепции синтезировали', outgoing: 'Синтезировал концепции' },
            'exemplify': { incoming: 'Его иллюстрировали', outgoing: 'Иллюстрировал' },
            'internal_contradiction': { incoming: 'Противоречил себе в', outgoing: 'Внутренние противоречия' }
        };
        
        Object.keys(interactionsByType).forEach(linkType => {
            const interaction = interactionsByType[linkType];
            const labels = interactionLabels[linkType] || { incoming: 'От', outgoing: 'К' };
            const typeLabel = relationTypesObj[linkType]?.label || linkType;
            
            const hasIncoming = interaction.incoming.size > 0;
            const hasOutgoing = interaction.outgoing.size > 0;
            
            if (!hasIncoming && !hasOutgoing) return;
            
            html += `<div class="interaction-section">`;
            html += `<div class="interaction-type">${typeLabel}</div>`;
            
            if (hasIncoming) {
                const philList = Array.from(interaction.incoming)
                    .map(phil => `<span class="philosopher-link" onclick="closePhilosopherDetailModal(); setTimeout(() => showPhilosopherDetailModal('${phil}'), 100);">${phil}</span>`)
                    .join(', ');
                html += `
                    <div class="interaction-direction">
                        <span class="interaction-direction-label">← ${labels.incoming}:</span>
                        <span class="philosopher-list">${philList} (${interaction.incoming.size})</span>
                    </div>
                `;
            }
            
            if (hasOutgoing) {
                const philList = Array.from(interaction.outgoing)
                    .map(phil => `<span class="philosopher-link" onclick="closePhilosopherDetailModal(); setTimeout(() => showPhilosopherDetailModal('${phil}'), 100);">${phil}</span>`)
                    .join(', ');
                html += `
                    <div class="interaction-direction">
                        <span class="interaction-direction-label">→ ${labels.outgoing}:</span>
                        <span class="philosopher-list">${philList} (${interaction.outgoing.size})</span>
                    </div>
                `;
            }
            
            html += `</div>`;
        });
    }
    
    // ========================================
    // РАЗДЕЛ НАПРАВЛЕНИЙ РАБОТЫ
    // ========================================
    
    const philosopherRubrics = new Set();
    nodes.filter(n => n.concept === philosopherName).forEach(n => {
        const nodeRubrics = conceptToRubrics[n.id] || [];
        nodeRubrics.forEach(rubricId => philosopherRubrics.add(rubricId));
    });
    
    if (philosopherRubrics.size > 0) {
        html += `
            <div class="philosopher-section-title">
                📚 Направления работы
            </div>
            <div class="description">
                Работал в следующих направлениях: 
        `;
        
        const rubricNames = Array.from(philosopherRubrics).map(rubricId => {
            const rubric = rubrics.find(r => r.id === rubricId);
            if (!rubric) return '';
            return `
                <span class="rubric-name-tooltip">
                    ${rubric.name}
                    <span class="rubric-tooltip-text">${rubric.description}</span>
                </span>
            `;
        }).filter(r => r).join(', ');
        
        html += rubricNames + '</div>';
    }
    
    // ========================================
    // РАЗДЕЛ КОНЦЕПЦИЙ ФИЛОСОФА
    // ========================================
    
    const philosopherConceptsNodes = nodes.filter(n => n.concept === philosopherName);
    
    if (philosopherConceptsNodes.length > 0) {
        html += `
            <div class="philosopher-section-title">
                💡 Концепции философа (${philosopherConceptsNodes.length})
            </div>
            <button class="toggle-all-descriptions-btn" onclick="toggleAllPhilosopherConceptDescriptions()">
                ▼ Развернуть все описания концепций
            </button>
            <div class="philosopher-concepts-section">
        `;
        
        philosopherConceptsNodes.forEach(conceptNode => {
            html += `
                <div class="concept-details-item" onclick="event.stopPropagation(); closePhilosopherDetailModal(); setTimeout(() => showDetailModal(nodes.find(n => n.id === '${conceptNode.id}')), 100);">
                    <div class="concept-details-header">
                        <div class="concept-details-name">${conceptNode.label}</div>
                        <button class="toggle-concept-desc-btn" onclick="event.stopPropagation(); togglePhilosopherConceptDescription('${conceptNode.id}')">▼</button>
                    </div>
                    <div class="concept-short-desc">${conceptNode.description}</div>
                    <div class="concept-extended-desc" id="phil-concept-desc-${conceptNode.id}">
                        ${conceptNode.extendedDescription}
                    </div>
                </div>
            `;
        });
        
        html += `</div>`;
    }
    
    // ========================================
    // РАЗДЕЛ СВЯЗЕЙ КОНЦЕПЦИЙ ФИЛОСОФА
    // ========================================
    
    const conceptConnections = links.filter(l => {
        const srcId = l.source.id || l.source;
        const tgtId = l.target.id || l.target;
        return philosopherConcepts_ids.includes(srcId) || philosopherConcepts_ids.includes(tgtId);
    });
    
    if (conceptConnections.length > 0) {
        const internalConnections = [];
        const externalConnectionsData = [];
        
        conceptConnections.forEach(conn => {
            const srcId = conn.source.id || conn.source;
            const tgtId = conn.target.id || conn.target;
            const srcNode = nodes.find(n => n.id === srcId);
            const tgtNode = nodes.find(n => n.id === tgtId);
            
            if (!srcNode || !tgtNode) return;
            
            if (srcNode.concept === philosopherName && tgtNode.concept === philosopherName) {
                internalConnections.push({ conn, srcNode, tgtNode });
            } else if (srcNode.concept === philosopherName || tgtNode.concept === philosopherName) {
                externalConnectionsData.push({ conn, srcNode, tgtNode });
            }
        });
        
        const hasConnectionDescriptions = conceptConnections.some(c => c.description);
        
        html += `
            <div class="philosopher-section-title">
                🔗 Связи концепций философа (${conceptConnections.length})
            </div>
        `;
        
        if (hasConnectionDescriptions) {
            html += `
                <button class="toggle-all-descriptions-btn" onclick="toggleAllPhilosopherConnectionDescriptions()">
                    ▼ Развернуть все описания связей
                </button>
            `;
        }
        
        html += `<div class="connections-section">`;
        
        // ВНУТРЕННИЕ СВЯЗИ
        if (internalConnections.length > 0) {
            html += `
                <div class="connections-subsection">
                    <div class="subsection-header" onclick="toggleSubsection('phil-internal-${philosopherName}')">
                        <div class="subsection-title">
                            🔗 Связи внутри системы ${philosopherName}
                            <span style="font-weight: 400; font-size: 11px; color: #95a5a6;">(${internalConnections.length})</span>
                        </div>
                        <span class="subsection-toggle" id="toggle-phil-internal-${philosopherName}">▼</span>
                    </div>
                    <div class="subsection-content" id="content-phil-internal-${philosopherName}">
            `;
            
            internalConnections.forEach(({ conn, srcNode, tgtNode }) => {
                const linkColor = relationTypesObj[conn.type].color;
                const linkLabel = relationTypesObj[conn.type].label;
                const arrow = conn.bidirectional ? '↔' : '→';
                
                html += `
                    <div class="connection-item">
                        <div class="concept-color" style="background: ${philColor}"></div>
                        <div style="flex-grow: 1; display: flex; align-items: center; gap: 8px;">
                            <span onclick="closePhilosopherDetailModal(); setTimeout(() => showDetailModal(nodes.find(n => n.id === '${srcNode.id}')), 100);" style="cursor: pointer;">${srcNode.label}</span>
                            <div class="connection-arrow" style="color: ${linkColor};">
                                ${arrow}
                                <span class="connection-arrow-tooltip">${linkLabel}</span>
                            </div>
                            <span onclick="closePhilosopherDetailModal(); setTimeout(() => showDetailModal(nodes.find(n => n.id === '${tgtNode.id}')), 100);" style="cursor: pointer;">${tgtNode.label}</span>
                        </div>
                        ${conn.description ? `
                            <button class="connection-toggle" onclick="event.stopPropagation(); toggleConnectionDescription('phil-${srcNode.id}-${tgtNode.id}')">
                                ▼
                            </button>
                        ` : ''}
                    </div>
                    ${conn.description ? `
                        <div class="connection-description" id="desc-phil-${srcNode.id}-${tgtNode.id}">
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
        
        // ВНЕШНИЕ СВЯЗИ
        if (externalConnectionsData.length > 0) {
            html += `
                <div class="connections-subsection">
                    <div class="subsection-header" onclick="toggleSubsection('phil-external-${philosopherName}')">
                        <div class="subsection-title">
                            🌐 Связи с концепциями других философов
                            <span style="font-weight: 400; font-size: 11px; color: #95a5a6;">(${externalConnectionsData.length})</span>
                        </div>
                        <span class="subsection-toggle" id="toggle-phil-external-${philosopherName}">▼</span>
                    </div>
                    <div class="subsection-content" id="content-phil-external-${philosopherName}">
            `;
            
            externalConnectionsData.forEach(({ conn, srcNode, tgtNode }) => {
                const linkColor = relationTypesObj[conn.type].color;
                const linkLabel = relationTypesObj[conn.type].label;
                const arrow = conn.bidirectional ? '↔' : '→';
                
                html += `
                    <div class="connection-item">
                        <div class="concept-color" style="background: ${philosopherConcepts[srcNode.concept].color}"></div>
                        <div style="flex-grow: 1; display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                            <span onclick="closePhilosopherDetailModal(); setTimeout(() => showDetailModal(nodes.find(n => n.id === '${srcNode.id}')), 100);" style="cursor: pointer;">${srcNode.label}</span>
                            <span style="font-size: 10px; color: #7f8c8d;">(${srcNode.concept})</span>
                            <div class="connection-arrow" style="color: ${linkColor};">
                                ${arrow}
                                <span class="connection-arrow-tooltip">${linkLabel}</span>
                            </div>
                            <span onclick="closePhilosopherDetailModal(); setTimeout(() => showDetailModal(nodes.find(n => n.id === '${tgtNode.id}')), 100);" style="cursor: pointer;">${tgtNode.label}</span>
                            <span style="font-size: 10px; color: #7f8c8d;">(${tgtNode.concept})</span>
                        </div>
                        ${conn.description ? `
                            <button class="connection-toggle" onclick="event.stopPropagation(); toggleConnectionDescription('phil-${srcNode.id}-${tgtNode.id}')">
                                ▼
                            </button>
                        ` : ''}
                    </div>
                    ${conn.description ? `
                        <div class="connection-description" id="desc-phil-${srcNode.id}-${tgtNode.id}">
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
    
    content.innerHTML = html;
    modal.classList.add('show');
    overlay.classList.add('show');
}

function closePhilosopherDetailModal() {
    const modal = document.getElementById('philosopherDetailModal');
    const overlay = document.getElementById('modalOverlay');
    const content = document.getElementById('philosopherModalContent');
    
    content.innerHTML = '';
    modal.classList.remove('show');
    overlay.classList.remove('show');
    
    unfreezeSimulation();
}

// Переключение описания концепции в модальном окне философа
function togglePhilosopherConceptDescription(conceptId) {
    const descElement = document.getElementById(`phil-concept-desc-${conceptId}`);
    const toggleBtn = event.target;
    
    if (descElement.classList.contains('show')) {
        descElement.classList.remove('show');
        toggleBtn.classList.remove('expanded');
    } else {
        descElement.classList.add('show');
        toggleBtn.classList.add('expanded');
    }
}

// Переключение всех описаний концепций философа
let allPhilosopherConceptDescriptionsExpanded = false;

function toggleAllPhilosopherConceptDescriptions() {
    const modal = document.getElementById('philosopherDetailModal');
    const descriptions = modal.querySelectorAll('.concept-extended-desc');
    const toggleButtons = modal.querySelectorAll('.toggle-concept-desc-btn');
    const toggleAllBtn = event.target;
    
    allPhilosopherConceptDescriptionsExpanded = !allPhilosopherConceptDescriptionsExpanded;
    
    descriptions.forEach(desc => {
        if (allPhilosopherConceptDescriptionsExpanded) {
            desc.classList.add('show');
        } else {
            desc.classList.remove('show');
        }
    });
    
    toggleButtons.forEach(btn => {
        if (allPhilosopherConceptDescriptionsExpanded) {
            btn.classList.add('expanded');
        } else {
            btn.classList.remove('expanded');
        }
    });
    
    toggleAllBtn.textContent = allPhilosopherConceptDescriptionsExpanded ? 
        '▲ Свернуть все описания концепций' : 
        '▼ Развернуть все описания концепций';
}

// Переключение всех описаний связей в модальном окне философа
let allPhilosopherConnectionDescriptionsExpanded = false;

function toggleAllPhilosopherConnectionDescriptions() {
    const modal = document.getElementById('philosopherDetailModal');
    const descriptions = modal.querySelectorAll('.connection-description');
    const toggleButtons = modal.querySelectorAll('.connection-toggle');
    const toggleAllBtn = event.target;
    
    allPhilosopherConnectionDescriptionsExpanded = !allPhilosopherConnectionDescriptionsExpanded;
    
    descriptions.forEach(desc => {
        if (allPhilosopherConnectionDescriptionsExpanded) {
            desc.classList.add('show');
        } else {
            desc.classList.remove('show');
        }
    });
    
    toggleButtons.forEach(btn => {
        if (allPhilosopherConnectionDescriptionsExpanded) {
            btn.classList.add('expanded');
        } else {
            btn.classList.remove('expanded');
        }
    });
    
    toggleAllBtn.textContent = allPhilosopherConnectionDescriptionsExpanded ? 
        '▲ Свернуть все описания связей' : 
        '▼ Развернуть все описания связей';
}
```

---

## 6-9. Остальные изменения

Пункты 6-9 остаются такими же, как в исправленной версии:
- Добавить обработчик двойного клика в `makeLegendsEditable`
- Модифицировать тег философа в `showDetailModal` для клика
- Обновить обработчики закрытия модальных окон

---

## Ключевые преимущества этого решения

✅ **Избегание дублирования** - общие стили вынесены в `.detail-modal`  
✅ **Единообразие** - оба окна используют одни и те же классы  
✅ **Гибкость** - специфичные стили только для окна философа  
✅ **Легкость поддержки** - изменения в одном месте влияют на оба окна  
✅ **Правильная архитектура** - классы вместо дублирования ID селекторов  

---

## Порядок применения изменений

1. Добавить класс `detail-modal` к окну концепции (строка 1634)
2. Добавить класс `modal-content` к контенту окна концепции (строка 1636)
3. Добавить HTML окна философа (после строки 1637)
4. Заменить CSS стили с ID на классы (строки 489-659)
5. Добавить специфичные стили для окна философа (после общих стилей)
6. Добавить функции окна философа (после строки 4070)
7. Обновить остальные части кода согласно пунктам 6-9
