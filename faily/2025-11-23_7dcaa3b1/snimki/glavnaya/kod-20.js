/**
 * Универсальная функция для генерации результатов метрик
 * @param {Array} data - массив данных результатов
 * @param {string} title - заголовок метрики
 * @param {string} description - описание метрики
 * @param {string} metricKey - ключ метрики для descriptions
 * @param {string} valueKey - ключ для значения в объекте данных
 * @param {boolean} isDecimal - форматировать ли как десятичное
 * @param {Object} options - дополнительные опции
 * @param {boolean} options.isComposite - составная ли метрика (с подхарактеристиками)
 * @param {Function} options.getDetailsHTML - функция для генерации HTML деталей
 * @param {Function} options.getConceptDescription - функция для получения описания концепции
 */
function generateMetricResults(data, title, description, metricKey, valueKey, isDecimal, options = {}) {
    const {
        isComposite = false,
        getDetailsHTML = null,
        getConceptDescription = (item) => item.node.description || null
    } = options;
    
    if (!data || data.length === 0) {
        return `
            <div class="stats-content-header">
                <h3 class="stats-content-title">${title}</h3>
                <p class="stats-content-subtitle">${description}</p>
                
                <div class="stats-content-actions">
                    <button class="stats-action-btn secondary" 
                            id="visualize-btn-${metricKey}"
                            onclick="toggleMetricVisualization('${metricKey}')">
                        <span id="visualize-icon-${metricKey}">📏</span>
                        <span id="visualize-text-${metricKey}">Визуализировать размером</span>
                    </button>
                </div>
            </div>
            
            ${generateMetricDescriptionBlock(metricKey)}
            
            <div class="empty-state">
                <div class="empty-state-icon">📊</div>
                <div class="empty-state-text">Нет данных для отображения</div>
            </div>
        `;
    }
    
    return `
        <div class="stats-content-header">
            <h3 class="stats-content-title">${title}</h3>
            <p class="stats-content-subtitle">${description}</p>
            
            <div class="stats-content-actions">
                <button class="stats-action-btn secondary" 
                        id="visualize-btn-${metricKey}"
                        onclick="toggleMetricVisualization('${metricKey}')">
                    <span id="visualize-icon-${metricKey}">📏</span>
                    <span id="visualize-text-${metricKey}">Визуализировать размером</span>
                </button>
            </div>
        </div>
        
        ${generateMetricDescriptionBlock(metricKey)}
        
        <div class="metric-results-grid">
            ${data.map((item, index) => {
                const value = item[valueKey];
                const displayValue = isDecimal ? value.toFixed(4) : Math.round(value);
                const conceptDesc = getConceptDescription(item);
                const hasDetails = isComposite || conceptDesc;
                
                // Генерируем HTML для деталей
                let detailsHTML = '';
                if (hasDetails) {
                    if (isComposite && getDetailsHTML) {
                        // Составная метрика - показываем подхарактеристики + описание
                        detailsHTML = getDetailsHTML(item, index);
                    } else if (conceptDesc) {
                        // Простая метрика - только описание концепции
                        detailsHTML = `
                            <div class="metric-detail-panel simple-detail">
                                <div class="metric-concept-description">
                                    <strong>О концепции:</strong>
                                    <p>${conceptDesc}</p>
                                </div>
                            </div>
                        `;
                    }
                }
                
                return `
                    <div class="metric-result-card ${hasDetails ? 'has-details' : ''}" 
                         data-concept-id="${item.node.id}"
                         onclick="highlightNodeById('${item.node.id}')">
                        <div class="metric-result-rank">#${index + 1}</div>
                        <div class="metric-result-name">${item.node.label}</div>
                        <div class="metric-result-value">${displayValue}</div>
                        <div class="metric-result-philosopher">${item.node.concept}</div>
                        
                        ${hasDetails ? `
                            <button class="metric-expand-btn" 
                                    onclick="event.stopPropagation(); toggleMetricDetails(this);"
                                    title="Показать детали">
                                <span class="expand-icon">▼</span>
                            </button>
                        ` : ''}
                        
                        ${hasDetails ? detailsHTML : ''}
                    </div>
                `;
            }).join('')}
        </div>
    `;
}

/**
 * Функция для переключения видимости деталей метрики
 */
function toggleMetricDetails(button) {
    const card = button.closest('.metric-result-card');
    const panel = card.querySelector('.metric-detail-panel');
    const icon = button.querySelector('.expand-icon');
    
    if (!panel) return;
    
    const isExpanded = card.classList.contains('expanded');
    
    if (isExpanded) {
        // Сворачиваем
        panel.style.display = 'none';
        icon.textContent = '▼';
        card.classList.remove('expanded');
    } else {
        // Разворачиваем
        panel.style.display = 'block';
        icon.textContent = '▲';
        card.classList.add('expanded');
    }
}