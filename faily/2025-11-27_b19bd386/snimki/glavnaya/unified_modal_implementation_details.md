# Детальная реализация функций унифицированной модальной системы

## 1. Функция hasUnsavedChanges()

```javascript
/**
 * Проверка наличия несохраненных изменений в формах редактирования
 * @returns {boolean} - true если есть несохраненные изменения
 */
function hasUnsavedChanges() {
    if (ModalContext.currentMode !== 'edit') {
        return false;
    }
    
    const entityType = ModalContext.currentEntity;
    const originalData = ModalContext.currentData;
    
    // Если это создание новой сущности (нет id), проверяем заполнены ли поля
    if (!originalData || !originalData.id) {
        return hasFilledFields();
    }
    
    // Проверяем изменения в зависимости от типа сущности
    switch(entityType) {
        case 'philosopher':
            return hasPhilosopherChanges(originalData);
        case 'concept':
            return hasConceptChanges(originalData);
        case 'connection':
            return hasConnectionChanges(originalData);
        default:
            return false;
    }
}

/**
 * Проверка заполненности полей при создании новой сущности
 */
function hasFilledFields() {
    const inputs = document.querySelectorAll('#universalModalContent input, #universalModalContent textarea, #universalModalContent select');
    
    for (let input of inputs) {
        if (input.type === 'checkbox' || input.type === 'radio') {
            continue; // Пропускаем чекбоксы и радио
        }
        
        const value = input.value.trim();
        if (value && value.length > 0) {
            return true;
        }
    }
    
    return false;
}

/**
 * Проверка изменений философа
 */
function hasPhilosopherChanges(original) {
    const philosopherData = philosophers.find(p => p.nameRu === original);
    if (!philosopherData) return false;
    
    const nameInput = document.getElementById('philName');
    const colorInput = document.getElementById('philColor');
    const birthInput = document.getElementById('philBirth');
    const deathInput = document.getElementById('philDeath');
    const descInput = document.getElementById('philDescription');
    
    if (!nameInput || !colorInput || !descInput) return false;
    
    const currentName = nameInput.value.trim();
    const currentColor = colorInput.value;
    const currentBirth = birthInput ? parseInt(birthInput.value) : null;
    const currentDeath = deathInput ? parseInt(deathInput.value) : null;
    const currentDesc = descInput.value.trim();
    
    return currentName !== philosopherData.nameRu ||
           currentColor !== philosopherConcepts[original].color ||
           currentBirth !== philosopherData.birth ||
           currentDeath !== philosopherData.death ||
           currentDesc !== philosopherData.description;
}

/**
 * Проверка изменений концепции
 */
function hasConceptChanges(original) {
    const labelInput = document.getElementById('conceptLabel');
    const philInput = document.getElementById('conceptPhilosopher');
    const rubricSelect = document.getElementById('conceptRubric');
    const descInput = document.getElementById('conceptDescription');
    const extDescInput = document.getElementById('conceptExtendedDescription');
    
    if (!labelInput || !philInput || !descInput || !extDescInput) return false;
    
    const currentLabel = labelInput.value.trim();
    const currentPhil = philInput.value;
    const currentRubrics = Array.from(rubricSelect.selectedOptions).map(opt => opt.value);
    const currentDesc = descInput.value.trim();
    const currentExtDesc = extDescInput.value.trim();
    
    const originalRubrics = conceptToRubrics[original.id] || [];
    
    return currentLabel !== original.label ||
           currentPhil !== original.concept ||
           JSON.stringify(currentRubrics.sort()) !== JSON.stringify(originalRubrics.sort()) ||
           currentDesc !== original.description ||
           currentExtDesc !== original.extendedDescription;
}

/**
 * Проверка изменений связи
 */
function hasConnectionChanges(original) {
    const typeInput = document.getElementById('connType');
    const weightInput = document.getElementById('connWeight');
    const biDirInput = document.getElementById('connBidirectional');
    const descInput = document.getElementById('connDescription');
    
    if (!typeInput || !weightInput || !biDirInput) return false;
    
    const currentType = typeInput.value;
    const currentWeight = parseInt(weightInput.value);
    const currentBiDir = biDirInput.checked;
    const currentDesc = descInput ? descInput.value.trim() : '';
    
    const srcChanged = ModalContext.editState.selectedSource !== (original.source.id || original.source);
    const tgtChanged = ModalContext.editState.selectedTarget !== (original.target.id || original.target);
    
    return currentType !== original.type ||
           currentWeight !== original.weight ||
           currentBiDir !== original.bidirectional ||
           currentDesc !== (original.description || '') ||
           srcChanged ||
           tgtChanged;
}
```

