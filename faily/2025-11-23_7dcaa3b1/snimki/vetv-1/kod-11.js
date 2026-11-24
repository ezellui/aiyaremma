function criticalPowerIndex(conceptId) {
    const incoming = _incomingLinks.get(conceptId) || [];
    const outgoing = _outgoingLinks.get(conceptId) || [];
    const concept = _conceptMap.get(conceptId);
    const philosopher = _philosopherMap.get(concept?.philosopher);
    
    // ============================================
    // 1. ОБЪЁМ КРИТИЧЕСКОЙ АКТИВНОСТИ
    // ============================================
    const critiques = outgoing.filter(r => r.type === 'critique');
    const oppositions = outgoing.filter(r => r.type === 'oppose');
    
    const rawCriticalActivity = critiques.length + oppositions.length;
    
    const weightedCriticalActivity = outgoing.reduce((sum, r) => {
        const typeWeight = {
            'critique': 2,
            'oppose': 3
        }[r.type] || 0;
        return sum + typeWeight * (r.weight || 1);
    }, 0);
    
    // ============================================
    // 2. КАЧЕСТВО ЦЕЛЕЙ (улучшено)
    // ============================================
    // Не просто средняя влиятельность, а распределение
    const targetAnalysis = critiques.concat(oppositions).reduce((acc, r) => {
        const targetIn = _incomingLinks.get(r.target) || [];
        const targetInfluence = targetIn.length;
        
        // Категоризация целей
        if (targetInfluence > 15) acc.majorTargets++; // Центральные концепции
        else if (targetInfluence > 5) acc.mediumTargets++;
        else acc.minorTargets++;
        
        acc.totalTargetInfluence += targetInfluence;
        
        return acc;
    }, { majorTargets: 0, mediumTargets: 0, minorTargets: 0, totalTargetInfluence: 0 });
    
    const averageTargetInfluence = rawCriticalActivity > 0
        ? targetAnalysis.totalTargetInfluence / rawCriticalActivity
        : 0;
    
    // Бонус за критику центральных концепций
    const majorTargetBonus = targetAnalysis.majorTargets * 2.0;
    
    // ============================================
    // 3. ЭФФЕКТИВНОСТЬ КРИТИКИ (новое!)
    // ============================================
    // Породила ли критика последствия?
    const criticalConsequences = critiques.concat(oppositions).reduce((sum, r) => {
        const targetOut = _outgoingLinks.get(r.target) || [];
        
        // Цель критики породила ответы/развития ПОСЛЕ критики?
        // (упрощение: считаем все исходящие от цели)
        const targetResponses = targetOut.filter(link => 
            link.type === 'develop' || 
            link.type === 'synthesize' ||
            link.type === 'complement'
        ).length;
        
        return sum + targetResponses;
    }, 0);
    
    // Породила ли сама критическая концепция развития?
    const ownDevelopments = outgoing.filter(r => 
        r.type === 'develop' || r.type === 'synthesize'
    ).length;
    
    // Эффективность = критика стимулировала изменения
    const effectiveness = criticalConsequences + ownDevelopments * 2;
    
    // ============================================
    // 4. ШИРОТА КРИТИЧЕСКОЙ АТАКИ (новое!)
    // ============================================
    // Сколько РАЗНЫХ философов/эпох критикует?
    const targetedPhilosophers = new Set(
        critiques.concat(oppositions).map(r => {
            const target = _conceptMap.get(r.target);
            return target?.philosopher;
        }).filter(Boolean)
    ).size;
    
    // Временной диапазон критикуемых
    const targetedEras = critiques.concat(oppositions).map(r => {
        const target = _conceptMap.get(r.target);
        const targetPhil = _philosopherMap.get(target?.philosopher);
        return targetPhil?.birth;
    }).filter(Boolean);
    
    const eraSpan = targetedEras.length > 0
        ? Math.max(...targetedEras) - Math.min(...targetedEras)
        : 0;
    
    // ============================================
    // 5. КОНСТРУКТИВНОСТЬ КРИТИКИ (новое!)
    // ============================================
    // Критика + синтез = конструктивная критика (Кант)
    // Критика без синтеза = деструктивная критика (Ницше, скептики)
    const synthesesAfterCritique = outgoing.filter(r => 
        r.type === 'synthesize'
    ).length;
    
    const constructivenessRatio = rawCriticalActivity > 0
        ? synthesesAfterCritique / rawCriticalActivity
        : 0;
    
    // ============================================
    // 6. ВРЕМЕННАЯ ПЕРСПЕКТИВА (новое!)
    // ============================================
    // Критика философов из прошлого (ретроспективная)
    const retroactiveCritiques = critiques.concat(oppositions).filter(r => {
        const target = _conceptMap.get(r.target);
        const targetPhil = _philosopherMap.get(target?.philosopher);
        return targetPhil && philosopher && targetPhil.birth < philosopher.birth;
    }).length;
    
    // Критика современников (синхронная)
    const contemporaryCritiques = critiques.concat(oppositions).filter(r => {
        const target = _conceptMap.get(r.target);
        const targetPhil = _philosopherMap.get(target?.philosopher);
        return targetPhil && philosopher && 
            Math.abs(targetPhil.birth - philosopher.birth) < 30;
    }).length;
    
    // ============================================
    // ИНТЕГРАЛЬНЫЙ ИНДЕКС
    // ============================================
    const total = 
        weightedCriticalActivity * 1.0 +        // Базовая активность
        majorTargetBonus * 1.5 +                 // Критика центральных концепций
        effectiveness * 2.0 +                    // Эффективность (главное!)
        targetedPhilosophers * 0.8 +             // Широта атаки
        eraSpan / 100 +                          // Временной диапазон
        (constructivenessRatio > 0.3 ? 3 : 0);   // Бонус за конструктивность
    
    return {
        total,
        
        // Активность
        rawCriticalActivity,
        weightedCriticalActivity,
        
        // Качество целей
        targets: {
            majorTargets: targetAnalysis.majorTargets,
            mediumTargets: targetAnalysis.mediumTargets,
            minorTargets: targetAnalysis.minorTargets,
            averageInfluence: averageTargetInfluence
        },
        
        // Эффективность
        effectiveness,
        criticalConsequences,
        ownDevelopments,
        
        // Широта
        targetedPhilosophers,
        eraSpan,
        
        // Тип критики
        constructivenessRatio,
        retroactiveCritiques,
        contemporaryCritiques,
        
        // Для обратной совместимости
        raw: rawCriticalActivity,
        weighted: weightedCriticalActivity,
        targetInfluence: averageTargetInfluence
    };
}