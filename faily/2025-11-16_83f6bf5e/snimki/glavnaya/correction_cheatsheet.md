# БЫСТРАЯ ШПАРГАЛКА: Корректировки базы данных

## ⚡ Краткое резюме

- ❌ **Удалить:** 14 связей (экзистенциалистский перекос)
- ➕ **Добавить:** 23 связи (аналитика + метафизика)
- 🔄 **Изменить веса:** ~12 связей
- ✅ **Итого:** 1149 → ~1158 связей

---

## 1️⃣ ЧТО УДАЛИТЬ (14 связей)

### Августин → Кьеркегор (убрать 3 из 6)
```javascript
// УДАЛИТЬ:
{ source: "two_cities", target: "stages_existence", type: "influence", weight: 1 },
{ source: "original_sin", target: "anxiety", type: "influence", weight: 2 },
{ source: "confession", target: "subjective_truth", type: "develop", weight: 2 },
```

### Кьеркегор → Хайдеггер (убрать 2 из 5)
```javascript
// УДАЛИТЬ:
{ source: "leap_faith", target: "ereignis", type: "influence", weight: 1 },
{ source: "despair", target: "sorge", type: "influence", weight: 2 },
```

### Ницше → Хайдеггер (убрать 2 из 4)
```javascript
// УДАЛИТЬ:
{ source: "perspectivism", target: "dasein", type: "influence", weight: 2 },
{ source: "god_dead", target: "aletheia", type: "influence", weight: 2 },
```

### Фихте ← Кьеркегор (убрать все 3)
```javascript
// УДАЛИТЬ:
{ source: "individual", target: "absolute_ego", type: "critique", weight: 3 },
{ source: "subjective_truth", target: "wissenschaftslehre", type: "critique", weight: 2 },
{ source: "anxiety", target: "absolute_ego", type: "critique", weight: 2 },
```

### Остальное (4 связи)
```javascript
// УДАЛИТЬ:
{ source: "nothingness", target: "body_without_organs", type: "influence", weight: 1 },
{ source: "bad_faith", target: "discipline", type: "dialogue", weight: 1, bidirectional: true },
{ source: "multiplicity", target: "ideas", type: "critique", weight: 2 },
{ source: "leap_faith", target: "intellectual_intuition", type: "critique", weight: 2 },
{ source: "denial_will", target: "absolute_idea", type: "oppose", weight: 2 },
```

---

## 2️⃣ ЧТО ДОБАВИТЬ (23 связи)

### Блок A: Аналитическая философия (11 связей)

```javascript
// ФРЕГЕ → ВИТГЕНШТЕЙН
{ source: "sense_reference", target: "picture_theory", type: "develop", weight: 3 },
{ source: "sense_reference", target: "language_game", type: "influence", weight: 2 },
{ source: "concept_script", target: "logical_atomism", type: "influence", weight: 2 },

// ФРЕГЕ → ГУССЕРЛЬ
{ source: "concept_script", target: "phenomenology", type: "influence", weight: 1 },
{ source: "sense_reference", target: "intentionality", type: "dialogue", weight: 1 },

// РАССЕЛ → ВИТГЕНШТЕЙН И ФЕНОМЕНОЛОГИЯ
{ source: "theory_descriptions", target: "language_game", type: "influence", weight: 2 },
{ source: "logical_atomism", target: "family_resemblance", type: "dialogue", weight: 2 },
{ source: "logical_atomism", target: "constitution", type: "influence", weight: 1 },
{ source: "theory_descriptions", target: "intentionality", type: "dialogue", weight: 1 },

// ВИТГЕНШТЕЙН → СОВРЕМЕННОСТЬ
{ source: "language_game", target: "lifeworld", type: "influence", weight: 2 },
{ source: "language_game", target: "hermeneutic_circle", type: "influence", weight: 2 },
{ source: "showing_saying", target: "aletheia", type: "dialogue", weight: 2 },
{ source: "language_game", target: "dialectic", type: "dialogue", weight: 1 },
```

### Блок B: Классическая метафизика (7 связей)

```javascript
// АРИСТОТЕЛЬ → ФОМА
{ source: "four_causes", target: "essence_existence", type: "develop", weight: 3 },
{ source: "form", target: "analogy_being", type: "develop", weight: 2 },
{ source: "entelechy", target: "five_ways", type: "influence", weight: 2 },

// АРИСТОТЕЛЬ → СПИНОЗА
{ source: "entelechy", target: "attributes", type: "influence", weight: 2 },

// ФОМА → ДЕКАРТ
{ source: "essence_existence", target: "infinite_idea", type: "influence", weight: 2 },
{ source: "five_ways", target: "ontological_proof", type: "develop", weight: 2 },

// ФОМА → ЛЕЙБНИЦ
{ source: "essence_existence", target: "sufficient_reason", type: "influence", weight: 2 },
```

