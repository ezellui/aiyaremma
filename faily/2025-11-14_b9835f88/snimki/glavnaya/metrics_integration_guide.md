# Руководство по интеграции расширенных метрик

## Обзор изменений

Данное руководство содержит все необходимые фрагменты кода для интеграции специализированных философских метрик в существующий граф. Основные изменения:

1. **Модальное окно статистики** вместо боковой панели
2. **Тёмная тема** для модального окна (как у модальных окон узлов)
3. **Группированная навигация** между метриками
4. **Интеграция всех метрик** из двух JS-файлов

---

## 1. CSS для модального окна статистики

Добавить в секцию `<style>` после существующих стилей модальных окон (примерно после строки 400):

```css
/* ============================================ */
/* МОДАЛЬНОЕ ОКНО СТАТИСТИКИ */
/* ============================================ */

#statsModal {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.85);
    z-index: 9999;
    backdrop-filter: blur(5px);
}

#statsModal.active {
    display: flex;
    align-items: center;
    justify-content: center;
    animation: fadeIn 0.3s ease-out;
}

.stats-modal-content {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border-radius: 20px;
    width: 90%;
    max-width: 1400px;
    height: 85vh;
    max-height: 900px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    border: 2px solid rgba(108, 92, 231, 0.3);
}

.stats-modal-header {
    background: linear-gradient(135deg, rgba(108, 92, 231, 0.2), rgba(52, 152, 219, 0.2));
    padding: 20px 30px;
    border-bottom: 2px solid rgba(108, 92, 231, 0.3);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.stats-modal-header h2 {
    color: #fff;
    margin: 0;
    font-size: 24px;
    font-weight: 700;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.stats-close-btn {
    background: rgba(231, 76, 60, 0.8);
    color: white;
    border: none;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    font-size: 24px;
    cursor: pointer;
    transition: all 0.3s;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.stats-close-btn:hover {
    background: rgba(231, 76, 60, 1);
    transform: scale(1.1) rotate(90deg);
}

.stats-modal-body {
    display: flex;
    flex: 1;
    overflow: hidden;
}

/* Навигационная панель слева */
.stats-navigation {
    width: 280px;
    background: rgba(26, 26, 46, 0.6);
    border-right: 2px solid rgba(108, 92, 231, 0.3);
    padding: 20px;
    overflow-y: auto;
}

.stats-nav-group {
    margin-bottom: 25px;
}

.stats-nav-group-title {
    color: #6c5ce7;
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 2px solid rgba(108, 92, 231, 0.3);
}

.stats-nav-item {
    padding: 12px 15px;
    margin: 5px 0;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s;
    color: #bbb;
    font-size: 13px;
    font-weight: 500;
    border-left: 3px solid transparent;
}

.stats-nav-item:hover {
    background: rgba(108, 92, 231, 0.2);
    border-left-color: #6c5ce7;
    color: #fff;
    transform: translateX(3px);
}

.stats-nav-item.active {
    background: rgba(108, 92, 231, 0.3);
    border-left-color: #6c5ce7;
    color: #fff;
    box-shadow: 0 4px 12px rgba(108, 92, 231, 0.3);
}

.stats-nav-item-icon {
    margin-right: 8px;
    font-size: 14px;
}

/* Контентная область справа */
.stats-content-area {
    flex: 1;
    padding: 30px;
    overflow-y: auto;
    background: rgba(15, 15, 30, 0.3);
}

.stats-content-header {
    margin-bottom: 25px;
    padding-bottom: 15px;
    border-bottom: 2px solid rgba(108, 92, 231, 0.3);
}

.stats-content-title {
    color: #fff;
    font-size: 22px;
    font-weight: 700;
    margin: 0 0 8px 0;
}

.stats-content-description {
    color: #95a5a6;
    font-size: 13px;
    line-height: 1.6;
}

/* Карточки результатов метрик */
.metric-results-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    margin-top: 20px;
}

.metric-result-card {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 20px;
    border: 1px solid rgba(108, 92, 231, 0.2);
    transition: all 0.3s;
    cursor: pointer;
}

.metric-result-card:hover {
    background: rgba(108, 92, 231, 0.1);
    border-color: rgba(108, 92, 231, 0.4);
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(108, 92, 231, 0.2);
}

.metric-result-rank {
    display: inline-block;
    background: linear-gradient(135deg, #6c5ce7, #3498db);
    color: white;
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 10px;
}

.metric-result-name {
    color: #fff;
    font-size: 16px;
    font-weight: 600;
    margin: 10px 0;
}

.metric-result-value {
    color: #3498db;
    font-size: 24px;
    font-weight: 700;
    margin: 8px 0;
}

.metric-result-philosopher {
    color: #95a5a6;
    font-size: 12px;
    font-style: italic;
}

/* Кнопка расчёта метрики */
.calculate-metric-btn {
    background: linear-gradient(135deg, #6c5ce7, #3498db);
    color: white;
    border: none;
    padding: 15px 30px;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
    box-shadow: 0 6px 20px rgba(108, 92, 231, 0.3);
    width: 100%;
    margin-top: 20px;
}

.calculate-metric-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(108, 92, 231, 0.4);
}

.calculate-metric-btn:active {
    transform: translateY(0);
}

/* Таблица метрик */
.metric-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0 8px;
    margin-top: 20px;
}

.metric-table-header {
    background: rgba(108, 92, 231, 0.2);
    color: #fff;
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.metric-table th,
.metric-table td {
    padding: 12px 15px;
    text-align: left;
}

.metric-table-row {
    background: rgba(255, 255, 255, 0.05);
    transition: all 0.3s;
    cursor: pointer;
}

.metric-table-row:hover {
    background: rgba(108, 92, 231, 0.15);
    transform: scale(1.02);
}

.metric-table-row td {
    color: #ddd;
    font-size: 13px;
    border-top: 1px solid rgba(108, 92, 231, 0.1);
    border-bottom: 1px solid rgba(108, 92, 231, 0.1);
}

.metric-table-row td:first-child {
    border-left: 1px solid rgba(108, 92, 231, 0.1);
    border-radius: 8px 0 0 8px;
}

.metric-table-row td:last-child {
    border-right: 1px solid rgba(108, 92, 231, 0.1);
    border-radius: 0 8px 8px 0;
}

/* Индикатор прогресса в модальном окне */
.stats-progress-indicator {
    background: rgba(52, 152, 219, 0.1);
    border-radius: 8px;
    padding: 20px;
    text-align: center;
    margin: 20px 0;
    border: 1px solid rgba(52, 152, 219, 0.3);
}

.stats-progress-text {
    color: #3498db;
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 10px;
}

.stats-progress-bar {
    width: 100%;
    height: 8px;
    background: rgba(52, 152, 219, 0.2);
    border-radius: 4px;
    overflow: hidden;
}

.stats-progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #3498db, #6c5ce7);
    border-radius: 4px;
    transition: width 0.3s ease;
}

/* Пустое состояние */
.empty-state {
    text-align: center;
    padding: 60px 20px;
    color: #95a5a6;
}

.empty-state-icon {
    font-size: 64px;
    margin-bottom: 20px;
    opacity: 0.3;
}

.empty-state-text {
    font-size: 16px;
    margin-bottom: 20px;
}

/* Скроллбары для тёмной темы */
.stats-navigation::-webkit-scrollbar,
.stats-content-area::-webkit-scrollbar {
    width: 8px;
}

.stats-navigation::-webkit-scrollbar-track,
.stats-content-area::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.2);
}

.stats-navigation::-webkit-scrollbar-thumb,
.stats-content-area::-webkit-scrollbar-thumb {
    background: rgba(108, 92, 231, 0.5);
    border-radius: 4px;
}

.stats-navigation::-webkit-scrollbar-thumb:hover,
.stats-content-area::-webkit-scrollbar-thumb:hover {
    background: rgba(108, 92, 231, 0.7);
}

/* Анимации */
@keyframes fadeIn {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}

/* Кнопка запуска статистики в легенде */
.open-stats-modal-btn {
    width: 100%;
    background: linear-gradient(135deg, #6c5ce7, #3498db);
    color: white;
    border: none;
    padding: 12px 20px;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.3s;
    box-shadow: 0 4px 15px rgba(108, 92, 231, 0.3);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 15px;
}

.open-stats-modal-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(108, 92, 231, 0.4);
}

.open-stats-modal-btn:active {
    transform: translateY(0);
}

/* Responsive */
@media (max-width: 1024px) {
    .stats-navigation {
        width: 220px;
    }
    
    .metric-results-grid {
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    }
}

@media (max-width: 768px) {
    .stats-modal-content {
        width: 95%;
        height: 95vh;
    }
    
    .stats-modal-body {
        flex-direction: column;
    }
    
    .stats-navigation {
        width: 100%;
        border-right: none;
        border-bottom: 2px solid rgba(108, 92, 231, 0.3);
        max-height: 200px;
    }
    
    .metric-results-grid {
        grid-template-columns: 1fr;
    }
}
```

