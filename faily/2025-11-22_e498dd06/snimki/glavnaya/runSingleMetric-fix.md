# КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Ошибка в функции runSingleMetric

## ❌ Проблема

При попытке рассчитать любые метрики (PageRank, Betweenness, Closeness, Eigenvector, Weighted Clustering, Local Cohesion, Rich-Club) возникает ошибка:

```
TypeError: document.getElementById(...) is null
```

**Место ошибки:** функция `runSingleMetric()` в строке 5141-5143

## 🔍 Причина

Функция `runSingleMetric()` пытается получить доступ к элементам, которые **не существуют** в HTML:
- `generalStatsSection`
- `metricsSection`
- `visualizationSection`

Это устаревший код из другой версии реализации, который не был удален.

Также функция пытается вызвать **несуществующую** функцию `switchMetric()` (строка 5148).

---

## ✅ РЕШЕНИЕ: Полная замена функции runSingleMetric

### Найти функцию (строка ~5089)

Найдите в файле функцию `async function runSingleMetric(metricName)` (примерно строка 5089-5156)

### Заменить ПОЛНОСТЬЮ на исправленную версию:

```javascript
// Расчёт одной метрики
async function runSingleMetric(metricName) {
    try {
        showProgress(`Расчёт ${metricName}...`, 0);
        
        switch(metricName) {
            case 'pagerank':
                await calculatePageRank(20, 0.85, (current, total) => {
                    const percent = Math.round((current / total) * 100);
                    showProgress('Расчёт PageRank...', percent);
                });
                break;
                
            case 'betweenness':
                await calculateBetweennessAsync((current, total) => {
                    const percent = Math.round((current / total) * 100);
                    showProgress('Расчёт Betweenness...', percent);
                });
                break;
                
            case 'closeness':
                await calculateClosenessCentrality((current, total) => {
                    const percent = Math.round((current / total) * 100);
                    showProgress('Расчёт Closeness...', percent);
                });
                break;
                
            case 'eigenvector':
                await calculateEigenvectorCentrality(100, (current, total) => {
                    const percent = Math.round((current / total) * 100);
                    showProgress('Расчёт Eigenvector...', percent);
                });
                break;
            
            // ========== НОВЫЕ МЕТРИКИ ==========
            
            case 'weighted-clustering':
                showProgress('Расчёт Weighted Clustering...', 50);
                await new Promise(resolve => setTimeout(resolve, 100));
                calculateWeightedClustering();
                showProgress('Расчёт Weighted Clustering...', 100);
                break;
            
            case 'local-cohesion':
                showProgress('Расчёт Local Cohesion...', 50);
                await new Promise(resolve => setTimeout(resolve, 100));
                calculateLocalCohesion();
                showProgress('Расчёт Local Cohesion...', 100);
                break;
            
            case 'rich-club':
                showProgress('Расчёт Rich-Club...', 50);
                await new Promise(resolve => setTimeout(resolve, 100));
                calculateRichClubCoefficient();
                showProgress('Расчёт Rich-Club...', 100);
                break;
                
            default:
                console.warn(`⚠️ Неизвестная метрика: ${metricName}`);
                break;
        }
        
        // УБРАНЫ строки с несуществующими элементами:
        // document.getElementById('generalStatsSection').style.display = 'block';
        // document.getElementById('metricsSection').style.display = 'block';
        // document.getElementById('visualizationSection').style.display = 'block';
        
        showProgress('Готово!', 100);
        setTimeout(() => {
            hideProgress();
            console.log(`✅ Метрика ${metricName} успешно рассчитана`);
        }, 500);
        
    } catch (error) {
        console.error('❌ Ошибка при расчёте метрики:', error);
        hideProgress();
        alert('Произошла ошибка при расчёте: ' + error.message);
    }
}
```

---

## 📝 Что было исправлено

### ❌ Удалено (строки 5141-5143):
```javascript
document.getElementById('generalStatsSection').style.display = 'block';
document.getElementById('metricsSection').style.display = 'block';
document.getElementById('visualizationSection').style.display = 'block';
```
**Причина:** Эти элементы не существуют в HTML и вызывают ошибку.

### ❌ Удалено (строка 5148):
```javascript
switchMetric(metricName);
```
**Причина:** Функция `switchMetric()` не существует.

### ✅ Добавлено:
```javascript
default:
    console.warn(`⚠️ Неизвестная метрика: ${metricName}`);
    break;
```
**Причина:** Обработка неизвестных метрик для отладки.

### ✅ Улучшено:
Добавлены обновления прогресса для новых метрик (weighted-clustering, local-cohesion, rich-club).

### ✅ Улучшено:
Добавлен вывод сообщения об ошибке с деталями:
```javascript
alert('Произошла ошибка при расчёте: ' + error.message);
```

---

## 🔧 Дополнительное исправление: функция calculateMetricFromModal

Функция `calculateMetricFromModal` вызывает `runSingleMetric` и работает некорректно - она закрывает модальное окно, что усложняет отладку.

