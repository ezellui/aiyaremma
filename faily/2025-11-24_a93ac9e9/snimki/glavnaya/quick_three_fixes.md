# БЫСТРО: Исправить 3 проблемы редактирования

## 🔧 Исправление #1: Белый ободок

### Строка 3807 - заменить:
```javascript
.attr("stroke", d => d3.color(philosopherConcepts[d.concept].color).darker(0.5));
```
на:
```javascript
.attr("stroke", "#fff")
.attr("stroke-width", 3);
```

### Строка 3819 - заменить:
```javascript
.attr("stroke", d => d3.color(philosopherConcepts[d.concept].color).darker(0.5));
```
на:
```javascript
.attr("stroke", "#fff")
.attr("stroke-width", 3);
```

---

## 🔧 Исправление #2: Дублирование философов

### Строка 2325 - добавить ПЕРЕД `Object.entries`:
```javascript
const philContainer = document.getElementById('philosopherFilters');
philContainer.innerHTML = ''; // ← ДОБАВИТЬ ЭТУ СТРОКУ
Object.entries(philosopherConcepts).forEach(([name, data]) => {
```

### Строка 2330 - также добавить value (если еще не добавлено):
```javascript
<input type="checkbox" id="phil-${name}" value="${name}" checked onchange="togglePhilosopher('${name}')">
```

### Строка 2340 - добавить ПЕРЕД `Object.entries`:
```javascript
const relContainer = document.getElementById('relationFilters');
relContainer.innerHTML = ''; // ← ДОБАВИТЬ ЭТУ СТРОКУ
Object.entries(relationTypesObj).forEach(([type, typeData]) => {
```

---

## 🔧 Исправление #3: undefined в годах

### Место 1: Строка 3908 - заменить:
```javascript
// Добавляем нового философа
philosopherConcepts[name] = {
    name: name,
    color: color,
    birth: birth || null,
    death: death || null
};
```
на:
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

### Место 2: Строка 3935 - заменить:
```javascript
delete philosopherConcepts[oldName];
philosopherConcepts[name] = {
    name: name,
    color: color,
    birth: birth || null,
    death: death || null
};
```
на:
```javascript
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

### Место 3: Строка 3943 - заменить:
```javascript
// Просто обновляем свойства
philosopherConcepts[name].color = color;
philosopherConcepts[name].birth = birth || null;
philosopherConcepts[name].death = death || null;
```
на:
```javascript
// Просто обновляем свойства
const years = (birth && death) ? `${birth}–${death}` : 
              birth ? `${birth}–...` : 
              death ? `...–${death}` : '...';

philosopherConcepts[name].color = color;
philosopherConcepts[name].years = years;
philosopherConcepts[name].birth = birth || null;
philosopherConcepts[name].death = death || null;
```

---

## ✅ Итого: 8 изменений

1. ✅ Строка 3807: белый stroke
2. ✅ Строка 3819: белый stroke
3. ✅ Строка 2325: очистка контейнера
4. ✅ Строка 2340: очистка контейнера
5. ✅ Строка 3909: добавить years
6. ✅ Строка 3936: добавить years
7. ✅ Строка 3943: обновлять years

После этого:
- ✅ Ободок остается белым
- ✅ Философы не дублируются
- ✅ Годы отображаются корректно (например: "1724–1804")