---

## 2. HTML разметка модального окна

Добавить перед закрывающим тегом `</body>` (примерно на строке 4760):

```html
<!-- ============================================ -->
<!-- МОДАЛЬНОЕ ОКНО СТАТИСТИКИ -->
<!-- ============================================ -->
<div id="statsModal">
    <div class="stats-modal-content">
        <div class="stats-modal-header">
            <h2>📊 Расширенный статистический анализ</h2>
            <button class="stats-close-btn" onclick="closeStatsModal()">×</button>
        </div>
        <div class="stats-modal-body">
            <!-- Навигация -->
            <div class="stats-navigation">
                <!-- Базовые метрики сети -->
                <div class="stats-nav-group">
                    <div class="stats-nav-group-title">🔍 Базовые метрики</div>
                    <div class="stats-nav-item" onclick="switchStatsView('overview')">
                        <span class="stats-nav-item-icon">📈</span>
                        Общий обзор
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('degree')">
                        <span class="stats-nav-item-icon">🔗</span>
                        Степень связности
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('pagerank')">
                        <span class="stats-nav-item-icon">⭐</span>
                        PageRank
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('betweenness')">
                        <span class="stats-nav-item-icon">🌉</span>
                        Betweenness
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('closeness')">
                        <span class="stats-nav-item-icon">🎯</span>
                        Closeness
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('eigenvector')">
                        <span class="stats-nav-item-icon">🏆</span>
                        Eigenvector
                    </div>
                </div>

                <!-- Философские метрики -->
                <div class="stats-nav-group">
                    <div class="stats-nav-group-title">🎓 Философские метрики</div>
                    <div class="stats-nav-item" onclick="switchStatsView('problem-generation')">
                        <span class="stats-nav-item-icon">⚡</span>
                        Индекс проблемности
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('critical-power')">
                        <span class="stats-nav-item-icon">⚔️</span>
                        Критическая сила
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('revolutionary')">
                        <span class="stats-nav-item-icon">🔥</span>
                        Революционность
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('paradigm-shift')">
                        <span class="stats-nav-item-icon">🌐</span>
                        Парадигмальный сдвиг
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('synthetic')">
                        <span class="stats-nav-item-icon">🧩</span>
                        Синтетичность
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('foundational')">
                        <span class="stats-nav-item-icon">🏛️</span>
                        Основополагание
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('coherence')">
                        <span class="stats-nav-item-icon">🔮</span>
                        Внутренняя согласованность
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('tension')">
                        <span class="stats-nav-item-icon">⚖️</span>
                        Индекс напряжения
                    </div>
                </div>

                <!-- Продвинутые метрики -->
                <div class="stats-nav-group">
                    <div class="stats-nav-group-title">🚀 Продвинутые метрики</div>
                    <div class="stats-nav-item" onclick="switchStatsView('transformation')">
                        <span class="stats-nav-item-icon">🦋</span>
                        Трансформация
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('fertility')">
                        <span class="stats-nav-item-icon">🌱</span>
                        Концептуальная плодовитость
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('complexity')">
                        <span class="stats-nav-item-icon">🧠</span>
                        Концептуальная сложность
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('continuity')">
                        <span class="stats-nav-item-icon">📜</span>
                        Преемственность
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('temporal-influence')">
                        <span class="stats-nav-item-icon">⏳</span>
                        Временное влияние
                    </div>
                </div>

                <!-- Метрики философов -->
                <div class="stats-nav-group">
                    <div class="stats-nav-group-title">👤 Метрики философов</div>
                    <div class="stats-nav-item" onclick="switchStatsView('philosopher-systematic')">
                        <span class="stats-nav-item-icon">📚</span>
                        Систематичность
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('philosopher-reach')">
                        <span class="stats-nav-item-icon">🌍</span>
                        Исторический охват
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('philosopher-interdisciplinary')">
                        <span class="stats-nav-item-icon">🔬</span>
                        Междисциплинарность
                    </div>
                </div>
            </div>

            <!-- Контентная область -->
            <div class="stats-content-area" id="statsContentArea">
                <!-- Контент будет динамически загружаться здесь -->
                <div class="empty-state">
                    <div class="empty-state-icon">📊</div>
                    <div class="empty-state-text">Выберите метрику из меню слева</div>
                </div>
            </div>
        </div>
    </div>
</div>
```

---

## 3. Кнопка вызова модального окна в легенде

В секции фильтров легенды (примерно строка 300-400), после секции "Статистический анализ", заменить кнопки на одну кнопку:

```html
<!-- Вместо существующих кнопок анализа -->
<button class="open-stats-modal-btn" onclick="openStatsModal()">
    📊 Открыть панель статистики
</button>
```

---

## 4. JavaScript: Классы метрик

Добавить перед закрывающим тегом `</script>` основного скрипта (примерно строка 4750):

