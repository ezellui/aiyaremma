# Добавление кнопки переворота связи

## Шаг 1: Добавить кнопку в HTML

### Найти строку 4768 (между двумя секциями выбора концепций)

**После строки 4767** (после кнопки "Указать на графе" для начальной концепции) добавить:

```html
            </div>
            
            <!-- Кнопка для переворота связи -->
            <div style="text-align: center; margin: 15px 0;">
                <button type="button" class="edit-btn edit-btn-secondary" onclick="swapConnectionConcepts()" style="padding: 8px 20px;">
                    <span style="font-size: 18px; margin-right: 5px;">⇅</span>
                    Поменять местами
                </button>
            </div>
            
            <!-- Выбор конечной концепции -->
```

**Полный фрагмент для замены (строки 4767-4770):**

```html
                <button class="edit-btn edit-btn-secondary" onclick="selectConceptOnGraph('source')" style="margin-top: 10px; width: 100%;">
                    Указать на графе
                </button>
            </div>
            
            <!-- Кнопка для переворота связи -->
            <div style="text-align: center; margin: 15px 0;">
                <button type="button" class="edit-btn edit-btn-secondary" onclick="swapConnectionConcepts()" style="padding: 8px 20px;">
                    <span style="font-size: 18px; margin-right: 5px;">⇅</span>
                    Поменять местами
                </button>
            </div>
            
            <!-- Выбор конечной концепции -->
            <div class="edit-form-group">
```

---

## Шаг 2: Добавить функцию переворота

### Добавить после функции selectConnectionConcept (примерно после строки с этой функцией):

```javascript
// Функция переворота связи (обмен source и target)
function swapConnectionConcepts() {
    const sourceInput = document.getElementById('connectionSourceSearch');
    const targetInput = document.getElementById('connectionTargetSearch');
    
    // Меняем значения полей
    const tempValue = sourceInput.value;
    sourceInput.value = targetInput.value;
    targetInput.value = tempValue;
    
    // Меняем ID концепций
    const tempId = editMode.connectionSourceId;
    editMode.connectionSourceId = editMode.connectionTargetId;
    editMode.connectionTargetId = tempId;
    
    // Визуальная обратная связь (анимация)
    const button = event.target.closest('button');
    if (button) {
        const icon = button.querySelector('span');
        if (icon) {
            icon.style.transform = 'rotate(180deg)';
            icon.style.transition = 'transform 0.3s ease';
            setTimeout(() => {
                icon.style.transform = 'rotate(0deg)';
            }, 300);
        }
    }
    
    console.log('Связь перевернута:', {
        source: editMode.connectionSourceId,
        target: editMode.connectionTargetId
    });
}
```

---

## Альтернативные варианты дизайна кнопки

### Вариант 1: Компактная круглая кнопка

```html
<div style="text-align: center; margin: 10px 0;">
    <button type="button" class="edit-btn edit-btn-secondary" onclick="swapConnectionConcepts()" 
            style="width: 40px; height: 40px; border-radius: 50%; padding: 0; font-size: 20px;" 
            title="Поменять местами начальную и конечную концепции">
        ⇅
    </button>
</div>
```

### Вариант 2: С иконкой стрелок

```html
<div style="text-align: center; margin: 15px 0;">
    <button type="button" class="edit-btn edit-btn-secondary" onclick="swapConnectionConcepts()" 
            style="padding: 10px 25px;" title="Изменить направление связи">
        <span style="font-size: 16px;">↓ ↑</span> Перевернуть связь
    </button>
</div>
```

### Вариант 3: Минималистичная ссылка

```html
<div style="text-align: center; margin: 10px 0;">
    <a href="javascript:void(0)" onclick="swapConnectionConcepts()" 
       style="color: #6c5ce7; text-decoration: none; font-size: 13px; cursor: pointer;">
        <span style="font-size: 16px; margin-right: 3px;">⇅</span>
        Поменять местами
    </a>
</div>
```

### Вариант 4: Между полями (inline)

Вместо отдельного блока, можно добавить справа от лейбла:

