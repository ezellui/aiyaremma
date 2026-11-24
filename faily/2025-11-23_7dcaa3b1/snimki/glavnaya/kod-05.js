function polemicalTensionIndex(conceptId) {
    const incoming = _incomingLinks.get(conceptId) || [];
    const outgoing = _outgoingLinks.get(conceptId) || [];
    
    // Концепция АТАКУЕТ другие (активная агрессия)
    const outgoingConflict = outgoing.filter(r => 
        r.type === 'oppose' || r.type === 'critique'
    ).reduce((sum, r) => sum + (r.weight || 1), 0);
    
    // Концепцию АТАКУЮТ (получение отпора)
    const incomingConflict = incoming.filter(r => 
        r.type === 'oppose' || r.type === 'critique'
    ).reduce((sum, r) => sum + (r.weight || 1), 0);
    
    // Двунаправленные диалоги (взаимная полемика)
    const mutualPolemics = incoming.filter(r => 
        r.type === 'dialogue' && r.bidirectional
    ).length;
    
    // Внутренние противоречия (самоконфликт)
    const selfContradiction = [...incoming, ...outgoing].filter(r => 
        r.type === 'internal_contradiction'
    ).length;
    
    const total = 
        outgoingConflict * 1.5 +        // Активная полемичность
        incomingConflict * 1.0 +        // Оспариваемость
        mutualPolemics * 2.0 +          // Взаимная полемика
        selfContradiction * 2.5;        // Самопротиворечие
    
    return {
        total,
        outgoingConflict,
        incomingConflict,
        mutualPolemics,
        selfContradiction
    };
}