function revolutionaryIndex(conceptId) {
    const concept = _conceptMap.get(conceptId);
    if (!concept) return { total: 0 };

    const philosopher = _philosopherMap.get(concept.philosopher);
    if (!philosopher) return { total: 0 };

    const incoming = _incomingLinks.get(conceptId) || [];
    const outgoing = _outgoingLinks.get(conceptId) || [];

    // ============================================
    // 1. НЕЗАВИСИМОСТЬ ОТ ТРАДИЦИИ (исправлено)
    // ============================================
    const weightedOppositionsToEarlier = incoming.filter(r => {
        const source = _conceptMap.get(r.source);
        if (!source) return false;
        const sourcePhil = _philosopherMap.get(source.philosopher);
        return sourcePhil && r.type === 'oppose' && sourcePhil.birth < philosopher.birth;
    }).reduce((sum, r) => sum + (r.weight || 1), 0);

    const weightedInfluencesFromEarlier = incoming.filter(r => {
        const source = _conceptMap.get(r.source);
        if (!source) return false;
        const sourcePhil = _philosopherMap.get(source.philosopher);
        return sourcePhil && r.type === 'influence' && sourcePhil.birth < philosopher.birth;
    }).reduce((sum, r) => sum + (r.weight || 1), 0);

    // Баланс: революционность = оппозиции минус укоренённость
    // Используем разность вместо деления (избегаем деления на 0)
    const independenceScore = weightedOppositionsToEarlier - weightedInfluencesFromEarlier * 0.5;

    // ============================================
    // 2. КРИТИКА ДОМИНИРУЮЩИХ ИДЕЙ (улучшено)
    // ============================================
    const weightedCritiquesOfInfluential = outgoing.filter(r => {
        if (r.type !== 'critique' && r.type !== 'oppose') return false;
        const targetIn = _incomingLinks.get(r.target) || [];
        return targetIn.length > 10; // Целится в "узлы" графа
    }).reduce((sum, r) => sum + (r.weight || 1), 0);

    // ============================================
    // 3. СИНТЕТИЧЕСКАЯ НОВИЗНА (взвешенная)
    // ============================================
    const weightedSyntheses = outgoing.filter(r => r.type === 'synthesize')
        .reduce((sum, r) => sum + (r.weight || 1), 0);

    // ============================================
    // 4. ДИСКУССИОННОСТЬ (новое)
    // ============================================
    // Двунаправленные диалоги - признак спорной новизны
    const bidirectionalDialogues = [...incoming, ...outgoing].filter(r => 
        r.type === 'dialogue' && r.bidirectional
    ).length / 2; // Делим на 2, т.к. каждая связь учитывается дважды

    // ============================================
    // 5. МЕЖДИСЦИПЛИНАРНОСТЬ (новое)
    // ============================================
    // Революционные концепции часто выходят за пределы одной рубрики
    const rubricDiversity = (conceptToRubrics[conceptId] || []).length;

    // ============================================
    // 6. ДОЛГОСРОЧНОЕ ВЛИЯНИЕ (новое)
    // ============================================
    // Влияние на философов через >50 лет - признак парадигмального сдвига
    const futureImpact = outgoing.filter(r => {
        const target = _conceptMap.get(r.target);
        if (!target) return false;
        const targetPhil = _philosopherMap.get(target.philosopher);
        return targetPhil && (targetPhil.birth - philosopher.birth) > 50;
    }).length;

    // ============================================
    // 7. ШИРОТА ВЛИЯНИЯ (новое)
    // ============================================
    // Количество различных философов, на которых повлияла концепция
    const influencedPhilosophersCount = new Set(
        outgoing.map(r => {
            const target = _conceptMap.get(r.target);
            return target?.philosopher;
        }).filter(Boolean)
    ).size;

    // ============================================
    // 8. РАЗНООБРАЗИЕ ОТНОШЕНИЙ (новое)
    // ============================================
    // Концепция, участвующая в разных типах связей, концептуально богаче
    const outgoingTypeDiversity = new Set(outgoing.map(r => r.type)).size;

    // ============================================
    // ИТОГОВАЯ ФОРМУЛА
    // ============================================
    const total = 
        independenceScore * 2.0 +                    // Автономия от традиции
        weightedCritiquesOfInfluential * 1.5 +       // Атака на центральные узлы
        weightedSyntheses * 1.8 +                    // Синтетическая креативность
        bidirectionalDialogues * 1.2 +               // Порождение дискуссий
        rubricDiversity * 0.8 +                      // Выход за дисциплинарные рамки
        futureImpact * 1.0 +                         // Влияние через поколения
        influencedPhilosophersCount * 0.7 +          // Широта воздействия
        outgoingTypeDiversity * 0.5;                 // Концептуальное богатство

    return {
        total,
        // Компоненты для анализа
        independenceScore,
        weightedOppositionsToEarlier,
        weightedInfluencesFromEarlier,
        weightedCritiquesOfInfluential,
        weightedSyntheses,
        bidirectionalDialogues,
        rubricDiversity,
        futureImpact,
        influencedPhilosophersCount,
        outgoingTypeDiversity
    };
}