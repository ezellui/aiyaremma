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
    
    // Получаем описание метрики
    const metricInfo = getMetricDescription('tension');
    
    let html = `
        <div class="stats-content-header">
            <h2 class="stats-content-title">⚖️ ${metricInfo.name}</h2>
            <p class="stats-content-subtitle">${metricInfo.description}</p>
        </div>
        
        <div class="metric-description-box">
            <div class="metric-description-section">
                <span class="metric-description-label">Интерпретация</span>
                <div class="metric-description-text">${metricInfo.interpretation}</div>
            </div>
            <div class="metric-description-section">
                <span class="metric-description-label">Применение</span>
                <div class="metric-description-text">${metricInfo.usage}</div>
            </div>
            <div class="metric-formula">${metricInfo.formula}</div>
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
                
                <div class="tension-summary">
                    <span class="tension-expand-hint">▼ Нажмите для деталей</span>
                </div>
                
                <div class="tension-detail-panel" style="display: none;">
                    <div class="tension-detail-section">
                        <h4 class="tension-detail-title">🔴 Имманентное напряжение: ${r.immanent.toFixed(1)}</h4>
                        <div class="tension-detail-list">
                            ${details.immanent.internalContradictions > 0 ? 
                                `<div class="tension-detail-item">
                                    <span class="tension-detail-label">Внутренние противоречия:</span>
                                    <span class="tension-detail-value">${details.immanent.internalContradictions.toFixed(1)}</span>
                                </div>` : ''}
                            ${details.immanent.acknowledgedLimits > 0 ? 
                                `<div class="tension-detail-item">
                                    <span class="tension-detail-label">Признанные ограничения:</span>
                                    <span class="tension-detail-value">${details.immanent.acknowledgedLimits}</span>
                                </div>` : ''}
                            ${details.immanent.conditionalDependencies > 0 ? 
                                `<div class="tension-detail-item">
                                    <span class="tension-detail-label">Условные зависимости:</span>
                                    <span class="tension-detail-value">${details.immanent.conditionalDependencies}</span>
                                </div>` : ''}
                            ${details.immanent.mediations > 0 ? 
                                `<div class="tension-detail-item">
                                    <span class="tension-detail-label">Опосредования:</span>
                                    <span class="tension-detail-value">${details.immanent.mediations}</span>
                                </div>` : ''}
                            ${details.immanent.complementarityNeeds > 0 ? 
                                `<div class="tension-detail-item">
                                    <span class="tension-detail-label">Потребность в дополнении:</span>
                                    <span class="tension-detail-value">${details.immanent.complementarityNeeds}</span>
                                </div>` : ''}
                        </div>
                    </div>
                    
                    <div class="tension-detail-section">
                        <h4 class="tension-detail-title">⚔️ Полемическое напряжение: ${r.polemical.toFixed(1)}</h4>
                        <div class="tension-detail-list">
                            ${details.polemical.outgoingConflict > 0 ? 
                                `<div class="tension-detail-item">
                                    <span class="tension-detail-label">Исходящая критика:</span>
                                    <span class="tension-detail-value">${details.polemical.outgoingConflict.toFixed(1)}</span>
                                </div>` : ''}
                            ${details.polemical.incomingConflict > 0 ? 
                                `<div class="tension-detail-item">
                                    <span class="tension-detail-label">Входящая критика:</span>
                                    <span class="tension-detail-value">${details.polemical.incomingConflict.toFixed(1)}</span>
                                </div>` : ''}
                            ${details.polemical.mutualPolemics > 0 ? 
                                `<div class="tension-detail-item">
                                    <span class="tension-detail-label">Взаимная полемика:</span>
                                    <span class="tension-detail-value">${details.polemical.mutualPolemics}</span>
                                </div>` : ''}
                        </div>
                    </div>
                    
                    <div class="tension-detail-section">
                        <h4 class="tension-detail-title">♦️ Диалектическое напряжение: ${r.dialectical.toFixed(1)}</h4>
                        <div class="tension-detail-list">
                            ${details.dialectical.unresolvedTension > 0 ? 
                                `<div class="tension-detail-item">
                                    <span class="tension-detail-label">Нерешённое напряжение:</span>
                                    <span class="tension-detail-value">${details.dialectical.unresolvedTension.toFixed(1)}</span>
                                </div>` : ''}
                            ${details.dialectical.syntheses > 0 ? 
                                `<div class="tension-detail-item">
                                    <span class="tension-detail-label">Синтезы:</span>
                                    <span class="tension-detail-value">${details.dialectical.syntheses}</span>
                                </div>` : ''}
                            ${details.dialectical.emergentConcepts > 0 ? 
                                `<div class="tension-detail-item">
                                    <span class="tension-detail-label">Порождённые концепции:</span>
                                    <span class="tension-detail-value">${details.dialectical.emergentConcepts}</span>
                                </div>` : ''}
                            ${details.dialectical.developments > 0 ? 
                                `<div class="tension-detail-item">
                                    <span class="tension-detail-label">Развития:</span>
                                    <span class="tension-detail-value">${details.dialectical.developments}</span>
                                </div>` : ''}
                            ${details.dialectical.culminations > 0 ? 
                                `<div class="tension-detail-item">
                                    <span class="tension-detail-label">Кульминации:</span>
                                    <span class="tension-detail-value">${details.dialectical.culminations}</span>
                                </div>` : ''}
                        </div>
                    </div>
                    
                    <div class="tension-analytics-section">
                        <div class="tension-analytics-item">
                            <span class="tension-analytics-label">Доминирующий тип:</span>
                            <span class="tension-analytics-value">${typeLabel}</span>
                        </div>
                        <div class="tension-analytics-item">
                            <span class="tension-analytics-label">Баланс Н/Р:</span>
                            <span class="tension-analytics-value">${ratioPercent}%</span>
                        </div>
                        <div class="tension-analytics-item">
                            <span class="tension-analytics-label">Средняя интенсивность:</span>
                            <span class="tension-analytics-value">${details.analytics.averageIntensity.toFixed(2)}</span>
                        </div>
                    </div>
                    
                    ${r.node.description ? 
                        `<div class="tension-concept-description">
                            <strong>О концепции:</strong> ${r.node.description}
                        </div>` : ''}
                </div>
            </div>
        `;
    });
    
    html += `</div>`;
    
    // Добавляем обработчик раскрытия/скрытия деталей
    setTimeout(() => {
        document.querySelectorAll('.tension-card').forEach(card => {
            card.addEventListener('click', function(e) {
                // Не раскрываем, если клик был на ссылке или кнопке
                if (e.target.closest('a, button')) return;
                
                const panel = this.querySelector('.tension-detail-panel');
                const hint = this.querySelector('.tension-expand-hint');
                
                if (panel.style.display === 'none') {
                    panel.style.display = 'block';
                    hint.textContent = '▲ Скрыть детали';
                    this.classList.add('expanded');
                } else {
                    panel.style.display = 'none';
                    hint.textContent = '▼ Нажмите для деталей';
                    this.classList.remove('expanded');
                }
            });
        });
    }, 0);
    
    return html;
}