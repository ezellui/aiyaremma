# КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Отсутствующая HTML-разметка модального окна

## Проблема
При попытке рассчитать метрики возникает ошибка **"TypeError: progressDiv is null"** потому что в HTML отсутствуют необходимые элементы:
- Модальное окно статистики `<div id="statsModal">`
- Заголовок с переключателями
- Индикатор прогресса `<div id="analysisProgress">`

## Решение: Полная замена HTML-разметки в теге `<body>`

### ❌ Текущая неправильная структура (строки 829-1063)
```html
<body>
    <div class="legend-section">
        <!-- Кнопка открытия -->
    </div>

    <div class="stats-modal-body">
        <!-- Навигация напрямую в body - НЕПРАВИЛЬНО! -->
        <div class="stats-navigation">
            <!-- ... -->
        </div>
        <div class="stats-content-area" id="statsContentArea">
            <!-- ... -->
        </div>
    </div>
    <!-- НЕТ модального окна и индикатора прогресса! -->
```

### ✅ ПРАВИЛЬНАЯ структура (полная замена)

**ЗАМЕНИТЬ содержимое `<body>` (строки 829-1063) на следующий код:**

```html
<body>

    <!-- ============================================ -->
    <!-- КНОПКА ОТКРЫТИЯ СТАТИСТИКИ (для легенды) -->
    <!-- ============================================ -->
    <div class="legend-section">
        <h4>📊 Статистический анализ</h4>
        <button class="open-stats-modal-btn" onclick="openStatsModal()">
            <span>📊</span>
            <span>Открыть панель статистики</span>
        </button>
    </div>

    <!-- ============================================ -->
    <!-- МОДАЛЬНОЕ ОКНО СТАТИСТИКИ -->
    <!-- ============================================ -->
    <div id="statsModal">
        <div class="stats-modal-content">
            
            <!-- Заголовок модального окна -->
            <div class="stats-modal-header">
                <div class="stats-modal-title-section">
                    <h2>📊 Статистический анализ графа философских концепций</h2>
                    <p class="stats-modal-subtitle">Расширенные метрики и визуализация сети</p>
                </div>
                
                <div class="stats-header-controls">
                    <!-- Переключатель учёта весов -->
                    <div class="stats-parameter-toggle">
                        <input type="checkbox" id="statsUseWeightsToggle" 
                               onchange="handleStatsParameterChange()">
                        <label for="statsUseWeightsToggle">Учитывать веса</label>
                    </div>
                    
                    <!-- Переключатель учёта направленности -->
                    <div class="stats-parameter-toggle">
                        <input type="checkbox" id="statsRespectDirectionToggle" 
                               onchange="handleStatsParameterChange()">
                        <label for="statsRespectDirectionToggle">Учитывать направленность</label>
                    </div>
                    
                    <!-- Кнопка закрытия -->
                    <button class="stats-close-btn" onclick="closeStatsModal()" title="Закрыть">×</button>
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
                        <div class="stats-nav-item" onclick="switchStatsView('overview', event)">
                            <span class="stats-nav-item-icon">📈</span>
                            <span class="stats-nav-item-text">Общий обзор</span>
                        </div>
                        <div class="stats-nav-item" onclick="switchStatsView('degree', event)">
                            <span class="stats-nav-item-icon">🔗</span>
                            <span class="stats-nav-item-text">Степень связности</span>
                        </div>
                        <div class="stats-nav-item" onclick="switchStatsView('pagerank', event)">
                            <span class="stats-nav-item-icon">⭐</span>
                            <span class="stats-nav-item-text">PageRank</span>
                        </div>
                        <div class="stats-nav-item" onclick="switchStatsView('betweenness', event)">
                            <span class="stats-nav-item-icon">🌉</span>
                            <span class="stats-nav-item-text">Betweenness</span>
                        </div>
                        <div class="stats-nav-item" onclick="switchStatsView('closeness', event)">
                            <span class="stats-nav-item-icon">🎯</span>
                            <span class="stats-nav-item-text">Closeness</span>
                        </div>
                        <div class="stats-nav-item" onclick="switchStatsView('eigenvector', event)">
                            <span class="stats-nav-item-icon">🏆</span>
                            <span class="stats-nav-item-text">Eigenvector</span>
                        </div>
                        <div class="stats-nav-item" onclick="switchStatsView('weighted-clustering', event)">
                            <span class="stats-nav-item-icon">🕸️</span>
                            <span class="stats-nav-item-text">Взвешенная кластеризация</span>
                        </div>
                        <div class="stats-nav-item" onclick="switchStatsView('local-cohesion', event)">
                            <span class="stats-nav-item-icon">🔵</span>
                            <span class="stats-nav-item-text">Локальная когезия</span>
                        </div>
                        <div class="stats-nav-item" onclick="switchStatsView('rich-club', event)">
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
                        <div class="stats-nav-item" onclick="switchStatsView('problem-generation', event)">
                            <span class="stats-nav-item-icon">💥</span>
                            <span class="stats-nav-item-text">Индекс проблемности</span>
                        </div>
                        <div class="stats-nav-item" onclick="switchStatsView('critical-power', event)">
                            <span class="stats-nav-item-icon">⚔️</span>
                            <span class="stats-nav-item-text">Критическая сила</span>
                        </div>
                        <div class="stats-nav-item" onclick="switchStatsView('tension', event)">
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
                        <div class="stats-nav-item" onclick="switchStatsView('revolutionary', event)">
                            <span class="stats-nav-item-icon">🌟</span>
                            <span class="stats-nav-item-text">Индекс революционности</span>
                        </div>
                        <div class="stats-nav-item" onclick="switchStatsView('paradigm-shift', event)">
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
                        <div class="stats-nav-item" onclick="switchStatsView('influence', event)">
                            <span class="stats-nav-item-icon">🎭</span>
                            <span class="stats-nav-item-text">Индекс влияния</span>
                        </div>
                        <div class="stats-nav-item" onclick="switchStatsView('foundational', event)">
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
                        <div class="stats-nav-item" onclick="switchStatsView('synthetic', event)">
                            <span class="stats-nav-item-icon">🔗</span>
                            <span class="stats-nav-item-text">Индекс синтетичности</span>
                        </div>
                        <div class="stats-nav-item" onclick="switchStatsView('dialogical', event)">
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
                        <div class="stats-nav-item" onclick="switchStatsView('coherence', event)">
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
                        <div class="stats-nav-item" onclick="switchStatsView('transformation', event)">
                            <span class="stats-nav-item-icon">🔄</span>
                            <span class="stats-nav-item-text">Индекс трансформации</span>
                        </div>
                        <div class="stats-nav-item" onclick="switchStatsView('fertility', event)">
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
                        <div class="stats-nav-item" onclick="switchStatsView('complexity', event)">
                            <span class="stats-nav-item-icon">📊</span>
                            <span class="stats-nav-item-text">Концептуальная сложность</span>
                        </div>
                        <div class="stats-nav-item" onclick="switchStatsView('continuity', event)">
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
                        <div class="stats-nav-item" onclick="switchStatsView('temporal-influence', event)">
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
                        <div class="stats-nav-item" onclick="switchStatsView('philosopher-profile', event)">
                            <span class="stats-nav-item-icon">📖</span>
                            <span class="stats-nav-item-text">Профиль философа</span>
                        </div>
                        <div class="stats-nav-item" onclick="switchStatsView('philosopher-systematic', event)">
                            <span class="stats-nav-item-icon">📚</span>
                            <span class="stats-nav-item-text">Систематичность</span>
                        </div>
                        <div class="stats-nav-item" onclick="switchStatsView('philosopher-reach', event)">
                            <span class="stats-nav-item-icon">🌍</span>
                            <span class="stats-nav-item-text">Исторический охват</span>
                        </div>
                        <div class="stats-nav-item" onclick="switchStatsView('philosopher-interdisciplinary', event)">
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
                        <div class="stats-nav-item" onclick="switchStatsView('concept-rankings', event)">
                            <span class="stats-nav-item-icon">🏅</span>
                            <span class="stats-nav-item-text">Рейтинги концепций</span>
                        </div>
                        <div class="stats-nav-item" onclick="switchStatsView('philosopher-rankings', event)">
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

    <!-- ============================================ -->
    <!-- ИНДИКАТОР ПРОГРЕССА РАСЧЁТОВ -->
    <!-- ============================================ -->
    <div id="analysisProgress" class="stats-progress-indicator" style="display: none;">
        <div class="stats-progress-text" id="progressLabel">Расчёт метрики...</div>
        <div class="stats-progress-bar">
            <div class="stats-progress-fill" id="progressBar" style="width: 0%;"></div>
        </div>
        <div class="stats-progress-text" id="progressPercent">0%</div>
    </div>

    <script>
        // Далее идёт JavaScript код (начиная с philosophers)
```

