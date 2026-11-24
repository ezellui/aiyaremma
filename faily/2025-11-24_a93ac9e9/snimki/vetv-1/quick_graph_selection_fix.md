# БЫСТРОЕ ИСПРАВЛЕНИЕ: Выбор концепций на графе

## Проблема:
- Затемнение не убирается при "Указать на графе"
- Окно не возвращается после выбора концепции

## Причина:
Используется `style.opacity = '0.3'` вместо полного скрытия окна и overlay

---

## Исправление 1: selectConceptOnGraph (строка 4474)

**ЗАМЕНИТЬ ВСЮ ФУНКЦИЮ:**

```javascript
function selectConceptOnGraph(target) {
    editMode.graphSelectionMode = true;
    editMode.graphSelectionTarget = target;
    
    const modeIndicator = document.getElementById('graphSelectionMode');
    const title = document.getElementById('selectionModeTitle');
    const desc = document.getElementById('selectionModeDesc');
    const modal = document.getElementById('editConnectionModal');
    const overlay = document.getElementById('modalOverlay');
    
    title.textContent = target === 'source' ? 
        'Выберите начальную концепцию' : 
        'Выберите конечную концепцию';
    desc.textContent = 'Кликните на концепцию в графе';
    
    modeIndicator.style.display = 'block';
    
    // Скрываем окно, overlay и убираем затемнение
    modal.style.display = 'none';
    overlay.classList.remove('show');
    resetHighlight();
}
```

---

## Исправление 2: cancelGraphSelection (строка 4493)

**ЗАМЕНИТЬ ВСЮ ФУНКЦИЮ:**

```javascript
function cancelGraphSelection() {
    editMode.graphSelectionMode = false;
    editMode.graphSelectionTarget = null;
    
    const modal = document.getElementById('editConnectionModal');
    const overlay = document.getElementById('modalOverlay');
    
    document.getElementById('graphSelectionMode').style.display = 'none';
    
    // Возвращаем окно и overlay
    modal.style.display = 'block';
    overlay.classList.add('show');
}
```

---

## ✅ Результат после исправлений:

1. ✅ Нажатие "Указать на графе" → окно исчезает, граф доступен, затемнение снято
2. ✅ Клик на концепцию → окно возвращается, поле заполнено
3. ✅ Нажатие "Отмена" → окно возвращается

---

## 📝 Что изменилось:

**Было:**
```javascript
document.getElementById('editConnectionModal').style.opacity = '0.3';  // ❌
```

**Стало:**
```javascript
modal.style.display = 'none';           // ✅ Полностью скрываем
overlay.classList.remove('show');        // ✅ Убираем серый фон
resetHighlight();                        // ✅ Убираем затемнение графа
```

---

## 🎯 Два вида затемнения:

1. **Overlay** - серый фон модального окна (`#modalOverlay`)
2. **Затемнение графа** - полупрозрачные узлы/связи (классы `.dimmed`)

Нужно убирать ОБА!
