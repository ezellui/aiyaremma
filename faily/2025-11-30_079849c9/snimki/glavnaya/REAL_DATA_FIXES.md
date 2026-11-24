# Исправления для работы с реальными данными

## 📋 Формат ваших данных

```javascript
// Философы
{ 
    id: "pythagoras", 
    name: "Пифагор", 
    color: "#8E44AD", 
    // ... другие поля
}

// Концепции (nodes)
{ 
    id: "number_essence", 
    label: "Число как сущность", 
    philosopher: "pythagoras",  // ← ID философа
    rubrics: ["being"], 
    description: "...",
    extendedDescription: "..."
}

// Связи (links)
{ 
    source: "number_essence",   // ← ID узла
    target: "harmony_spheres",  // ← ID узла
    type: "presuppose", 
    weight: 3, 
    description: "..." 
}
```

## 🐛 Найденные проблемы и решения

### Проблема 1: "node not found: number_essence" ✅ ИСПРАВЛЕНО

**Ошибка:**
```
Error: node not found: number_essence
at force.js:74
```

**Причина:**
D3 forceLink по умолчанию ожидает, что `source` и `target` - это объекты узлов, а не строки (id).

**Было:**
```javascript
.force("link", d3.forceLink(links).distance(60).strength(0.3))
```

**Стало:**
```javascript
.force("link", d3.forceLink(links).id(d => d.id).distance(60).strength(0.3))
//                                  ↑ ДОБАВЛЕНО: указываем как связывать id
```

**Что делает `.id(d => d.id)`:**
Говорит D3: "когда в links встречаются `source: "number_essence"`, найди узел где `node.id === "number_essence"`"

---

### Проблема 2: "Ожидалось определение цвета, но найдено «undefined»" ✅ ИСПРАВЛЕНО

**Ошибка:**
```
Expected a color definition, but found 'undefined'
```

**Причина:**
В вашем формате данных цвет хранится в объекте `philosopher`, а не в объекте `node`.

**Ваши данные:**
```javascript
// У узла НЕТ поля color
{ 
    id: "number_essence", 
    philosopher: "pythagoras",  // ← Только ссылка на философа
}

// Цвет есть у философа
{ 
    id: "pythagoras", 
    color: "#8E44AD"  // ← Цвет здесь!
}
```

**Решение 1: Создали маппинг**
```javascript
// После определения philosophers
const philosopherColors = {};
philosophers.forEach(p => {
    philosopherColors[p.id] = p.color;
});
// Теперь: philosopherColors["pythagoras"] === "#8E44AD"
```

**Решение 2: Используем маппинг**

Canvas версия:
```javascript
// БЫЛО:
ctx.fillStyle = node.color;  // ❌ node.color === undefined

// СТАЛО:
ctx.fillStyle = philosopherColors[node.philosopher] || '#999';
//                ↑ Получаем цвет из философа
```

SVG версия:
```javascript
// БЫЛО:
.attr("fill", d => philosopherColors[d.philosopherId] || "#999")

// СТАЛО:
.attr("fill", d => philosopherColors[d.philosopher] || "#999")
//                                     ↑ Используем правильное поле
```

---

### Проблема 3: "can't access lexical declaration 'tickCount' before initialization" ✅ ИСПРАВЛЕНО

**Ошибка:**
```
ReferenceError: can't access lexical declaration 'tickCount' before initialization
```

**Причина:**
Функция `render()` использует `tickCount`, но `tickCount` объявлялся ПОСЛЕ создания симуляции.

**Порядок выполнения (НЕПРАВИЛЬНЫЙ):**
```
1. Создаётся simulation
2. Определяется render() (использует tickCount)
3. Объявляется tickCount  ❌
4. resizeCanvas() вызывает render()
   → ошибка: tickCount не определён
```

**Решение:**
Объявили переменные состояния ДО симуляции:

```javascript
// ПЕРЕМЕННЫЕ СОСТОЯНИЯ - В НАЧАЛЕ
let simulationRunning = true;
let tickCount = 0;
let frameCount = 0;
let lastFpsUpdate = performance.now();

// ПОТОМ симуляция
const simulation = d3.forceSimulation(nodes)...

// ПОТОМ функции
function render() {
    // Теперь tickCount доступен!
    document.getElementById('ticks').textContent = tickCount;
}
```

---

## ✅ Итоговые изменения

### Canvas версия (`canvas_graph.html`):

1. ✅ Добавлено `.id(d => d.id)` в forceLink (строка ~234)
2. ✅ Создан маппинг `philosopherColors` (после philosophers)
3. ✅ Изменено `node.color` → `philosopherColors[node.philosopher]` (в render)
4. ✅ Переменные состояния объявлены до симуляции
5. ✅ Тестовые данные обновлены: `philosopher: phil.id` вместо `phil.name`

### SVG версия (`optimized_graph.html`):

