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
    }).filter(r => r.value > 0);
    
    // Сортировки по разным критериям
    const byTotal = [...results].sort((a, b) => b.value - a.value);
    const byImmanent = [...results].sort((a, b) => b.immanent - a.immanent);
    const byPolemical = [...results].sort((a, b) => b.polemical - a.polemical);
    const byDialectical = [...results].sort((a, b) => b.dialectical - a.dialectical);
    
    let html = `
        <div class="metric-header">
            <h2>⚖️ Индекс напряжения</h2>
            <p class="metric-description">Концепции с наибольшим внутренним напряжением</p>
        </div>
        
        <div class="tension-tabs">
            <button class="tab-btn active" data-tab="total">Общий рейтинг</button>
            <button class="tab-btn" data-tab="immanent">🔴 Имманентное</button>
            <button class="tab-btn" data-tab="polemical">⚔️ Полемическое</button>
            <button class="tab-btn" data-tab="dialectical">♦️ Диалектическое</button>
        </div>
        
        <div class="tab-content active" data-content="total">
            ${generateTensionList(byTotal.slice(0, 30), 'total')}
        </div>
        <div class="tab-content" data-content="immanent">
            ${generateTensionList(byImmanent.slice(0, 30), 'immanent')}
        </div>
        <div class="tab-content" data-content="polemical">
            ${generateTensionList(byPolemical.slice(0, 30), 'polemical')}
        </div>
        <div class="tab-content" data-content="dialectical">
            ${generateTensionList(byDialectical.slice(0, 30), 'dialectical')}
        </div>
    `;
    
    // Добавляем обработчик переключения вкладок
    setTimeout(() => {
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const tab = this.dataset.tab;
                
                // Переключаем активную кнопку
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                
                // Переключаем контент
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                document.querySelector(`[data-content="${tab}"]`).classList.add('active');
            });
        });
    }, 0);
    
    return html;
}

function generateTensionList(results, sortBy) {
    return results.map((r, index) => {
        const details = r.details;
        const typeIcon = {
            'immanent': '🔴',
            'polemical': '⚔️',
            'dialectical': '♦️'
        }[r.dominantType] || '⚖️';
        
        const displayValue = sortBy === 'total' ? r.value : r[sortBy];
        
        return `
            <div class="metric-item tension-item">
                <div class="metric-rank">${index + 1}</div>
                <div class="metric-content">
                    <div class="metric-main">
                        <span class="metric-icon">${typeIcon}</span>
                        <span class="concept-label">${r.node.label}</span>
                        <span class="philosopher-name">${r.node.concept}</span>
                        <span class="metric-value">${displayValue.toFixed(1)}</span>
                    </div>
                    
                    <div class="tension-components">
                        <span class="component immanent">И: ${r.immanent.toFixed(1)}</span>
                        <span class="component polemical">П: ${r.polemical.toFixed(1)}</span>
                        <span class="component dialectical">Д: ${r.dialectical.toFixed(1)}</span>
                    </div>
                    
                    ${r.node.description ? `<div class="metric-description-text">${r.node.description}</div>` : ''}
                </div>
            </div>
        `;
    }).join('');
}