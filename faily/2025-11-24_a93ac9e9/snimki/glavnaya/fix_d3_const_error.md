# ИСПРАВЛЕНИЕ: const → let для переменных D3

## ❌ Ошибка
```
invalid assignment to const 'link' (строка 3763)
```

А после исправления появится аналогичная для `node` (строка 3788).

## Проблема

D3 переменные `link` и `node` объявлены как константы, но функция `updateGraphVisualization` переприсваивает их при обновлении графа:

```javascript
// Строка 3763:
link = link.data(links, ...);  // ❌ Переприсваивание const

// Строка 3785:
link = linkEnter.merge(link);  // ❌ Переприсваивание const

// Строка 3788:
node = node.data(nodes, ...);  // ❌ Переприсваивание const

// Строка 3814:
node = nodeEnter.merge(node);  // ❌ Переприсваивание const
```

## ✅ РЕШЕНИЕ

### Исправление 1: link (КРИТИЧНО)

**Строка 2811** - найти:
```javascript
const link = g.append("g")
    .selectAll("path")
    .data(links)
```

**Заменить на:**
```javascript
let link = g.append("g")
    .selectAll("path")
    .data(links)
```

---

### Исправление 2: node (КРИТИЧНО)

**Строка 3003** - найти:
```javascript
const node = g.append("g")
    .selectAll("g")
    .data(nodes)
```

**Заменить на:**
```javascript
let node = g.append("g")
    .selectAll("g")
    .data(nodes)
```

---

## 📝 Полный список изменений const → let

Для полной работы редактирования нужно изменить **5 переменных**:

### 1. Строка 1779 - nodes (массив данных):
```javascript
let nodes = concepts.map(c => ({
```

### 2. Строка 1788 - links (массив данных):
```javascript
let links = relations.map(r => ({
```

### 3. Строка 2811 - link (D3 selection для связей):
```javascript
let link = g.append("g")
```

### 4. Строка 3003 - node (D3 selection для узлов):
```javascript
let node = g.append("g")
```

### 5. После строки 1795 - connections (если еще не добавлено):
```javascript
let connections = relations.map(r => ({
    from: r.source,
    to: r.target,
    type: r.type,
    weight: r.weight || 2,
    bidirectional: r.bidirectional || false,
    description: r.description
}));
```

---

## 🎯 Зачем нужны эти переменные?

1. **nodes** и **links** - исходные данные, переприсваиваются в `updateGraphData()`
2. **link** и **node** - D3 selections, переприсваиваются в `updateGraphVisualization()`
3. **connections** - данные для редактирования с полями `from`/`to` вместо `source`/`target`

---

## ✅ Проверка после исправления

1. Откройте окно добавления философа
2. Заполните все поля (имя, цвет, годы)
3. Нажмите "Сохранить"
4. **Не должно быть ошибок** ✅
5. Философ должен появиться в легенде
6. Граф должен обновиться

Затем:
7. Добавьте концепцию для этого философа
8. Граф должен обновиться без ошибок
9. Создайте связь между концепциями
10. Всё должно работать без ошибок ✅

---

## 🔍 Почему это происходит?

D3.js использует паттерн **update pattern**, где:
```javascript
// 1. Получаем новую выборку с обновленными данными
selection = selection.data(newData);

// 2. Удаляем старые элементы
selection.exit().remove();

// 3. Добавляем новые элементы
const enter = selection.enter().append(...);

// 4. ПЕРЕПРИСВАИВАЕМ переменную объединенной выборкой
selection = enter.merge(selection);  // ← Вот почему нужен let!
```

Без `let` последняя строка выдает ошибку при попытке переприсвоить `const`.

---

## 💡 Совет на будущее

При работе с D3.js всегда используйте `let` для переменных, хранящих selections:
- `let selection = svg.selectAll(...)`
- `let nodes = g.selectAll(".node")`
- `let links = g.selectAll(".link")`

Это избавит от подобных ошибок при использовании update pattern.
