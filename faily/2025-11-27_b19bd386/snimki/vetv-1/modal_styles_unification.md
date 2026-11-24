# Унификация стилей модальных окон

## Обзор

Этот рефакторинг объединяет общие CSS стили для всех модальных окон приложения (детальной информации и редактирования), избегая дублирования кода и упрощая поддержку.

---

## Текущее состояние

**Существующие модальные окна:**
1. `#detailModal` и `#philosopherDetailModal` - окна детальной информации (класс `.detail-modal`)
2. `#editPhilosopherModal`, `#editConceptModal`, `#editConnectionModal` - окна редактирования (класс `.edit-modal`)

**Проблема:** Много дублирующихся CSS свойств между `.detail-modal` и `.edit-modal`

---

## Архитектура после рефакторинга

```
.modal-base (базовый класс)
  ├── .modal-detail (специфика для окон детальной информации)
  └── .modal-edit (специфика для окон редактирования)
```

---

## 1. Обновить HTML - добавить базовый класс

### 1.1. Окна детальной информации

**Строка 1634-1637 - окно концепции:**

**Было:**
```html
<div id="detailModal" class="detail-modal">
    <button class="close-btn" onclick="closeDetailModal()">×</button>
    <div id="modalContent" class="modal-content"></div>
</div>
```

**Заменить на:**
```html
<div id="detailModal" class="modal-base modal-detail">
    <button class="modal-close-btn" onclick="closeDetailModal()">×</button>
    <div id="modalContent" class="modal-content"></div>
</div>
```

**После строки 1637 - окно философа:**

**Было:**
```html
<div id="philosopherDetailModal" class="detail-modal">
    <button class="close-btn" onclick="closePhilosopherDetailModal()">×</button>
    <div id="philosopherModalContent" class="modal-content"></div>
</div>
```

**Заменить на:**
```html
<div id="philosopherDetailModal" class="modal-base modal-detail">
    <button class="modal-close-btn" onclick="closePhilosopherDetailModal()">×</button>
    <div id="philosopherModalContent" class="modal-content"></div>
</div>
```

### 1.2. Окна редактирования

**Найти все три окна редактирования (строки примерно 5200-5366) и обновить классы:**

**Было (пример для окна философа):**
```html
<div id="editPhilosopherModal" class="edit-modal">
    <div class="edit-modal-header">
        <h3 id="editPhilosopherTitle">Редактировать философа</h3>
        <button class="edit-modal-close" onclick="closeEditPhilosopherModal()">×</button>
    </div>
    <div class="edit-modal-body">
        ...
    </div>
</div>
```

**Заменить на:**
```html
<div id="editPhilosopherModal" class="modal-base modal-edit">
    <div class="modal-edit-header">
        <h3 id="editPhilosopherTitle">Редактировать философа</h3>
        <button class="modal-close-btn" onclick="closeEditPhilosopherModal()">×</button>
    </div>
    <div class="modal-edit-body">
        ...
    </div>
</div>
```

**То же самое для:**
- `#editConceptModal`
- `#editConnectionModal`

---

## 2. Рефакторинг CSS - создать базовые стили

**Место замены:** Удалить весь блок `.detail-modal` (строки 489-659) и `.edit-modal` (строки 1114-1146), заменить на:

