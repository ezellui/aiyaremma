function problemGenerationIndex(conceptId) {
    const incoming = _incomingLinks.get(conceptId) || [];
    const outgoing = _outgoingLinks.get(conceptId) || [];
    const concept = _conceptMap.get(conceptId);
    const philosopher = _philosopherMap.get(concept.philosopher);

    // 1. ПОРОЖДЕНИЕ РАЗВИТИЯ (главный маркер!)
    // Сколько концепций пытались РАЗВИТЬ/решить эту проблему
    const developmentAttempts = outgoing.filter(r => 
        r.type === 'develop' || r.type === 'synthesize'
    ).length;

    // 2. УСТОЙЧИВОСТЬ ДИСКУССИИ
    // Временной диапазон философов, вступающих в диалог с концепцией
    const discussionSpan = incoming.length > 0 ? (() => {
        const years = incoming.map(r => {
            const source = _conceptMap.get(r.source);
            const phil = _philosopherMap.get(source?.philosopher);
            return phil?.birth;
        }).filter(Boolean);
        return years.length > 0 ? Math.max(...years) - Math.min(...years) : 0;
    })() : 0;

    // 3. ДВУНАПРАВЛЕННЫЕ ДИАЛОГИ
    // Проблема стимулирует взаимный обмен
    const bidirectionalDebates = incoming.filter(r => 
        r.type === 'dialogue' && r.bidirectional
    ).length;

    // 4. КРИТИКА КАК ПРИЗНАК ПРОБЛЕМНОСТИ (но не главный!)
    // Только если критика ведёт к развитию
    const productiveCritique = incoming.filter(r => {
        if (r.type !== 'critique' && r.type !== 'oppose') return false;
        // Проверяем: породила ли эта критика новые концепции?
        const criticSource = r.source;
        const criticOutgoing = _outgoingLinks.get(criticSource) || [];
        return criticOutgoing.some(link => link.type === 'develop');
    }).length;

    // 5. РАЗНООБРАЗИЕ ОТВЕТОВ
    // Проблема порождает РАЗНЫЕ типы реакций
    const responseTypeDiversity = new Set(outgoing.map(r => r.type)).size;

    // 6. МЕЖДИСЦИПЛИНАРНОСТЬ
    // Проблемы часто выходят за рамки одной рубрики
    const rubricSpan = (conceptToRubrics[conceptId] || []).length;

    const total = 
        developmentAttempts * 3.0 +           // Главное: сколько пытались развить
        discussionSpan / 100 +                // Долговечность дискуссии (в веках)
        bidirectionalDebates * 2.0 +          // Взаимный диалог
        productiveCritique * 1.5 +            // Критика, породившая развитие
        responseTypeDiversity * 1.0 +         // Разнообразие ответов
        rubricSpan * 0.8;                     // Выход за дисциплинарные рамки

    return {
        total,
        developmentAttempts,
        discussionSpan,
        bidirectionalDebates,
        productiveCritique,
        responseTypeDiversity,
        rubricSpan
    };
}