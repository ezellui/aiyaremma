function dialecticalTensionIndex(conceptId) {
    const incoming = _incomingLinks.get(conceptId) || [];
    const outgoing = _outgoingLinks.get(conceptId) || [];
    
    // 1. Внутренние противоречия (тезис-антитезис)
    const contradictions = [...incoming, ...outgoing].filter(r => 
        r.type === 'internal_contradiction'
    ).reduce((sum, r) => sum + (r.weight || 1), 0);
    
    // 2. Опосредования (Vermittlung - снятие противоречий)
    const mediations = [...incoming, ...outgoing].filter(r => 
        r.type === 'mediate'
    ).length;
    
    // 3. Синтезы (Aufhebung - диалектическое снятие)
    const syntheses = outgoing.filter(r => 
        r.type === 'synthesize'
    ).length;
    
    // 4. Кульминации (переход к новому качеству)
    const culminations = outgoing.filter(r => 
        r.type === 'culminate'
    ).length;
    
    // Напряжение = противоречия минус разрешения
    const unresolved = contradictions - (syntheses + culminations * 0.5);
    
    const total = 
        contradictions * 2.0 +          // Исходное противоречие
        mediations * 1.5 +              // Опосредование
        Math.max(unresolved, 0) * 1.2;  // Нерешённое напряжение
    
    return {
        total,
        contradictions,
        mediations,
        syntheses,
        culminations,
        unresolved
    };
}