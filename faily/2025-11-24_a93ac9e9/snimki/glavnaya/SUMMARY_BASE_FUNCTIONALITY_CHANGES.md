# СВОДНЫЙ ДОКУМЕНТ: Изменения базового функционала графа

Этот документ содержит все изменения, которые НЕ относятся к функциям/разметке/стилям редактирования, но были необходимы для корректной работы всей системы.

---

## 1. БАЗОВЫЕ СТРУКТУРЫ ДАННЫХ

### 1.1. Изменение const на let для массивов данных

**Проблема**: Переменные nodes и links объявлены как const, но переприсваиваются в updateGraphData()

**Строка 1779** - изменить:
```javascript
// Было:
const nodes = concepts.map(c => ({

// Стало:
let nodes = concepts.map(c => ({
```

**Строка 1788** - изменить:
```javascript
// Было:
const links = relations.map(r => ({

// Стало:
let links = relations.map(r => ({
```

**Причина**: Функция `updateGraphData()` переприсваивает эти переменные при обновлении графа.

---

### 1.2. Добавление переменной connections

**Проблема**: Переменная connections используется в 17 местах, но нигде не определена.

**После строки 1795** - добавить:
```javascript
        }));
        
        // Создаём connections для функционала редактирования
        let connections = relations.map(r => ({
            from: r.source,
            to: r.target,
            type: r.type,
            weight: r.weight || 2,
            bidirectional: r.bidirectional || false,
            description: r.description
        }));
        
        // Создаём обратный индекс концепция → рубрики
```

**Причина**: 
- Нужна отдельная структура с полями `from/to` вместо `source/target`
- D3 модифицирует поля `source/target` в links, превращая их в объекты
- connections сохраняет исходные строковые ID для редактирования

**Использование**:
- findConnection()
- getConceptConnections()
- updateGraphData()
- deletePhilosopher()
- deleteConcept()
- saveConnection()
- deleteConnection()
- И другие функции редактирования

---

### 1.3. Исправление структуры philosopherConcepts

**Проблема**: При инициализации philosopherConcepts сохраняются только поля color и years, но отсутствуют name, birth, death.

**Строки 1755-1761** - заменить:
```javascript
// Было:
const philosopherConcepts = {};
philosophers.forEach(p => {
    philosopherConcepts[p.nameRu] = {
        color: p.color,
        years: p.years
    };
});

// Стало:
const philosopherConcepts = {};
philosophers.forEach(p => {
    philosopherConcepts[p.nameRu] = {
        name: p.nameRu,
        color: p.color,
        years: p.years,
        birth: p.birth,
        death: p.death
    };
});
```

**Причина**: 
- Функции редактирования используют все эти поля
- findPhilosopherByName() ищет p.name
- openEditPhilosopherModal() использует philosopher.name, .birth, .death

**Затронуто**: ~25 использований в функциях редактирования и фильтрах

---

## 2. D3 ВИЗУАЛИЗАЦИЯ

### 2.1. Изменение const на let для D3 selections

**Проблема**: D3 переприсваивает selections при использовании update pattern.

**Строка 2811** - изменить:
```javascript
// Было:
const link = g.append("g")

// Стало:
let link = g.append("g")
```

**Строка 3003** - изменить:
```javascript
// Было:
const node = g.append("g")

// Стало:
let node = g.append("g")
```

**Причина**: 
- D3 update pattern требует переприсваивания: `selection = selection.data(...).merge(...)`
- Используется в updateGraphVisualization()

---

### 2.2. Исправление белого ободка узлов

**Проблема**: После обновления графа у узлов ободок становится цветным вместо белого.

**Строка 3807** в updateGraphVisualization - изменить:
```javascript
// Было:
.attr("stroke", d => d3.color(philosopherConcepts[d.concept].color).darker(0.5));

// Стало:
.attr("stroke", "#fff")
.attr("stroke-width", 3);
```

**Строка 3819** в updateGraphVisualization - изменить:
```javascript
// Было:
node.select("circle")
    .attr("fill", d => philosopherConcepts[d.concept].color)
    .attr("stroke", d => d3.color(philosopherConcepts[d.concept].color).darker(0.5));

// Стало:
node.select("circle")
    .attr("fill", d => philosopherConcepts[d.concept].color)
    .attr("stroke", "#fff")
    .attr("stroke-width", 3);
```

