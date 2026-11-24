/**
 * Обработка поиска концепций для редактирования связи
 */
function handleConnectionEditSearch(type, query) {
    const resultsContainer = document.getElementById(`conn${type.charAt(0).toUpperCase() + type.slice(1)}Results`);
    
    if (!query || query.trim() === '') {
        resultsContainer.classList.remove('show');
        return;
    }
    
    // Определяем, какая концепция уже выбрана
    const otherType = type === 'source' ? 'target' : 'source';
    const otherSelected = ModalContext.editState[`selected${otherType.charAt(0).toUpperCase() + otherType.slice(1)}`];
    
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
        <div class="modal-concept-search-item" onclick="selectConnectionEditConcept('${type}', '${node.id}')">
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
 * Выбор концепции для редактирования связи
 */
function selectConnectionEditConcept(type, conceptId) {
    const conceptData = nodes.find(n => n.id === conceptId);
    if (!conceptData) return;
    
    // Сохраняем выбор
    const capitalizedType = type.charAt(0).toUpperCase() + type.slice(1);
    ModalContext.editState[`selected${capitalizedType}`] = conceptId;
    
    // Обновляем отображение выбранной концепции
    const selectedDiv = document.getElementById(`conn${capitalizedType}Selected`);
    const labelSpan = document.getElementById(`conn${capitalizedType}Label`);
    const philSpan = document.getElementById(`conn${capitalizedType}Phil`);
    
    selectedDiv.style.display = 'block';
    labelSpan.textContent = conceptData.label;
    philSpan.textContent = conceptData.concept;
    
    // Скрываем результаты поиска
    const resultsContainer = document.getElementById(`conn${capitalizedType}Results`);
    resultsContainer.classList.remove('show');
    
    // Очищаем поле поиска
    const searchInput = document.getElementById(`conn${capitalizedType}Search`);
    searchInput.value = '';
}

/**
 * Обработчик для закрытия результатов поиска при клике вне
 * (для режима редактирования связи)
 */
function setupConnectionEditSearchHandlers() {
    document.addEventListener('click', function(event) {
        const sourceSearch = document.getElementById('connSourceSearch');
        const targetSearch = document.getElementById('connTargetSearch');
        const sourceResults = document.getElementById('connSourceResults');
        const targetResults = document.getElementById('connTargetResults');
        
        if (sourceSearch && !sourceSearch.contains(event.target) && 
            !event.target.closest('.modal-concept-search-item')) {
            if (sourceResults) sourceResults.classList.remove('show');
        }
        
        if (targetSearch && !targetSearch.contains(event.target) && 
            !event.target.closest('.modal-concept-search-item')) {
            if (targetResults) targetResults.classList.remove('show');
        }
    });
}