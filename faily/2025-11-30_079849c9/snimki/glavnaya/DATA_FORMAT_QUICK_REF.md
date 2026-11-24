# Быстрая справка: Формат данных для графа

## ✅ Правильный формат ваших данных

### Philosophers (философы)
```javascript
const philosophers = [
    { 
        id: "pythagoras",           // ← ID для ссылок
        name: "Пифагор", 
        nameRu: "Пифагор",
        color: "#8E44AD",           // ← Цвет для визуализации
        birth: -570, 
        death: -495,
        years: "570-495 до н.э.",
        description: "..."
    },
    // ... остальные философы
];
```

### Nodes/Concepts (узлы/концепции)
```javascript
const nodes = [  // или const concepts = [
    { 
        id: "number_essence",       // ← Уникальный ID
        label: "Число как сущность",
        philosopher: "pythagoras",  // ← ID философа (НЕ name!)
        rubrics: ["being"], 
        description: "...",
        extendedDescription: "..."
    },
    // ... остальные концепции
];
```

### Links/Relations (связи)
```javascript
const links = [  // или const relations = [
    { 
        source: "number_essence",   // ← ID узла-источника
        target: "harmony_spheres",  // ← ID узла-цели
        type: "presuppose",
        weight: 3,
        description: "..."
    },
    // ... остальные связи
];
```

---

## 🔑 Ключевые моменты

### ✅ ПРАВИЛЬНО:
```javascript
// Узел ссылается на философа по ID
{ 
    id: "number_essence",
    philosopher: "pythagoras"  // ← ID, не name!
}

// Связь использует ID узлов
{ 
    source: "number_essence",  // ← ID узла (строка)
    target: "harmony_spheres"  // ← ID узла (строка)
}

// Философ имеет цвет
{
    id: "pythagoras",
    color: "#8E44AD"  // ← Обязательно!
}
```

### ❌ НЕПРАВИЛЬНО:
```javascript
// НЕ используйте name для ссылок
{ 
    philosopher: "Пифагор"  // ❌ Должно быть: "pythagoras"
}

// НЕ используйте объекты вместо ID
{ 
    source: { id: "number_essence", ... }  // ❌ Должно быть: "number_essence"
}

// НЕ добавляйте color к узлу
{
    id: "number_essence",
    color: "#8E44AD"  // ❌ color только у philosopher!
}
```

---

## 📝 Как заменить тестовые данные

### Canvas версия (`canvas_graph.html`)

Найдите блок (примерно строки 185-230):
```javascript
const philosophers = [ ... ];
const nodes = [];
const links = [];

// Удалите циклы for (строки 203-230)
// Вставьте свои данные
```

Замените на:
```javascript
const philosophers = [
    { id: "pythagoras", name: "Пифагор", color: "#8E44AD", ... },
    // ... ваши философы
];

const nodes = [
    { id: "number_essence", label: "...", philosopher: "pythagoras", ... },
    // ... ваши концепции
];

const links = [
    { source: "number_essence", target: "harmony_spheres", type: "presuppose", ... },
    // ... ваши связи
];
```

### SVG версия (`optimized_graph.html`)

Найдите блок (примерно строки 151-186):
```javascript
const philosophers = [ ... ];
const concepts = [];
const relations = [];
```

Замените на свои данные (используя те же имена `concepts` и `relations`).

---

## 🐛 Если что-то не работает

### Проблема: "node not found: XXX"
```javascript
// ✅ РЕШЕНИЕ: Добавлен .id(d => d.id) в forceLink
.force("link", d3.forceLink(links).id(d => d.id).distance(60).strength(0.3))
//                                  ↑ УЖЕ ИСПРАВЛЕНО
```

### Проблема: Цвет undefined
```javascript
// ✅ РЕШЕНИЕ: Используется philosopherColors маппинг
ctx.fillStyle = philosopherColors[node.philosopher] || '#999';
//              ↑ УЖЕ ИСПРАВЛЕНО
```

### Проблема: tickCount not defined
```javascript
// ✅ РЕШЕНИЕ: Переменные объявлены в начале
let tickCount = 0;  // ← УЖЕ ИСПРАВЛЕНО (до симуляции)
```

---

## 🧪 Быстрая проверка данных

Вставьте в консоль DevTools (F12):

```javascript
// 1. Проверка philosophers
console.log('Philosophers:', philosophers.length);
console.log('First:', philosophers[0]);
// Должно быть: { id: "...", color: "...", ... }

// 2. Проверка nodes
console.log('Nodes:', nodes.length);
console.log('First:', nodes[0]);
// Должно быть: { id: "...", philosopher: "...", ... }

// 3. Проверка links
console.log('Links:', links.length);
console.log('First:', links[0]);
// Должно быть: { source: "...", target: "...", ... }

// 4. Проверка маппинга цветов
console.log('Colors:', philosopherColors);
// Должно быть: { pythagoras: "#8E44AD", ... }

// 5. Проверка соответствия
nodes.forEach(n => {
    if (!philosopherColors[n.philosopher]) {
        console.error('Unknown philosopher:', n.philosopher, 'in node:', n.id);
    }
});
// Не должно быть ошибок
```

---

## ✅ Все исправлено!

Оба файла готовы к работе с вашими данными. Просто замените тестовые данные на реальные! 🚀
