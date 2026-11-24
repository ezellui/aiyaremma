# Темная тема для окон редактирования

## Замена CSS стилей

Найдите и замените следующие стили в секции CSS (примерно строки 1044-1410).

---

### 1. Основной контейнер модального окна (строка ~1050)

**Найти:**
```css
background: white;
```

**Заменить на:**
```css
background: rgba(42, 42, 62, 0.98);
border: 1px solid rgba(255, 255, 255, 0.15);
```

---

### 2. Тело модального окна (строка ~1112-1114)

**Найти:**
```css
.edit-modal-body {
    padding: 25px;
}
```

**Заменить на:**
```css
.edit-modal-body {
    padding: 25px;
    background: rgba(42, 42, 62, 0.98);
    color: #e0e0e0;
}
```

---

### 3. Лейблы полей (строка ~1120-1126)

**Найти:**
```css
.edit-form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
    color: #2d3436;
    font-size: 14px;
}
```

**Заменить на:**
```css
.edit-form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
    color: #a29bfe;
    font-size: 14px;
}
```

---

### 4. Поля ввода, textarea, select (строка ~1128-1147)

**Найти:**
```css
.edit-form-group input[type="text"],
.edit-form-group input[type="number"],
.edit-form-group textarea,
.edit-form-group select {
    width: 100%;
    padding: 10px 12px;
    border: 2px solid #e1e8ed;
    border-radius: 8px;
    font-size: 14px;
    font-family: inherit;
    transition: border-color 0.3s;
    box-sizing: border-box;
}

.edit-form-group input:focus,
.edit-form-group textarea:focus,
.edit-form-group select:focus {
    outline: none;
    border-color: #667eea;
}
```

**Заменить на:**
```css
.edit-form-group input[type="text"],
.edit-form-group input[type="number"],
.edit-form-group textarea,
.edit-form-group select {
    width: 100%;
    padding: 10px 12px;
    background: rgba(255, 255, 255, 0.08);
    border: 2px solid rgba(255, 255, 255, 0.15);
    border-radius: 8px;
    font-size: 14px;
    font-family: inherit;
    color: #e0e0e0;
    transition: all 0.3s;
    box-sizing: border-box;
}

.edit-form-group input:focus,
.edit-form-group textarea:focus,
.edit-form-group select:focus {
    outline: none;
    border-color: #a29bfe;
    background: rgba(255, 255, 255, 0.12);
}

.edit-form-group input::placeholder,
.edit-form-group textarea::placeholder {
    color: rgba(224, 224, 224, 0.5);
}
```

---

### 5. Color input (строка ~1154-1160)

**Найти:**
```css
.edit-form-group input[type="color"] {
    width: 60px;
    height: 40px;
    border: 2px solid #e1e8ed;
    border-radius: 8px;
    cursor: pointer;
}
```

**Заменить на:**
```css
.edit-form-group input[type="color"] {
    width: 60px;
    height: 40px;
    background: rgba(255, 255, 255, 0.08);
    border: 2px solid rgba(255, 255, 255, 0.15);
    border-radius: 8px;
    cursor: pointer;
}
```

---

### 6. Checkbox labels (строка ~1185-1189)

**Найти:**
```css
.edit-form-checkbox label {
    margin: 0;
    cursor: pointer;
    font-weight: 600;
}
```

**Заменить на:**
```css
.edit-form-checkbox label {
    margin: 0;
    cursor: pointer;
    font-weight: 600;
    color: #e0e0e0;
}
```

---

### 7. Разделитель действий (строка ~1192-1198)

**Найти:**
```css
.edit-modal-actions {
    display: flex;
    gap: 10px;
    margin-top: 25px;
    padding-top: 20px;
    border-top: 2px solid #e1e8ed;
}
```

**Заменить на:**
```css
.edit-modal-actions {
    display: flex;
    gap: 10px;
    margin-top: 25px;
    padding-top: 20px;
    border-top: 2px solid rgba(255, 255, 255, 0.15);
}
```

---

### 8. Секция списка (строка ~1242-1253)

**Найти:**
```css
.edit-list-section {
    margin-top: 20px;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;
}

.edit-list-section h4 {
    margin: 0 0 15px 0;
    font-size: 16px;
    color: #2d3436;
}
```

**Заменить на:**
```css
.edit-list-section {
    margin-top: 20px;
    padding: 15px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    border-left: 3px solid #a29bfe;
}

.edit-list-section h4 {
    margin: 0 0 15px 0;
    font-size: 16px;
    color: #a29bfe;
}
```

---

### 9. Элементы списка (строка ~1255-1284)

**Найти:**
```css
.edit-list-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px;
    background: white;
    border-radius: 6px;
    margin-bottom: 8px;
    transition: background 0.2s;
}

.edit-list-item:hover {
    background: #e8f4f8;
}

.edit-list-item-content {
    flex: 1;
    cursor: pointer;
}

.edit-list-item-name {
    font-weight: 600;
    color: #2d3436;
    margin-bottom: 3px;
}

.edit-list-item-desc {
    font-size: 12px;
    color: #636e72;
}
```