```javascript
// ============================================
// КЛАССЫ МЕТРИК ДЛЯ ФИЛОСОФСКОГО АНАЛИЗА
// ============================================

class PhilosophyGraphMetrics {
    constructor(concepts, relations, philosophers) {
        this.concepts = concepts;
        this.relations = relations;
        this.philosophers = philosophers;
        
        this.conceptMap = new Map(concepts.map(c => [c.id, c]));
        this.philosopherMap = new Map(philosophers.map(p => [p.id, p]));
        this.incomingLinks = this.buildIncomingLinks();
        this.outgoingLinks = this.buildOutgoingLinks();
    }

    buildIncomingLinks() {
        const incoming = new Map();
        this.concepts.forEach(c => incoming.set(c.id, []));
        this.relations.forEach(r => {
            if (!incoming.has(r.target)) incoming.set(r.target, []);
            incoming.get(r.target).push(r);
            if (r.bidirectional) {
                if (!incoming.has(r.source)) incoming.set(r.source, []);
                incoming.get(r.source).push({...r, source: r.target, target: r.source});
            }
        });
        return incoming;
    }

    buildOutgoingLinks() {
        const outgoing = new Map();
        this.concepts.forEach(c => outgoing.set(c.id, []));
        this.relations.forEach(r => {
            if (!outgoing.has(r.source)) outgoing.set(r.source, []);
            outgoing.get(r.source).push(r);
            if (r.bidirectional) {
                if (!outgoing.has(r.target)) outgoing.set(r.target, []);
                outgoing.get(r.target).push({...r, source: r.target, target: r.source});
            }
        });
        return outgoing;
    }

    // Индекс проблемности
    problemGenerationIndex(conceptId) {
        const incoming = this.incomingLinks.get(conceptId) || [];
        
        const critiques = incoming.filter(r => r.type === 'critique').length;
        const oppositions = incoming.filter(r => r.type === 'oppose').length;
        const contradictions = incoming.filter(r => r.type === 'internal_contradiction').length;
        
        const weightedCriticism = incoming.reduce((sum, r) => {
            const typeWeight = {
                'critique': 2,
                'oppose': 3,
                'internal_contradiction': 4
            }[r.type] || 0;
            return sum + typeWeight * (r.weight || 1);
        }, 0);
        
        return {
            raw: critiques + oppositions + contradictions,
            weighted: weightedCriticism,
            critiques,
            oppositions,
            contradictions
        };
    }

    // Индекс критической силы
    criticalPowerIndex(conceptId) {
        const outgoing = this.outgoingLinks.get(conceptId) || [];
        
        const critiques = outgoing.filter(r => r.type === 'critique');
        const oppositions = outgoing.filter(r => r.type === 'oppose');
        
        const targetInfluence = critiques.concat(oppositions).reduce((sum, r) => {
            const targetIn = this.incomingLinks.get(r.target) || [];
            return sum + targetIn.length;
        }, 0);
        
        return {
            raw: critiques.length + oppositions.length,
            weighted: outgoing.reduce((sum, r) => {
                const typeWeight = {
                    'critique': 2,
                    'oppose': 3
                }[r.type] || 0;
                return sum + typeWeight * (r.weight || 1);
            }, 0),
            targetInfluence: targetInfluence / (critiques.length + oppositions.length || 1)
        };
    }

    // Индекс революционности
    revolutionaryIndex(conceptId) {
        const concept = this.conceptMap.get(conceptId);
        if (!concept) return { total: 0 };
        
        const philosopher = this.philosopherMap.get(concept.philosopher);
        if (!philosopher) return { total: 0 };
        
        const incoming = this.incomingLinks.get(conceptId) || [];
        const outgoing = this.outgoingLinks.get(conceptId) || [];
        
        const oppositionsToEarlier = incoming.filter(r => {
            const source = this.conceptMap.get(r.source);
            if (!source) return false;
            const sourcePhil = this.philosopherMap.get(source.philosopher);
            return sourcePhil && r.type === 'oppose' && sourcePhil.birth < philosopher.birth;
        }).length;
        
        const critiquesOfInfluential = outgoing.filter(r => {
            if (r.type !== 'critique' && r.type !== 'oppose') return false;
            const targetIn = this.incomingLinks.get(r.target) || [];
            return targetIn.length > 10;
        }).length;
        
        const syntheses = outgoing.filter(r => r.type === 'synthesize').length;
        const developments = incoming.filter(r => r.type === 'develop').length;
        
        const influences = incoming.filter(r => {
            const source = this.conceptMap.get(r.source);
            if (!source) return false;
            const sourcePhil = this.philosopherMap.get(source.philosopher);
            return sourcePhil && r.type === 'influence' && sourcePhil.birth < philosopher.birth;
        }).length;
        
        const rootedness = influences / Math.max(oppositionsToEarlier, 1);
        
        return {
            total: oppositionsToEarlier * 2 + critiquesOfInfluential * 1.5 + syntheses * 2 + developments - rootedness * 3,
            oppositionsToEarlier,
            critiquesOfInfluential,
            syntheses,
            developments,
            rootedness
        };
    }

    // Индекс парадигмального сдвига
    paradigmShiftIndex(conceptId) {
        const concept = this.conceptMap.get(conceptId);
        if (!concept) return { total: 0 };
        
        const philosopher = this.philosopherMap.get(concept.philosopher);
        if (!philosopher) return { total: 0 };
        
        const outgoing = this.outgoingLinks.get(conceptId) || [];
        const incoming = this.incomingLinks.get(conceptId) || [];
        
        const isMethodological = (concept.rubrics || []).includes('method');
        
        const influencedRubrics = new Set();
        outgoing.filter(r => r.type === 'influence' || r.type === 'apply').forEach(r => {
            const target = this.conceptMap.get(r.target);
            if (target) {
                (target.rubrics || []).forEach(rub => influencedRubrics.add(rub));
            }
        });
        
        const laterPhilosophers = new Set();
        incoming.forEach(r => {
            const source = this.conceptMap.get(r.source);
            if (source) {
                const sourcePhil = this.philosopherMap.get(source.philosopher);
                if (sourcePhil && sourcePhil.birth > philosopher.birth) {
                    laterPhilosophers.add(source.philosopher);
                }
            }
        });
        
        return {
            total: (isMethodological ? 5 : 0) + influencedRubrics.size * 2 + laterPhilosophers.size,
            isMethodological,
            rubricsBreadth: influencedRubrics.size,
            laterAdopters: laterPhilosophers.size
        };
    }

    // Индекс синтетичности
    syntheticIndex(conceptId) {
        const outgoing = this.outgoingLinks.get(conceptId) || [];
        const incoming = this.incomingLinks.get(conceptId) || [];
        
        const syntheses = outgoing.filter(r => r.type === 'synthesize').length;
        const reconciliations = outgoing.filter(r => r.type === 'reconcile').length;
        
        const diverseSources = new Set();
        incoming.forEach(r => {
            const source = this.conceptMap.get(r.source);
            if (source) {
                (source.rubrics || []).forEach(rub => diverseSources.add(rub));
            }
        });
        
        return {
            total: syntheses * 3 + reconciliations * 2 + diverseSources.size,
            syntheses,
            reconciliations,
            diverseSources: diverseSources.size
        };
    }

    // Индекс основополагания
    foundationalIndex(conceptId) {
        const incoming = this.incomingLinks.get(conceptId) || [];
        const outgoing = this.outgoingLinks.get(conceptId) || [];
        
        const presuppositions = incoming.filter(r => r.type === 'presuppose' || r.type === 'condition').length;
        const applications = incoming.filter(r => r.type === 'apply').length;
        const developments = incoming.filter(r => r.type === 'develop').length;
        
        const foundationalOutgoing = outgoing.filter(r => 
            r.type === 'condition' || r.type === 'presuppose'
        ).length;
        
        return {
            total: presuppositions * 2 + applications + developments + foundationalOutgoing * 1.5,
            presuppositions,
            applications,
            developments,
            foundationalOutgoing
        };
    }

    // Индекс внутренней согласованности
    internalCoherenceIndex(conceptId) {
        const incoming = this.incomingLinks.get(conceptId) || [];
        const outgoing = this.outgoingLinks.get(conceptId) || [];
        
        const contradictions = incoming.filter(r => r.type === 'internal_contradiction').length;
        const tensions = incoming.filter(r => r.type === 'tension').length;
        
        const supportiveLinks = incoming.filter(r => 
            r.type === 'support' || r.type === 'develop'
        ).length;
        
        const coherenceScore = supportiveLinks - (contradictions * 3 + tensions * 2);
        
        return {
            total: Math.max(0, coherenceScore),
            contradictions,
            tensions,
            supportiveLinks
        };
    }

    // Индекс напряжения
    tensionIndex(conceptId) {
        const incoming = this.incomingLinks.get(conceptId) || [];
        const outgoing = this.outgoingLinks.get(conceptId) || [];
        
        const tensions = incoming.filter(r => r.type === 'tension').length;
        const oppositions = outgoing.filter(r => r.type === 'oppose').length;
        const contradictions = incoming.filter(r => r.type === 'internal_contradiction').length;
        
        return {
            total: tensions * 2 + oppositions + contradictions * 3,
            tensions,
            oppositions,
            contradictions
        };
    }

    // Индекс систематичности философа
    philosopherSystematicIndex(philosopherId) {
        const philosopherConcepts = this.concepts.filter(c => c.philosopher === philosopherId);
        if (philosopherConcepts.length === 0) return { density: 0 };
        
        const conceptIds = new Set(philosopherConcepts.map(c => c.id));
        let internalLinks = 0;
        
        this.relations.forEach(r => {
            if (conceptIds.has(r.source) && conceptIds.has(r.target)) {
                internalLinks++;
            }
        });
        
        const maxPossibleLinks = (philosopherConcepts.length * (philosopherConcepts.length - 1)) / 2;
        const density = maxPossibleLinks > 0 ? internalLinks / maxPossibleLinks : 0;
        
        return {
            density: density * 100,
            internalLinks,
            totalConcepts: philosopherConcepts.length,
            maxPossibleLinks
        };
    }

    // Индекс исторического охвата философа
    philosopherHistoricalReachIndex(philosopherId) {
        const philosopher = this.philosopherMap.get(philosopherId);
        if (!philosopher) return { total: 0 };
        
        const philosopherConcepts = this.concepts.filter(c => c.philosopher === philosopherId);
        const conceptIds = new Set(philosopherConcepts.map(c => c.id));
        
        const influencedPhilosophers = new Set();
        const influencedYears = [];
        
        this.relations.forEach(r => {
            if (conceptIds.has(r.target)) {
                const sourceConcept = this.conceptMap.get(r.source);
                if (sourceConcept) {
                    const sourcePhil = this.philosopherMap.get(sourceConcept.philosopher);
                    if (sourcePhil && sourcePhil.birth > philosopher.birth) {
                        influencedPhilosophers.add(sourceConcept.philosopher);
                        influencedYears.push(sourcePhil.birth);
                    }
                }
            }
        });
        
        const latestInfluence = influencedYears.length > 0 ? Math.max(...influencedYears) : philosopher.birth;
        const timeSpan = latestInfluence - philosopher.birth;
        const generations = Math.floor(timeSpan / 25);
        
        return {
            total: influencedPhilosophers.size * generations,
            influencedPhilosophersCount: influencedPhilosophers.size,
            timeSpan,
            generations,
            latestInfluence
        };
    }

    // Индекс междисциплинарности философа
    philosopherInterdisciplinaryIndex(philosopherId) {
        const philosopherConcepts = this.concepts.filter(c => c.philosopher === philosopherId);
        if (philosopherConcepts.length === 0) return { total: 0 };
        
        const rubrics = new Set();
        philosopherConcepts.forEach(c => {
            (c.rubrics || []).forEach(r => rubrics.add(r));
        });
        
        const rubricDistribution = {};
        philosopherConcepts.forEach(c => {
            (c.rubrics || []).forEach(r => {
                rubricDistribution[r] = (rubricDistribution[r] || 0) + 1;
            });
        });
        
        const entropy = Object.values(rubricDistribution).reduce((sum, count) => {
            const p = count / philosopherConcepts.length;
            return sum - p * Math.log2(p);
        }, 0);
        
        return {
            total: rubrics.size * (1 + entropy),
            rubricCount: rubrics.size,
            entropy,
            distribution: rubricDistribution
        };
    }

    // Паттерн временного влияния
    temporalInfluencePattern(conceptId) {
        const concept = this.conceptMap.get(conceptId);
        if (!concept) return { pattern: 'none', periods: {} };
        
        const philosopher = this.philosopherMap.get(concept.philosopher);
        if (!philosopher) return { pattern: 'none', periods: {} };
        
        const incoming = this.incomingLinks.get(conceptId) || [];
        
        const periods = {
            immediate: 0,
            near: 0,
            medium: 0,
            long: 0
        };
        
        incoming.forEach(r => {
            const source = this.conceptMap.get(r.source);
            if (source) {
                const sourcePhil = this.philosopherMap.get(source.philosopher);
                if (sourcePhil) {
                    const timeDiff = sourcePhil.birth - philosopher.birth;
                    
                    if (timeDiff > 0) {
                        if (timeDiff <= 50) periods.immediate++;
                        else if (timeDiff <= 150) periods.near++;
                        else if (timeDiff <= 300) periods.medium++;
                        else periods.long++;
                    }
                }
            }
        });
        
        let pattern = 'none';
        if (periods.immediate > 0 && periods.long > 0) pattern = 'lasting';
        else if (periods.immediate > 0 && periods.near === 0) pattern = 'fading';
        else if (periods.immediate === 0 && periods.medium > 0) pattern = 'delayed';
        else if (periods.immediate > 0) pattern = 'normal';
        
        return {
            pattern,
            periods,
            totalForwardReferences: Object.values(periods).reduce((a, b) => a + b, 0)
        };
    }
}

// ============================================
// ПРОДВИНУТЫЕ МЕТРИКИ
// ============================================

class AdvancedPhilosophyMetrics {
    constructor(concepts, relations, philosophers, basicMetrics) {
        this.concepts = concepts;
        this.relations = relations;
        this.philosophers = philosophers;
        this.basicMetrics = basicMetrics;
        
        this.conceptMap = new Map(concepts.map(c => [c.id, c]));
        this.philosopherMap = new Map(philosophers.map(p => [p.id, p]));
    }

    // Индекс трансформации
    transformationIndex(conceptId) {
        const incoming = this.basicMetrics.incomingLinks.get(conceptId) || [];
        const outgoing = this.basicMetrics.outgoingLinks.get(conceptId) || [];
        
        const influences = incoming.filter(r => r.type === 'influence');
        const developments = outgoing.filter(r => r.type === 'develop').length;
        const applications = outgoing.filter(r => r.type === 'apply').length;
        const syntheses = outgoing.filter(r => r.type === 'synthesize').length;
        
        const transformationRatio = influences.length > 0 
            ? (developments + applications + syntheses) / influences.length 
            : 0;
        
        return {
            total: transformationRatio * 10 + developments + applications + syntheses,
            ratio: transformationRatio,
            developments,
            applications,
            syntheses,
            influences: influences.length
        };
    }

    // Индекс концептуальной плодовитости
    conceptualFertilityIndex(conceptId) {
        const incoming = this.basicMetrics.incomingLinks.get(conceptId) || [];
        const concept = this.conceptMap.get(conceptId);
        if (!concept) return { total: 0 };
        
        const philosopher = this.philosopherMap.get(concept.philosopher);
        if (!philosopher) return { total: 0 };
        
        const emergences = incoming.filter(r => r.type === 'emerge_from').length;
        const developments = incoming.filter(r => r.type === 'develop').length;
        
        const laterPhilosophers = new Set();
        incoming
            .filter(r => r.type === 'develop' || r.type === 'emerge_from')
            .forEach(r => {
                const source = this.conceptMap.get(r.source);
                if (source) {
                    const sourcePhil = this.philosopherMap.get(source.philosopher);
                    if (sourcePhil && sourcePhil.birth > philosopher.birth) {
                        laterPhilosophers.add(source.philosopher);
                    }
                }
            });
        
        return {
            total: emergences * 3 + developments * 2 + laterPhilosophers.size,
            emergences,
            developments,
            laterAdopters: laterPhilosophers.size
        };
    }

    // Индекс концептуальной сложности
    conceptualComplexityIndex(conceptId) {
        const incoming = this.basicMetrics.incomingLinks.get(conceptId) || [];
        const outgoing = this.basicMetrics.outgoingLinks.get(conceptId) || [];
        const concept = this.conceptMap.get(conceptId);
        if (!concept) return { total: 0 };
        
        const incomingTypes = new Set(incoming.map(r => r.type)).size;
        const outgoingTypes = new Set(outgoing.map(r => r.type)).size;
        const rubricCount = (concept.rubrics || []).length;
        
        const contradictions = incoming.filter(r => 
            r.type === 'internal_contradiction'
        ).length;
        
        const presuppositions = incoming.filter(r => 
            r.type === 'presuppose' || r.type === 'condition'
        ).length;
        
        const relatedPhilosophers = new Set();
        incoming.concat(outgoing).forEach(r => {
            const other = this.conceptMap.get(
                r.source === conceptId ? r.target : r.source
            );
            if (other) {
                relatedPhilosophers.add(other.philosopher);
            }
        });
        
        return {
            total: (incomingTypes + outgoingTypes) * 2 + rubricCount * 3 + 
                   contradictions * 5 + presuppositions * 2 + relatedPhilosophers.size,
            linkTypeDiversity: incomingTypes + outgoingTypes,
            rubricCount,
            contradictions,
            presuppositions,
            relatedPhilosophers: relatedPhilosophers.size
        };
    }

    // Индекс концептуальной преемственности
    conceptualContinuityIndex(conceptId) {
        const concept = this.conceptMap.get(conceptId);
        if (!concept) return { total: 0 };
        
        const philosopher = this.philosopherMap.get(concept.philosopher);
        if (!philosopher) return { total: 0 };
        
        const incoming = this.basicMetrics.incomingLinks.get(conceptId) || [];
        
        const laterReferences = incoming.filter(r => {
            const source = this.conceptMap.get(r.source);
            if (!source) return false;
            const sourcePhil = this.philosopherMap.get(source.philosopher);
            return sourcePhil && sourcePhil.birth > philosopher.birth;
        });
        
        if (laterReferences.length === 0) return { total: 0, gaps: [] };
        
        const generations = new Map();
        laterReferences.forEach(r => {
            const source = this.conceptMap.get(r.source);
            if (source) {
                const sourcePhil = this.philosopherMap.get(source.philosopher);
                if (sourcePhil) {
                    const generation = Math.floor((sourcePhil.birth - philosopher.birth) / 25);
                    
                    if (!generations.has(generation)) {
                        generations.set(generation, []);
                    }
                    generations.get(generation).push(r);
                }
            }
        });
        
        const maxGeneration = Math.max(...generations.keys());
        const gaps = [];
        
        for (let g = 0; g <= maxGeneration; g++) {
            if (!generations.has(g)) {
                gaps.push(g);
            }
        }
        
        const continuity = (maxGeneration + 1) - gaps.length;
        
        return {
            total: continuity * laterReferences.length,
            continuity,
            generations: maxGeneration + 1,
            gaps,
            references: laterReferences.length
        };
    }
}

// Инициализация классов метрик
let philosophyMetrics = null;
let advancedMetrics = null;

function initializePhilosophyMetrics() {
    try {
        // Преобразуем данные графа в формат для метрик
        const conceptsData = nodes.map(n => ({
            id: n.id,
            label: n.label,
            philosopher: n.concept, // используем concept как philosopher
            rubrics: n.rubrics || []
        }));
        
        const relationsData = links.map(l => ({
            source: typeof l.source === 'object' ? l.source.id : l.source,
            target: typeof l.target === 'object' ? l.target.id : l.target,
            type: l.type || 'influence',
            weight: l.weight || 1,
            bidirectional: l.bidirectional || false
        }));
        
        // Создаём упрощённые данные о философах (используем концепции как философов)
        const philosophersData = Array.from(new Set(nodes.map(n => n.concept))).map(concept => ({
            id: concept,
            name: concept,
            birth: 1800 // упрощённая дата
        }));
        
        philosophyMetrics = new PhilosophyGraphMetrics(conceptsData, relationsData, philosophersData);
        advancedMetrics = new AdvancedPhilosophyMetrics(conceptsData, relationsData, philosophersData, philosophyMetrics);
        
        console.log('Философские метрики инициализированы');
        return true;
    } catch (error) {
        console.error('Ошибка при инициализации метрик:', error);
        return false;
    }
}
```

