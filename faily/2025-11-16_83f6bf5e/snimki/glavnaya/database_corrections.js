// ============================================================================
// КОРРЕКТИРОВКИ ДЛЯ НОВОЙ БАЗЫ ФИЛОСОФСКИХ КОНЦЕПЦИЙ
// ============================================================================
// 
// Цель: Сохранить структурные преимущества (диаметр 29, средний путь 9.90)
//       при устранении философских искажений
//
// Итоговый баланс:
//   - Удалить: 14 связей (избыточные экзистенциалистские)
//   - Добавить: 23 связи (аналитическая философия + классическая метафизика)
//   - Изменить веса: ~12 связей
//   - Итого: ~1158 связей (было 1149)
//
// ============================================================================

// ============================================================================
// РАЗДЕЛ 1: СВЯЗИ, КОТОРЫЕ НУЖНО УДАЛИТЬ
// ============================================================================

// ----------------------------------------------------------------------------
// 1.1. Избыточная детализация: Августин → Кьеркегор (удалить 3 из 6)
// ----------------------------------------------------------------------------
// УДАЛИТЬ:
    { source: "two_cities", target: "stages_existence", type: "influence", weight: 1 },
    { source: "original_sin", target: "anxiety", type: "influence", weight: 2 },
    { source: "confession", target: "subjective_truth", type: "develop", weight: 2 },

// ОСТАВИТЬ (3 связи достаточно для передачи влияния):
    { source: "faith_reason", target: "leap_faith", type: "develop", weight: 3 },
    { source: "grace", target: "absurd", type: "influence", weight: 2 },
    { source: "time_augustine", target: "moment", type: "develop", weight: 2 },


// ----------------------------------------------------------------------------
// 1.2. Избыточные: Кьеркегор → Хайдеггер (удалить 2 из 5)
// ----------------------------------------------------------------------------
// УДАЛИТЬ:
    { source: "leap_faith", target: "ereignis", type: "influence", weight: 1 },
    { source: "despair", target: "sorge", type: "influence", weight: 2 },

// ОСТАВИТЬ (3 основные связи):
    { source: "anxiety", target: "geworfenheit", type: "develop", weight: 3 },
    { source: "individual", target: "dasein", type: "develop", weight: 3 },
    { source: "moment", target: "sein_zum_tode", type: "influence", weight: 2 },


// ----------------------------------------------------------------------------
// 1.3. Избыточные: Ницше → Хайдеггер (удалить 2 из 4)
// ----------------------------------------------------------------------------
// УДАЛИТЬ:
    { source: "perspectivism", target: "dasein", type: "influence", weight: 2 },
    { source: "god_dead", target: "aletheia", type: "influence", weight: 2 },

// ОСТАВИТЬ (2 ключевые связи):
    { source: "will_power", target: "sein", type: "influence", weight: 2 },
    { source: "eternal_return", target: "ereignis", type: "influence", weight: 2 },


// ----------------------------------------------------------------------------
// 1.4. Избыточные критические: Фихте ← Кьеркегор (удалить все 3)
// ----------------------------------------------------------------------------
// УДАЛИТЬ (все усиливают экзистенциалистский перекос):
    { source: "individual", target: "absolute_ego", type: "critique", weight: 3 },
    { source: "subjective_truth", target: "wissenschaftslehre", type: "critique", weight: 2 },
    { source: "anxiety", target: "absolute_ego", type: "critique", weight: 2 },


// ----------------------------------------------------------------------------
// 1.5. Некоторые Сартр → постмодернизм (удалить 2)
// ----------------------------------------------------------------------------
// УДАЛИТЬ:
    { source: "nothingness", target: "body_without_organs", type: "influence", weight: 1 },
    { source: "bad_faith", target: "discipline", type: "dialogue", weight: 1, bidirectional: true },

// ОСТАВИТЬ (важные диалоги):
    { source: "difference", target: "for_itself", type: "critique", weight: 2, bidirectional: true },
    { source: "freedom_sartre", target: "deterritorialization", type: "influence", weight: 2 },
    { source: "power_knowledge", target: "freedom_sartre", type: "critique", weight: 2, bidirectional: true },
    { source: "engagement", target: "care_self", type: "dialogue", weight: 2, bidirectional: true },


// ----------------------------------------------------------------------------
// 1.6. Постмодернистская критика Платона (удалить 1)
// ----------------------------------------------------------------------------
// УДАЛИТЬ:
    { source: "multiplicity", target: "ideas", type: "critique", weight: 2 },

// ОСТАВИТЬ (важная критика):
    { source: "difference", target: "eidos", type: "critique", weight: 3 },


// ----------------------------------------------------------------------------
// 1.7. Шеллинг ← Кьеркегор (удалить 1 из 2)
// ----------------------------------------------------------------------------
// УДАЛИТЬ:
    { source: "leap_faith", target: "intellectual_intuition", type: "critique", weight: 2 },

