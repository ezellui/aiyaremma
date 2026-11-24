# БЫСТРОЕ ИСПРАВЛЕНИЕ: Логика кнопок визуализации

## 🎯 Главная проблема

Функция `updateVisualizationControlSection()` **не вызывается** при включении визуализации, только при сбросе.

## ⚡ 3 БЫСТРЫХ ИСПРАВЛЕНИЯ

### 1️⃣ В конце visualizeMetricBySize() (строка ~5016)

**ДОБАВИТЬ одну строку:**

```javascript
isVisualizingBySize = true;
currentVisualizedMetric = metricName;

updateVisualizationButtonText(metricName);
updateVisualizationControlSection(); // ← ДОБАВИТЬ ЭТУ СТРОКУ

console.log(`✅ Визуализация метрики "${metricName}" активирована`);
```

### 2️⃣ В конце resetNodeSizes() (строка ~5054)

**ДОБАВИТЬ одну строку:**

```javascript
if (metricToUpdate) {
    updateVisualizationButtonText(metricToUpdate);
}

updateVisualizationControlSection(); // ← ДОБАВИТЬ ЭТУ СТРОКУ

console.log('✅ Оригинальные размеры узлов восстановлены');
```

### 3️⃣ Расширить словарь метрик в updateVisualizationControlSection()

**ЗАМЕНИТЬ** короткий словарь на ПОЛНЫЙ (см. полный документ).

---

## ✅ Проверка

После исправлений:

1. **Включаем визуализацию** → Кнопка в легенде ПОЯВЛЯЕТСЯ с названием
2. **Сбрасываем** → Кнопка ИСЧЕЗАЕТ
3. **Консоль** показывает логи: "✅ Секция легенды показана" и "🔽 Секция легенды скрыта"

---

## 🚀 Время: 2 минуты

Просто добавьте 2 строчки вызова `updateVisualizationControlSection()` и расширьте словарь!

Полная информация в файле **visualization-logic-fix.md**.
