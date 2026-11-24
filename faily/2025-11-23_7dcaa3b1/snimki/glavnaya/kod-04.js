function tensionIndex(conceptId) {
    const incoming = _incomingLinks.get(conceptId) || [];
    const outgoing = _outgoingLinks.get(conceptId) || [];
    const concept = _conceptMap.get(conceptId);
    
    // ============================================
    // 1. ВНУТРЕННИЕ ПРОТИВОРЕЧИЯ (главный источник напряжения)
    // ============================================
    const internalContradictions = [...incoming, ...outgoing].filter(r => 
        r.type === 'internal_contradiction'
    ).reduce((sum, r) => {
        // Двунаправленные противоречия создают большее напряжение
        return sum + (r.weight || 1) * (r.bidirectional ? 1.5 : 1);
    }, 0);
    
    // ============================================
    // 2. ОГРАНИЧЕНИЯ (напряжение границ)
    // ============================================
    // Концепция имеет признанные пределы применимости
    const acknowledgedLimits = [...incoming, ...outgoing].filter(r => 
        r.type === 'limit'
    ).length;
    
    // ============================================
    // 3. УСЛОВНОСТЬ (напряжение зависимости)
    // ============================================
    // Концепция требует выполнения условий
    const conditionalDependencies = incoming.filter(r => 
        r.type === 'condition'
    ).length;
    
    // ============================================
    // 4. ОПОСРЕДОВАНИЕ (напряжение между терминами)
    // ============================================
    // Связи типа "mediate" - концепция выступает посредником
    // между противоположностями (источник напряжения)
    const mediations = [...incoming, ...outgoing].filter(r => 
        r.type === 'mediate'
    ).length;
    
    // ============================================
    // 5. ПОЛУЧЕНИЕ КРИТИКИ (внешнее давление)
    // ============================================
    const incomingCritiques = incoming.filter(r => 
        r.type === 'critique' || r.type === 'oppose'
    ).reduce((sum, r) => sum + (r.weight || 1), 0);
    
    // ============================================
    // 6. ДОПОЛНИТЕЛЬНОСТЬ (напряжение неполноты)
    // ============================================
    // Концепция требует дополнения - признак внутренней недостаточности
    const complementarityNeeds = [...incoming, ...outgoing].filter(r => 
        r.type === 'complement'
    ).length;
    
    const total = 
        internalContradictions * 3.0 +      // Имманентное противоречие - главное
        acknowledgedLimits * 1.5 +          // Признанные границы
        conditionalDependencies * 1.2 +     // Зависимость от условий
        mediations * 2.0 +                  // Опосредование противоположностей
        incomingCritiques * 1.0 +           // Внешнее давление критики
        complementarityNeeds * 1.0;         // Потребность в дополнении
    
    return {
        total,
        internalContradictions,
        acknowledgedLimits,
        conditionalDependencies,
        mediations,
        incomingCritiques,
        complementarityNeeds
    };
}