// ОСТАВИТЬ:
    { source: "philosophy_revelation", target: "stages_existence", type: "influence", weight: 2 },


// ----------------------------------------------------------------------------
// 1.8. Шопенгауэр → Гегель (удалить 1 из 3, остальные уменьшить вес)
// ----------------------------------------------------------------------------
// УДАЛИТЬ:
    { source: "denial_will", target: "absolute_idea", type: "oppose", weight: 2 },

// Остальные две связи см. в разделе корректировки весов


// ============================================================================
// ИТОГО УДАЛИТЬ: 14 связей
// ============================================================================


// ============================================================================
// РАЗДЕЛ 2: НОВЫЕ СВЯЗИ ДЛЯ ДОБАВЛЕНИЯ
// ============================================================================

// ----------------------------------------------------------------------------
// 2.1. Усиление Витгенштейна и аналитической философии (+11 связей)
// ----------------------------------------------------------------------------

    // Фреге → Витгенштейн (фундаментальное влияние)
    { source: "sense_reference", target: "picture_theory", type: "develop", weight: 3 },
    { source: "sense_reference", target: "language_game", type: "influence", weight: 2 },
    { source: "concept_script", target: "logical_atomism", type: "influence", weight: 2 },

    // Рассел → аналитическая философия
    { source: "theory_descriptions", target: "language_game", type: "influence", weight: 2 },
    { source: "logical_atomism", target: "family_resemblance", type: "dialogue", weight: 2 },

    // Витгенштейн → современная философия (усиление)
    { source: "language_game", target: "lifeworld", type: "influence", weight: 2 },
    { source: "language_game", target: "hermeneutic_circle", type: "influence", weight: 2 },
    { source: "showing_saying", target: "aletheia", type: "dialogue", weight: 2 },

    // Усиление Фреге
    { source: "concept_script", target: "phenomenology", type: "influence", weight: 1 },
    { source: "sense_reference", target: "intentionality", type: "dialogue", weight: 1 },

    // Рассел → феноменология
    { source: "logical_atomism", target: "constitution", type: "influence", weight: 1 },


// ----------------------------------------------------------------------------
// 2.2. Усиление классической метафизики (+7 связей)
// ----------------------------------------------------------------------------

    // Аристотель → Фома (базовые связи, которые должны были быть изначально)
    { source: "four_causes", target: "essence_existence", type: "develop", weight: 3 },
    { source: "form", target: "analogy_being", type: "develop", weight: 2 },
    { source: "entelechy", target: "five_ways", type: "influence", weight: 2 },

    // Фома → Декарт (схоластический мост)
    { source: "essence_existence", target: "infinite_idea", type: "influence", weight: 2 },
    { source: "five_ways", target: "ontological_proof", type: "develop", weight: 2 },

    // Аристотель → Спиноза
    { source: "entelechy", target: "attributes", type: "influence", weight: 2 },

    // Фома → Лейбниц (схоластическое влияние)
    { source: "essence_existence", target: "sufficient_reason", type: "influence", weight: 2 },


// ----------------------------------------------------------------------------
// 2.3. Баланс герменевтики (+3 связи)
// ----------------------------------------------------------------------------

    // Гадамер → современность (усиление герменевтики)
    { source: "horizon_understanding", target: "language_game", type: "dialogue", weight: 2, bidirectional: true },
    { source: "tradition_gadamer", target: "showing_saying", type: "influence", weight: 1 },

    // Дильтей → современность
    { source: "verstehen", target: "language_game", type: "influence", weight: 2 },


// ----------------------------------------------------------------------------
// 2.4. Дополнительные важные связи (+2 связи)
// ----------------------------------------------------------------------------

    // Гегель ↔ Витгенштейн (неожиданная, но важная связь)
    { source: "language_game", target: "dialectic", type: "dialogue", weight: 1 },

    // Рассел → Гуссерль
    { source: "theory_descriptions", target: "intentionality", type: "dialogue", weight: 1 },


// ============================================================================
// ИТОГО ДОБАВИТЬ: 23 связи
// ============================================================================


// ============================================================================
// РАЗДЕЛ 3: КОРРЕКТИРОВКИ ВЕСОВ СУЩЕСТВУЮЩИХ СВЯЗЕЙ
// ============================================================================