**Причина**: Соответствие стилю исходной визуализации (строка 3017).

---

## 3. ОБРАБОТЧИКИ КЛИКОВ НА ГРАФЕ

### 3.1. Создание функции handleNodeClick

**Проблема**: 
1. Обработчик клика был анонимной функцией
2. updateGraphVisualization() пытается использовать несуществующую функцию handleNodeClick
3. Shift-логика не была интегрирована

**ПЕРЕД строкой 3025** - добавить функцию:
```javascript
// Обработчик кликов на узлах (с поддержкой shift+click для редактирования)
function handleNodeClick(event, d) {
    event.stopPropagation();
    
    // Обработка shift+клик для редактирования
    if (event.shiftKey) {
        if (editMode.graphSelectionMode) {
            handleConceptSelection(d.id);
            return;
        } else if (editMode.pendingConceptSelection.length > 0) {
            const firstConceptId = editMode.pendingConceptSelection[0];
            if (firstConceptId === d.id) {
                editMode.pendingConceptSelection = [];
                node.classed('selected', false);
                openEditConceptModal(d.id);
            } else {
                editMode.pendingConceptSelection = [];
                node.classed('selected', false);
                openEditConnectionModal(firstConceptId, d.id);
            }
            return;
        } else {
            editMode.pendingConceptSelection = [d.id];
            node.classed('selected', n => n.id === d.id);
            return;
        }
    }
    
    // Отменяем выбор если кликнули без shift
    if (editMode.pendingConceptSelection.length > 0) {
        editMode.pendingConceptSelection = [];
        node.classed('selected', false);
    }
    
    // Обычная логика клика (двойной клик, выделение)
    clickCount++;
    
    if (clickTimer) {
        clearTimeout(clickTimer);
        clickTimer = null;
    }
    
    if (clickCount === 1) {
        lastClickedNode = d;
        clickTimer = setTimeout(() => {
            // Одинарный клик - выделение
            if (event.ctrlKey || event.metaKey) {
                if (selectedNodes.has(lastClickedNode)) {
                    selectedNodes.delete(lastClickedNode);
                } else {
                    selectedNodes.add(lastClickedNode);
                }
            } else {
                const connectedToSelectedEdges = isNodeConnectedToSelectedEdges(lastClickedNode);
                
                if (connectedToSelectedEdges && selectedEdges.size > 0) {
                    if (selectedNodes.size === 1 && selectedNodes.has(lastClickedNode)) {
                        selectedNodes.clear();
                    } else {
                        selectedNodes.clear();
                        selectedNodes.add(lastClickedNode);
                    }
                } else {
                    selectedEdges.clear();
                    if (selectedNodes.size === 1 && selectedNodes.has(lastClickedNode)) {
                        selectedNodes.clear();
                    } else {
                        selectedNodes.clear();
                        selectedNodes.add(lastClickedNode);
                    }
                }
            }
            
            highlightCombined();
            clickCount = 0;
            clickTimer = null;
            lastClickedNode = null;
        }, 300);
    } else if (clickCount === 2) {
        // Двойной клик - детальная информация
        showDetailModal(d);
        clickCount = 0;
        clickTimer = null;
        lastClickedNode = null;
    }
}
```

**Строка 3029** - заменить анонимную функцию на:
```javascript
node.on("click", handleNodeClick);
```

**Удалить строки 3030-3094** - вся анонимная функция.

**Строка 3798** - уже должна содержать:
```javascript
.on("click", handleNodeClick)
```

**Функционал**:
- Обычный клик → выделение узла
- Двойной клик → детальная информация
- Shift+клик → выбор для редактирования/создания связи
- Ctrl/Cmd+клик → множественное выделение

---

### 3.2. Добавление функции handleLinkClick

**Проблема**: Функция вызывается на строке 3781, но нигде не определена.