```html
<!-- Выбор начальной концепции -->
<div class="edit-form-group">
    <label style="display: flex; justify-content: space-between; align-items: center;">
        <span>Начальная концепция *</span>
        <button type="button" class="edit-btn edit-btn-secondary" onclick="swapConnectionConcepts()" 
                style="padding: 4px 10px; font-size: 12px; margin-left: 10px;">
            ⇅ Поменять
        </button>
    </label>
    <div class="concept-search-container">
        <!-- ... -->
    </div>
</div>
```

---

## Расширенная версия функции с проверками

Если хотите добавить проверки и уведомления:

```javascript
function swapConnectionConcepts() {
    const sourceInput = document.getElementById('connectionSourceSearch');
    const targetInput = document.getElementById('connectionTargetSearch');
    
    // Проверяем, заполнены ли оба поля
    if (!editMode.connectionSourceId || !editMode.connectionTargetId) {
        alert('Сначала выберите обе концепции');
        return;
    }
    
    // Проверяем, не одинаковые ли концепции
    if (editMode.connectionSourceId === editMode.connectionTargetId) {
        alert('Начальная и конечная концепции одинаковы');
        return;
    }
    
    // Меняем значения полей
    const tempValue = sourceInput.value;
    sourceInput.value = targetInput.value;
    targetInput.value = tempValue;
    
    // Меняем ID концепций
    const tempId = editMode.connectionSourceId;
    editMode.connectionSourceId = editMode.connectionTargetId;
    editMode.connectionTargetId = tempId;
    
    // Визуальная обратная связь
    const button = event.target.closest('button');
    if (button) {
        const originalText = button.innerHTML;
        button.innerHTML = '<span style="font-size: 18px;">✓</span> Перевернуто';
        button.disabled = true;
        button.style.background = '#27ae60';
        button.style.color = 'white';
        
        setTimeout(() => {
            button.innerHTML = originalText;
            button.disabled = false;
            button.style.background = '';
            button.style.color = '';
        }, 1000);
    }
    
    console.log('Связь перевернута:', {
        source: editMode.connectionSourceId,
        target: editMode.connectionTargetId
    });
}
```

---

## Рекомендация

**Используйте основное решение** (Вариант с кнопкой "⇅ Поменять местами"):
- Хорошо заметна
- Понятная
- Занимает отдельное пространство между полями
- Не перегружает интерфейс

Если хотите более компактное решение - используйте **Вариант 1** (круглая кнопка).

---

## Проверка после добавления

1. Откройте окно редактирования связи
2. Выберите начальную концепцию (например, "Категорический императив")
3. Выберите конечную концепцию (например, "Вещь в себе")
4. Нажмите кнопку "⇅ Поменять местами"
5. Проверьте, что значения в полях поменялись местами
6. Сохраните связь и убедитесь, что направление корректное

---

## Дополнительно: Учет двунаправленных связей

Если связь двунаправленная (`bidirectional = true`), можно показать предупреждение:

```javascript
function swapConnectionConcepts() {
    // ... код выше ...
    
    // Проверяем двунаправленность
    const bidirectionalCheckbox = document.getElementById('connectionBidirectional');
    if (bidirectionalCheckbox && bidirectionalCheckbox.checked) {
        if (!confirm('Связь двунаправленная. Направление не имеет значения. Всё равно поменять местами?')) {
            return;
        }
    }
    
    // ... остальной код ...
}
```

---

## Итого: Минимальные изменения

### 1. Добавить HTML кнопку (после строки 4767):
```html
<div style="text-align: center; margin: 15px 0;">
    <button type="button" class="edit-btn edit-btn-secondary" onclick="swapConnectionConcepts()" style="padding: 8px 20px;">
        <span style="font-size: 18px; margin-right: 5px;">⇅</span>
        Поменять местами
    </button>
</div>
```

### 2. Добавить JavaScript функцию (после selectConnectionConcept):
```javascript
function swapConnectionConcepts() {
    const sourceInput = document.getElementById('connectionSourceSearch');
    const targetInput = document.getElementById('connectionTargetSearch');
    
    const tempValue = sourceInput.value;
    sourceInput.value = targetInput.value;
    targetInput.value = tempValue;
    
    const tempId = editMode.connectionSourceId;
    editMode.connectionSourceId = editMode.connectionTargetId;
    editMode.connectionTargetId = tempId;
}
```

Готово! 🎉