---

## Дополнительное исправление: обновление вызовов switchStatsView

Все вызовы `switchStatsView()` в навигации теперь должны передавать `event` как второй параметр для корректной работы подсветки активного пункта меню.

**Примеры исправленных вызовов:**
```html
<!-- Было -->
<div class="stats-nav-item" onclick="switchStatsView('overview')">

<!-- Стало -->
<div class="stats-nav-item" onclick="switchStatsView('overview', event)">
```

---

## Инструкция по применению

### Шаг 1: Найти тег `<body>` (строка 829)

### Шаг 2: Удалить ВСЁ содержимое от `<body>` до `<script>` (строки 829-1064)

### Шаг 3: Вставить ПОЛНЫЙ код из раздела "✅ ПРАВИЛЬНАЯ структура" выше

### Шаг 4: Проверить, что после вставки идёт открывающий тег `<script>` с комментарием про философов

---

## Что изменилось

### ✅ Добавлено:
1. **Модальное окно** `<div id="statsModal">` - теперь окно правильно скрывается/показывается
2. **Заголовок окна** с названием и подзаголовком
3. **Переключатели параметров**:
   - `statsUseWeightsToggle` - учёт весов связей
   - `statsRespectDirectionToggle` - учёт направленности
4. **Кнопка закрытия** модального окна (×)
5. **Индикатор прогресса** `analysisProgress` с элементами:
   - `progressLabel` - текст статуса
   - `progressBar` - визуальная полоса прогресса
   - `progressPercent` - процент выполнения

### ✅ Исправлено:
1. Правильная вложенность элементов
2. Все необходимые `id` для работы JavaScript
3. Передача параметра `event` в вызовах `switchStatsView()`

---

## Проверка после применения

После замены HTML проверьте:

1. ✅ Кнопка "Открыть панель статистики" открывает модальное окно
2. ✅ Модальное окно появляется с затемнением фона
3. ✅ Переключатели "Учитывать веса" и "Учитывать направленность" отображаются
4. ✅ Кнопка закрытия (×) закрывает окно
5. ✅ При расчёте метрик появляется индикатор прогресса
6. ✅ **НЕТ ошибки "progressDiv is null"**

---

## Приоритет исправления

🔴 **КРИТИЧЕСКИЙ** - без этого исправления невозможен расчёт ЛЮБЫХ метрик!

Это исправление должно быть применено В ПЕРВУЮ ОЧЕРЕДЬ, до всех остальных исправлений из файла `corrections.md`.