---

## 2. Код для добавления в generatePhilosopherViewContent

**Из предыдущей функции `showPhilosopherDetailModal` следует взять:**

### Начало: после строки с `<div class="description">${formattedDescription}</div>`
### Конец: перед строкой `content.innerHTML = html;`

**Конкретно нужно добавить следующий код:**

```javascript
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
        <div class="modal-section-title">
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
                .map(phil => `<span class="philosopher-link" onclick="openUniversalModal('philosopher', '${phil}', 'view');">${phil}</span>`)
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
                .map(phil => `<span class="philosopher-link" onclick="openUniversalModal('philosopher', '${phil}', 'view');">${phil}</span>`)
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
        <div class="modal-section-title">
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
        <div class="modal-section-title">
            💡 Концепции философа (${philosopherConceptsNodes.length})
        </div>
        <button class="toggle-all-descriptions-btn" onclick="toggleAllPhilosopherConceptDescriptions()">
            ▼ Развернуть все описания концепций
        </button>
        <div class="philosopher-concepts-section">
    `;
    
    philosopherConceptsNodes.forEach(conceptNode => {
        html += `
            <div class="concept-details-item" onclick="event.stopPropagation(); openUniversalModal('concept', nodes.find(n => n.id === '${conceptNode.id}'), 'view');">
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
        <div class="modal-section-title">
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
                    <div class="concept-color" style="background: ${philosopherConcepts[philosopherName].color}"></div>
                    <div style="flex-grow: 1; display: flex; align-items: center; gap: 8px;">
                        <span onclick="event.stopPropagation(); openUniversalModal('concept', nodes.find(n => n.id === '${srcNode.id}'), 'view');" style="cursor: pointer;">${srcNode.label}</span>
                        <div class="connection-arrow" style="color: ${linkColor};">
                            ${arrow}
                            <span class="connection-arrow-tooltip">${linkLabel}</span>
                        </div>
                        <span onclick="event.stopPropagation(); openUniversalModal('concept', nodes.find(n => n.id === '${tgtNode.id}'), 'view');" style="cursor: pointer;">${tgtNode.label}</span>
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
                        <span onclick="event.stopPropagation(); openUniversalModal('concept', nodes.find(n => n.id === '${srcNode.id}'), 'view');" style="cursor: pointer;">${srcNode.label}</span>
                        <span style="font-size: 10px; color: #7f8c8d;">(${srcNode.concept})</span>
                        <div class="connection-arrow" style="color: ${linkColor};">
                            ${arrow}
                            <span class="connection-arrow-tooltip">${linkLabel}</span>
                        </div>
                        <span onclick="event.stopPropagation(); openUniversalModal('concept', nodes.find(n => n.id === '${tgtNode.id}'), 'view');" style="cursor: pointer;">${tgtNode.label}</span>
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
```

---

## 3. Код для добавления в generateConceptViewContent

**Из предыдущей функции `showDetailModal` следует взять:**

### Начало: после кнопки "Перейти к узлу"
### Конец: перед строкой `content.innerHTML = html;`

**Конкретно нужно добавить следующий код:**

```javascript
// ========================================
// СЕКЦИЯ СВЯЗЕЙ УЗЛА
// ========================================

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
                    <div style="flex-grow: 1;" onclick="openUniversalModal('concept', nodes.find(n => n.id === '${connectedNode.id}'), 'view');">
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
                    <div style="flex-grow: 1;" onclick="openUniversalModal('concept', nodes.find(n => n.id === '${connectedNode.id}'), 'view');">
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

// ========================================
// СЕКЦИЯ РУБРИК
// ========================================

const conceptRubrics = conceptToRubrics[conceptData.id] || [];

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
                                <div class="concept-item" onclick="openUniversalModal('concept', nodes.find(n => n.id === '${c.id}'), 'view');">
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
```

---

## 4. Функция generateConnectionViewContent

```javascript
/**
 * Генерация контента для просмотра связи
 */
function generateConnectionViewContent(connectionData) {
    // Инициализируем состояние поиска для просмотра связи
    if (!ModalContext.editState.connectionView) {
        ModalContext.editState.connectionView = {
            selectedSource: null,
            selectedTarget: null
        };
    }
    
    let html = `
        <h2>Просмотр связи</h2>
        
        <div class="modal-section-title" style="margin-top: 0;">
            🔍 Поиск узлов
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 25px;">
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
        
        <div id="connectionVisualization" style="min-height: 150px;">
            <div style="text-align: center; color: #95a5a6; padding: 40px; font-size: 13px;">
                Выберите обе концепции для отображения связи
            </div>
        </div>
    `;
    
    return html;
}

/**
 * Обработка поиска концепций для просмотра связи
 */
function handleConnectionViewSearch(type, query) {
    const resultsContainer = document.getElementById(`connView${type.charAt(0).toUpperCase() + type.slice(1)}Results`);
    
    if (!query || query.trim() === '') {
        resultsContainer.classList.remove('show');
        return;
    }
    
    // Определяем, какая концепция уже выбрана
    const otherType = type === 'source' ? 'target' : 'source';
    const otherSelected = ModalContext.editState.connectionView[`selected${otherType.charAt(0).toUpperCase() + otherType.slice(1)}`];
    
    // Фильтруем концепции
    let filteredNodes;
    
    if (otherSelected) {
        // Если другая концепция выбрана, показываем только связанные с ней
        const connectedNodeIds = new Set();
        
        links.forEach(l => {
            const srcId = l.source.id || l.source;
            const tgtId = l.target.id || l.target;
            
            if (srcId === otherSelected) {
                connectedNodeIds.add(tgtId);
            }
            if (tgtId === otherSelected) {
                connectedNodeIds.add(srcId);
            }
        });
        
        filteredNodes = nodes.filter(n => connectedNodeIds.has(n.id));
    } else {
        // Иначе показываем все концепции
        filteredNodes = nodes;
    }
    
    // Применяем поисковый запрос
    const lowerQuery = query.toLowerCase();
    const results = filteredNodes.filter(node => {
        const labelWords = node.label.toLowerCase().split(/\s+/);
        const philosopherWords = node.concept.toLowerCase().split(/\s+/);
        
        const labelMatch = labelWords.some(word => word.startsWith(lowerQuery));
        const philosopherMatch = philosopherWords.some(word => word.startsWith(lowerQuery));
        
        return labelMatch || philosopherMatch;
    }).sort((a, b) => {
        // Сортируем по хронологии философа
        const aOrder = philosopherOrder[a.concept] || 0;
        const bOrder = philosopherOrder[b.concept] || 0;
        
        if (aOrder !== bOrder) {
            return aOrder - bOrder;
        }
        
        return a.label.localeCompare(b.label);
    });
    
    // Отображаем результаты
    if (results.length === 0) {
        resultsContainer.innerHTML = '<div style="padding: 15px; text-align: center; color: #95a5a6; font-size: 11px;">Ничего не найдено</div>';
        resultsContainer.classList.add('show');
        return;
    }
    
    resultsContainer.innerHTML = results.map(node => `
        <div class="modal-concept-search-item" onclick="selectConnectionViewConcept('${type}', '${node.id}')">
            <div style="width: 12px; height: 12px; border-radius: 50%; background: ${philosopherConcepts[node.concept].color}; box-shadow: 0 0 6px currentColor;"></div>
            <div style="flex: 1;">
                <div style="font-weight: 600; color: #e0e0e0; font-size: 13px;">${node.label}</div>
                <div style="font-size: 11px; color: #b0b0b0; font-style: italic;">${node.concept}</div>
            </div>
        </div>
    `).join('');
    
    resultsContainer.classList.add('show');
}

/**
 * Выбор концепции для просмотра связи
 */
function selectConnectionViewConcept(type, conceptId) {
    const conceptData = nodes.find(n => n.id === conceptId);
    if (!conceptData) return;
    
    // Сохраняем выбор
    const capitalizedType = type.charAt(0).toUpperCase() + type.slice(1);
    ModalContext.editState.connectionView[`selected${capitalizedType}`] = conceptId;
    
    // Обновляем отображение выбранной концепции
    const selectedDiv = document.getElementById(`connView${capitalizedType}Selected`);
    const labelSpan = document.getElementById(`connView${capitalizedType}Label`);
    const philSpan = document.getElementById(`connView${capitalizedType}Phil`);
    
    selectedDiv.style.display = 'block';
    labelSpan.textContent = conceptData.label;
    philSpan.textContent = conceptData.concept;
    
    // Скрываем результаты поиска
    const resultsContainer = document.getElementById(`connView${capitalizedType}Results`);
    resultsContainer.classList.remove('show');
    
    // Очищаем поле поиска
    const searchInput = document.getElementById(`connView${capitalizedType}Search`);
    searchInput.value = '';
    
    // Обновляем визуализацию связи
    updateConnectionVisualization();
}

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
    
    // Находим все связи между этими концепциями
    const connections = links.filter(l => {
        const srcId = l.source.id || l.source;
        const tgtId = l.target.id || l.target;
        
        return (srcId === sourceId && tgtId === targetId) || 
               (srcId === targetId && tgtId === sourceId);
    });
    
    const vizContainer = document.getElementById('connectionVisualization');
    
    if (connections.length === 0) {
        vizContainer.innerHTML = `
            <div style="text-align: center; color: #e74c3c; padding: 40px; font-size: 13px;">
                ⚠️ Связь между выбранными концепциями не найдена
            </div>
        `;
        return;
    }
    
    // Генерируем визуализацию для каждой связи
    let html = `<div class="modal-section-title" style="margin-bottom: 15px;">🔗 Найденные связи (${connections.length})</div>`;
    
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
    
    vizContainer.innerHTML = html;
}

// Закрытие результатов поиска при клике вне их (для просмотра связи)
document.addEventListener('click', function(event) {
    const sourceSearch = document.getElementById('connViewSourceSearch');
    const targetSearch = document.getElementById('connViewTargetSearch');
    const sourceResults = document.getElementById('connViewSourceResults');
    const targetResults = document.getElementById('connViewTargetResults');
    
    if (sourceSearch && !sourceSearch.contains(event.target) && 
        !event.target.closest('.modal-concept-search-item')) {
        if (sourceResults) sourceResults.classList.remove('show');
    }
    
    if (targetSearch && !targetSearch.contains(event.target) && 
        !event.target.closest('.modal-concept-search-item')) {
        if (targetResults) targetResults.classList.remove('show');
    }
});
```

---

## 5. Реализация savePhilosopherData()

```javascript
/**
 * Сохранение данных философа
 */
function savePhilosopherData() {
    const name = document.getElementById('philName').value.trim();
    const color = document.getElementById('philColor').value;
    const birthInput = document.getElementById('philBirth');
    const deathInput = document.getElementById('philDeath');
    const birth = birthInput ? (parseInt(birthInput.value) || null) : null;
    const death = deathInput ? (parseInt(deathInput.value) || null) : null;
    const description = document.getElementById('philDescription').value.trim();
    
    // Валидация
    if (!name) {
        alert('Укажите имя философа');
        return;
    }
    
    // Генерируем id (безопасное имя для использования в качестве ключа)
    const id = name.toLowerCase()
        .replace(/\s+/g, '_')
        .replace(/[^a-z0-9_]/g, '');
    
    // Вычисляем years
    let years = '';
    if (birth && death) {
        const birthAbs = Math.abs(birth);
        const deathAbs = Math.abs(death);
        const birthSuffix = birth < 0 ? ' до н.э.' : '';
        const deathSuffix = death < 0 ? ' до н.э.' : '';
        years = `${birthAbs}${birthSuffix}-${deathAbs}${deathSuffix}`;
    } else if (birth) {
        const birthAbs = Math.abs(birth);
        const birthSuffix = birth < 0 ? ' до н.э.' : '';
        years = `${birthAbs}${birthSuffix}-?`;
    }
    
    const originalName = ModalContext.currentData; // это имя философа или null
    const isNew = !originalName || !philosophers.find(p => p.nameRu === originalName);
    
    if (isNew) {
        // Создаем нового философа
        
        // Проверяем, не существует ли уже философ с таким именем
        if (philosophers.find(p => p.nameRu === name)) {
            alert('Философ с таким именем уже существует');
            return;
        }
        
        const newPhilosopher = {
            id: id,
            name: name,
            nameRu: name,
            color: color,
            birth: birth,
            death: death,
            years: years,
            description: description
        };
        
        philosophers.push(newPhilosopher);
        
        // Обновляем philosopherConcepts
        philosopherConcepts[name] = {
            name: name,
            color: color,
            years: years,
            birth: birth,
            death: death
        };
        
        // Обновляем philosopherOrder
        philosopherOrder[name] = birth || 0;
        
        console.log('Создан новый философ:', newPhilosopher);
        
    } else {
        // Редактируем существующего философа
        
        const philosopherIndex = philosophers.findIndex(p => p.nameRu === originalName);
        if (philosopherIndex === -1) {
            alert('Философ не найден');
            return;
        }
        
        const oldName = originalName;
        const nameChanged = name !== oldName;
        
        // Обновляем данные философа
        philosophers[philosopherIndex] = {
            ...philosophers[philosopherIndex],
            nameRu: name,
            name: name,
            color: color,
            birth: birth,
            death: death,
            years: years,
            description: description
        };
        
        // Обновляем philosopherConcepts
        if (nameChanged) {
            // Удаляем старую запись
            delete philosopherConcepts[oldName];
        }
        
        philosopherConcepts[name] = {
            name: name,
            color: color,
            years: years,
            birth: birth,
            death: death
        };
        
        // Обновляем philosopherOrder
        if (nameChanged) {
            delete philosopherOrder[oldName];
        }
        philosopherOrder[name] = birth || 0;
        
        // Если имя изменилось, обновляем ссылки в концепциях
        if (nameChanged) {
            nodes.forEach(node => {
                if (node.concept === oldName) {
                    node.concept = name;
                }
            });
            
            concepts.forEach(concept => {
                // Находим соответствующего философа по старому имени
                const phil = philosophers.find(p => p.nameRu === oldName);
                if (phil && concept.philosopher === phil.id) {
                    // Обновляем id философа (если нужно)
                    concept.philosopher = id;
                }
            });
        }
        
        console.log('Обновлен философ:', philosophers[philosopherIndex]);
    }
    
    // Обновляем фильтры в легенде
    initFilters();
    setTimeout(makeLegendsEditable, 100);
    
    // Обновляем граф (перерисовываем узлы с новыми цветами)
    node.selectAll('circle')
        .attr('fill', d => philosopherConcepts[d.concept].color);
    
    // Закрываем окно и переходим в режим просмотра
    openUniversalModal('philosopher', name, 'view');
}
```

---

## 6. Реализация saveConceptData()

```javascript
/**
 * Сохранение данных концепции
 */
function saveConceptData() {
    const label = document.getElementById('conceptLabel').value.trim();
    const philosopher = document.getElementById('conceptPhilosopher').value;
    const rubricSelect = document.getElementById('conceptRubric');
    const selectedRubrics = Array.from(rubricSelect.selectedOptions).map(opt => opt.value);
    const description = document.getElementById('conceptDescription').value.trim();
    const extendedDescription = document.getElementById('conceptExtendedDescription').value.trim();
    
    // Валидация
    if (!label || !philosopher) {
        alert('Укажите название концепции и философа');
        return;
    }
    
    const originalData = ModalContext.currentData;
    const isNew = !originalData || !originalData.id;
    
    if (isNew) {
        // Создаем новую концепцию
        
        // Генерируем уникальный id
        const id = `concept_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        // Находим id философа
        const philosopherData = philosophers.find(p => p.nameRu === philosopher);
        if (!philosopherData) {
            alert('Философ не найден');
            return;
        }
        
        const newConcept = {
            id: id,
            label: label,
            philosopher: philosopherData.id,
            rubrics: selectedRubrics,
            description: description,
            extendedDescription: extendedDescription
        };
        
        const newNode = {
            id: id,
            label: label,
            concept: philosopher,
            rubrics: selectedRubrics,
            description: description,
            extendedDescription: extendedDescription
        };
        
        concepts.push(newConcept);
        nodes.push(newNode);
        
        // Обновляем conceptToRubrics
        conceptToRubrics[id] = selectedRubrics;
        
        console.log('Создана новая концепция:', newConcept);
        
        // Добавляем узел на граф
        addNodeToGraph(newNode);
        
    } else {
        // Редактируем существующую концепцию
        
        const conceptIndex = concepts.findIndex(c => c.id === originalData.id);
        const nodeIndex = nodes.findIndex(n => n.id === originalData.id);
        
        if (conceptIndex === -1 || nodeIndex === -1) {
            alert('Концепция не найдена');
            return;
        }
        
        // Находим id философа
        const philosopherData = philosophers.find(p => p.nameRu === philosopher);
        if (!philosopherData) {
            alert('Философ не найден');
            return;
        }
        
        // Обновляем данные концепции
        concepts[conceptIndex] = {
            ...concepts[conceptIndex],
            label: label,
            philosopher: philosopherData.id,
            rubrics: selectedRubrics,
            description: description,
            extendedDescription: extendedDescription
        };
        
        nodes[nodeIndex] = {
            ...nodes[nodeIndex],
            label: label,
            concept: philosopher,
            rubrics: selectedRubrics,
            description: description,
            extendedDescription: extendedDescription
        };
        
        // Обновляем conceptToRubrics
        conceptToRubrics[originalData.id] = selectedRubrics;
        
        console.log('Обновлена концепция:', concepts[conceptIndex]);
        
        // Обновляем узел на графе
        updateNodeOnGraph(nodes[nodeIndex]);
    }
    
    // Закрываем окно
    closeUniversalModal();
}