**После функции handleNodeClick** - добавить:
```javascript
// Обработчик кликов на связях
function handleLinkClick(event, d) {
    if (selectedEdges.has(d)) {
        selectedEdges.delete(d);
    } else {
        if (!(event.ctrlKey || event.metaKey)) {
            selectedEdges.clear();
            selectedNodes.clear();
        }
        selectedEdges.add(d);
    }
    highlightCombined();
}
```

**Использование**: Строки 2869, 3781 - клик на связи в обычном режиме (без shift).

---

## 4. ЛЕГЕНДА И ФИЛЬТРЫ

### 4.1. Очистка контейнеров в initFilters

**Проблема**: Контейнеры не очищаются перед добавлением элементов → дублирование при повторном вызове.

**Строка 2325** - добавить ПЕРЕД `Object.entries`:
```javascript
const philContainer = document.getElementById('philosopherFilters');
philContainer.innerHTML = ''; // ← ДОБАВИТЬ
Object.entries(philosopherConcepts).forEach(([name, data]) => {
```

**Строка 2340** - добавить ПЕРЕД `Object.entries`:
```javascript
const relContainer = document.getElementById('relationFilters');
relContainer.innerHTML = ''; // ← ДОБАВИТЬ
Object.entries(relationTypesObj).forEach(([type, typeData]) => {
```

**Причина**: 
- initFilters() вызывается при каждом изменении (создание/удаление философа)
- Без очистки каждый раз добавляются новые элементы к существующим
- Результат: двойной/тройной набор философов в легенде

---

### 4.2. Добавление value к чекбоксам философов

**Проблема**: Без атрибута value, checkbox.value возвращает "on" вместо имени философа.

**Строка 2330** - изменить:
```javascript
// Было:
<input type="checkbox" id="phil-${name}" checked onchange="togglePhilosopher('${name}')">

// Стало:
<input type="checkbox" id="phil-${name}" value="${name}" checked onchange="togglePhilosopher('${name}')">
```

**Использование**: 
- makeLegendsEditable() на строке 4590 читает checkbox.value
- Без value не работает shift+клик на философе в легенде

---

## 5. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ

### 5.1. Исправление findPhilosopherByName

**Проблема**: 
1. Ищет по p.name, которое не существует (см. 1.3)
2. Неэффективный O(n) поиск вместо O(1)
3. Ключ в philosopherConcepts УЖЕ является именем

**Строки 3688-3690** - заменить:
```javascript
// Было:
function findPhilosopherByName(name) {
    return Object.values(philosopherConcepts).find(p => p.name === name);
}

// Стало:
function findPhilosopherByName(name) {
    if (philosopherConcepts[name]) {
        return { name: name, ...philosopherConcepts[name] };
    }
    return null;
}
```

**Причина**: 
- philosopherConcepts имеет структуру: `{ "Кант": {...}, "Гегель": {...} }`
- Имя философа - это ключ объекта
- Прямой доступ philosopherConcepts[name] намного эффективнее

---

## 6. КОНТЕКСТНОЕ МЕНЮ (ОПЦИОНАЛЬНО)

**Проблема**: Для открытия детальной информации нужен двойной клик, что неудобно.

**После строки 3022** - добавить (опционально):
```javascript
node.on("contextmenu", function(event, d) {
    event.preventDefault();
    showDetailModal(d);
});
```

**Функционал**: Правый клик на узле открывает детальную информацию.

---

## 7. СВОДНАЯ ТАБЛИЦА ВСЕХ ИЗМЕНЕНИЙ

