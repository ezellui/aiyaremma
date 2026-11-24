# БЫСТРО: Исправить const → let для D3

## ❌ Ошибки
```
invalid assignment to const 'link'
invalid assignment to const 'node'
```

## ✅ Два исправления

### 1. Строка 2811:
```javascript
// Было:
const link = g.append("g")

// Стало:
let link = g.append("g")
```

### 2. Строка 3003:
```javascript
// Было:
const node = g.append("g")

// Стало:
let node = g.append("g")
```

---

## 📋 Итого: все изменения const → let

Для полной работы редактирования измените **5 мест**:

1. **Строка 1779**: `let nodes = concepts.map(...`
2. **Строка 1788**: `let links = relations.map(...`
3. **Строка 2811**: `let link = g.append("g")`
4. **Строка 3003**: `let node = g.append("g")`
5. **После 1795**: `let connections = relations.map(...` (если еще не добавлено)

---

После этого все операции редактирования должны работать без ошибок! ✅

## 🎯 Почему это нужно?

D3.js переприсваивает эти переменные при обновлении графа:
```javascript
link = link.data(newData);      // Обновление
link = linkEnter.merge(link);   // Объединение
```

С `const` это невозможно → ошибка.
С `let` всё работает ✅
