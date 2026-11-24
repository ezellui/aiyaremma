# БЫСТРО: Темная тема для окон редактирования

## Готовый CSS для замены

Найдите блок стилей модальных окон редактирования (примерно строки 1044-1402) и замените соответствующие части на этот код:

```css
/* ============================================ */
/* МОДАЛЬНЫЕ ОКНА РЕДАКТИРОВАНИЯ - ТЕМНАЯ ТЕМА */
/* ============================================ */

.edit-modal {
    display: none;
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: rgba(42, 42, 62, 0.98);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 15px;
    box-shadow: 0 10px 50px rgba(0, 0, 0, 0.5);
    z-index: 10001;
    max-width: 600px;
    width: 90%;
    max-height: 85vh;
    overflow-y: auto;
    padding: 0;
}

.edit-modal.show {
    display: block;
    animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
    from {
        opacity: 0;
        transform: translate(-50%, -48%);
    }
    to {
        opacity: 1;
        transform: translate(-50%, -50%);
    }
}

.edit-modal-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px 25px;
    border-radius: 15px 15px 0 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.edit-modal-header h3 {
    margin: 0;
    font-size: 20px;
    font-weight: 600;
}

.edit-modal-close {
    background: rgba(255, 255, 255, 0.2);
    border: none;
    color: white;
    font-size: 24px;
    cursor: pointer;
    width: 35px;
    height: 35px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.3s;
}

.edit-modal-close:hover {
    background: rgba(255, 255, 255, 0.3);
}

.edit-modal-body {
    padding: 25px;
    background: rgba(42, 42, 62, 0.98);
    color: #e0e0e0;
}

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

/* Поиск концепций */
.concept-search-container {
    position: relative;
    margin-bottom: 15px;
}

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

## ✅ Готово!

После замены все модальные окна редактирования (философов, концепций, связей) будут в единой темной теме с окном детальной информации.

**Цветовая схема:**
- 🌑 Фон: темно-фиолетовый полупрозрачный
- 💜 Акценты: светло-фиолетовый (#a29bfe)
- 📝 Текст: светло-серый (#e0e0e0)
- 🎨 Градиентные кнопки с ховер-эффектами
