// Пример расширенного отображения для карточки концепции
function displayCriticalPowerDetails(conceptId) {
    const cpi = criticalPowerIndex(conceptId);
    
    return `
        **Критическая сила: ${cpi.total.toFixed(1)}**
        
        📊 Профиль критики:
        • Эффективность: ${cpi.effectiveness} ${getEffectivenessEmoji(cpi.effectiveness)}
        • Тип: ${cpi.constructivenessRatio > 0.5 ? 'Конструктивная' : 'Деструктивная'}
        • Активность: ${cpi.rawCriticalActivity} критик
        
        🎯 Цели:
        • Центральные концепции: ${cpi.targets.majorTargets}
        • Средние: ${cpi.targets.mediumTargets}
        • Периферийные: ${cpi.targets.minorTargets}
        
        🌍 Охват:
        • Философов: ${cpi.targetedPhilosophers}
        • Эпох: ${Math.round(cpi.eraSpan / 100)} веков
        
        ⚡ Последствия:
        • Порождённых ответов: ${cpi.criticalConsequences}
        • Собственных развитий: ${cpi.ownDevelopments}
    `;
}

function getEffectivenessEmoji(eff) {
    if (eff > 40) return '🔥 (очень высокая)';
    if (eff > 20) return '⚡ (высокая)';
    if (eff > 10) return '✓ (средняя)';
    return '• (низкая)';
}