| # | Тип | Строка | Что изменить | Причина |
|---|-----|--------|-------------|---------|
| 1 | Переменная | 1779 | `const nodes` → `let nodes` | Переприсваивание в updateGraphData |
| 2 | Переменная | 1788 | `const links` → `let links` | Переприсваивание в updateGraphData |
| 3 | Добавление | После 1795 | Создать `let connections` | Используется в 17 местах редактирования |
| 4 | Структура | 1755-1761 | Добавить поля в philosopherConcepts | Используется в редактировании и фильтрах |
| 5 | Переменная | 2811 | `const link` → `let link` | D3 update pattern |
| 6 | Переменная | 3003 | `const node` → `let node` | D3 update pattern |
| 7 | Функция | Перед 3025 | Создать handleNodeClick | Обработка кликов + shift-логика |
| 8 | Замена | 3029 | Заменить анонимную функцию | Использование handleNodeClick |
| 9 | Удаление | 3030-3094 | Удалить анонимную функцию | Дублирование кода |
| 10 | Функция | После 3025 | Создать handleLinkClick | Обработка кликов на связях |
| 11 | Стиль | 3807 | Исправить stroke узлов | Белый ободок |
| 12 | Стиль | 3819 | Исправить stroke узлов | Белый ободок |
| 13 | Очистка | 2325 | Добавить innerHTML = '' | Избежать дублирования |
| 14 | Очистка | 2340 | Добавить innerHTML = '' | Избежать дублирования |
| 15 | Атрибут | 2330 | Добавить value="${name}" | Shift+клик на легенде |
| 16 | Функция | 3688-3690 | Исправить findPhilosopherByName | Эффективность O(1) |
| 17 | Обработчик | После 3022 | Добавить contextmenu (опц.) | Правый клик → детали |

---

## 8. ПОРЯДОК ПРИМЕНЕНИЯ ИЗМЕНЕНИЙ

Рекомендуемый порядок (чтобы избежать ошибок):

1. **Структуры данных** (№1-4): nodes, links, connections, philosopherConcepts
2. **D3 переменные** (№5-6): link, node
3. **Обработчики** (№7-10): handleNodeClick, handleLinkClick
4. **Визуализация** (№11-12): Белый ободок
5. **Легенда** (№13-15): Очистка контейнеров, value
6. **Вспомогательные** (№16-17): findPhilosopherByName, contextmenu

---

## 9. ПРОВЕРКА ПОСЛЕ ВСЕХ ИЗМЕНЕНИЙ

После применения всех изменений проверьте:

✅ **Базовый функционал**:
- [ ] Граф отображается корректно
- [ ] Клик на узел → выделение
- [ ] Двойной клик на узел → детальная информация
- [ ] Клик на связь → выделение
- [ ] Ctrl+клик → множественное выделение
- [ ] Фильтры философов работают
- [ ] У всех узлов белый ободок

✅ **Shift+клик (редактирование)**:
- [ ] Shift+клик на узел → выделение желтым
- [ ] Shift+клик на второй узел → окно связи
- [ ] Shift+клик дважды на узел → окно редактирования
- [ ] Shift+клик на связь → окно редактирования связи
- [ ] Shift+клик на философе в легенде → окно редактирования

✅ **Редактирование**:
- [ ] Создание философа работает без ошибок
- [ ] Философы не дублируются в легенде
- [ ] Годы жизни отображаются корректно
- [ ] Граф обновляется без ошибок
- [ ] Все модальные окна закрываются корректно

---

## 10. ИТОГО

**Всего изменений базового функционала**: 17

**Категории**:
- Структуры данных: 4 изменения
- D3 переменные: 2 изменения
- Обработчики: 4 изменения
- Визуализация: 2 изменения
- Легенда/фильтры: 3 изменения
- Вспомогательные: 2 изменения

**Критичность**:
- 🔴 Критично (без этого не работает): 14 изменений
- 🟡 Важно (баги/неудобства): 2 изменения
- 🟢 Опционально (улучшение UX): 1 изменение

---

## ПРИЛОЖЕНИЕ: Полный список функций, затронутых изменениями

### Изменены напрямую:
1. `handleNodeClick` - создана заново
2. `handleLinkClick` - создана заново
3. `findPhilosopherByName` - исправлена логика
4. `initFilters` - добавлена очистка
5. `updateGraphVisualization` - исправлен stroke

### Используют измененные переменные:
1. `updateGraphData` - использует connections, переприсваивает links
2. `updateGraphVisualization` - использует nodes, links, node, link
3. `findPhilosopherByName` - использует philosopherConcepts
4. `openEditPhilosopherModal` - использует philosopherConcepts
5. `savePhilosopher` - модифицирует philosopherConcepts
6. Все функции редактирования - используют connections

### D3 тикающие функции:
1. `ticked` - использует node, link
2. `drag handlers` - используют node
3. `simulation` - использует nodes, links

---

**Документ составлен на основе беседы от 25.11.2024**
**Версия: 1.0**
