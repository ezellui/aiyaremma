function generateTensionContent() {
    if (!concepts || !relations) {
        initializePhilosophyMetrics();
    }
    
    const results = nodes.map(n => {
        const metric = tensionIndex(n.id);
        return {
            node: n,
            value: metric.total,
            details: metric,
            dominantType: metric.analytics.dominantType,
            immanent: metric.immanentTension,
            polemical: metric.polemicalTension,
            dialectical: metric.dialecticalTension
        };
    }).filter(r => r.value > 0).sort((a, b) => b.value - a.value);
    
    const typeIcons = {
        'immanent': '🔴',
        'polemical': '⚔️',
        'dialectical': '♦️'
    };
    
    const typeLabels = {
        'immanent': 'Имманентное',
        'polemical': 'Полемическое',
        'dialectical': 'Диалектическое'
    };
    
    let html = `
        <div class="stats-content-header">
            <h2 class="stats-content-title">⚖️ Индекс напряжения</h2>
            <p class="stats-content-subtitle">
                Концепции с наибольшим внутренним напряжением. 
                Напряжение измеряется по трём осям: имманентное (внутренние противоречия), 
                полемическое (конфликтность позиции) и диалектическое (продуктивность противоречия).
            </p>
        </div>
        
        <div class="metric-description-box">
            <div class="metric-description-section">
                <span class="metric-description-label">🔴 Имманентное напряжение</span>
                <div class="metric-description-text">
                    Внутренние противоречия, признанные ограничения, условные зависимости, 
                    опосредования и потребность в дополнении внутри самой концепции.
                </div>
            </div>
            <div class="metric-description-section">
                <span class="metric-description-label">⚔️ Полемическое напряжение</span>
                <div class="metric-description-text">
                    Конфликтность позиции: исходящая и входящая критика, взаимная полемика с другими концепциями.
                </div>
            </div>
            <div class="metric-description-section">
                <span class="metric-description-label">♦️ Диалектическое напряжение</span>
                <div class="metric-description-text">
                    Продуктивность противоречия: нерешённое напряжение, порождённые концепции, 
                    попытки синтеза и развития.
                </div>
            </div>
            <div class="metric-formula">
                Индекс = Имманентное × 1.0 + Полемическое × 0.8 + Диалектическое × 1.2
            </div>
        </div>
        
        <div class="metric-results-grid">
    `;
    
    results.slice(0, 30).forEach((r, index) => {
        const details = r.details;
        const ratio = details.analytics.tensionResolutionRatio;
        const ratioPercent = Math.round(ratio * 100);
        const typeIcon = typeIcons[r.dominantType] || '⚖️';
        const typeLabel = typeLabels[r.dominantType] || 'Смешанное';
        
        // Вычисляем проценты для визуальной шкалы
        const immanentPercent = (r.immanent / r.value * 100).toFixed(1);
        const polemicalPercent = (r.polemical / r.value * 100).toFixed(1);
        const dialecticalPercent = (r.dialectical / r.value * 100).toFixed(1);
        
        html += `
            <div class="metric-result-card tension-card" data-concept-id="${r.node.id}">
                <div class="metric-result-rank">#${index + 1}</div>
                
                <div class="metric-result-name">
                    <span class="tension-type-icon">${typeIcon}</span>
                    ${r.node.label}
                </div>
                
                <div class="metric-result-philosopher">${r.node.concept}</div>
                
                <div class="metric-result-value">${r.value.toFixed(1)}</div>
                
                <div class="tension-breakdown-bar">
                    <div class="tension-segment tension-immanent" 
                         style="width: ${immanentPercent}%"
                         title="Имманентное: ${r.immanent.toFixed(1)}">
                    </div>
                    <div class="tension-segment tension-polemical" 
                         style="width: ${polemicalPercent}%"
                         title="Полемическое: ${r.polemical.toFixed(1)}">
                    </div>
                    <div class="tension-segment tension-dialectical" 
                         style="width: ${dialecticalPercent}%"
                         title="Диалектическое: ${r.dialectical.toFixed(1)}">
                    </div>
                </div>
                
                <div class="metric-result-details">
                    <div class="metric-result-detail-badge tension-badge-immanent">
                        🔴 ${r.immanent.toFixed(1)}
                    </div>
                    <div class="metric-result-detail-badge tension-badge-polemical">
                        ⚔️ ${r.polemical.toFixed(1)}
                    </div>
                    <div class="metric-result-detail-badge tension-badge-dialectical">
                        ♦️ ${r.dialectical.toFixed(1)}
                    </div>
                </div>
                
                <div class="tension-dominant-type">
                    Доминирует: ${typeLabel}
                </div>
                
                ${ratio > 0 ? `
                    <div class="tension-resolution-indicator">
                        <span class="tension-resolution-label">Баланс Н/Р:</span>
                        <span class="tension-resolution-value">${ratioPercent}%</span>
                    </div>
                ` : ''}
                
                ${r.node.description ? `
                    <div class="tension-description">
                        ${r.node.description}
                    </div>
                ` : ''}
            </div>
        `;
    });
    
    html += `</div>`;
    
    // Добавляем обработчик клика для отображения деталей
    setTimeout(() => {
        document.querySelectorAll('.tension-card').forEach(card => {
            card.addEventListener('click', function() {
                const conceptId = this.dataset.conceptId;
                showTensionDetails(conceptId);
            });
        });
    }, 0);
    
    return html;
}