/**
 * Добавление нового узла на граф
 */
function addNodeToGraph(nodeData) {
    // Добавляем к данным симуляции
    simulation.nodes().push(nodeData);
    
    // Создаем новый визуальный элемент
    const newNodeGroup = g.select('g:nth-child(2)') // Группа узлов
        .append('g')
        .datum(nodeData)
        .attr('class', 'node')
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));
    
    newNodeGroup.append('circle')
        .attr('r', 18)
        .attr('fill', philosopherConcepts[nodeData.concept].color)
        .attr('stroke', '#fff');
    
    newNodeGroup.append('text')
        .attr('dy', -25)
        .attr('text-anchor', 'middle')
        .text(nodeData.label);
    
    // Обновляем выборку node
    node = g.selectAll('.node');
    
    // Инициализируем обработчики для нового узла
    newNodeGroup.on('click', handleNodeClick);
    
    // Перезапускаем симуляцию
    simulation.alpha(0.3).restart();
    
    // Обновляем фильтры
    updateFilterStats();
}

/**
 * Обновление существующего узла на графе
 */
function updateNodeOnGraph(nodeData) {
    // Обновляем текст и цвет
    node.filter(d => d.id === nodeData.id)
        .select('text')
        .text(nodeData.label);
    
    node.filter(d => d.id === nodeData.id)
        .select('circle')
        .attr('fill', philosopherConcepts[nodeData.concept].color);
    
    // Обновляем данные в симуляции
    const simNode = simulation.nodes().find(n => n.id === nodeData.id);
    if (simNode) {
        Object.assign(simNode, nodeData);
    }
}
```

---

## 7. Реализация saveConnectionData()

```javascript
/**
 * Сохранение данных связи
 */