### Найти функцию (строка ~3747)

Найдите функцию `async function calculateMetricFromModal(metricKey)`

### Опциональное улучшение (рекомендуется):

```javascript
// Расчёт метрики из модального окна
async function calculateMetricFromModal(metricKey) {
    try {
        // НЕ закрываем модальное окно - пользователь видит прогресс
        // closeStatsModal(); // ЗАКОММЕНТИРОВАНО
        
        // Используем существующие функции расчёта
        await runSingleMetric(metricKey);
        
        // После расчёта - переключаемся на вкладку с этой метрикой
        setTimeout(() => {
            // Если окно было закрыто - открываем
            if (!isStatsModalOpen) {
                openStatsModal();
            }
            
            // Переключаемся на нужную метрику
            switchStatsView(metricKey);
            updateActiveNavItem(metricKey);
        }, 600);
        
    } catch (error) {
        console.error('❌ Ошибка при расчёте метрики:', error);
        alert('Произошла ошибка при расчёте метрики: ' + error.message);
        
        // Если окно было закрыто - открываем обратно
        if (!isStatsModalOpen) {
            openStatsModal();
        }
    }
}
```

**Преимущества этого варианта:**
- Пользователь видит индикатор прогресса в реальном времени
- Не нужно искать кнопку метрики по onclick-атрибуту
- Проще отлаживать ошибки
- Более плавная работа интерфейса

---

## ✅ Проверка после исправления

После применения исправлений проверьте:

### Базовые метрики
- [ ] **PageRank** - рассчитывается без ошибок, показывает прогресс
- [ ] **Betweenness** - рассчитывается без ошибок, показывает прогресс
- [ ] **Closeness** - рассчитывается без ошибок, показывает прогресс
- [ ] **Eigenvector** - рассчитывается без ошибок, показывает прогресс

### Новые метрики
- [ ] **Weighted Clustering** - рассчитывается без ошибок
- [ ] **Local Cohesion** - рассчитывается без ошибок
- [ ] **Rich-Club** - рассчитывается без ошибок

### Интерфейс
- [ ] Индикатор прогресса показывается
- [ ] Индикатор прогресса обновляется (0% → 50% → 100%)
- [ ] Индикатор прогресса исчезает после завершения
- [ ] Нет ошибок в консоли браузера
- [ ] После расчёта отображаются результаты

### Консоль браузера
- [ ] Сообщение `✅ Метрика [название] успешно рассчитана`
- [ ] НЕТ ошибок `TypeError: document.getElementById(...) is null`
- [ ] НЕТ ошибок `switchMetric is not defined`

---

## 🎯 Сводка изменений

| Что | Было | Стало | Причина |
|-----|------|-------|---------|
| Строки 5141-5143 | Обращение к несуществующим элементам | Удалены | Элементы не существуют в HTML |
| Строка 5148 | Вызов `switchMetric()` | Удалена | Функция не существует |
| Обработка ошибок | Простое сообщение | С деталями ошибки | Лучшая отладка |
| Новые метрики | Без обновления прогресса | С обновлением прогресса | Визуальная обратная связь |
| Default case | Отсутствует | Добавлен | Обработка неизвестных метрик |

---

## 📋 Порядок применения исправлений

### Обязательное исправление:
1. ✅ Заменить функцию `runSingleMetric()` (строки ~5089-5156)

### Рекомендуемое улучшение:
2. ⚠️ Улучшить функцию `calculateMetricFromModal()` (строки ~3747-3770)

---

## 🚨 Важно

Это исправление нужно применить **ПОСЛЕ** исправления HTML из файла `html-fixes.md`.

**Правильный порядок:**
1. ✅ `html-fixes.md` - исправление HTML-разметки
2. ✅ `runSingleMetric-fix.md` - исправление функции расчёта (этот файл)
3. ✅ `corrections.md` - остальные исправления JavaScript

---

## 💡 Почему возникла эта ошибка

Эта ошибка возникла из-за того, что:

1. **Копирование кода из другого проекта** - элементы `generalStatsSection`, `metricsSection`, `visualizationSection` были частью другой HTML-структуры
2. **Неполная адаптация кода** - при переносе кода не были удалены ссылки на старые элементы
3. **Отсутствие проверки** - код не проверял существование элементов перед обращением к ним

**Вывод:** При интеграции кода из разных источников важно проверять, что все используемые элементы действительно существуют в HTML.

---

## ✨ Результат

После применения этого исправления:
- ✅ Все метрики будут рассчитываться без ошибок
- ✅ Индикатор прогресса будет работать корректно
- ✅ Пользователь увидит результаты расчётов
- ✅ Не будет ошибок в консоли браузера
- ✅ Улучшенная обработка ошибок для отладки

---

## 🔗 Связанные исправления

- `html-fixes.md` - исправление отсутствующей HTML-разметки (применить первым)
- `corrections.md` - другие исправления JavaScript (применить после этого файла)

Удачи! 🚀
