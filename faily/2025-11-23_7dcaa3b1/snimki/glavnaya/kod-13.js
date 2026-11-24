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
    
    let html = `
        <div class="metric-header">
            <h2>⚖️ Индекс напряжения</h2>
            <p class="metric-description">Концепции с наибольшим внутренним напряжением</p>
        </div>
        <div class="metric-results">
    `;
    
    results.slice(0, 30).forEach((r, index) => {
        const details = r.details;
        const typeIcon = {
            'immanent': '🔴',
            'polemical': '⚔️',
            'dialectical': '♦️'
        }[r.dominantType] || '⚖️';
        
        html += `
            <div class="metric-item tension-item collapsible" data-id="${r.node.id}">
                <div class="metric-rank">${index + 1}</div>
                <div class="metric-content">
                    <div class="metric-main clickable">
                        <span class="metric-icon">${typeIcon}</span>
                        <span class="concept-label">${r.node.label}</span>
                        <span class="philosopher-name">${r.node.concept}</span>
                        <span class="metric-value">${r.value.toFixed(1)}</span>
                        <span class="expand-icon">▼</span>
                    </div>
                    
                    <div class="tension-detail-panel" style="display: none;">
                        <div class="detail-section">
                            <h4>🔴 Имманентное напряжение: ${r.immanent.toFixed(1)}</h4>
                            <ul>
                                ${details.immanent.internalContradictions > 0 ? `<li>Внутренние противоречия: ${details.immanent.internalContradictions.toFixed(1)}</li>` : ''}
                                ${details.immanent.acknowledgedLimits > 0 ? `<li>Признанные ограничения: ${details.immanent.acknowledgedLimits}</li>` : ''}
                                ${details.immanent.conditionalDependencies > 0 ? `<li>Условные зависимости: ${details.immanent.conditionalDependencies}</li>` : ''}
                                ${details.immanent.mediations > 0 ? `<li>Опосредования: ${details.immanent.mediations}</li>` : ''}
                                ${details.immanent.complementarityNeeds > 0 ? `<li>Потребность в дополнении: ${details.immanent.complementarityNeeds}</li>` : ''}
                            </ul>
                        </div>
                        
                        <div class="detail-section">
                            <h4>⚔️ Полемическое напряжение: ${r.polemical.toFixed(1)}</h4>
                            <ul>
                                ${details.polemical.outgoingConflict > 0 ? `<li>Исходящая критика: ${details.polemical.outgoingConflict.toFixed(1)}</li>` : ''}
                                ${details.polemical.incomingConflict > 0 ? `<li>Входящая критика: ${details.polemical.incomingConflict.toFixed(1)}</li>` : ''}
                                ${details.polemical.mutualPolemics > 0 ? `<li>Взаимная полемика: ${details.polemical.mutualPolemics}</li>` : ''}
                            </ul>
                        </div>
                        
                        <div class="detail-section">
                            <h4>♦️ Диалектическое напряжение: ${r.dialectical.toFixed(1)}</h4>
                            <ul>
                                ${details.dialectical.unresolvedTension > 0 ? `<li>Нерешённое напряжение: ${details.dialectical.unresolvedTension.toFixed(1)}</li>` : ''}
                                ${details.dialectical.syntheses > 0 ? `<li>Синтезы: ${details.dialectical.syntheses}</li>` : ''}
                                ${details.dialectical.emergentConcepts > 0 ? `<li>Порождённые концепции: ${details.dialectical.emergentConcepts}</li>` : ''}
                                ${details.dialectical.developments > 0 ? `<li>Развития: ${details.dialectical.developments}</li>` : ''}
                            </ul>
                            <p class="analytics-info">
                                Баланс напряжения/разрешения: ${Math.round(details.analytics.tensionResolutionRatio * 100)}%
                                <br>Средняя интенсивность: ${details.analytics.averageIntensity.toFixed(1)}
                            </p>
                        </div>
                        
                        ${r.node.description ? `<div class="concept-description">${r.node.description}</div>` : ''}
                    </div>
                </div>
            </div>
        `;
    });
    
    html += `</div>`;
    
    // Добавляем обработчик раскрытия/скрытия деталей
    setTimeout(() => {
        document.querySelectorAll('.tension-item .metric-main.clickable').forEach(item => {
            item.addEventListener('click', function() {
                const panel = this.nextElementSibling;
                const icon = this.querySelector('.expand-icon');
                
                if (panel.style.display === 'none') {
                    panel.style.display = 'block';
                    icon.textContent = '▲';
                    this.parentElement.parentElement.classList.add('expanded');
                } else {
                    panel.style.display = 'none';
                    icon.textContent = '▼';
                    this.parentElement.parentElement.classList.remove('expanded');
                }
            });
        });
    }, 0);
    
    return html;
}