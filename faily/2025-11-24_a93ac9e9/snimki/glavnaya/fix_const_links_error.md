# ИСПРАВЛЕНИЕ: invalid assignment to const 'links'

## Проблема

Ошибка возникает потому что:
1. `links` объявлена как `const` (строка 1788)
2. Функция `updateGraphData()` пытается переприсвоить `links` (строка 3741)
3. Константы нельзя переприсваивать → ошибка

## ✅ РЕШЕНИЕ

### Исправление 1: Изменить const на let для links

**Строка 1788** - найти:
```javascript
const links = relations.map(r => ({
```

**Заменить на:**
```javascript
let links = relations.map(r => ({
```

---

### Исправление 2: Также изменить для nodes (для безопасности)

**Строка 1779** - найти:
```javascript
const nodes = concepts.map(c => ({
```

**Заменить на:**
```javascript
let nodes = concepts.map(c => ({
```

Хотя nodes не переприсваивается напрямую, её лучше тоже сделать `let` для единообразия и на будущее.

---

### ВАЖНО: Проверить наличие connections

Функция `updateGraphData` также использует переменную `connections`:
```javascript
links = connections.map(conn => ({
```

**Проверьте, была ли добавлена переменная `connections`** после строки 1795.

Если НЕТ, нужно добавить после строки 1795:

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

---

## 📝 Итоговый список изменений

### 1. Строка 1779:
```javascript
// Было:
const nodes = concepts.map(c => ({

// Стало:
let nodes = concepts.map(c => ({
```

### 2. Строка 1788:
```javascript
// Было:
const links = relations.map(r => ({

// Стало:
let links = relations.map(r => ({
```

### 3. После строки 1795 (если connections еще не добавлена):
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
        const conceptToRubrics = {};
```

---

## ✅ Проверка после исправления

1. Откройте окно добавления философа
2. Заполните имя, цвет, годы жизни
3. Нажмите "Сохранить"
4. Ошибка должна исчезнуть
5. Философ должен появиться в легенде
6. Граф должен обновиться без ошибок

---

## 🔍 Объяснение

### Почему const не работает?

```javascript
const links = [1, 2, 3];

// ✅ Можно изменять содержимое:
links.push(4);        // OK
links[0] = 10;        // OK

// ❌ Нельзя переприсваивать:
links = [5, 6, 7];    // ERROR: invalid assignment to const
```

### Когда использовать let vs const?

- `const` - когда переменная НЕ будет переприсваиваться
- `let` - когда переменная МОЖЕТ быть переприсвоена

Для `nodes`, `links`, `connections` используем `let`, потому что:
- `updateGraphData()` переприсваивает `links`
- В будущем может потребоваться переприсваивание и `nodes`
- Единообразие кода

---

## 🎯 Минимальное решение (только критическое)

Если хотите исправить только то, что ломается прямо сейчас:

**Строка 1788** - изменить:
```javascript
const links = relations.map(r => ({
```
на:
```javascript
let links = relations.map(r => ({
```

Этого достаточно, чтобы убрать ошибку.

Но **рекомендуется сделать все 3 изменения** для полной совместимости с функционалом редактирования.