```css
/* ============================================ */
/* БАЗОВЫЕ СТИЛИ ДЛЯ ВСЕХ МОДАЛЬНЫХ ОКОН */
/* ============================================ */

/* Базовый класс для всех модальных окон */
.modal-base {
    display: none;
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    border-radius: 15px;
    max-height: 85vh;
    overflow-y: auto;
    z-index: 2000;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.7);
}

.modal-base.show {
    display: block;
    animation: modalFadeIn 0.3s ease-out;
}

@keyframes modalFadeIn {
    from {
        opacity: 0;
        transform: translate(-50%, -48%);
    }
    to {
        opacity: 1;
        transform: translate(-50%, -50%);
    }
}

/* Overlay (общий для всех модальных окон) */
#modalOverlay {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.7);
    z-index: 1999;
}

#modalOverlay.show {
    display: block;
}

/* Общие стили scrollbar для всех модальных окон */
.modal-base::-webkit-scrollbar {
    width: 6px;
}

.modal-base::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 10px;
}

.modal-base::-webkit-scrollbar-thumb {
    background: #a29bfe;
    border-radius: 10px;
}

.modal-base::-webkit-scrollbar-thumb:hover {
    background: #8b7fe6;
}

/* Общая кнопка закрытия для всех окон */
.modal-close-btn {
    position: absolute;
    top: 12px;
    right: 12px;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.15);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: white;
    cursor: pointer;
    font-size: 18px;
    line-height: 1;
    transition: all 0.2s;
    z-index: 10;
}

.modal-close-btn:hover {
    background: rgba(255, 255, 255, 0.25);
    transform: rotate(90deg);
}

/* ============================================ */
/* СПЕЦИФИЧНЫЕ СТИЛИ ДЛЯ ОКОН ДЕТАЛЬНОЙ ИНФОРМАЦИИ */
/* ============================================ */

.modal-detail {
    background: rgba(0, 0, 0, 0.92);
    color: white;
    padding: 25px 30px;
    max-width: 550px;
    max-height: 80vh;
}

/* Окно философа чуть шире */
#philosopherDetailModal.modal-detail {
    max-width: 650px;
}

.modal-detail h2 {
    margin: 0 0 8px 0;
    color: #a29bfe;
    font-size: 22px;
    font-weight: 600;
}

.modal-detail .philosopher-tag {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 600;
    color: white;
    margin-bottom: 12px;
    opacity: 0.9;
}

.modal-detail .description {
    color: #e0e0e0;
    margin-bottom: 18px;
    line-height: 1.6;
    font-size: 13px;
}

.modal-detail .rubric-section {
    background: rgba(255, 255, 255, 0.08);
    padding: 18px;
    border-radius: 10px;
    border-left: 3px solid #a29bfe;
}

.modal-detail .rubric-title {
    font-size: 15px;
    font-weight: 700;
    color: #a29bfe;
    margin-bottom: 6px;
}

.modal-detail .rubric-description {
    font-size: 12px;
    color: #b0b0b0;
    margin-bottom: 14px;
    font-style: italic;
}

.modal-detail .related-concepts {
    margin-top: 12px;
}

.modal-detail .related-title {
    font-size: 13px;
    font-weight: 700;
    color: #e0e0e0;
    margin-bottom: 8px;
}

.modal-detail .concept-item {
    display: flex;
    align-items: center;
    padding: 7px 10px;
    margin: 4px 0;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-detail .concept-item:hover {
    background: rgba(255, 255, 255, 0.15);
    transform: translateX(5px);
    border-color: rgba(162, 155, 254, 0.4);
}

.modal-detail .concept-color {
    width: 11px;
    height: 11px;
    border-radius: 50%;
    margin-right: 10px;
    flex-shrink: 0;
    box-shadow: 0 0 8px currentColor;
}

.modal-detail .concept-name {
    font-size: 13px;
    color: #e0e0e0;
    flex-grow: 1;
}

.modal-detail .concept-philosopher {
    font-size: 10px;
    color: #a0a0a0;
    font-style: italic;
}

/* ============================================ */
/* СПЕЦИФИЧНЫЕ СТИЛИ ДЛЯ ОКОН РЕДАКТИРОВАНИЯ */
/* ============================================ */

.modal-edit {
    background: rgba(42, 42, 62, 0.98);
    max-width: 600px;
    width: 90%;
    padding: 0;
    z-index: 10001; /* Выше, чем окна детальной информации */
}

/* Header окон редактирования */
.modal-edit-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px 25px;
    border-radius: 15px 15px 0 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: relative;
}

.modal-edit-header h3 {
    margin: 0;
    font-size: 20px;
    font-weight: 600;
}

/* Кнопка закрытия в header'е окна редактирования */
.modal-edit .modal-close-btn {
    position: static;
    background: rgba(255, 255, 255, 0.2);
    width: 35px;
    height: 35px;
    font-size: 24px;
}

.modal-edit .modal-close-btn:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: none; /* Убираем rotation для окон редактирования */
}

/* Body окон редактирования */
.modal-edit-body {
    padding: 25px;
    background: rgba(42, 42, 62, 0.98);
    color: #e0e0e0;
}

/* Формы */
.edit-form-group {
    margin-bottom: 20px;
}

.edit-form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
    color: #a29bfe;
    font-size: 14px;
}

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

.edit-form-group textarea {
    min-height: 80px;
    resize: vertical;
}

.edit-form-group input[type="color"] {
    width: 60px;
    height: 40px;
    background: rgba(255, 255, 255, 0.08);
    border: 2px solid rgba(255, 255, 255, 0.15);
    border-radius: 8px;
    cursor: pointer;
}

.edit-form-group.inline {
    display: flex;
    gap: 15px;
}

.edit-form-group.inline > div {
    flex: 1;
}

.edit-form-checkbox {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 15px;
}

.edit-form-checkbox input[type="checkbox"] {
    width: 20px;
    height: 20px;
    cursor: pointer;
    accent-color: #667eea;
}

.edit-form-checkbox label {
    margin: 0;
    cursor: pointer;
    font-weight: 600;
    color: #e0e0e0;
}

/* Кнопки действий */
.edit-modal-actions {
    display: flex;
    gap: 10px;
    margin-top: 25px;
    padding-top: 20px;
    border-top: 2px solid rgba(255, 255, 255, 0.15);
}

.edit-btn {
    flex: 1;
    padding: 12px 20px;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
}

.edit-btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.edit-btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.edit-btn-secondary {
    background: #95a5a6;
    color: white;
}

.edit-btn-secondary:hover {
    background: #7f8c8d;
}

.edit-btn-danger {
    background: #e74c3c;
    color: white;
}

.edit-btn-danger:hover {
    background: #c0392b;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(231, 76, 60, 0.4);
}

/* Секция списка элементов в модальном окне */
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

.edit-list-item-actions {
    display: flex;
    gap: 8px;
}

.edit-list-btn {
    padding: 6px 12px;
    border: none;
    border-radius: 5px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}

.edit-list-btn-edit {
    background: #3498db;
    color: white;
}

.edit-list-btn-edit:hover {
    background: #2980b9;
}

.edit-list-btn-delete {
    background: #e74c3c;
    color: white;
}

.edit-list-btn-delete:hover {
    background: #c0392b;
}

.edit-list-btn-add {
    width: 100%;
    padding: 10px;
    background: #27ae60;
    color: white;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.3s;
    margin-top: 10px;
}

.edit-list-btn-add:hover {
    background: #229954;
}
```