// Функция для отображения детальной информации о напряжении
function showTensionDetails(conceptId) {
    const metric = tensionIndex(conceptId);
    const node = nodes.find(n => n.id === conceptId);
    
    if (!node || !metric) return;
    
    const details = metric.details || metric;
    
    let detailsHTML = `
        <div class="metric-description-box">
            <h3 style="color: #fff; margin-top: 0;">${node.label}</h3>
            <p style="color: rgba(255,255,255,0.6); font-size: 13px; margin-bottom: 20px;">
                ${node.concept} | Общий индекс: ${metric.total.toFixed(2)}
            </p>
            
            <div class="metric-description-section">
                <span class="metric-description-label">🔴 Имманентное напряжение: ${metric.immanentTension.toFixed(2)}</span>
                <div class="metric-description-text">
                    ${details.immanent.internalContradictions > 0 ? `• Внутренние противоречия: ${details.immanent.internalContradictions.toFixed(1)}<br>` : ''}
                    ${details.immanent.acknowledgedLimits > 0 ? `• Признанные ограничения: ${details.immanent.acknowledgedLimits}<br>` : ''}
                    ${details.immanent.conditionalDependencies > 0 ? `• Условные зависимости: ${details.immanent.conditionalDependencies}<br>` : ''}
                    ${details.immanent.mediations > 0 ? `• Опосредования: ${details.immanent.mediations}<br>` : ''}
                    ${details.immanent.complementarityNeeds > 0 ? `• Потребность в дополнении: ${details.immanent.complementarityNeeds}` : ''}
                </div>
            </div>
            
            <div class="metric-description-section">
                <span class="metric-description-label">⚔️ Полемическое напряжение: ${metric.polemicalTension.toFixed(2)}</span>
                <div class="metric-description-text">
                    ${details.polemical.outgoingConflict > 0 ? `• Исходящая критика: ${details.polemical.outgoingConflict.toFixed(1)}<br>` : ''}
                    ${details.polemical.incomingConflict > 0 ? `• Входящая критика: ${details.polemical.incomingConflict.toFixed(1)}<br>` : ''}
                    ${details.polemical.mutualPolemics > 0 ? `• Взаимная полемика: ${details.polemical.mutualPolemics}` : ''}
                </div>
            </div>
            
            <div class="metric-description-section">
                <span class="metric-description-label">♦️ Диалектическое напряжение: ${metric.dialecticalTension.toFixed(2)}</span>
                <div class="metric-description-text">
                    ${details.dialectical.unresolvedTension > 0 ? `• Нерешённое напряжение: ${details.dialectical.unresolvedTension.toFixed(1)}<br>` : ''}
                    ${details.dialectical.syntheses > 0 ? `• Синтезы: ${details.dialectical.syntheses}<br>` : ''}
                    ${details.dialectical.emergentConcepts > 0 ? `• Порождённые концепции: ${details.dialectical.emergentConcepts}<br>` : ''}
                    ${details.dialectical.developments > 0 ? `• Развития: ${details.dialectical.developments}<br>` : ''}
                    ${details.dialectical.culminations > 0 ? `• Кульминации: ${details.dialectical.culminations}` : ''}
                </div>
            </div>
            
            <div class="metric-formula">
                Доминирующий тип: ${details.analytics.dominantType === 'immanent' ? 'Имманентное' : 
                                     details.analytics.dominantType === 'polemical' ? 'Полемическое' : 'Диалектическое'}<br>
                Баланс напряжения/разрешения: ${Math.round(details.analytics.tensionResolutionRatio * 100)}%<br>
                Средняя интенсивность связей: ${details.analytics.averageIntensity.toFixed(2)}
            </div>
        </div>
    `;
    
    // Можно вывести в модальное окно или заменить содержимое
    // Здесь простой alert, но лучше использовать модальное окно
    const detailsContainer = document.createElement('div');
    detailsContainer.innerHTML = detailsHTML;
    
    // Если есть функция показа модального окна, используем её
    // Иначе можно добавить всплывающее окно
    console.log('Детали напряжения для:', node.label, metric);
    
    // Пример: замена содержимого в stats-content-area (если это уместно)
    // или создание модального окна
}