function saveConnectionData() {
    const type = document.getElementById('connType').value;
    const weight = parseInt(document.getElementById('connWeight').value);
    const bidirectional = document.getElementById('connBidirectional').checked;
    const description = document.getElementById('connDescription').value.trim();
    
    // Получаем выбранные концепции из ModalContext.editState
    const source = ModalContext.editState.selectedSource;
    const target = ModalContext.editState.selectedTarget;
    
    // Валидация
    if (!type) {
        alert('Укажите тип связи');
        return;
    }
    
    if (!source || !target) {
        alert('Выберите обе концепции');
        return;
    }
    
    if (source === target) {
        alert('Нельзя создать связь концепции с самой собой');
        return;
    }
    
    const originalData = ModalContext.currentData;
    const isNew = !originalData || (!originalData.source && !originalData.target);
    
    if (isNew) {
        // Создаем новую связь
        
        // Проверяем, не существует ли уже такая связь
        const existingLink = links.find(l => {
            const srcId = l.source.id || l.source;
            const tgtId = l.target.id || l.target;
            return (srcId === source && tgtId === target) || 
                   (srcId === target && tgtId === source);
        });
        
        if (existingLink) {
            const overwrite = confirm('Связь между этими концепциями уже существует. Заменить её?');
            if (!overwrite) return;
            
            // Удаляем старую связь
            const linkIndex = links.indexOf(existingLink);
            const connIndex = connections.findIndex(c => 
                c.from === (existingLink.source.id || existingLink.source) && 
                c.to === (existingLink.target.id || existingLink.target)
            );
            
            if (linkIndex !== -1) links.splice(linkIndex, 1);
            if (connIndex !== -1) connections.splice(connIndex, 1);
            
            // Удаляем визуальный элемент
            link.filter(d => d === existingLink).remove();
        }
        
        const newConnection = {
            from: source,
            to: target,
            type: type,
            weight: weight,
            bidirectional: bidirectional,
            description: description
        };
        
        const newLink = {
            source: source,
            target: target,
            type: type,
            weight: weight,
            bidirectional: bidirectional,
            description: description
        };
        
        connections.push(newConnection);
        links.push(newLink);
        
        console.log('Создана новая связь:', newConnection);
        
        // Добавляем связь на граф
        addLinkToGraph(newLink);
        
    } else {
        // Редактируем существующую связь
        
        const originalSrcId = originalData.source.id || originalData.source;
        const originalTgtId = originalData.target.id || originalData.target;
        
        const linkIndex = links.findIndex(l => {
            const srcId = l.source.id || l.source;
            const tgtId = l.target.id || l.target;
            return srcId === originalSrcId && tgtId === originalTgtId;
        });
        
        const connIndex = connections.findIndex(c => 
            c.from === originalSrcId && c.to === originalTgtId
        );
        
        if (linkIndex === -1 || connIndex === -1) {
            alert('Связь не найдена');
            return;
        }
        
        // Обновляем данные связи
        connections[connIndex] = {
            ...connections[connIndex],
            from: source,
            to: target,
            type: type,
            weight: weight,
            bidirectional: bidirectional,
            description: description
        };
        
        links[linkIndex] = {
            ...links[linkIndex],
            source: source,
            target: target,
            type: type,
            weight: weight,
            bidirectional: bidirectional,
            description: description
        };
        
        console.log('Обновлена связь:', connections[connIndex]);
        
        // Обновляем связь на графе
        updateLinkOnGraph(links[linkIndex]);
    }
    
    // Закрываем окно
    closeUniversalModal();
}

