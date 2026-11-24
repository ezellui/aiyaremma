# БЫСТРОЕ ИСПРАВЛЕНИЕ: Окно не закрывается

## Проблема
`modal.style.display = 'block'` создает inline стиль, который **блокирует** работу `modal.classList.remove('show')`

## ✅ РЕШЕНИЕ (выберите одно)

### Вариант 1 (РЕКОМЕНДУЕТСЯ): Использовать z-index

Заменить в **selectConceptOnGraph** (строка ~4474):
```javascript
// ❌ Удалить эту строку:
modal.style.display = 'none';

// ✅ Добавить эти строки:
modal.style.zIndex = '1';
modal.style.opacity = '0.3';
```

Заменить в **cancelGraphSelection** (строка ~4493):
```javascript
// ❌ Удалить эту строку:
modal.style.display = 'block';

// ✅ Добавить эти строки:
modal.style.zIndex = '';
modal.style.opacity = '';
```

---

### Вариант 2 (ПРОЩЕ): Очистить inline стили при закрытии

Добавить в **closeEditConnectionModal** (строка 4437, после `modal.classList.remove('show')`):

```javascript
function closeEditConnectionModal() {
    const modal = document.getElementById('editConnectionModal');
    const overlay = document.getElementById('modalOverlay');
    
    modal.classList.remove('show');
    modal.style.display = '';      // ✅ ДОБАВИТЬ
    modal.style.zIndex = '';       // ✅ ДОБАВИТЬ
    modal.style.opacity = '';      // ✅ ДОБАВИТЬ
    overlay.classList.remove('show');
    
    // ... остальной код без изменений
}
```

---

## Какой вариант выбрать?

- **Вариант 1**: Чище, модальное окно видно полупрозрачным
- **Вариант 2**: Проще, всего 3 строки добавить

Оба работают одинаково хорошо!

---

## Проверка

После исправления:
1. Откройте окно редактирования связи
2. Нажмите "Указать на графе"
3. Выберите концепцию
4. Нажмите кнопку "×" → должно закрыться ✅
5. Откройте снова и нажмите ESC → должно закрыться ✅
