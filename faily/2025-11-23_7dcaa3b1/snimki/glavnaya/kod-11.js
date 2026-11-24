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
            // Дополнительные поля для удобства
            dominantType: metric.analytics.dominantType,
            immanent: metric.immanentTension,
            polemical: metric.polemicalTension,
            dialectical: metric.dialecticalTension
        };
    }).filter(r => r.value > 0).sort((a, b) => b.value - a.value);
    
    // Генерируем HTML с детализацией
    let html = `
        <div class="metric-header">
            <h2>⚖️ Индекс напряжения</h2>
            <p class="metric-description">
                Концепции с наибольшим внутренним напряжением.
                <span class="legend">
                    <span class="legend-item"><span class="badge immanent">И</span> Имманентное</span>
                    <span class="legend-item"><span class="badge polemical">П</span> Полемическое</span>
                    <span class="legend-item"><span class="badge dialectical">Д</span> Диалектическое</span>
                </span>
            </p>
        </div>
        <div class="metric-results">
    `;
    
    results.slice(0, 30).forEach((r, index) => {
        const details = r.details;
        const ratio = details.analytics.tensionResolutionRatio;
        const ratioPercent = Math.round(ratio * 100);
        
        // Определяем иконку по доминирующему типу
        const typeIcon = {
            'immanent': '🔴',
            'polemical': '⚔️',
            'dialectical': '♦️'
        }[r.dominantType] || '⚖️';
        
        // Цвет по доминирующему типу
        const typeClass = r.dominantType;
        
        html += `
            <div class="metric-item tension-item ${typeClass}">
                <div class="metric-rank">${index + 1}</div>
                <div class="metric-content">
                    <div class="metric-main">
                        <span class="metric-icon">${typeIcon}</span>
                        <span class="concept-label">${r.node.label}</span>
                        <span class="philosopher-name">${r.node.concept}</span>
                        <span class="metric-value">${r.value.toFixed(1)}</span>
                    </div>
                    
                    <div class="tension-breakdown">
                        <div class="tension-bar">
                            <div class="tension-segment immanent" 
                                 style="width: ${(r.immanent / r.value * 100).toFixed(1)}%"
                                 title="Имманентное: ${r.immanent.toFixed(1)}">
                            </div>
                            <div class="tension-segment polemical" 
                                 style="width: ${(r.polemical / r.value * 100).toFixed(1)}%"
                                 title="Полемическое: ${r.polemical.toFixed(1)}">
                            </div>
                            <div class="tension-segment dialectical" 
                                 style="width: ${(r.dialectical / r.value * 100).toFixed(1)}%"
                                 title="Диалектическое: ${r.dialectical.toFixed(1)}">
                            </div>
                        </div>
                        <div class="tension-details">
                            <span class="detail-item">И: ${r.immanent.toFixed(1)}</span>
                            <span class="detail-item">П: ${r.polemical.toFixed(1)}</span>
                            <span class="detail-item">Д: ${r.dialectical.toFixed(1)}</span>
                            ${ratio > 0 ? `<span class="resolution-ratio" title="Баланс напряжения/разрешения">⚖ ${ratioPercent}%</span>` : ''}
                        </div>
                    </div>
                    
                    ${r.node.description ? `<div class="metric-description-text">${r.node.description}</div>` : ''}
                </div>
            </div>
        `;
    });
    
    html += `</div>`;
    
    return html;
}