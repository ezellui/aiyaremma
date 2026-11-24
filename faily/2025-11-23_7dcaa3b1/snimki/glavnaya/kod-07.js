function tensionIndex(conceptId) {
    const incoming = _incomingLinks.get(conceptId) || [];
    const outgoing = _outgoingLinks.get(conceptId) || [];
    const concept = _conceptMap.get(conceptId);
    
    // ============================================
    // УРОВЕНЬ 1: ИММАНЕНТНОЕ НАПРЯЖЕНИЕ
    // (внутренняя противоречивость концепции)
    // ============================================
    
    // 1.1 Внутренние противоречия (главный источник)
    const internalContradictions = [...incoming, ...outgoing].filter(r => 
        r.type === 'internal_contradiction'
    ).reduce((sum, r) => {
        const bidirectionalBonus = r.bidirectional ? 1.5 : 1;
        return sum + (r.weight || 1) * bidirectionalBonus;
    }, 0);
    
    // 1.2 Ограничения (напряжение границ)
    const acknowledgedLimits = [...incoming, ...outgoing].filter(r => 
        r.type === 'limit'
    ).length;
    
    // 1.3 Условность (зависимость от предпосылок)
    const conditionalDependencies = incoming.filter(r => 
        r.type === 'condition'
    ).length;
    
    // 1.4 Опосредование (стоять между противоположностями)
    const mediations = [...incoming, ...outgoing].filter(r => 
        r.type === 'mediate'
    ).length;
    
    // 1.5 Потребность в дополнении (неполнота)
    const complementarityNeeds = [...incoming, ...outgoing].filter(r => 
        r.type === 'complement'
    ).length;
    
    const immanentTension = 
        internalContradictions * 3.0 +
        acknowledgedLimits * 1.5 +
        conditionalDependencies * 1.2 +
        mediations * 2.0 +
        complementarityNeeds * 1.0;
    
    // ============================================
    // УРОВЕНЬ 2: ПОЛЕМИЧЕСКОЕ НАПРЯЖЕНИЕ
    // (конфликтность позиции)
    // ============================================
    
    // 2.1 Исходящая агрессия (активная критика)
    const outgoingConflict = outgoing.filter(r => 
        r.type === 'oppose' || r.type === 'critique'
    ).reduce((sum, r) => sum + (r.weight || 1), 0);
    
    // 2.2 Входящая критика (оспариваемость)
    const incomingConflict = incoming.filter(r => 
        r.type === 'oppose' || r.type === 'critique'
    ).reduce((sum, r) => sum + (r.weight || 1), 0);
    
    // 2.3 Взаимная полемика (двусторонние споры)
    const mutualPolemics = incoming.filter(r => 
        r.type === 'dialogue' && r.bidirectional
    ).length;
    
    const polemicalTension = 
        outgoingConflict * 1.5 +
        incomingConflict * 1.0 +
        mutualPolemics * 2.0;
    
    // ============================================
    // УРОВЕНЬ 3: ДИАЛЕКТИЧЕСКОЕ НАПРЯЖЕНИЕ
    // (продуктивность противоречия)
    // ============================================
    
    // 3.1 Синтезы (попытки разрешения)
    const syntheses = outgoing.filter(r => 
        r.type === 'synthesize'
    ).length;
    
    // 3.2 Кульминации (переходы к новому качеству)
    const culminations = outgoing.filter(r => 
        r.type === 'culminate'
    ).length;
    
    // 3.3 Порождение новых концепций
    const emergentConcepts = incoming.filter(r => 
        r.type === 'emerge_from'
    ).length;
    
    // 3.4 Развития (попытки преодолеть противоречие)
    const developments = outgoing.filter(r => 
        r.type === 'develop'
    ).length;
    
    // Нерешённое напряжение = противоречия минус разрешения
    const totalContradictions = internalContradictions + 
        (incomingConflict + outgoingConflict) / 4; // Внешние конфликты тоже создают противоречия
    const resolutionAttempts = syntheses + culminations + developments * 0.5;
    const unresolvedTension = Math.max(totalContradictions - resolutionAttempts, 0);
    
    const dialecticalTension = 
        unresolvedTension * 2.0 +           // Нерешённое напряжение
        emergentConcepts * 1.5 +            // Плодотворность
        mediations * 1.0;                   // Опосредование (здесь тоже релевантно)
    
    // ============================================
    // ИНТЕГРАЛЬНЫЙ ИНДЕКС
    // ============================================
    
    // Взвешенная сумма трёх типов напряжения
    const total = 
        immanentTension * 1.0 +         // Имманентное (базовое)
        polemicalTension * 0.8 +        // Полемическое (контекстное)
        dialecticalTension * 1.2;       // Диалектическое (продуктивное, поэтому выше)
    
    // ============================================
    // ДОПОЛНИТЕЛЬНЫЕ АНАЛИТИЧЕСКИЕ МЕТРИКИ
    // ============================================
    
    // Баланс между напряжением и разрешением
    const tensionResolutionRatio = totalContradictions > 0 
        ? resolutionAttempts / totalContradictions 
        : 0;
    
    // Доминирующий тип напряжения
    const dominantType = 
        immanentTension > polemicalTension && immanentTension > dialecticalTension ? 'immanent' :
        polemicalTension > dialecticalTension ? 'polemical' : 'dialectical';
    
    // Интенсивность (средний вес связей)
    const allTensionLinks = [
        ...incoming.filter(r => ['internal_contradiction', 'oppose', 'critique', 'limit'].includes(r.type)),
        ...outgoing.filter(r => ['internal_contradiction', 'oppose', 'critique'].includes(r.type))
    ];
    const averageIntensity = allTensionLinks.length > 0
        ? allTensionLinks.reduce((sum, r) => sum + (r.weight || 1), 0) / allTensionLinks.length
        : 0;
    
    return {
        // Общий индекс
        total,
        
        // Три уровня напряжения
        immanentTension,
        polemicalTension,
        dialecticalTension,
        
        // Компоненты имманентного напряжения
        immanent: {
            internalContradictions,
            acknowledgedLimits,
            conditionalDependencies,
            mediations,
            complementarityNeeds
        },
        
        // Компоненты полемического напряжения
        polemical: {
            outgoingConflict,
            incomingConflict,
            mutualPolemics
        },
        
        // Компоненты диалектического напряжения
        dialectical: {
            unresolvedTension,
            syntheses,
            culminations,
            emergentConcepts,
            developments,
            resolutionAttempts
        },
        
        // Аналитические метрики
        analytics: {
            dominantType,
            tensionResolutionRatio,
            averageIntensity,
            totalContradictions
        }
    };
}