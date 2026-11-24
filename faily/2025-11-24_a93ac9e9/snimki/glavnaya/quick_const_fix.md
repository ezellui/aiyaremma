# БЫСТРОЕ ИСПРАВЛЕНИЕ: const → let

## ❌ Ошибка
```
invalid assignment to const 'links'
```

## ✅ Решение

### Изменение 1 (КРИТИЧНО):
**Строка 1788** - заменить:
```javascript
const links = relations.map(r => ({
```
на:
```javascript
let links = relations.map(r => ({
```

### Изменение 2 (РЕКОМЕНДУЕТСЯ):
**Строка 1779** - заменить:
```javascript
const nodes = concepts.map(c => ({
```
на:
```javascript
let nodes = concepts.map(c => ({
```

### Изменение 3 (ЕСЛИ connections НЕ СОЗДАНА):

**После строки 1795** добавить:
```javascript
        }));
        
        // Создаём connections для редактирования
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

## 🎯 Минимум (только чтобы убрать ошибку):
- Изменить **const** на **let** в строке 1788

## 💯 Полное решение (чтобы всё работало):
- Изменить **const** на **let** в строках 1779 и 1788
- Добавить **connections** после строки 1795 (если её еще нет)

---

После этого создание философа должно работать без ошибок! ✅