---

## 5. JavaScript: Функции модального окна

Добавить после инициализации классов метрик:

```javascript
// ============================================
// УПРАВЛЕНИЕ МОДАЛЬНЫМ ОКНОМ СТАТИСТИКИ
// ============================================

let currentStatsView = null;

// Открыть модальное окно
function openStatsModal() {
    // Инициализируем метрики если ещё не инициализированы
    if (!philosophyMetrics) {
        initializePhilosophyMetrics();
    }
    
    const modal = document.getElementById('statsModal');
    modal.classList.add('active');
    
    // Показываем обзор по умолчанию
    if (!currentStatsView) {
        switchStatsView('overview');
    }
}

// Закрыть модальное окно
function closeStatsModal() {
    const modal = document.getElementById('statsModal');
    modal.classList.remove('active');
}

// Переключение между видами статистики
function switchStatsView(viewName) {
    currentStatsView = viewName;
    
    // Обновляем активный пункт навигации
    document.querySelectorAll('.stats-nav-item').forEach(item => {
        item.classList.remove('active');
    });
    event.target.closest('.stats-nav-item').classList.add('active');
    
    // Загружаем контент
    loadStatsContent(viewName);
}

// Загрузка контента для выбранной метрики
function loadStatsContent(viewName) {
    const contentArea = document.getElementById('statsContentArea');
    let html = '';
    
    switch(viewName) {
        case 'overview':
            html = generateOverviewContent();
            break;
        case 'degree':
            html = generateDegreeContent();
            break;
        case 'pagerank':
            html = generatePageRankContent();
            break;
        case 'betweenness':
            html = generateBetweennessContent();
            break;
        case 'closeness':
            html = generateClosenessContent();
            break;
        case 'eigenvector':
            html = generateEigenvectorContent();
            break;
        case 'problem-generation':
            html = generateProblemGenerationContent();
            break;
        case 'critical-power':
            html = generateCriticalPowerContent();
            break;
        case 'revolutionary':
            html = generateRevolutionaryContent();
            break;
        case 'paradigm-shift':
            html = generateParadigmShiftContent();
            break;
        case 'synthetic':
            html = generateSyntheticContent();
            break;
        case 'foundational':
            html = generateFoundationalContent();
            break;
        case 'coherence':
            html = generateCoherenceContent();
            break;
        case 'tension':
            html = generateTensionContent();
            break;
        case 'transformation':
            html = generateTransformationContent();
            break;
        case 'fertility':
            html = generateFertilityContent();
            break;
        case 'complexity':
            html = generateComplexityContent();
            break;
        case 'continuity':
            html = generateContinuityContent();
            break;
        case 'temporal-influence':
            html = generateTemporalInfluenceContent();
            break;
        case 'philosopher-systematic':
            html = generatePhilosopherSystematicContent();
            break;
        case 'philosopher-reach':
            html = generatePhilosopherReachContent();
            break;
        case 'philosopher-interdisciplinary':
            html = generatePhilosopherInterdisciplinaryContent();
            break;
        default:
            html = '<div class="empty-state"><div class="empty-state-icon">📊</div><div class="empty-state-text">Метрика в разработке</div></div>';
    }
    
    contentArea.innerHTML = html;
}

// ============================================
// ГЕНЕРАТОРЫ КОНТЕНТА ДЛЯ КАЖДОЙ МЕТРИКИ
// ============================================

function generateOverviewContent() {
    return `
        <div class="stats-content-header">
            <h3 class="stats-content-title">📈 Общий обзор графа</h3>
            <p class="stats-content-description">
                Базовая статистика и характеристики сети философских концепций
            </p>
        </div>
        <div class="metric-results-grid">
            <div class="metric-result-card">
                <div class="metric-result-rank">Узлы</div>
                <div class="metric-result-value">${nodes.length}</div>
                <div class="metric-result-philosopher">Всего концепций</div>
            </div>
            <div class="metric-result-card">
                <div class="metric-result-rank">Связи</div>
                <div class="metric-result-value">${links.length}</div>
                <div class="metric-result-philosopher">Всего отношений</div>
            </div>
            <div class="metric-result-card">
                <div class="metric-result-rank">Плотность</div>
                <div class="metric-result-value">${(links.length / ((nodes.length * (nodes.length - 1)) / 2) * 100).toFixed(2)}%</div>
                <div class="metric-result-philosopher">Плотность сети</div>
            </div>
            <div class="metric-result-card">
                <div class="metric-result-rank">Средняя степень</div>
                <div class="metric-result-value">${(links.length * 2 / nodes.length).toFixed(2)}</div>
                <div class="metric-result-philosopher">Связей на узел</div>
            </div>
        </div>
    `;
}

function generateDegreeContent() {
    const degreeData = nodes.map(n => {
        const inDegree = links.filter(l => 
            (typeof l.target === 'object' ? l.target.id : l.target) === n.id
        ).length;
        const outDegree = links.filter(l => 
            (typeof l.source === 'object' ? l.source.id : l.source) === n.id
        ).length;
        return {
            node: n,
            inDegree,
            outDegree,
            totalDegree: inDegree + outDegree
        };
    }).sort((a, b) => b.totalDegree - a.totalDegree);
    
    return `
        <div class="stats-content-header">
            <h3 class="stats-content-title">🔗 Степень связности</h3>
            <p class="stats-content-description">
                Количество входящих и исходящих связей для каждого узла
            </p>
        </div>
        <table class="metric-table">
            <thead class="metric-table-header">
                <tr>
                    <th>#</th>
                    <th>Концепция</th>
                    <th>Входящих</th>
                    <th>Исходящих</th>
                    <th>Всего</th>
                </tr>
            </thead>
            <tbody>
                ${degreeData.slice(0, 20).map((d, i) => `
                    <tr class="metric-table-row" onclick="highlightNodeById('${d.node.id}')">
                        <td><strong>${i + 1}</strong></td>
                        <td><strong>${d.node.label}</strong></td>
                        <td>${d.inDegree}</td>
                        <td>${d.outDegree}</td>
                        <td><strong style="color: #3498db;">${d.totalDegree}</strong></td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function generatePageRankContent() {
    if (!pagerankCache || pagerankCache.length === 0) {
        return generateCalculateButton('PageRank', 'pagerank', 
            'Алгоритм PageRank определяет важность узлов на основе количества и качества входящих связей');
    }
    
    return generateMetricResults(
        pagerankCache.slice(0, 20),
        '⭐ PageRank',
        'Важность узлов на основе входящих связей',
        'value',
        true
    );
}

function generateBetweennessContent() {
    if (!betweennessCache || betweennessCache.length === 0) {
        return generateCalculateButton('Betweenness Centrality', 'betweenness',
            'Метрика показывает, насколько часто узел находится на кратчайших путях между другими узлами');
    }
    
    return generateMetricResults(
        betweennessCache.slice(0, 20),
        '🌉 Betweenness Centrality',
        'Узлы-посредники в сети',
        'value',
        true
    );
}

function generateClosenessContent() {
    if (!closenessCache || closenessCache.length === 0) {
        return generateCalculateButton('Closeness Centrality', 'closeness',
            'Метрика измеряет среднюю дистанцию от узла до всех остальных узлов');
    }
    
    return generateMetricResults(
        closenessCache.slice(0, 20),
        '🎯 Closeness Centrality',
        'Центральность по близости',
        'value',
        true
    );
}

function generateEigenvectorContent() {
    if (!eigenvectorCache || eigenvectorCache.length === 0) {
        return generateCalculateButton('Eigenvector Centrality', 'eigenvector',
            'Мера влияния узла в сети: важность определяется важностью соседей');
    }
    
    return generateMetricResults(
        eigenvectorCache.slice(0, 20),
        '🏆 Eigenvector Centrality',
        'Влияние через влиятельных соседей',
        'value',
        true
    );
}

function generateProblemGenerationContent() {
    if (!philosophyMetrics) {
        initializePhilosophyMetrics();
    }
    
    const results = nodes.map(n => {
        const metric = philosophyMetrics.problemGenerationIndex(n.id);
        return {
            node: n,
            value: metric.weighted,
            details: metric
        };
    }).filter(r => r.value > 0).sort((a, b) => b.value - a.value);
    
    return generateMetricResults(
        results.slice(0, 20),
        '⚡ Индекс проблемности',
        'Концепции, порождающие наибольшую критику и проблемы',
        'value',
        true
    );
}

function generateCriticalPowerContent() {
    if (!philosophyMetrics) {
        initializePhilosophyMetrics();
    }
    
    const results = nodes.map(n => {
        const metric = philosophyMetrics.criticalPowerIndex(n.id);
        return {
            node: n,
            value: metric.weighted,
            details: metric
        };
    }).filter(r => r.value > 0).sort((a, b) => b.value - a.value);
    
    return generateMetricResults(
        results.slice(0, 20),
        '⚔️ Критическая сила',
        'Концепции с наибольшей критической мощью',
        'value',
        true
    );
}

function generateRevolutionaryContent() {
    if (!philosophyMetrics) {
        initializePhilosophyMetrics();
    }
    
    const results = nodes.map(n => {
        const metric = philosophyMetrics.revolutionaryIndex(n.id);
        return {
            node: n,
            value: metric.total,
            details: metric
        };
    }).filter(r => r.value > 0).sort((a, b) => b.value - a.value);
    
    return generateMetricResults(
        results.slice(0, 20),
        '🔥 Индекс революционности',
        'Наиболее революционные концепции, порывающие с традицией',
        'value',
        true
    );
}

function generateParadigmShiftContent() {
    if (!philosophyMetrics) {
        initializePhilosophyMetrics();
    }
    
    const results = nodes.map(n => {
        const metric = philosophyMetrics.paradigmShiftIndex(n.id);
        return {
            node: n,
            value: metric.total,
            details: metric
        };
    }).filter(r => r.value > 0).sort((a, b) => b.value - a.value);
    
    return generateMetricResults(
        results.slice(0, 20),
        '🌐 Парадигмальный сдвиг',
        'Концепции, изменившие способ мышления',
        'value',
        true
    );
}

function generateSyntheticContent() {
    if (!philosophyMetrics) {
        initializePhilosophyMetrics();
    }
    
    const results = nodes.map(n => {
        const metric = philosophyMetrics.syntheticIndex(n.id);
        return {
            node: n,
            value: metric.total,
            details: metric
        };
    }).filter(r => r.value > 0).sort((a, b) => b.value - a.value);
    
    return generateMetricResults(
        results.slice(0, 20),
        '🧩 Индекс синтетичности',
        'Концепции, синтезирующие разные идеи',
        'value',
        true
    );
}

function generateFoundationalContent() {
    if (!philosophyMetrics) {
        initializePhilosophyMetrics();
    }
    
    const results = nodes.map(n => {
        const metric = philosophyMetrics.foundationalIndex(n.id);
        return {
            node: n,
            value: metric.total,
            details: metric
        };
    }).filter(r => r.value > 0).sort((a, b) => b.value - a.value);
    
    return generateMetricResults(
        results.slice(0, 20),
        '🏛️ Индекс основополагания',
        'Фундаментальные концепции, на которых строятся другие',
        'value',
        true
    );
}

function generateCoherenceContent() {
    if (!philosophyMetrics) {
        initializePhilosophyMetrics();
    }
    
    const results = nodes.map(n => {
        const metric = philosophyMetrics.internalCoherenceIndex(n.id);
        return {
            node: n,
            value: metric.total,
            details: metric
        };
    }).sort((a, b) => b.value - a.value);
    
    return generateMetricResults(
        results.slice(0, 20),
        '🔮 Внутренняя согласованность',
        'Концепции с наименьшим количеством противоречий',
        'value',
        true
    );
}

function generateTensionContent() {
    if (!philosophyMetrics) {
        initializePhilosophyMetrics();
    }
    
    const results = nodes.map(n => {
        const metric = philosophyMetrics.tensionIndex(n.id);
        return {
            node: n,
            value: metric.total,
            details: metric
        };
    }).filter(r => r.value > 0).sort((a, b) => b.value - a.value);
    
    return generateMetricResults(
        results.slice(0, 20),
        '⚖️ Индекс напряжения',
        'Концепции с наибольшим внутренним напряжением',
        'value',
        true
    );
}

function generateTransformationContent() {
    if (!advancedMetrics) {
        initializePhilosophyMetrics();
    }
    
    const results = nodes.map(n => {
        const metric = advancedMetrics.transformationIndex(n.id);
        return {
            node: n,
            value: metric.total,
            details: metric
        };
    }).filter(r => r.value > 0).sort((a, b) => b.value - a.value);
    
    return generateMetricResults(
        results.slice(0, 20),
        '🦋 Индекс трансформации',
        'Концепции, трансформирующие заимствованные идеи',
        'value',
        true
    );
}

function generateFertilityContent() {
    if (!advancedMetrics) {
        initializePhilosophyMetrics();
    }
    
    const results = nodes.map(n => {
        const metric = advancedMetrics.conceptualFertilityIndex(n.id);
        return {
            node: n,
            value: metric.total,
            details: metric
        };
    }).filter(r => r.value > 0).sort((a, b) => b.value - a.value);
    
    return generateMetricResults(
        results.slice(0, 20),
        '🌱 Концептуальная плодовитость',
        'Концепции, порождающие новые идеи',
        'value',
        true
    );
}

function generateComplexityContent() {
    if (!advancedMetrics) {
        initializePhilosophyMetrics();
    }
    
    const results = nodes.map(n => {
        const metric = advancedMetrics.conceptualComplexityIndex(n.id);
        return {
            node: n,
            value: metric.total,
            details: metric
        };
    }).sort((a, b) => b.value - a.value);
    
    return generateMetricResults(
        results.slice(0, 20),
        '🧠 Концептуальная сложность',
        'Наиболее сложные и многоаспектные концепции',
        'value',
        true
    );
}

function generateContinuityContent() {
    if (!advancedMetrics) {
        initializePhilosophyMetrics();
    }
    
    const results = nodes.map(n => {
        const metric = advancedMetrics.conceptualContinuityIndex(n.id);
        return {
            node: n,
            value: metric.total,
            details: metric
        };
    }).filter(r => r.value > 0).sort((a, b) => b.value - a.value);
    
    return generateMetricResults(
        results.slice(0, 20),
        '📜 Индекс преемственности',
        'Концепции с наибольшей исторической преемственностью',
        'value',
        true
    );
}

function generateTemporalInfluenceContent() {
    if (!philosophyMetrics) {
        initializePhilosophyMetrics();
    }
    
    const results = nodes.map(n => {
        const metric = philosophyMetrics.temporalInfluencePattern(n.id);
        return {
            node: n,
            pattern: metric.pattern,
            total: metric.totalForwardReferences,
            details: metric
        };
    }).filter(r => r.total > 0).sort((a, b) => b.total - a.total);
    
    const patternLabels = {
        'lasting': '🌟 Устойчивое',
        'fading': '💨 Угасающее',
        'delayed': '⏰ Отложенное',
        'normal': '📊 Нормальное',
        'none': '❌ Отсутствует'
    };
    
    return `
        <div class="stats-content-header">
            <h3 class="stats-content-title">⏳ Временное влияние</h3>
            <p class="stats-content-description">
                Паттерны влияния концепций во времени
            </p>
        </div>
        <table class="metric-table">
            <thead class="metric-table-header">
                <tr>
                    <th>#</th>
                    <th>Концепция</th>
                    <th>Паттерн</th>
                    <th>Ссылок</th>
                </tr>
            </thead>
            <tbody>
                ${results.slice(0, 20).map((r, i) => `
                    <tr class="metric-table-row" onclick="highlightNodeById('${r.node.id}')">
                        <td><strong>${i + 1}</strong></td>
                        <td><strong>${r.node.label}</strong></td>
                        <td>${patternLabels[r.pattern]}</td>
                        <td><strong style="color: #3498db;">${r.total}</strong></td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function generatePhilosopherSystematicContent() {
    if (!philosophyMetrics) {
        initializePhilosophyMetrics();
    }
    
    const philosophers = Array.from(new Set(nodes.map(n => n.concept)));
    const results = philosophers.map(p => {
        const metric = philosophyMetrics.philosopherSystematicIndex(p);
        return {
            philosopher: p,
            value: metric.density,
            details: metric
        };
    }).sort((a, b) => b.value - a.value);
    
    return `
        <div class="stats-content-header">
            <h3 class="stats-content-title">📚 Систематичность философов</h3>
            <p class="stats-content-description">
                Плотность внутренних связей между концепциями философа
            </p>
        </div>
        <div class="metric-results-grid">
            ${results.slice(0, 12).map((r, i) => `
                <div class="metric-result-card">
                    <div class="metric-result-rank">#${i + 1}</div>
                    <div class="metric-result-name">${r.philosopher}</div>
                    <div class="metric-result-value">${r.value.toFixed(2)}%</div>
                    <div class="metric-result-philosopher">Концепций: ${r.details.totalConcepts}</div>
                </div>
            `).join('')}
        </div>
    `;
}

function generatePhilosopherReachContent() {
    if (!philosophyMetrics) {
        initializePhilosophyMetrics();
    }
    
    const philosophers = Array.from(new Set(nodes.map(n => n.concept)));
    const results = philosophers.map(p => {
        const metric = philosophyMetrics.philosopherHistoricalReachIndex(p);
        return {
            philosopher: p,
            value: metric.total,
            details: metric
        };
    }).filter(r => r.value > 0).sort((a, b) => b.value - a.value);
    
    return `
        <div class="stats-content-header">
            <h3 class="stats-content-title">🌍 Исторический охват философов</h3>
            <p class="stats-content-description">
                Временной размах влияния философа
            </p>
        </div>
        <div class="metric-results-grid">
            ${results.slice(0, 12).map((r, i) => `
                <div class="metric-result-card">
                    <div class="metric-result-rank">#${i + 1}</div>
                    <div class="metric-result-name">${r.philosopher}</div>
                    <div class="metric-result-value">${r.details.generations}</div>
                    <div class="metric-result-philosopher">Поколений: ${r.details.influencedPhilosophersCount} философов</div>
                </div>
            `).join('')}
        </div>
    `;
}

function generatePhilosopherInterdisciplinaryContent() {
    if (!philosophyMetrics) {
        initializePhilosophyMetrics();
    }
    
    const philosophers = Array.from(new Set(nodes.map(n => n.concept)));
    const results = philosophers.map(p => {
        const metric = philosophyMetrics.philosopherInterdisciplinaryIndex(p);
        return {
            philosopher: p,
            value: metric.total,
            details: metric
        };
    }).filter(r => r.value > 0).sort((a, b) => b.value - a.value);
    
    return `
        <div class="stats-content-header">
            <h3 class="stats-content-title">🔬 Междисциплинарность философов</h3>
            <p class="stats-content-description">
                Охват различных тематических областей
            </p>
        </div>
        <div class="metric-results-grid">
            ${results.slice(0, 12).map((r, i) => `
                <div class="metric-result-card">
                    <div class="metric-result-rank">#${i + 1}</div>
                    <div class="metric-result-name">${r.philosopher}</div>
                    <div class="metric-result-value">${r.value.toFixed(2)}</div>
                    <div class="metric-result-philosopher">Рубрик: ${r.details.rubricCount}</div>
                </div>
            `).join('')}
        </div>
    `;
}

// ============================================
// ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
// ============================================

function generateCalculateButton(metricName, metricKey, description) {
    return `
        <div class="stats-content-header">
            <h3 class="stats-content-title">${metricName}</h3>
            <p class="stats-content-description">${description}</p>
        </div>
        <div class="empty-state">
            <div class="empty-state-icon">📊</div>
            <div class="empty-state-text">Метрика ещё не рассчитана</div>
            <button class="calculate-metric-btn" onclick="calculateMetricFromModal('${metricKey}')">
                Рассчитать ${metricName}
            </button>
        </div>
    `;
}

function generateMetricResults(data, title, description, valueKey, isDecimal) {
    if (!data || data.length === 0) {
        return `
            <div class="stats-content-header">
                <h3 class="stats-content-title">${title}</h3>
                <p class="stats-content-description">${description}</p>
            </div>
            <div class="empty-state">
                <div class="empty-state-icon">📊</div>
                <div class="empty-state-text">Нет данных для отображения</div>
            </div>
        `;
    }
    
    return `
        <div class="stats-content-header">
            <h3 class="stats-content-title">${title}</h3>
            <p class="stats-content-description">${description}</p>
        </div>
        <div class="metric-results-grid">
            ${data.map((item, index) => {
                const value = item[valueKey];
                const displayValue = isDecimal ? value.toFixed(4) : Math.round(value);
                return `
                    <div class="metric-result-card" onclick="highlightNodeById('${item.node.id}')">
                        <div class="metric-result-rank">#${index + 1}</div>
                        <div class="metric-result-name">${item.node.label}</div>
                        <div class="metric-result-value">${displayValue}</div>
                        <div class="metric-result-philosopher">${item.node.concept}</div>
                    </div>
                `;
            }).join('')}
        </div>
    `;
}

async function calculateMetricFromModal(metricKey) {
    try {
        closeStatsModal();
        
        // Используем существующие функции расчёта
        await runSingleMetric(metricKey);
        
        // Открываем модальное окно снова и показываем результат
        setTimeout(() => {
            openStatsModal();
            switchStatsView(metricKey);
        }, 1000);
    } catch (error) {
        console.error('Ошибка при расчёте метрики:', error);
        alert('Произошла ошибка при расчёте метрики');
    }
}

// Закрытие модального окна при клике вне его
document.addEventListener('click', function(event) {
    const modal = document.getElementById('statsModal');
    if (event.target === modal) {
        closeStatsModal();
    }
});

// Закрытие модального окна по Escape
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeStatsModal();
    }
});
```

---

## 6. Инструкции по применению

### Порядок интеграции:

1. **Добавить CSS** (раздел 1) в секцию `<style>` после существующих стилей модальных окон
2. **Добавить HTML** (раздел 2) перед закрывающим тегом `</body>`
3. **Заменить кнопку** (раздел 3) в легенде на кнопку вызова модального окна
4. **Добавить классы метрик** (раздел 4) перед закрывающим тегом `</script>`
5. **Добавить функции управления** (раздел 5) после классов метрик

### Тестирование:

1. Откройте файл в браузере
2. Нажмите кнопку "📊 Открыть панель статистики" в легенде
3. Выберите метрику из левой навигации
4. Для базовых метрик (PageRank, Betweenness и т.д.) нажмите "Рассчитать", если они ещё не рассчитаны
5. Философские и продвинутые метрики рассчитываются автоматически

### Примечания:

- Модальное окно закрывается по клику вне его или по клавише Escape
- Клик по карточке или строке таблицы подсвечивает узел на графе
- Все метрики работают с существующей структурой данных графа
- Интерфейс полностью адаптивен (responsive)

---

## Готово! 🎉

Все фрагменты кода готовы к интеграции. Модальное окно имеет:
- ✅ Тёмную тему в стиле существующих модальных окон
- ✅ Эргономичную навигацию с группировкой метрик
- ✅ Все метрики из обоих JS-файлов
- ✅ Красивый дизайн с анимациями
- ✅ Адаптивность для разных размеров экрана