1. ✅ `.id(d => d.id)` уже был
2. ✅ `philosopherColors` маппинг уже был
3. ✅ Изменено `d.philosopherId` → `d.philosopher` (в fill)
4. ✅ Тестовые данные обновлены: `philosopher: phil.id` вместо `philosopherId`

---

## 🧪 Тестирование с вашими данными

### Шаг 1: Замените тестовые данные

**Canvas версия:**
```javascript
// Замените этот блок (примерно строки 185-225)
const philosophers = [
    { id: "pythagoras", name: "Пифагор", color: "#8E44AD", ... },
    // ... ваши философы
];

const nodes = [
    { 
        id: "number_essence", 
        label: "Число как сущность", 
        philosopher: "pythagoras",  // ← ID философа
        description: "...",
    },
    // ... ваши концепции
];

const links = [
    { source: "number_essence", target: "harmony_spheres", type: "presuppose", ... },
    // ... ваши связи
];
```

**SVG версия:**
```javascript
// Замените блок с concepts и relations (примерно строки 151-185)
const philosophers = [ /* ваши данные */ ];
const concepts = [ /* ваши концепции */ ];
const relations = [ /* ваши связи */ ];
```

### Шаг 2: Проверьте в консоли

Откройте DevTools (F12) и выполните:

```javascript
// Проверка маппинга цветов
console.log(philosopherColors);
// Должно показать: { pythagoras: "#8E44AD", ... }

// Проверка узлов
console.log(nodes[0]);
// Должно быть: { id: "number_essence", philosopher: "pythagoras", ... }

// Проверка связей
console.log(links[0]);
// Должно быть: { source: {...}, target: {...}, ... }
// После инициализации D3 превращает строки в объекты!
```

### Шаг 3: Проверьте визуализацию

- ✅ Граф отображается без ошибок
- ✅ Узлы имеют правильные цвета
- ✅ Связи соединяют узлы корректно
- ✅ Перетаскивание работает
- ✅ Индикаторы обновляются

---

## 🎨 Дополнительная настройка цветов

Если у некоторых философов нет цвета, или вы хотите изменить цвет по умолчанию:

```javascript
// В render() (Canvas версия):
ctx.fillStyle = philosopherColors[node.philosopher] || '#999';
//                                                      ↑ Цвет по умолчанию

// В attr("fill") (SVG версия):
.attr("fill", d => philosopherColors[d.philosopher] || "#999")
//                                                      ↑ Цвет по умолчанию
```

---

## 🔍 Отладка проблем с данными

### Если узлы не отображаются:

```javascript
// Проверьте структуру
console.log('Philosophers:', philosophers.length);
console.log('Nodes:', nodes.length);
console.log('Links:', links.length);

// Проверьте первый узел
console.log('First node:', nodes[0]);
// Должно быть: { id: "...", philosopher: "...", x: ..., y: ... }

// Проверьте маппинг
console.log('Color for first node:', philosopherColors[nodes[0].philosopher]);
// Должен быть цвет, например "#8E44AD"
```

### Если связи не работают:

```javascript
// Проверьте что source/target это строки ДО симуляции
console.log('Link before sim:', links[0]);
// { source: "number_essence", target: "harmony_spheres", ... }

// После tick симуляции они становятся объектами
setTimeout(() => {
    console.log('Link after sim:', links[0]);
    // { source: {id: "number_essence", ...}, target: {id: "harmony_spheres", ...} }
}, 1000);
```

### Если цвета неправильные:

```javascript
// Проверьте что все философы имеют id и color
philosophers.forEach(p => {
    if (!p.id || !p.color) {
        console.warn('Philosopher missing id or color:', p);
    }
});

// Проверьте что все узлы ссылаются на существующих философов
nodes.forEach(n => {
    if (!philosopherColors[n.philosopher]) {
        console.warn('Node references unknown philosopher:', n.id, n.philosopher);
    }
});
```

---

## 📚 Дополнительная информация

### Почему нужен .id(d => d.id)?

D3 forceLink работает двумя способами:

**Способ 1: Объекты (по умолчанию)**
```javascript
const nodes = [{ id: "a" }, { id: "b" }];
const links = [{ source: nodes[0], target: nodes[1] }];
//                       ↑ объект    ↑ объект
```

**Способ 2: ID строки (с .id())**
```javascript
const nodes = [{ id: "a" }, { id: "b" }];
const links = [{ source: "a", target: "b" }];
//                       ↑ строка ↑ строка

// Нужно сказать D3 как найти узел по строке:
.force("link", d3.forceLink(links).id(d => d.id))
```

Ваш формат использует Способ 2, поэтому нужен `.id()`.

---

## ✅ Всё готово!

Обе версии (`canvas_graph.html` и `optimized_graph.html`) теперь совместимы с вашим форматом данных.

Просто замените тестовые данные на свои реальные данные philosophers/nodes/links! 🚀
