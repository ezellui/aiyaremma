# БЫСТРО: Добавить кнопку переворота связи

## Шаг 1: Добавить кнопку в HTML

**После строки 4767** (после кнопки "Указать на графе" для начальной концепции):

```html
            </div>
            
            <!-- Кнопка переворота связи -->
            <div style="text-align: center; margin: 15px 0;">
                <button type="button" class="edit-btn edit-btn-secondary" onclick="swapConnectionConcepts()" style="padding: 8px 20px;">
                    <span style="font-size: 18px; margin-right: 5px;">⇅</span>
                    Поменять местами
                </button>
            </div>
            
            <!-- Выбор конечной концепции -->
```

---

## Шаг 2: Добавить функцию

**После функции selectConnectionConcept** добавить:

```javascript
// Переворот связи (обмен source и target)
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
}
```

---

## ✅ Готово!

Теперь в окне редактирования связи между полями выбора концепций появится кнопка "⇅ Поменять местами", которая меняет местами начальную и конечную концепции.

---

## 🎨 Альтернативные варианты кнопки

### Компактная круглая:
```html
<div style="text-align: center; margin: 10px 0;">
    <button type="button" class="edit-btn edit-btn-secondary" onclick="swapConnectionConcepts()" 
            style="width: 40px; height: 40px; border-radius: 50%; padding: 0; font-size: 20px;" 
            title="Поменять местами">
        ⇅
    </button>
</div>
```

### Как ссылка:
```html
<div style="text-align: center; margin: 10px 0;">
    <a href="javascript:void(0)" onclick="swapConnectionConcepts()" 
       style="color: #6c5ce7; text-decoration: none; cursor: pointer;">
        <span style="font-size: 16px;">⇅</span> Поменять местами
    </a>
</div>
```

Выберите тот вариант, который больше нравится!