**Заменить на:**
```css
.edit-list-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px;
    background: rgba(255, 255, 255, 0.08);
    border-radius: 6px;
    margin-bottom: 8px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: all 0.2s;
}

.edit-list-item:hover {
    background: rgba(255, 255, 255, 0.15);
    border-color: rgba(162, 155, 254, 0.4);
}

.edit-list-item-content {
    flex: 1;
    cursor: pointer;
}

.edit-list-item-name {
    font-weight: 600;
    color: #e0e0e0;
    margin-bottom: 3px;
}

.edit-list-item-desc {
    font-size: 12px;
    color: #b0b0b0;
}
```

---

### 10. Поиск концепций - input (строка ~1342-1349)

**Найти:**
```css
.concept-search-input {
    width: 100%;
    padding: 10px 12px;
    border: 2px solid #e1e8ed;
    border-radius: 8px;
    font-size: 14px;
    box-sizing: border-box;
}
```

**Заменить на:**
```css
.concept-search-input {
    width: 100%;
    padding: 10px 12px;
    background: rgba(255, 255, 255, 0.08);
    border: 2px solid rgba(255, 255, 255, 0.15);
    border-radius: 8px;
    font-size: 14px;
    color: #e0e0e0;
    box-sizing: border-box;
    transition: all 0.3s;
}

.concept-search-input:focus {
    outline: none;
    border-color: #a29bfe;
    background: rgba(255, 255, 255, 0.12);
}

.concept-search-input::placeholder {
    color: rgba(224, 224, 224, 0.5);
}
```

---

### 11. Результаты поиска концепций (строка ~1351-1402)

**Найти:**
```css
.concept-search-results {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    max-height: 200px;
    overflow-y: auto;
    background: white;
    border: 2px solid #667eea;
    border-radius: 8px;
    margin-top: 5px;
    z-index: 1000;
    display: none;
}

.concept-search-results.show {
    display: block;
}

.concept-search-item {
    padding: 10px;
    cursor: pointer;
    border-bottom: 1px solid #e1e8ed;
    display: flex;
    align-items: center;
    gap: 10px;
}

.concept-search-item:hover {
    background: #f0f3ff;
}

.concept-search-item:last-child {
    border-bottom: none;
}

.concept-search-color {
    width: 12px;
    height: 12px;
    border-radius: 50%;
}

.concept-search-name {
    font-weight: 600;
    color: #2d3436;
}

.concept-search-philosopher {
    font-size: 12px;
    color: #636e72;
    margin-left: auto;
}
```

**Заменить на:**
```css
.concept-search-results {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    max-height: 200px;
    overflow-y: auto;
    background: rgba(42, 42, 62, 0.98);
    border: 2px solid #a29bfe;
    border-radius: 8px;
    margin-top: 5px;
    z-index: 1000;
    display: none;
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.5);
}

.concept-search-results.show {
    display: block;
}

.concept-search-item {
    padding: 10px;
    cursor: pointer;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    display: flex;
    align-items: center;
    gap: 10px;
    transition: all 0.2s;
}

.concept-search-item:hover {
    background: rgba(162, 155, 254, 0.2);
}

.concept-search-item:last-child {
    border-bottom: none;
}

.concept-search-color {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    box-shadow: 0 0 6px currentColor;
}

.concept-search-name {
    font-weight: 600;
    color: #e0e0e0;
}

.concept-search-philosopher {
    font-size: 12px;
    color: #b0b0b0;
    margin-left: auto;
}
```

---

## 📋 Краткий список изменений

Всего **11 блоков CSS** нужно изменить:

1. `.edit-modal` - фон темный + border
2. `.edit-modal-body` - фон темный + цвет текста
3. `.edit-form-group label` - цвет #a29bfe
4. Input/textarea/select - темный фон + светлый текст + темные borders
5. Color input - темный фон + темный border
6. Checkbox label - светлый цвет
7. `.edit-modal-actions` - темный border
8. `.edit-list-section` - темный фон + border-left
9. `.edit-list-item` - темный фон + светлый текст
10. `.concept-search-input` - темный фон + светлый текст
11. `.concept-search-results` и items - темный фон + светлый текст

---

## ✅ Результат

После применения всех изменений:
- ✅ Все модальные окна будут в темной теме
- ✅ Единый стиль с окном детальной информации
- ✅ Цветовая схема: фон темно-фиолетовый, текст светлый, акценты фиолетовые
- ✅ Улучшенная читаемость и визуальная согласованность

---

## 🎨 Цветовая палитра темной темы

- Фон модальных окон: `rgba(42, 42, 62, 0.98)`
- Фон элементов: `rgba(255, 255, 255, 0.08)`
- Границы: `rgba(255, 255, 255, 0.15)`
- Основной текст: `#e0e0e0`
- Вторичный текст: `#b0b0b0`
- Акценты (заголовки): `#a29bfe`
- Hover: `rgba(255, 255, 255, 0.15)` или `rgba(162, 155, 254, 0.2)`