// ----------------------------------------------------------------------------
// 3.1. УВЕЛИЧИТЬ ВЕСА (усилить влияние) - ~6 связей
// ----------------------------------------------------------------------------

    // Аристотель - ключевые концепции (найти в коде и увеличить)
    // { source: "four_causes", target: "act_potency", type: "...", weight: 2 }, → weight: 3
    // { source: "four_causes", target: "form", type: "...", weight: 2 }, → weight: 3
    // { source: "act_potency", target: "entelechy", type: "...", weight: 2 }, → weight: 3

    // Гегель - синтез (усилить ключевые связи)
    // { source: "absolute_idea", target: "objective_spirit", type: "...", weight: 2 }, → weight: 3
    // { source: "dialectic", target: "absolute_idea", type: "...", weight: 2 }, → weight: 3

    // Витгенштейн (уже в новой базе, увеличить вес)
    // { source: "language_game", target: "rhizome", type: "influence", weight: 2 }, → weight: 3
    // { source: "family_resemblance", target: "multiplicity", type: "influence", weight: 2 }, → weight: 3


// ----------------------------------------------------------------------------
// 3.2. УМЕНЬШИТЬ ВЕСА (ослабить перекосы) - ~6 связей
// ----------------------------------------------------------------------------

    // Сартр → постмодернизм (ослабить)
    // { source: "freedom_sartre", target: "deterritorialization", type: "influence", weight: 2 }, → weight: 1

    // Шопенгауэр → Гегель (слишком сильная критика, ослабить)
    // { source: "will_schop", target: "absolute_idea", type: "critique", weight: 3 }, → weight: 2
    // { source: "suffering", target: "dialectic", type: "oppose", weight: 2 }, → weight: 1

    // Некоторые экзистенциалистские (где weight: 3 избыточен)
    // { source: "for_itself", target: "nothingness", type: "...", weight: 3 }, → weight: 2 (где уместно)

    // Абсолютное Я → связи (где weight: 3 избыточен)
    // Проверить и при необходимости снизить некоторые weight: 3 → 2


// ============================================================================
// РАЗДЕЛ 4: ИНСТРУКЦИИ ПО ПРИМЕНЕНИЮ
// ============================================================================

/*

ПОШАГОВАЯ ИНСТРУКЦИЯ:

1. УДАЛЕНИЕ СВЯЗЕЙ (14 штук):
   - Найти в массиве relations каждую связь из раздела 1
   - Удалить всю строку с этой связью
   - Проверить, нет ли последней запятой перед закрывающей скобкой

2. ДОБАВЛЕНИЕ СВЯЗЕЙ (23 штуки):
   - Скопировать все связи из раздела 2
   - Вставить в конец массива relations (перед закрывающей скобкой ]
   - Убедиться, что после предыдущей последней связи стоит запятая

3. КОРРЕКТИРОВКА ВЕСОВ (~12 связей):
   - Найти каждую связь, указанную в разделе 3
   - Изменить только значение weight согласно инструкциям
   - НЕ менять другие параметры

4. ПРОВЕРКА СИНТАКСИСА:
   - Проверить все запятые
   - Убедиться, что нет лишних запятых перед ]
   - Проверить правильность кавычек

5. ТЕСТИРОВАНИЕ:
   - Запустить скрипт подсчёта метрик
   - Проверить, что:
     * Общее количество связей: ~1158
     * PageRank Витгенштейна: должен вырасти
     * Eigenvector Аристотеля: должен вырасти
     * Betweenness Dasein: должен немного снизиться

ОЖИДАЕМЫЕ РЕЗУЛЬТАТЫ:

Метрика                          | До корректировки | После корректировки
-------------------------------- | ---------------- | -------------------
Количество связей                | 1149             | ~1158
PageRank Витгенштейна (место)    | вне топ-10       | топ-5-7
Eigenvector Аристотеля (место)   | вне топ-10       | топ-3-5
Betweenness Абсолютной идеи      | вне топ-10       | топ-7-10
Экзистенциалистские связи        | ~35 (19.6%)      | ~20 (11.2%)
Аналитическая философия          | недооценена      | сбалансирована

ФИЛОСОФСКАЯ ОЦЕНКА после корректировок:
  • Философская адекватность: 6.0/10 → 7.5/10
  • Структурная связность: 9.0/10 → 8.5/10 (небольшое снижение допустимо)
  • Баланс эпох: 5.5/10 → 8.0/10
  • ИТОГО: 6.5/10 → 8.0/10

*/


// ============================================================================
// РАЗДЕЛ 5: КОНКРЕТНЫЕ ПРИМЕРЫ ПОИСКА И ЗАМЕНЫ
// ============================================================================

