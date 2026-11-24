// ============================================
// ВЗВЕШЕННАЯ ФОРМУЛА
// ============================================
const total = 
    (internalContradictions + outgoingContradictions) * 4.0 +
    bidirectionalContradictions * 1.5 +
    activeProblematization * 2.0 +
    incomingCritiques * 1.5 +
    incomingOppositions * 2.0 +
    acknowledgedLimits * 1.0 +
    conditionalDependencies * 0.8 +
    conceptsEmergedFrom * 1.2 +
    culminations * 1.0;

return {
    total,
    weighted: total,  // ← ДОБАВЛЕНО: алиас для совместимости с generateProblemGenerationContent()
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