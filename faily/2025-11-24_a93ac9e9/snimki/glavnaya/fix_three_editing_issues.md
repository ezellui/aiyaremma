# ИСПРАВЛЕНИЕ: Три проблемы с редактированием

## Проблема #1: Белый ободок становится цветным

### Причина:
В `updateGraphVisualization` stroke устанавливается как `.darker(0.5)` вместо белого.

### Исправление 1.1: Строка 3807

**Найти:**
```javascript
nodeEnter.append("circle")
    .attr("r", 12)
    .attr("fill", d => philosopherConcepts[d.concept].color)
    .attr("stroke", d => d3.color(philosopherConcepts[d.concept].color).darker(0.5));
```

**Заменить на:**
```javascript
nodeEnter.append("circle")
    .attr("r", 12)
    .attr("fill", d => philosopherConcepts[d.concept].color)
    .attr("stroke", "#fff")
    .attr("stroke-width", 3);
```

### Исправление 1.2: Строка 3817-3819

**Найти:**
```javascript
// Обновляем цвета существующих узлов (на случай изменения философа)
node.select("circle")
    .attr("fill", d => philosopherConcepts[d.concept].color)
    .attr("stroke", d => d3.color(philosopherConcepts[d.concept].color).darker(0.5));
```

**Заменить на:**
```javascript
// Обновляем цвета существующих узлов (на случай изменения философа)
node.select("circle")
    .attr("fill", d => philosopherConcepts[d.concept].color)
    .attr("stroke", "#fff")
    .attr("stroke-width", 3);
```

---

## Проблема #2: Двойной набор философов в панели

### Причина:
`initFilters()` не очищает контейнеры перед добавлением новых элементов, поэтому при каждом вызове добавляет элементы к существующим.

### Исправление 2: Строки 2324-2326 и 2339-2340

**Найти (строка 2324-2326):**
```javascript
function initFilters() {
    // Создаем фильтры философов
    const philContainer = document.getElementById('philosopherFilters');
    Object.entries(philosopherConcepts).forEach(([name, data]) => {
```

**Заменить на:**
```javascript
function initFilters() {
    // Создаем фильтры философов
    const philContainer = document.getElementById('philosopherFilters');
    philContainer.innerHTML = ''; // ✅ ОЧИЩАЕМ контейнер перед добавлением
    Object.entries(philosopherConcepts).forEach(([name, data]) => {
```

**И найти (строка 2339-2340):**
```javascript
    // Создаем фильтры связей (без изменений)
    const relContainer = document.getElementById('relationFilters');
    Object.entries(relationTypesObj).forEach(([type, typeData]) => {
```

**Заменить на:**
```javascript
    // Создаем фильтры связей (без изменений)
    const relContainer = document.getElementById('relationFilters');
    relContainer.innerHTML = ''; // ✅ ОЧИЩАЕМ контейнер перед добавлением
    Object.entries(relationTypesObj).forEach(([type, typeData]) => {
```

---

## Проблема #3: undefined в годах жизни философа

### Причина:
При создании философа поле `years` не заполняется, но используется в легенде (строка 2333).

### Исправление 3.1: Создание нового философа (строки 3908-3914)

**Найти:**
```javascript
// Добавляем нового философа
philosopherConcepts[name] = {
    name: name,
    color: color,
    birth: birth || null,
    death: death || null
};
```

**Заменить на:**
```javascript
// Добавляем нового философа
const years = (birth && death) ? `${birth}–${death}` : 
              birth ? `${birth}–...` : 
              death ? `...–${death}` : '...';

philosopherConcepts[name] = {
    name: name,
    color: color,
    years: years,
    birth: birth || null,
    death: death || null
};
```

### Исправление 3.2: Обновление философа при изменении имени (строки 3935-3940)

**Найти:**
```javascript
// Удаляем старую запись и создаем новую
delete philosopherConcepts[oldName];
philosopherConcepts[name] = {
    name: name,
    color: color,
    birth: birth || null,
    death: death || null
};
```

**Заменить на:**
```javascript
// Удаляем старую запись и создаем новую
delete philosopherConcepts[oldName];

const years = (birth && death) ? `${birth}–${death}` : 
              birth ? `${birth}–...` : 
              death ? `...–${death}` : '...';

philosopherConcepts[name] = {
    name: name,
    color: color,
    years: years,
    birth: birth || null,
    death: death || null
};
```

### Исправление 3.3: Обновление философа без изменения имени (строки 3942-3946)

**Найти:**
```javascript
} else {
    // Просто обновляем свойства
    philosopherConcepts[name].color = color;
    philosopherConcepts[name].birth = birth || null;
    philosopherConcepts[name].death = death || null;
}
```

**Заменить на:**
```javascript
} else {
    // Просто обновляем свойства
    const years = (birth && death) ? `${birth}–${death}` : 
                  birth ? `${birth}–...` : 
                  death ? `...–${death}` : '...';
    
    philosopherConcepts[name].color = color;
    philosopherConcepts[name].years = years;
    philosopherConcepts[name].birth = birth || null;
    philosopherConcepts[name].death = death || null;
}
```

---

## 📝 Краткий список всех изменений

### 1. Белый ободок (2 места):
- Строка 3807: добавить `.attr("stroke", "#fff").attr("stroke-width", 3)`
- Строка 3819: заменить `.darker(0.5)` на `"#fff"` и добавить stroke-width

### 2. Дублирование философов (2 места):
- Строка 2325: добавить `philContainer.innerHTML = '';`
- Строка 2340: добавить `relContainer.innerHTML = '';`

### 3. undefined в годах (3 места):
- Строка 3909: добавить формирование `years` и включить в объект
- Строка 3936: добавить формирование `years` и включить в объект
- Строка 3943: добавить формирование `years` и обновление поля

---

## ✅ Проверка после исправления

### Проблема #1 - Ободок:
1. Создайте нового философа
2. Проверьте, что у всех узлов остался **белый** ободок ✅

### Проблема #2 - Дублирование:
1. Создайте нового философа
2. Проверьте, что в панели легенд философы **не дублируются** ✅
3. Каждый философ показан **один раз** ✅

### Проблема #3 - Годы:
1. Создайте философа с годами рождения 1724 и смерти 1804
2. В панели должно быть: `Кант (1724–1804)` ✅
3. Создайте философа только с годом рождения 1940
4. В панели должно быть: `Делёз (1940–...)` ✅

---

## 🎯 Дополнительно: Форматы годов

Код поддерживает разные форматы:
- `1724–1804` - оба года указаны
- `1940–...` - только год рождения
- `...–1789` - только год смерти
- `...` - годы не указаны

Можете изменить формат на свой вкус, например:
- `1724-1804` (обычный дефис)
- `1724 - 1804` (с пробелами)
- `*1724 †1804` (со звездочкой и крестом)
- `р. 1724` (только рождение)

---

## 💡 Почему это важно?

1. **Белый ободок** - визуальная согласованность графа
2. **Без дублирования** - чистота интерфейса и корректная работа чекбоксов
3. **Годы жизни** - информативность и полнота данных о философе