/**
 * Добавление новой связи на граф
 */
function addLinkToGraph(linkData) {
    // Находим узлы для связи
    const sourceNode = simulation.nodes().find(n => n.id === linkData.source);
    const targetNode = simulation.nodes().find(n => n.id === linkData.target);
    
    if (!sourceNode || !targetNode) {
        console.error('Не найдены узлы для связи');
        return;
    }
    
    // Заменяем ID на объекты узлов (для D3 симуляции)
    linkData.source = sourceNode;
    linkData.target = targetNode;
    
    // Добавляем к данным симуляции
    simulation.force('link').links().push(linkData);
    
    // Создаем новый визуальный элемент
    const linkGroup = g.select('g:nth-child(1)'); // Группа связей
    
    let classes = 'link';
    if (linkData.bidirectional) classes += ' bidirectional';
    if (linkData.type === 'internal_contradiction') classes += ' internal-contradiction';
    if (linkData.weight === 1) classes += ' weight-weak';
    else if (linkData.weight === 2) classes += ' weight-medium';
    else if (linkData.weight === 3) classes += ' weight-strong';
    
    const newLink = linkGroup.append('path')
        .datum(linkData)
        .attr('class', classes)
        .attr('stroke', relationTypesObj[linkData.type].color)
        .attr('marker-end', `url(#arrow-${linkData.type})`)
        .style('cursor', 'pointer');
    
    // Обновляем выборку link
    link = g.selectAll('.link');
    
    // Инициализируем обработчики для новой связи
    newLink.on('click', handleLinkClick);
    newLink.on('mouseover', function(event, d) {
        // Tooltip обработчик
    });
    
    // Перезапускаем симуляцию
    simulation.alpha(0.3).restart();
    
    // Обновляем фильтры
    updateFilterStats();
}

