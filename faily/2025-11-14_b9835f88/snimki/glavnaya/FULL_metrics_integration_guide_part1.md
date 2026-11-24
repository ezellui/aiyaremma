# ПОЛНОЕ РУКОВОДСТВО ПО ИНТЕГРАЦИИ МЕТРИК
## Версия 2.0 - Исчерпывающая

---

## 📋 СОДЕРЖАНИЕ

1. [Что удалить из исходного кода](#что-удалить)
2. [CSS для модального окна](#css)
3. [HTML разметка](#html)
4. [Классы метрик (полная версия)](#классы-метрик)
5. [Описания метрик](#описания-метрик)
6. [Функции управления модальным окном](#функции-управления)
7. [Генераторы контента для всех метрик](#генераторы-контента)
8. [Функция визуализации размером узлов](#визуализация)
9. [Инструкции по применению](#инструкции)

---

## 1. ЧТО УДАЛИТЬ ИЗ ИСХОДНОГО КОДА {#что-удалить}

### Удалить следующие секции:

**A. В HTML (внутри тега `<div id="legend">`):**

Найти и удалить секцию "Статистический анализ" (примерно строки 300-380):
```html
<!-- Секция "Статистический анализ" -->
<div class="legend-section">
    <h4>📊 Статистический анализ</h4>
    <!-- ... весь блок с кнопками анализа ... -->
</div>
```

**B. В JavaScript:**

Найти и удалить/закомментировать функции (примерно строки 4240-4630):
```javascript
// Функция switchMetric() - УДАЛИТЬ или закомментировать
// Функция showMetric() - УДАЛИТЬ или закомментировать  
// Функция formatMetricResults() - УДАЛИТЬ или закомментировать
```

**ВАЖНО:** Не удаляйте следующие функции - они будут использоваться модальным окном:
- `runSingleMetric()`
- `calculatePageRank()`
- `calculateBetweennessAsync()`
- `calculateClosenessCentrality()`
- `calculateEigenvectorCentrality()`
- `calculateWeightedClustering()`
- `calculateLocalCohesion()`
- `calculateRichClubCoefficient()`
- `visualizeMetricBySize()` (если она есть)
- `resetNodeSizes()` (если она есть)
- `applyMetricVisualization()` (если она есть)

---

## 2. CSS ДЛЯ МОДАЛЬНОГО ОКНА {#css}

Добавить в секцию `<style>` после существующих стилей (примерно после строки 500):

```css
/* ============================================ */
/* МОДАЛЬНОЕ ОКНО РАСШИРЕННОЙ СТАТИСТИКИ */
/* ============================================ */

#statsModal {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.88);
    z-index: 9999;
    backdrop-filter: blur(8px);
}

#statsModal.active {
    display: flex;
    align-items: center;
    justify-content: center;
    animation: statsModalFadeIn 0.3s ease-out;
}

@keyframes statsModalFadeIn {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}

.stats-modal-content {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border-radius: 20px;
    width: 92%;
    max-width: 1600px;
    height: 90vh;
    max-height: 950px;
    box-shadow: 0 25px 70px rgba(0, 0, 0, 0.6);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    border: 2px solid rgba(108, 92, 231, 0.4);
    animation: statsModalSlideIn 0.4s ease-out;
}

@keyframes statsModalSlideIn {
    from {
        transform: translateY(-30px) scale(0.95);
        opacity: 0;
    }
    to {
        transform: translateY(0) scale(1);
        opacity: 1;
    }
}

.stats-modal-header {
    background: linear-gradient(135deg, rgba(108, 92, 231, 0.25), rgba(52, 152, 219, 0.25));
    padding: 22px 35px;
    border-bottom: 2px solid rgba(108, 92, 231, 0.4);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 15px;
}

.stats-modal-title-section {
    flex: 1;
}

.stats-modal-header h2 {
    color: #fff;
    margin: 0 0 5px 0;
    font-size: 26px;
    font-weight: 700;
    text-shadow: 0 2px 6px rgba(0, 0, 0, 0.4);
}

.stats-modal-subtitle {
    color: rgba(255, 255, 255, 0.7);
    font-size: 13px;
    margin: 0;
}

.stats-header-controls {
    display: flex;
    gap: 15px;
    align-items: center;
}

.stats-parameter-toggle {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 15px;
    background: rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    transition: all 0.3s;
    cursor: pointer;
}

.stats-parameter-toggle:hover {
    background: rgba(255, 255, 255, 0.12);
}

.stats-parameter-toggle input[type="checkbox"] {
    width: 18px;
    height: 18px;
    cursor: pointer;
    accent-color: #6c5ce7;
}

.stats-parameter-toggle label {
    color: #fff;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    user-select: none;
}

.stats-close-btn {
    background: rgba(231, 76, 60, 0.9);
    color: white;
    border: none;
    border-radius: 50%;
    width: 42px;
    height: 42px;
    font-size: 26px;
    cursor: pointer;
    transition: all 0.3s;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 10px rgba(231, 76, 60, 0.3);
}

.stats-close-btn:hover {
    background: rgba(231, 76, 60, 1);
    transform: scale(1.12) rotate(90deg);
    box-shadow: 0 6px 15px rgba(231, 76, 60, 0.5);
}

.stats-modal-body {
    display: flex;
    flex: 1;
    overflow: hidden;
}

/* ============================================ */
/* НАВИГАЦИОННАЯ ПАНЕЛЬ */
/* ============================================ */

.stats-navigation {
    width: 320px;
    background: rgba(20, 20, 40, 0.7);
    border-right: 2px solid rgba(108, 92, 231, 0.4);
    padding: 25px 20px;
    overflow-y: auto;
    overflow-x: hidden;
}

.stats-nav-group {
    margin-bottom: 28px;
}

.stats-nav-group-title {
    color: #6c5ce7;
    font-size: 12px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin-bottom: 14px;
    padding-bottom: 10px;
    border-bottom: 2px solid rgba(108, 92, 231, 0.4);
    display: flex;
    align-items: center;
    gap: 8px;
}

.stats-nav-item {
    padding: 13px 16px;
    margin: 6px 0;
    background: rgba(255, 255, 255, 0.04);
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.3s;
    color: rgba(255, 255, 255, 0.7);
    font-size: 13px;
    font-weight: 500;
    border-left: 3px solid transparent;
    display: flex;
    align-items: center;
    gap: 10px;
}

.stats-nav-item:hover {
    background: rgba(108, 92, 231, 0.25);
    border-left-color: #6c5ce7;
    color: #fff;
    transform: translateX(4px);
    box-shadow: 0 2px 8px rgba(108, 92, 231, 0.2);
}

.stats-nav-item.active {
    background: linear-gradient(135deg, rgba(108, 92, 231, 0.4), rgba(52, 152, 219, 0.4));
    border-left-color: #6c5ce7;
    color: #fff;
    box-shadow: 0 4px 15px rgba(108, 92, 231, 0.4);
    font-weight: 600;
}

.stats-nav-item-icon {
    font-size: 16px;
    min-width: 20px;
    text-align: center;
}

.stats-nav-item-text {
    flex: 1;
}

/* ============================================ */
/* КОНТЕНТНАЯ ОБЛАСТЬ */
/* ============================================ */

.stats-content-area {
    flex: 1;
    padding: 35px;
    overflow-y: auto;
    background: rgba(10, 10, 25, 0.4);
}

.stats-content-header {
    margin-bottom: 28px;
    padding-bottom: 18px;
    border-bottom: 2px solid rgba(108, 92, 231, 0.3);
}

.stats-content-title {
    color: #fff;
    font-size: 24px;
    font-weight: 700;
    margin: 0 0 10px 0;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.stats-content-subtitle {
    color: rgba(255, 255, 255, 0.6);
    font-size: 13px;
    margin: 0 0 15px 0;
    line-height: 1.5;
}

/* Детальное описание метрики */
.metric-description-box {
    background: linear-gradient(135deg, rgba(52, 152, 219, 0.12), rgba(108, 92, 231, 0.08));
    border-left: 4px solid #3498db;
    padding: 18px 20px;
    border-radius: 12px;
    margin-bottom: 25px;
    font-size: 12px;
    line-height: 1.7;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.metric-description-section {
    margin-bottom: 14px;
}

.metric-description-section:last-child {
    margin-bottom: 0;
}

.metric-description-label {
    font-weight: 700;
    color: #3498db;
    margin-bottom: 6px;
    display: block;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.metric-description-text {
    color: rgba(255, 255, 255, 0.85);
    line-height: 1.6;
}

.metric-formula {
    background: rgba(0, 0, 0, 0.25);
    padding: 10px 14px;
    border-radius: 6px;
    font-family: 'Courier New', monospace;
    font-size: 11px;
    color: #e8e8e8;
    margin-top: 8px;
    border: 1px solid rgba(108, 92, 231, 0.2);
}

/* Кнопки управления в заголовке */
.stats-content-actions {
    display: flex;
    gap: 12px;
    margin-top: 15px;
}

.stats-action-btn {
    background: linear-gradient(135deg, #6c5ce7, #3498db);
    color: white;
    border: none;
    padding: 11px 22px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
    box-shadow: 0 4px 12px rgba(108, 92, 231, 0.3);
    display: flex;
    align-items: center;
    gap: 8px;
}

.stats-action-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(108, 92, 231, 0.45);
}

.stats-action-btn:active {
    transform: translateY(0);
}

.stats-action-btn.secondary {
    background: linear-gradient(135deg, #27ae60, #2ecc71);
}

.stats-action-btn.danger {
    background: linear-gradient(135deg, #e74c3c, #c0392b);
}

/* ============================================ */
/* ОТОБРАЖЕНИЕ РЕЗУЛЬТАТОВ */
/* ============================================ */

/* Сетка карточек */
.metric-results-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 18px;
    margin-top: 25px;
}

.metric-result-card {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.06), rgba(255, 255, 255, 0.03));
    border-radius: 14px;
    padding: 22px;
    border: 1px solid rgba(108, 92, 231, 0.25);
    transition: all 0.3s;
    cursor: pointer;
    position: relative;
    overflow: hidden;
}

.metric-result-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #6c5ce7, #3498db);
    transform: scaleX(0);
    transition: transform 0.3s;
}

.metric-result-card:hover {
    background: linear-gradient(135deg, rgba(108, 92, 231, 0.15), rgba(52, 152, 219, 0.1));
    border-color: rgba(108, 92, 231, 0.5);
    transform: translateY(-4px);
    box-shadow: 0 10px 25px rgba(108, 92, 231, 0.25);
}

.metric-result-card:hover::before {
    transform: scaleX(1);
}

.metric-result-rank {
    display: inline-block;
    background: linear-gradient(135deg, #6c5ce7, #3498db);
    color: white;
    padding: 5px 12px;
    border-radius: 14px;
    font-size: 11px;
    font-weight: 700;
    margin-bottom: 12px;
    letter-spacing: 0.5px;
}

.metric-result-name {
    color: #fff;
    font-size: 17px;
    font-weight: 600;
    margin: 12px 0;
    line-height: 1.3;
}

.metric-result-value {
    color: #3498db;
    font-size: 28px;
    font-weight: 700;
    margin: 10px 0;
    text-shadow: 0 2px 6px rgba(52, 152, 219, 0.3);
}

.metric-result-philosopher {
    color: rgba(255, 255, 255, 0.5);
    font-size: 12px;
    font-style: italic;
    margin-top: 8px;
}

.metric-result-details {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 12px;
}

.metric-result-detail-badge {
    background: rgba(108, 92, 231, 0.2);
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 10px;
    color: rgba(255, 255, 255, 0.8);
}

/* Таблица результатов */
.metric-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0 10px;
    margin-top: 25px;
}

.metric-table-header {
    background: linear-gradient(135deg, rgba(108, 92, 231, 0.3), rgba(52, 152, 219, 0.25));
    color: #fff;
    font-weight: 700;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

.metric-table th {
    padding: 14px 18px;
    text-align: left;
    border: none;
}

.metric-table th:first-child {
    border-radius: 10px 0 0 10px;
}

.metric-table th:last-child {
    border-radius: 0 10px 10px 0;
}

.metric-table-row {
    background: rgba(255, 255, 255, 0.04);
    transition: all 0.3s;
    cursor: pointer;
}

.metric-table-row:hover {
    background: rgba(108, 92, 231, 0.2);
    transform: scale(1.02);
    box-shadow: 0 4px 15px rgba(108, 92, 231, 0.2);
}

.metric-table td {
    padding: 14px 18px;
    color: rgba(255, 255, 255, 0.85);
    font-size: 13px;
    border-top: 1px solid rgba(108, 92, 231, 0.15);
    border-bottom: 1px solid rgba(108, 92, 231, 0.15);
}

.metric-table-row td:first-child {
    border-left: 1px solid rgba(108, 92, 231, 0.15);
    border-radius: 10px 0 0 10px;
}

.metric-table-row td:last-child {
    border-right: 1px solid rgba(108, 92, 231, 0.15);
    border-radius: 0 10px 10px 0;
}

.metric-table-row td strong {
    color: #fff;
    font-weight: 600;
}

.metric-table-value {
    color: #3498db !important;
    font-weight: 700 !important;
    font-size: 15px !important;
}

/* ============================================ */
/* КНОПКИ И ЭЛЕМЕНТЫ УПРАВЛЕНИЯ */
/* ============================================ */

.calculate-metric-btn {
    background: linear-gradient(135deg, #6c5ce7, #3498db);
    color: white;
    border: none;
    padding: 16px 32px;
    border-radius: 12px;
    font-size: 14px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.3s;
    box-shadow: 0 6px 20px rgba(108, 92, 231, 0.35);
    width: 100%;
    max-width: 400px;
    margin: 25px auto;
    display: block;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

.calculate-metric-btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 28px rgba(108, 92, 231, 0.5);
}

.calculate-metric-btn:active {
    transform: translateY(-1px);
}

/* ============================================ */
/* ИНДИКАТОР ПРОГРЕССА */
/* ============================================ */

.stats-progress-indicator {
    background: linear-gradient(135deg, rgba(52, 152, 219, 0.15), rgba(108, 92, 231, 0.1));
    border-radius: 12px;
    padding: 25px;
    text-align: center;
    margin: 25px 0;
    border: 1px solid rgba(52, 152, 219, 0.3);
}

.stats-progress-text {
    color: #3498db;
    font-size: 15px;
    font-weight: 700;
    margin-bottom: 15px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.stats-progress-bar {
    width: 100%;
    height: 10px;
    background: rgba(52, 152, 219, 0.2);
    border-radius: 5px;
    overflow: hidden;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
}

.stats-progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #3498db, #6c5ce7, #3498db);
    background-size: 200% 100%;
    border-radius: 5px;
    transition: width 0.3s ease;
    animation: progressShimmer 2s linear infinite;
}

@keyframes progressShimmer {
    0% {
        background-position: 200% 0;
    }
    100% {
        background-position: -200% 0;
    }
}

/* ============================================ */
/* ПУСТОЕ СОСТОЯНИЕ */
/* ============================================ */

.empty-state {
    text-align: center;
    padding: 80px 30px;
    color: rgba(255, 255, 255, 0.5);
}

.empty-state-icon {
    font-size: 72px;
    margin-bottom: 25px;
    opacity: 0.25;
    animation: emptyStatePulse 3s ease-in-out infinite;
}

@keyframes emptyStatePulse {
    0%, 100% {
        transform: scale(1);
        opacity: 0.25;
    }
    50% {
        transform: scale(1.05);
        opacity: 0.35;
    }
}

.empty-state-text {
    font-size: 17px;
    margin-bottom: 25px;
    color: rgba(255, 255, 255, 0.6);
}

.empty-state-hint {
    font-size: 13px;
    color: rgba(255, 255, 255, 0.4);
    max-width: 400px;
    margin: 0 auto;
    line-height: 1.6;
}

/* ============================================ */
/* СКРОЛЛБАРЫ */
/* ============================================ */

.stats-navigation::-webkit-scrollbar,
.stats-content-area::-webkit-scrollbar {
    width: 10px;
}

.stats-navigation::-webkit-scrollbar-track,
.stats-content-area::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.3);
    border-radius: 5px;
}

.stats-navigation::-webkit-scrollbar-thumb,
.stats-content-area::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #6c5ce7, #3498db);
    border-radius: 5px;
    border: 2px solid rgba(0, 0, 0, 0.3);
}

.stats-navigation::-webkit-scrollbar-thumb:hover,
.stats-content-area::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #7c6cf7, #4aa8eb);
}

/* ============================================ */
/* КНОПКА В ЛЕГЕНДЕ */
/* ============================================ */

.open-stats-modal-btn {
    width: 100%;
    background: linear-gradient(135deg, #6c5ce7, #3498db);
    color: white;
    border: none;
    padding: 14px 22px;
    border-radius: 12px;
    font-size: 13px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.3s;
    box-shadow: 0 5px 18px rgba(108, 92, 231, 0.35);
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-top: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
}

.open-stats-modal-btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 7px 24px rgba(108, 92, 231, 0.5);
}

.open-stats-modal-btn:active {
    transform: translateY(-1px);
}

/* ============================================ */
/* RESPONSIVE */
/* ============================================ */

@media (max-width: 1200px) {
    .stats-navigation {
        width: 260px;
    }
    
    .metric-results-grid {
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    }
}

@media (max-width: 900px) {
    .stats-modal-content {
        width: 96%;
        height: 95vh;
    }
    
    .stats-modal-body {
        flex-direction: column;
    }
    
    .stats-navigation {
        width: 100%;
        max-height: 220px;
        border-right: none;
        border-bottom: 2px solid rgba(108, 92, 231, 0.4);
        display: flex;
        overflow-x: auto;
        overflow-y: hidden;
        flex-wrap: nowrap;
        padding: 15px 20px;
    }
    
    .stats-nav-group {
        min-width: 200px;
        margin-right: 20px;
    }
    
    .metric-results-grid {
        grid-template-columns: 1fr;
    }
    
    .stats-header-controls {
        width: 100%;
        justify-content: flex-start;
    }
}

@media (max-width: 600px) {
    .stats-modal-header {
        padding: 18px 20px;
    }
    
    .stats-modal-header h2 {
        font-size: 20px;
    }
    
    .stats-content-area {
        padding: 20px;
    }
    
    .metric-results-grid {
        gap: 12px;
    }
    
    .metric-result-card {
        padding: 18px;
    }
}
```

---

## 3. HTML РАЗМЕТКА {#html}

Заменить секцию "Статистический анализ" в легенде на:

```html
<!-- Заменить всю секцию статистического анализа на эту кнопку -->
<div class="legend-section">
    <h4>📊 Статистический анализ</h4>
    <button class="open-stats-modal-btn" onclick="openStatsModal()">
        <span>📊</span>
        <span>Открыть панель статистики</span>
    </button>
</div>
```

Добавить перед закрывающим тегом `</body>`:

```html
<!-- ============================================ -->
<!-- МОДАЛЬНОЕ ОКНО РАСШИРЕННОЙ СТАТИСТИКИ -->
<!-- ============================================ -->
<div id="statsModal">
    <div class="stats-modal-content">
        <!-- Заголовок -->
        <div class="stats-modal-header">
            <div class="stats-modal-title-section">
                <h2>📊 Расширенный статистический анализ</h2>
                <p class="stats-modal-subtitle">Полный набор метрик для историко-философского анализа сети концепций</p>
            </div>
            
            <div class="stats-header-controls">
                <!-- Переключатель весов -->
                <div class="stats-parameter-toggle" title="Учитывать веса связей при расчёте">
                    <input type="checkbox" id="statsUseWeightsToggle" onchange="handleStatsParameterChange()">
                    <label for="statsUseWeightsToggle">Учитывать веса</label>
                </div>
                
                <!-- Переключатель направленности -->
                <div class="stats-parameter-toggle" title="Учитывать направления связей при расчёте">
                    <input type="checkbox" id="statsRespectDirectionToggle" onchange="handleStatsParameterChange()">
                    <label for="statsRespectDirectionToggle">Учитывать направленность</label>
                </div>
                
                <!-- Кнопка закрытия -->
                <button class="stats-close-btn" onclick="closeStatsModal()" title="Закрыть (Esc)">×</button>
            </div>
        </div>
        
        <!-- Тело модального окна -->
        <div class="stats-modal-body">
            <!-- Навигационная панель слева -->
            <div class="stats-navigation">
                <!-- Базовые метрики сети -->
                <div class="stats-nav-group">
                    <div class="stats-nav-group-title">
                        <span>🔍</span>
                        <span>Базовые метрики</span>
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('overview')">
                        <span class="stats-nav-item-icon">📈</span>
                        <span class="stats-nav-item-text">Общий обзор</span>
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('degree')">
                        <span class="stats-nav-item-icon">🔗</span>
                        <span class="stats-nav-item-text">Степень связности</span>
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('pagerank')">
                        <span class="stats-nav-item-icon">⭐</span>
                        <span class="stats-nav-item-text">PageRank</span>
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('betweenness')">
                        <span class="stats-nav-item-icon">🌉</span>
                        <span class="stats-nav-item-text">Betweenness</span>
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('closeness')">
                        <span class="stats-nav-item-icon">🎯</span>
                        <span class="stats-nav-item-text">Closeness</span>
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('eigenvector')">
                        <span class="stats-nav-item-icon">🏆</span>
                        <span class="stats-nav-item-text">Eigenvector</span>
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('weighted-clustering')">
                        <span class="stats-nav-item-icon">🕸️</span>
                        <span class="stats-nav-item-text">Взвешенная кластеризация</span>
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('local-cohesion')">
                        <span class="stats-nav-item-icon">🔵</span>
                        <span class="stats-nav-item-text">Локальная когезия</span>
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('rich-club')">
                        <span class="stats-nav-item-icon">👑</span>
                        <span class="stats-nav-item-text">Rich-Club</span>
                    </div>
                </div>

                <!-- Философские метрики проблемности и критичности -->
                <div class="stats-nav-group">
                    <div class="stats-nav-group-title">
                        <span>⚡</span>
                        <span>Проблемность и критика</span>
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('problem-generation')">
                        <span class="stats-nav-item-icon">💥</span>
                        <span class="stats-nav-item-text">Индекс проблемности</span>
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('critical-power')">
                        <span class="stats-nav-item-icon">⚔️</span>
                        <span class="stats-nav-item-text">Критическая сила</span>
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('tension')">
                        <span class="stats-nav-item-icon">⚖️</span>
                        <span class="stats-nav-item-text">Индекс напряжения</span>
                    </div>
                </div>

                <!-- Философские метрики революционности -->
                <div class="stats-nav-group">
                    <div class="stats-nav-group-title">
                        <span>🔥</span>
                        <span>Революционность и новизна</span>
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('revolutionary')">
                        <span class="stats-nav-item-icon">🌟</span>
                        <span class="stats-nav-item-text">Индекс революционности</span>
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('paradigm-shift')">
                        <span class="stats-nav-item-icon">🌐</span>
                        <span class="stats-nav-item-text">Парадигмальный сдвиг</span>
                    </div>
                </div>

                <!-- Философские метрики влияния -->
                <div class="stats-nav-group">
                    <div class="stats-nav-group-title">
                        <span>💫</span>
                        <span>Влияние и центральность</span>
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('influence')">
                        <span class="stats-nav-item-icon">🎭</span>
                        <span class="stats-nav-item-text">Индекс влияния</span>
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('foundational')">
                        <span class="stats-nav-item-icon">🏛️</span>
                        <span class="stats-nav-item-text">Индекс основополагания</span>
                    </div>
                </div>

                <!-- Философские метрики синтеза и диалога -->
                <div class="stats-nav-group">
                    <div class="stats-nav-group-title">
                        <span>🧩</span>
                        <span>Синтез и диалог</span>
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('synthetic')">
                        <span class="stats-nav-item-icon">🔗</span>
                        <span class="stats-nav-item-text">Индекс синтетичности</span>
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('dialogical')">
                        <span class="stats-nav-item-icon">💬</span>
                        <span class="stats-nav-item-text">Индекс диалогичности</span>
                    </div>
                </div>

                <!-- Философские метрики когерентности -->
                <div class="stats-nav-group">
                    <div class="stats-nav-group-title">
                        <span>🔮</span>
                        <span>Когерентность системы</span>
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('coherence')">
                        <span class="stats-nav-item-icon">✨</span>
                        <span class="stats-nav-item-text">Внутренняя когерентность</span>
                    </div>
                </div>

                <!-- Продвинутые метрики трансформации -->
                <div class="stats-nav-group">
                    <div class="stats-nav-group-title">
                        <span>🦋</span>
                        <span>Трансформация и развитие</span>
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('transformation')">
                        <span class="stats-nav-item-icon">🔄</span>
                        <span class="stats-nav-item-text">Индекс трансформации</span>
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('fertility')">
                        <span class="stats-nav-item-icon">🌱</span>
                        <span class="stats-nav-item-text">Концептуальная плодовитость</span>
                    </div>
                </div>

                <!-- Продвинутые метрики сложности -->
                <div class="stats-nav-group">
                    <div class="stats-nav-group-title">
                        <span>🧠</span>
                        <span>Сложность и структура</span>
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('complexity')">
                        <span class="stats-nav-item-icon">📊</span>
                        <span class="stats-nav-item-text">Концептуальная сложность</span>
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('continuity')">
                        <span class="stats-nav-item-icon">📜</span>
                        <span class="stats-nav-item-text">Индекс преемственности</span>
                    </div>
                </div>

                <!-- Временные метрики -->
                <div class="stats-nav-group">
                    <div class="stats-nav-group-title">
                        <span>⏳</span>
                        <span>Временная динамика</span>
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('temporal-influence')">
                        <span class="stats-nav-item-icon">🕐</span>
                        <span class="stats-nav-item-text">Временное влияние</span>
                    </div>
                </div>

                <!-- Метрики философов -->
                <div class="stats-nav-group">
                    <div class="stats-nav-group-title">
                        <span>👤</span>
                        <span>Метрики философов</span>
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('philosopher-profile')">
                        <span class="stats-nav-item-icon">📖</span>
                        <span class="stats-nav-item-text">Профиль философа</span>
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('philosopher-systematic')">
                        <span class="stats-nav-item-icon">📚</span>
                        <span class="stats-nav-item-text">Систематичность</span>
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('philosopher-reach')">
                        <span class="stats-nav-item-icon">🌍</span>
                        <span class="stats-nav-item-text">Исторический охват</span>
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('philosopher-interdisciplinary')">
                        <span class="stats-nav-item-icon">🔬</span>
                        <span class="stats-nav-item-text">Междисциплинарность</span>
                    </div>
                </div>

                <!-- Сравнительный анализ -->
                <div class="stats-nav-group">
                    <div class="stats-nav-group-title">
                        <span>⚖️</span>
                        <span>Сравнительный анализ</span>
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('concept-rankings')">
                        <span class="stats-nav-item-icon">🏅</span>
                        <span class="stats-nav-item-text">Рейтинги концепций</span>
                    </div>
                    <div class="stats-nav-item" onclick="switchStatsView('philosopher-rankings')">
                        <span class="stats-nav-item-icon">🎖️</span>
                        <span class="stats-nav-item-text">Рейтинги философов</span>
                    </div>
                </div>
            </div>

            <!-- Контентная область справа -->
            <div class="stats-content-area" id="statsContentArea">
                <!-- Контент будет динамически загружаться здесь -->
                <div class="empty-state">
                    <div class="empty-state-icon">📊</div>
                    <div class="empty-state-text">Выберите метрику из меню слева</div>
                    <div class="empty-state-hint">
                        Используйте переключатели "Учитывать веса" и "Учитывать направленность" 
                        для изменения способа расчёта метрик
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
```

---

## 4. КЛАССЫ МЕТРИК (ПОЛНАЯ ВЕРСИЯ) {#классы-метрик}

Добавить перед закрывающим тегом `</script>` основного скрипта:

```javascript
// ============================================
// ПОЛНЫЕ КЛАССЫ МЕТРИК ДЛЯ ФИЛОСОФСКОГО АНАЛИЗА
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

    // 1. МЕТРИКИ ПРОБЛЕМНОСТИ И КРИТИЧНОСТИ
    
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

    // 2. МЕТРИКИ РЕВОЛЮЦИОННОСТИ И НОВИЗНЫ

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

    // 3. МЕТРИКИ ВЛИЯНИЯ И ЦЕНТРАЛЬНОСТИ

    influenceIndex(conceptId) {
        const concept = this.conceptMap.get(conceptId);
        if (!concept) return { total: 0 };
        
        const philosopher = this.philosopherMap.get(concept.philosopher);
        if (!philosopher) return { total: 0 };
        
        const incoming = this.incomingLinks.get(conceptId) || [];
        
        const forwardInfluence = incoming.reduce((sum, r) => {
            const source = this.conceptMap.get(r.source);
            if (!source) return sum;
            const sourcePhil = this.philosopherMap.get(source.philosopher);
            if (!sourcePhil) return sum;
            
            if (sourcePhil.birth > philosopher.birth) {
                const typeWeight = {
                    'influence': 3,
                    'develop': 2.5,
                    'apply': 2,
                    'dialogue': 1.5
                }[r.type] || 1;
                return sum + typeWeight * (r.weight || 1);
            }
            return sum;
        }, 0);
        
        const contemporaryInfluence = incoming.reduce((sum, r) => {
            const source = this.conceptMap.get(r.source);
            if (!source) return sum;
            const sourcePhil = this.philosopherMap.get(source.philosopher);
            if (!sourcePhil) return sum;
            
            const timeDiff = Math.abs(sourcePhil.birth - philosopher.birth);
            if (timeDiff < 50) {
                const typeWeight = {
                    'dialogue': 2,
                    'critique': 1.5,
                    'synthesize': 2
                }[r.type] || 1;
                return sum + typeWeight * (r.weight || 1);
            }
            return sum;
        }, 0);
        
        const totalIncoming = incoming.length;
        
        return {
            total: forwardInfluence + contemporaryInfluence * 0.5,
            forward: forwardInfluence,
            contemporary: contemporaryInfluence,
            incoming: totalIncoming
        };
    }

    foundationalIndex(conceptId) {
        const outgoing = this.outgoingLinks.get(conceptId) || [];
        const incoming = this.incomingLinks.get(conceptId) || [];
        
        const presuppositions = outgoing.filter(r => r.type === 'presuppose').length;
        const conditions = outgoing.filter(r => r.type === 'condition').length;
        const emergences = incoming.filter(r => r.type === 'emerge_from').length;
        const applications = incoming.filter(r => r.type === 'apply').length;
        const developments = incoming.filter(r => r.type === 'develop').length;
        
        return {
            total: presuppositions * 3 + conditions * 2 + emergences * 2.5 + applications + developments,
            presuppositions,
            conditions,
            emergences,
            applications,
            developments
        };
    }

    // 4. МЕТРИКИ СИНТЕТИЧНОСТИ И ДИАЛОГА

    syntheticIndex(conceptId) {
        const concept = this.conceptMap.get(conceptId);
        if (!concept) return { total: 0 };
        
        const incoming = this.incomingLinks.get(conceptId) || [];
        const outgoing = this.outgoingLinks.get(conceptId) || [];
        
        const syntheses = outgoing.filter(r => r.type === 'synthesize').length;
        const reconciliations = outgoing.filter(r => r.type === 'reconcile').length;
        
        const influenceSources = new Set(
            incoming
                .filter(r => r.type === 'influence' || r.type === 'develop')
                .map(r => {
                    const src = this.conceptMap.get(r.source);
                    return src ? src.philosopher : null;
                })
                .filter(p => p !== null)
        );
        
        const sourceRubrics = new Set();
        incoming
            .filter(r => r.type === 'influence' || r.type === 'develop')
            .forEach(r => {
                const source = this.conceptMap.get(r.source);
                if (source) {
                    (source.rubrics || []).forEach(rub => sourceRubrics.add(rub));
                }
            });
        
        return {
            total: syntheses * 3 + reconciliations * 2 + influenceSources.size * 2 + sourceRubrics.size,
            syntheses,
            reconciliations,
            diverseInfluences: influenceSources.size,
            thematicBreadth: sourceRubrics.size
        };
    }

    dialogicalIndex(conceptId) {
        const incoming = this.incomingLinks.get(conceptId) || [];
        const outgoing = this.outgoingLinks.get(conceptId) || [];
        
        const dialogues = incoming.filter(r => r.type === 'dialogue').length;
        const bidirectional = incoming.filter(r => r.bidirectional).length;
        const complements = incoming.filter(r => r.type === 'complement').length + 
                           outgoing.filter(r => r.type === 'complement').length;
        
        return {
            total: dialogues * 2 + bidirectional * 3 + complements,
            dialogues,
            bidirectional,
            complements
        };
    }

    // 5. МЕТРИКИ КОГЕРЕНТНОСТИ И ПРОБЛЕМНОСТИ СИСТЕМЫ

    internalCoherenceIndex(conceptId) {
        const concept = this.conceptMap.get(conceptId);
        if (!concept) return { total: 0 };
        
        const incoming = this.incomingLinks.get(conceptId) || [];
        const outgoing = this.outgoingLinks.get(conceptId) || [];
        
        const internalLinks = incoming.concat(outgoing).filter(r => {
            const other = this.conceptMap.get(r.source === conceptId ? r.target : r.source);
            return other && other.philosopher === concept.philosopher;
        });
        
        const positive = internalLinks.filter(r => 
            ['presuppose', 'consequence', 'develop', 'apply', 'complement', 
             'condition', 'exemplify', 'culminate', 'mediate'].includes(r.type)
        ).length;
        
        const negative = internalLinks.filter(r => 
            ['internal_contradiction', 'oppose'].includes(r.type)
        ).length;
        
        const coherenceScore = positive - negative * 2;
        
        return {
            total: Math.max(0, coherenceScore),
            positive,
            negative,
            coherenceScore
        };
    }

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

    // 6. МЕТРИКИ ФИЛОСОФОВ

    philosopherProfile(philosopherId) {
        const philosopherConcepts = this.concepts.filter(c => c.philosopher === philosopherId);
        if (philosopherConcepts.length === 0) return null;
        
        const metrics = philosopherConcepts.map(c => ({
            influence: this.influenceIndex(c.id).total,
            revolutionary: this.revolutionaryIndex(c.id).total,
            coherence: this.internalCoherenceIndex(c.id).total
        }));
        
        const averages = {
            influence: metrics.reduce((sum, m) => sum + m.influence, 0) / metrics.length,
            revolutionary: metrics.reduce((sum, m) => sum + m.revolutionary, 0) / metrics.length,
            coherence: metrics.reduce((sum, m) => sum + m.coherence, 0) / metrics.length
        };
        
        return {
            philosopherId,
            conceptsCount: philosopherConcepts.length,
            metrics,
            averages
        };
    }

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
        
        const entropy = Object.values(rubricDistribution).length > 0 
            ? Object.values(rubricDistribution).reduce((sum, count) => {
                const p = count / philosopherConcepts.length;
                return sum - p * Math.log2(p);
            }, 0)
            : 0;
        
        return {
            total: rubrics.size * (1 + entropy),
            rubricCount: rubrics.size,
            entropy,
            distribution: rubricDistribution
        };
    }

    // 7. СРАВНИТЕЛЬНЫЕ И ВРЕМЕННЫЕ МЕТРИКИ

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

    generateRankings() {
        const allConcepts = this.concepts.map(c => ({
            id: c.id,
            label: c.label,
            philosopher: c.philosopher,
            influence: this.influenceIndex(c.id).total,
            revolutionary: this.revolutionaryIndex(c.id).total,
            problematic: this.problemGenerationIndex(c.id).weighted,
            synthetic: this.syntheticIndex(c.id).total,
            foundational: this.foundationalIndex(c.id).total,
            critical: this.criticalPowerIndex(c.id).weighted
        }));
        
        return {
            mostInfluential: [...allConcepts].sort((a, b) => b.influence - a.influence).slice(0, 20),
            mostRevolutionary: [...allConcepts].sort((a, b) => b.revolutionary - a.revolutionary).slice(0, 20),
            mostProblematic: [...allConcepts].sort((a, b) => b.problematic - a.problematic).slice(0, 20),
            mostSynthetic: [...allConcepts].sort((a, b) => b.synthetic - a.synthetic).slice(0, 20),
            mostFoundational: [...allConcepts].sort((a, b) => b.foundational - a.foundational).slice(0, 20),
            mostCritical: [...allConcepts].sort((a, b) => b.critical - a.critical).slice(0, 20)
        };
    }

    generatePhilosopherRankings() {
        const allPhilosophers = this.philosophers.map(p => {
            const profile = this.philosopherProfile(p.id);
            const systematic = this.philosopherSystematicIndex(p.id);
            const historical = this.philosopherHistoricalReachIndex(p.id);
            const interdisciplinary = this.philosopherInterdisciplinaryIndex(p.id);
            
            return {
                id: p.id,
                name: p.name,
                influence: profile ? profile.averages.influence : 0,
                revolutionary: profile ? profile.averages.revolutionary : 0,
                systematic: systematic.density,
                historicalReach: historical.total,
                interdisciplinary: interdisciplinary.total,
                coherence: profile ? profile.averages.coherence : 0
            };
        }).filter(p => p.influence > 0 || p.revolutionary > 0);
        
        return {
            mostInfluential: [...allPhilosophers].sort((a, b) => b.influence - a.influence).slice(0, 20),
            mostRevolutionary: [...allPhilosophers].sort((a, b) => b.revolutionary - a.revolutionary).slice(0, 20),
            mostSystematic: [...allPhilosophers].sort((a, b) => b.systematic - a.systematic).slice(0, 20),
            greatestHistoricalReach: [...allPhilosophers].sort((a, b) => b.historicalReach - a.historicalReach).slice(0, 20),
            mostInterdisciplinary: [...allPhilosophers].sort((a, b) => b.interdisciplinary - a.interdisciplinary).slice(0, 20)
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
let statsParametersCache = { weights: false, direction: false };

function initializePhilosophyMetrics() {
    try {
        const conceptsData = nodes.map(n => ({
            id: n.id,
            label: n.label,
            philosopher: n.concept,
            rubrics: n.rubrics || []
        }));
        
        const relationsData = links.map(l => ({
            source: typeof l.source === 'object' ? l.source.id : l.source,
            target: typeof l.target === 'object' ? l.target.id : l.target,
            type: l.type || 'influence',
            weight: l.weight || 1,
            bidirectional: l.bidirectional || false
        }));
        
        const philosophersData = Array.from(new Set(nodes.map(n => n.concept))).map((concept, idx) => ({
            id: concept,
            name: concept,
            birth: 1800 + idx * 10
        }));
        
        philosophyMetrics = new PhilosophyGraphMetrics(conceptsData, relationsData, philosophersData);
        advancedMetrics = new AdvancedPhilosophyMetrics(conceptsData, relationsData, philosophersData, philosophyMetrics);
        
        console.log('✅ Философские метрики инициализированы');
        return true;
    } catch (error) {
        console.error('❌ Ошибка при инициализации метрик:', error);
        return false;
    }
}
```

---

*Это только начало документа. Из-за ограничений по размеру, я создам продолжение в следующем сообщении. Следующие секции будут включать:*

- **5. Описания метрик** (с учётом параметров)
- **6. Функции управления модальным окном**
- **7. Генераторы контента для всех метрик**
- **8. Функция визуализации размером узлов**
- **9. Инструкции по применению**

Нужно ли мне продолжить создание документа?