/*

ПРИМЕР 1: Удаление связи Августин → Кьеркегор

НАЙТИ:
    { source: "two_cities", target: "stages_existence", type: "influence", weight: 1 },

УДАЛИТЬ: всю эту строку


ПРИМЕР 2: Добавление связи Фреге → Витгенштейн

В конце массива relations, перед закрывающей скобкой ], ДОБАВИТЬ:

    // Усиление аналитической философии
    { source: "sense_reference", target: "picture_theory", type: "develop", weight: 3 },
    { source: "sense_reference", target: "language_game", type: "influence", weight: 2 },
    { source: "concept_script", target: "logical_atomism", type: "influence", weight: 2 }


ПРИМЕР 3: Изменение веса Шопенгауэр → Гегель

НАЙТИ:
    { source: "will_schop", target: "absolute_idea", type: "critique", weight: 3 },

ЗАМЕНИТЬ НА:
    { source: "will_schop", target: "absolute_idea", type: "critique", weight: 2 },

*/


// ============================================================================
// РАЗДЕЛ 6: АЛЬТЕРНАТИВНЫЙ ПОДХОД - ГОТОВЫЕ БЛОКИ КОДА
// ============================================================================

/*

Если вы хотите просто скопировать готовые блоки кода, используйте секции ниже.
Они уже содержат все необходимые корректировки.

*/

// ----------------------------------------------------------------------------
// 6.1. ПОЛНЫЙ БЛОК: Аналитическая философия (готов к вставке)
// ----------------------------------------------------------------------------

    // ============================================
    // АНАЛИТИЧЕСКАЯ ФИЛОСОФИЯ - УСИЛЕНИЕ
    // ============================================
    
    // ФРЕГЕ - ВИТГЕНШТЕЙН
    { source: "sense_reference", target: "picture_theory", type: "develop", weight: 3 },
    { source: "sense_reference", target: "language_game", type: "influence", weight: 2 },
    { source: "concept_script", target: "logical_atomism", type: "influence", weight: 2 },
    
    // ФРЕГЕ - ГУССЕРЛЬ (связь аналитики и феноменологии)
    { source: "concept_script", target: "phenomenology", type: "influence", weight: 1 },
    { source: "sense_reference", target: "intentionality", type: "dialogue", weight: 1 },
    
    // РАССЕЛ - ВИТГЕНШТЕЙН
    { source: "theory_descriptions", target: "language_game", type: "influence", weight: 2 },
    { source: "logical_atomism", target: "family_resemblance", type: "dialogue", weight: 2 },
    { source: "logical_atomism", target: "constitution", type: "influence", weight: 1 },
    { source: "theory_descriptions", target: "intentionality", type: "dialogue", weight: 1 },
    
    // ВИТГЕНШТЕЙН - СОВРЕМЕННАЯ ФИЛОСОФИЯ
    { source: "language_game", target: "lifeworld", type: "influence", weight: 2 },
    { source: "language_game", target: "hermeneutic_circle", type: "influence", weight: 2 },
    { source: "showing_saying", target: "aletheia", type: "dialogue", weight: 2 },
    { source: "language_game", target: "dialectic", type: "dialogue", weight: 1 },


// ----------------------------------------------------------------------------
// 6.2. ПОЛНЫЙ БЛОК: Классическая метафизика (готов к вставке)
// ----------------------------------------------------------------------------

    // ============================================
    // КЛАССИЧЕСКАЯ МЕТАФИЗИКА - УСИЛЕНИЕ
    // ============================================
    
    // АРИСТОТЕЛЬ - ФОМА (базовые связи)
    { source: "four_causes", target: "essence_existence", type: "develop", weight: 3 },
    { source: "form", target: "analogy_being", type: "develop", weight: 2 },
    { source: "entelechy", target: "five_ways", type: "influence", weight: 2 },
    
    // АРИСТОТЕЛЬ - СПИНОЗА
    { source: "entelechy", target: "attributes", type: "influence", weight: 2 },
    
    // ФОМА - ДЕКАРТ (схоластический мост к модерну)
    { source: "essence_existence", target: "infinite_idea", type: "influence", weight: 2 },
    { source: "five_ways", target: "ontological_proof", type: "develop", weight: 2 },
    
    // ФОМА - ЛЕЙБНИЦ
    { source: "essence_existence", target: "sufficient_reason", type: "influence", weight: 2 },


// ----------------------------------------------------------------------------
// 6.3. ПОЛНЫЙ БЛОК: Герменевтика (готов к вставке)
// ----------------------------------------------------------------------------

    // ============================================
    // ГЕРМЕНЕВТИКА - БАЛАНС
    // ============================================
    
    // ГАДАМЕР - ВИТГЕНШТЕЙН (герменевтика и аналитика)
    { source: "horizon_understanding", target: "language_game", type: "dialogue", weight: 2, bidirectional: true },
    { source: "tradition_gadamer", target: "showing_saying", type: "influence", weight: 1 },
    
    // ДИЛЬТЕЙ - ВИТГЕНШТЕЙН
    { source: "verstehen", target: "language_game", type: "influence", weight: 2 },


// ============================================================================
// КОНЕЦ ФАЙЛА КОРРЕКТИРОВОК
// ============================================================================