/**
 * Обновление существующей связи на графе
 */
function updateLinkOnGraph(linkData) {
    const srcId = linkData.source.id || linkData.source;
    const tgtId = linkData.target.id || linkData.target;
    
    // Находим и обновляем визуальный элемент
    link.filter(d => {
        const dSrcId = d.source.id || d.source;
        const dTgtId = d.target.id || d.target;
        return dSrcId === srcId && dTgtId === tgtId;
    })
    .attr('stroke', relationTypesObj[linkData.type].color)
    .attr('marker-end', `url(#arrow-${linkData.type})`)
    .attr('class', function() {
        let classes = 'link';
        if (linkData.bidirectional) classes += ' bidirectional';
        if (linkData.type === 'internal_contradiction') classes += ' internal-contradiction';
        if (linkData.weight === 1) classes += ' weight-weak';
        else if (linkData.weight === 2) classes += ' weight-medium';
        else if (linkData.weight === 3) classes += ' weight-strong';
        return classes;
    });
    
    // Обновляем данные в симуляции
    const simLink = simulation.force('link').links().find(l => {
        const lSrcId = l.source.id || l.source;
        const lTgtId = l.target.id || l.target;
        return lSrcId === srcId && lTgtId === tgtId;
    });
    
    if (simLink) {
        Object.assign(simLink, linkData);
    }
}
```

---

## Дополнительные замечания

### Инициализация ModalContext.editState

При открытии модального окна для редактирования связи нужно инициализировать `editState`:

```javascript
// В функции openUniversalModal, перед генерацией контента
if (entityType === 'connection' && mode === 'edit') {
    ModalContext.editState.selectedSource = data?.source?.id || data?.source || null;
    ModalContext.editState.selectedTarget = data?.target?.id || data?.target || null;
}
```

### Обработка поиска концепций в режиме редактирования связи

В функции `generateConnectionEditContent` нужно добавить инициализацию обработчиков поиска после отрисовки:

```javascript
// После установки content.innerHTML = html
setTimeout(() => {
    const sourceInput = document.getElementById('connSourceSearch');
    const targetInput = document.getElementById('connTargetSearch');
    
    if (sourceInput) {
        sourceInput.addEventListener('input', (e) => handleConnectionEditSearch('source', e.target.value));
        sourceInput.addEventListener('focus', (e) => handleConnectionEditSearch('source', e.target.value));
    }
    
    if (targetInput) {
        targetInput.addEventListener('input', (e) => handleConnectionEditSearch('target', e.target.value));
        targetInput.addEventListener('focus', (e) => handleConnectionEditSearch('target', e.target.value));
    }
}, 0);
```

### Функция handleConnectionEditSearch

Аналогична `handleConnectionViewSearch`, но с сохранением выбора в `ModalContext.editState`:

```javascript
function handleConnectionEditSearch(type, query) {
    // Аналогично handleConnectionViewSearch
    // Но вместо ModalContext.editState.connectionView
    // используем ModalContext.editState напрямую
}
```
