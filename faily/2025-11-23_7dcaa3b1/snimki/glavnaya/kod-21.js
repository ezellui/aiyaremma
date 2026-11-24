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
    
    // Функция для генерации HTML деталей напряжения
    const getTensionDetailsHTML = (item, index) => {
        const r = item;
        const details = r.details;
        const ratio = details.analytics.tensionResolutionRatio;
        const ratioPercent = Math.round(ratio * 100);
        const typeLabel = typeLabels[r.dominantType] || 'Смешанное';
        
        // Вычисляем проценты для визуальной шкалы
        const immanentPercent = (r.immanent / r.value * 100).toFixed(1);
        const polemicalPercent = (r.polemical / r.value * 100).toFixed(1);
        const dialecticalPercent = (r.dialectical / r.value * 100).toFixed(1);
        
        return `
            <div class="metric-detail-panel tension-detail">
                <!-- Визуальная шкала напряжения -->
                <div class="tension-breakdown-section">
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
                    
                    <div class="tension-badges">
                        <div class="tension-badge tension-badge-immanent">
                            🔴 ${r.immanent.toFixed(1)}
                        </div>
                        <div class="tension-badge tension-badge-polemical">
                            ⚔️ ${r.polemical.toFixed(1)}
                        </div>
                        <div class="tension-badge tension-badge-dialectical">
                            ♦️ ${r.dialectical.toFixed(1)}
                        </div>
                    </div>
                </div>
                
                <!-- Имманентное напряжение -->
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
                
                <!-- Полемическое напряжение -->
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
                
                <!-- Диалектическое напряжение -->
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
                
                <!-- Аналитика -->
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
                
                <!-- Описание концепции -->
                ${r.node.description ? 
                    `<div class="metric-concept-description">
                        <strong>О концепции:</strong>
                        <p>${r.node.description}</p>
                    </div>` : ''}
            </div>
        `;
    };
    
    // Используем универсальную функцию generateMetricResults
    return generateMetricResults(
        results.slice(0, 30),
        '⚖️ Индекс напряжения',
        'Концепции с наибольшим внутренним напряжением',
        'tension',
        'value',
        true,
        {
            isComposite: true,
            getDetailsHTML: getTensionDetailsHTML,
            getConceptDescription: (item) => item.node.description
        }
    );
}