---

## 3. Обновить остальные CSS селекторы

**Найти и заменить во всем файле:**

| Старый селектор | Новый селектор |
|----------------|----------------|
| `.detail-modal` | `.modal-detail` |
| `.edit-modal` | `.modal-edit` |
| `.close-btn` | `.modal-close-btn` |
| `.edit-modal-header` | `.modal-edit-header` |
| `.edit-modal-close` | `.modal-close-btn` (уже общий класс) |
| `.edit-modal-body` | `.modal-edit-body` |

**Важно:** Убедитесь, что заменяете только в CSS, а не в JavaScript!

---

## 4. Проверка специфичных стилей

После рефакторинга проверьте, что остались следующие специфичные стили:

**Для окон детальной информации (около строк 662-870):**
- Все стили для подсказок рубрик (`.rubric-name-tooltip`)
- Стили для кликабельных философов (`.philosopher-link`)
- Секции взаимодействия (`.interaction-section`)
- Концепции философа (`.concept-details-item`)
- Все они уже правильно именованы и не требуют изменений

**Для окон редактирования (около строк 1422-1558):**
- Стили для поиска концепций (`.concept-search-container`)
- Режим выбора на графе (`.graph-selection-mode`)
- Все они уже правильно именованы и не требуют изменений

---

## 5. Итоговая структура CSS

После рефакторинга CSS будет организован так:

```
1. БАЗОВЫЕ СТИЛИ ДЛЯ ВСЕХ МОДАЛЬНЫХ ОКОН
   - .modal-base (общие свойства)
   - #modalOverlay (общий overlay)
   - .modal-base::-webkit-scrollbar (общий scrollbar)
   - .modal-close-btn (общая кнопка закрытия)

2. СПЕЦИФИЧНЫЕ СТИЛИ ДЛЯ ОКОН ДЕТАЛЬНОЙ ИНФОРМАЦИИ
   - .modal-detail (специфика: фон, размер, padding)
   - .modal-detail h2, .philosopher-tag, .description и т.д.

3. СПЕЦИФИЧНЫЕ СТИЛИ ДЛЯ ОКОН РЕДАКТИРОВАНИЯ
   - .modal-edit (специфика: фон, размер, z-index)
   - .modal-edit-header, .modal-edit-body
   - .edit-form-group, .edit-btn и т.д.

4. ДОПОЛНИТЕЛЬНЫЕ СПЕЦИФИЧНЫЕ СТИЛИ
   - Для философов (подсказки, взаимодействие и т.д.)
   - Для редактирования (поиск концепций, списки и т.д.)
```

---

## Преимущества рефакторинга

✅ **Устранение дублирования** - общие свойства определены один раз  
✅ **Единообразие** - все модальные окна используют общий базовый класс  
✅ **Легкость поддержки** - изменения в базовых стилях применяются ко всем окнам  
✅ **Расширяемость** - легко добавить новый тип модального окна  
✅ **Читаемость** - четкая иерархия стилей  
✅ **Консистентность** - одинаковые эффекты (анимация, scrollbar) для всех окон  

---

## Порядок применения изменений

1. **Обновить HTML окон детальной информации** (строки 1634-1640)
2. **Обновить HTML окон редактирования** (строки ~5200-5366)
3. **Заменить CSS блок** для `.detail-modal` и `.edit-modal` на новый унифицированный
4. **Проверить специфичные стили** - убедиться, что они не затронуты
5. **Тестировать** - открыть все типы модальных окон и проверить работу

---

## Карта изменений классов

### HTML классы
```
Окна детальной информации:
  detail-modal → modal-base modal-detail
  close-btn → modal-close-btn

Окна редактирования:
  edit-modal → modal-base modal-edit
  edit-modal-header → modal-edit-header
  edit-modal-close → modal-close-btn
  edit-modal-body → modal-edit-body
```

### CSS селекторы
```
.detail-modal → .modal-detail
.edit-modal → .modal-edit
.close-btn → .modal-close-btn
.edit-modal-header → .modal-edit-header
.edit-modal-close → .modal-close-btn
.edit-modal-body → .modal-edit-body
```

---

## Примечание

Этот рефакторинг **не требует изменений в JavaScript** - все функции продолжат работать с существующими ID элементов. Меняются только классы для стилизации.
