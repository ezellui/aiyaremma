return {
    total,
    weighted: total,  // ← ДОБАВИТЬ ЭТУ СТРОКУ для совместимости
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