### Блок C: Герменевтика (3 связи)

```javascript
// ГАДАМЕР ↔ ВИТГЕНШТЕЙН
{ source: "horizon_understanding", target: "language_game", type: "dialogue", weight: 2, bidirectional: true },
{ source: "tradition_gadamer", target: "showing_saying", type: "influence", weight: 1 },

// ДИЛЬТЕЙ → ВИТГЕНШТЕЙН
{ source: "verstehen", target: "language_game", type: "influence", weight: 2 },
```

---

## 3️⃣ КАКИЕ ВЕСА ИЗМЕНИТЬ (12 связей)

### Увеличить (усилить влияние)

```javascript
// НАЙТИ И ИЗМЕНИТЬ:
// Витгенштейн
language_game → rhizome: weight: 2 → 3
family_resemblance → multiplicity: weight: 2 → 3

// Аристотель (найти подходящие связи между ключевыми концепциями)
four_causes → act_potency: weight: 2 → 3 (если есть)
four_causes → form: weight: 2 → 3 (если есть)
act_potency → entelechy: weight: 2 → 3 (если есть)

// Гегель
absolute_idea → objective_spirit: weight: 2 → 3 (если есть)
dialectic → absolute_idea: weight: 2 → 3 (если есть)
```

### Уменьшить (ослабить перекосы)

```javascript
// НАЙТИ И ИЗМЕНИТЬ:
// Шопенгауэр → Гегель
will_schop → absolute_idea: weight: 3 → 2
suffering → dialectic: weight: 2 → 1

// Сартр
freedom_sartre → deterritorialization: weight: 2 → 1

// Проверить другие экзистенциалистские связи с weight: 3
// и снизить до 2, где уместно
```

---

## 📊 Ожидаемые результаты

### Метрики
- Количество связей: 1149 → ~1158
- Диаметр: ~29-30 (стабильно)
- Средний путь: ~10.0-10.2 (+0.1-0.3)

### PageRank топ-10
✅ **Витгенштейн** вернётся в топ-5 (было 4 место в старой базе)
✅ **Гадамер** вернётся в топ-10
✅ **Гуссерль** вернётся в топ-10
⬇️ **Сартр** выпадет из топа

### Eigenvector топ-10
✅ **Аристотель** (Четыре причины) вернётся в топ-2-5
✅ Классическая метафизика восстановлена

### Betweenness топ-10
✅ **Абсолютная идея (Гегель)** вернётся в топ-6-7
✅ **Диалектика (Гегель)** вернётся в топ-10

### Баланс направлений XX века
| Направление | До | После |
|-------------|-----|-------|
| Экзистенциализм | 19.6% | 11.2% ⬇️ |
| Аналитическая философия | 2.8% | 9.0% ⬆️ |
| Классическая метафизика | 5.6% | 9.6% ⬆️ |

---

## ✅ Чек-лист применения

- [ ] Сделать резервную копию: `cp new_base.js new_base_backup.js`
- [ ] Удалить 14 связей из раздела 1️⃣
- [ ] Добавить 23 связи из раздела 2️⃣ (блоки A, B, C)
- [ ] Изменить ~12 весов из раздела 3️⃣
- [ ] Проверить синтаксис JavaScript (запятые, кавычки)
- [ ] Запустить подсчёт метрик
- [ ] Проверить результаты против прогноза

---

## 🎯 Финальная оценка

**До корректировок:** 6.5/10
**После корректировок:** 8.0/10

**Улучшения:**
- ✅ Философская адекватность: 6.0 → 7.5-8.0
- ✅ Баланс эпох: 5.5 → 8.0
- ✅ Структурная связность: 9.0 → 8.5-9.0 (допустимое снижение)

---

## 📁 Полные файлы

1. **database_corrections.js** - Полный код всех корректировок
2. **corrections_report.md** - Детальный отчёт с обоснованиями
3. **correction_cheatsheet.md** - Эта быстрая шпаргалка

---

**Важно:** Эти корректировки сохраняют технические преимущества новой базы (высокую связность, малый диаметр), устраняя философские искажения и восстанавливая исторически правильный баланс.
