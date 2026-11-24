function problemGenerationIndex(conceptId) {
    const incoming = _incomingLinks.get(conceptId) || [];
    const outgoing = _outgoingLinks.get(conceptId) || [];
    
    // ============================================
    // 1. ИММАНЕНТНЫЕ ПРОТИВОРЕЧИЯ (исходный подход верен!)
    // ============================================
    const internalContradictions = incoming.filter(r => 
        r.type === 'internal_contradiction'
    ).reduce((sum, r) => sum + (r.weight || 1), 0);
    
    // Также учитываем противоречия, которые эта концепция порождает
    const outgoingContradictions = outgoing.filter(r => 
        r.type === 'internal_contradiction'
    ).reduce((sum, r) => sum + (r.weight || 1), 0);
    
    // ============================================
    // 2. ПОРОЖДЕНИЕ ПРОБЛЕМАТИЗАЦИИ (новое!)
    // ============================================
    // Исходящие критики и оппозиции - активная проблемность
    const activeProblematization = outgoing.filter(r => 
        r.type === 'critique' || r.type === 'oppose'
    ).reduce((sum, r) => sum + (r.weight || 1), 0);
    
    // ============================================
    // 3. ПОЛУЧЕНИЕ КРИТИКИ (исходный подход)
    // ============================================
    const incomingCritiques = incoming.filter(r => 
        r.type === 'critique'
    ).reduce((sum, r) => sum + (r.weight || 1), 0);
    
    const incomingOppositions = incoming.filter(r => 
        r.type === 'oppose'
    ).reduce((sum, r) => sum + (r.weight || 1), 0);
    
    // ============================================
    // 4. ОГРАНИЧЕНИЯ И УСЛОВИЯ (новое!)
    // ============================================
    // Связи типа "limit" - концепция имеет признанные границы
    const acknowledgedLimits = incoming.filter(r => 
        r.type === 'limit'
    ).length;
    
    // Связи типа "condition" - концепция требует условий
    const conditionalDependencies = incoming.filter(r => 
        r.type === 'condition'
    ).length;
    
    // ============================================
    // 5. ПОРОЖДЕНИЕ РАЗВИТИЯ (новое!)
    // ============================================
    // Сколько концепций "возникли из" данной (emerge_from)
    const conceptsEmergedFrom = incoming.filter(r => 
        r.type === 'emerge_from'
    ).length;
    
    // Сколько концепций эта концепция "кульминирует в"
    const culminations = outgoing.filter(r => 
        r.type === 'culminate'
    ).length;
    
    // ============================================
    // 6. ДВУНАПРАВЛЕННЫЕ ПРОБЛЕМЫ (новое!)
    // ============================================
    const bidirectionalContradictions = incoming.filter(r => 
        r.type === 'internal_contradiction' && r.bidirectional
    ).length;
    
    // ============================================
    // ВЗВЕШЕННАЯ ФОРМУЛА
    // ============================================
    const total = 
        (internalContradictions + outgoingContradictions) * 4.0 +  // Имманентные апории
        bidirectionalContradictions * 1.5 +                         // Взаимные противоречия
        activeProblematization * 2.0 +                              // Активная критика
        incomingCritiques * 1.5 +                                   // Получение критики
        incomingOppositions * 2.0 +                                 // Оппозиции
        acknowledgedLimits * 1.0 +                                  // Признанные ограничения
        conditionalDependencies * 0.8 +                             // Условность
        conceptsEmergedFrom * 1.2 +                                 // Порождение новых концепций
        culminations * 1.0;                                         // Кульминации
    
    return {
        total,
        internalContradictions,
        outgoingContradictions,
        bidirectionalContradictions,
        activeProblematization,
        incomingCritiques,
        incomingOppositions,
        acknowledgedLimits,
        conditionalDependencies,
        conceptsEmergedFrom,
        culminations,
        // Старый формат для совместимости
        raw: incomingCritiques + incomingOppositions + internalContradictions,
        critiques: incomingCritiques,
        oppositions: incomingOppositions,
        contradictions: internalContradictions
    };
}