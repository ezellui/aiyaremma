# ПОЛНОЕ РУКОВОДСТВО ПО ИНТЕГРАЦИИ МЕТРИК
## Версия 2.0 - Часть 2

---

## 5. ОПИСАНИЯ МЕТРИК {#описания-метрик}

Добавить после инициализации классов метрик:

```javascript
// ============================================
// ОПИСАНИЯ МЕТРИК С УЧЁТОМ ПАРАМЕТРОВ
// ============================================

const metricDescriptions = {
    // Базовые метрики
    overview: {
        name: "Общий обзор графа",
        description: "Базовая статистика сети философских концепций",
        interpretation: () => "Общие характеристики сети: количество узлов, связей, плотность сети и средняя степень связности.",
        usage: "Используйте для понимания общей структуры и масштаба сети.",
        formula: () => "Плотность = 2E / (N × (N-1)), где E - рёбра, N - узлы"
    },
    
    degree: {
        name: "Степень связности (Degree Centrality)",
        description: "Количество связей каждого узла",
        interpretation: () => {
            if (respectDirection) {
                return "Направленный: отдельно считаются входящие (сколько влияют на концепцию) и исходящие (на сколько влияет концепция) связи. Высокий InDegree = много ссылаются, высокий OutDegree = много цитирует других.";
            } else {
                return "Ненаправленный: общее количество связей узла. Высокая степень = концепция активно связана с другими идеями в сети.";
            }
        },
        usage: () => {
            const base = "Простейшая метрика влияния. Концепции с высокой степенью связности — это хабы сети.";
            return respectDirection 
                ? base + " При учёте направленности можно различить \"авторитеты\" (высокий InDegree) и \"концентраторы\" (высокий OutDegree)."
                : base;
        },
        formula: () => respectDirection 
            ? "Degree(v) = InDegree(v) + OutDegree(v)" 
            : "Degree(v) = |{u : (v,u) ∈ E}|"
    },
    
    pagerank: {
        name: "PageRank",
        description: "Важность узла на основе важности ссылающихся на него узлов",
        interpretation: () => {
            if (respectDirection && useWeightedPaths) {
                return "Направленный взвешенный: концепция важна, если на неё ссылаются важные концепции через сильные связи. Вес связи усиливает передачу важности.";
            } else if (respectDirection && !useWeightedPaths) {
                return "Направленный: концепция важна через входящие ссылки от важных узлов. Количество ссылок важнее их силы.";
            } else if (!respectDirection && useWeightedPaths) {
                return "Ненаправленный взвешенный: важность распространяется через сильные связи в обе стороны.";
            } else {
                return "Ненаправленный: классический PageRank, все связи равноценны и симметричны.";
            }
        },
        usage: () => {
            const base = "Выявляет «авторитеты» — концепции, на которые ссылаются другие важные концепции.";
            return useWeightedPaths 
                ? base + " С весами показывает концепции, получающие сильное влияние от авторитетных источников."
                : base + " Без весов — чисто топологическая важность.";
        },
        formula: () => {
            const base = "PR(v) = (1-d)/N + d × Σ PR(u)/OutDegree(u)";
            return useWeightedPaths ? base + ", с учётом весов w(u,v)" : base;
        }
    },
    
    betweenness: {
        name: "Betweenness Centrality",
        description: "Как часто узел лежит на кратчайших путях между другими узлами",
        interpretation: () => {
            if (respectDirection && useWeightedPaths) {
                return "Направленный взвешенный: концепция — мост в НАПРАВЛЕННЫХ потоках влияния с учётом силы связей. Высокое значение = незаменимый посредник в передаче СИЛЬНОГО влияния.";
            } else if (respectDirection && !useWeightedPaths) {
                return "Направленный: концепция-мост в направленных путях влияния. Контролирует потоки идей между традициями.";
            } else if (!respectDirection && useWeightedPaths) {
                return "Ненаправленный взвешенный: посредник в сильно связанных путях. Может быть менее связан количественно, но критичен в сильных взаимосвязях.";
            } else {
                return "Ненаправленный: классический betweenness. Концепция-мост между разными частями сети.";
            }
        },
        usage: () => {
            const base = "Ищите «мосты» и «узкие места» — концепции, через которые проходит философское влияние.";
            return useWeightedPaths 
                ? base + " С весами выявляет мосты в СУЩЕСТВЕННЫХ (сильных) связях."
                : base;
        },
        formula: () => {
            const base = "BC(v) = Σ (σ_st(v) / σ_st)";
            return useWeightedPaths 
                ? base + ", где пути взвешены обратно пропорционально весам рёбер" 
                : base + ", где σ_st — число кратчайших путей s→t";
        }
    },
    
    closeness: {
        name: "Closeness Centrality",
        description: "Средняя близость узла ко всем остальным узлам",
        interpretation: () => {
            if (respectDirection && useWeightedPaths) {
                return "Направленный взвешенный: как быстро концепция ВЛИЯЕТ на остальные через сильные прямые пути. Высокое значение = эффективный источник влияния.";
            } else if (respectDirection && !useWeightedPaths) {
                return "Направленный: насколько быстро концепция может повлиять на остальную сеть через направленные пути (независимо от силы).";
            } else if (!respectDirection && useWeightedPaths) {
                return "Ненаправленный взвешенный: центральность через СИЛЬНЫЕ связи. Концепция близка к другим через фундаментальные, а не случайные связи.";
            } else {
                return "Ненаправленный: топологическая близость. Концепция в центре сети, недалеко от остальных.";
            }
        },
        usage: () => {
            const base = "Находите концепции в «центре» сети — те, от которых близко до всех остальных идей.";
            return useWeightedPaths 
                ? base + " С весами — концепции, центральные в СИЛЬНЫХ связях."
                : base;
        },
        formula: () => {
            const base = "CC(v) = (N-1) / Σ dist(v,u)";
            return useWeightedPaths 
                ? base + ", где dist — взвешенное расстояние" 
                : base;
        }
    },
    
    eigenvector: {
        name: "Eigenvector Centrality",
        description: "Влиятельность узла через связи с другими влиятельными узлами",
        interpretation: () => {
            if (respectDirection && useWeightedPaths) {
                return "Направленный взвешенный: концепция важна, если на неё СИЛЬНО влияют другие важные концепции. Входящая связь от влиятельного узла с весом 3 даёт больше 'очков', чем с весом 1.";
            } else if (respectDirection && !useWeightedPaths) {
                return "Направленный: концепция важна через входящие связи от других важных узлов. Количество важнее силы связи.";
            } else if (!respectDirection && useWeightedPaths) {
                return "Ненаправленный взвешенный: концепция важна через СИЛЬНЫЕ связи с другими важными концепциями. Взаимное усиление через фундаментальные влияния.";
            } else {
                return "Ненаправленный: концепция важна, если связана с другими важными концепциями. Симметричное взаимное усиление, все связи равны.";
            }
        },
        usage: () => {
            const base = "Используйте для выявления концепций, которые составляют ядро философской традиции. Они важны не сами по себе, а через взаимное усиление с другими ключевыми идеями.";
            return useWeightedPaths 
                ? base + " С весами выделяет ядро ФУНДАМЕНТАЛЬНЫХ взаимосвязей."
                : base;
        },
        formula: () => {
            const base = "x(v) = (1/λ) × Σ A(v,u) × x(u)";
            return useWeightedPaths 
                ? base + ", где A — взвешенная матрица смежности" 
                : base + ", где A — бинарная матрица смежности";
        }
    },
    
    'weighted-clustering': {
        name: "Взвешенная кластеризация (Weighted Clustering)",
        description: "Плотность связей в окрестности узла с учётом весов",
        interpretation: () => {
            if (useWeightedPaths) {
                return "С весами: насколько плотны и СИЛЬНЫ связи в окрестности концепции. Высокое значение = концепция в кластере плотных И фундаментальных взаимосвязей.";
            } else {
                return "Без весов: классическая кластеризация — насколько соседи узла связаны между собой. Высокое значение = концепция в плотном кластере идей.";
            }
        },
        usage: () => {
            const base = "Основная метрика кластеризации.";
            return useWeightedPaths 
                ? base + " С весами выявляет концепции в плотных кластерах СИЛЬНЫХ взаимосвязей. Идеально для философских систем с градацией важности связей."
                : base + " Без весов — классическая кластеризация по топологии.";
        },
        formula: () => useWeightedPaths 
            ? "C_w(i) = Σ(w_ij + w_ih + w_jh)/3 / max_triangles (взвешенная)" 
            : "C(v) = 2e(v) / (k(v)(k(v)-1)) (стандартная)"
    },
    
    'local-cohesion': {
        name: "Локальная когезия (Local Cohesion Score)",
        description: "Комбинированная метрика: кластеризация × сила связей × количество соседей",
        interpretation: () => {
            return "Высокое значение = концепция одновременно: (1) в плотном кластере, (2) с сильными связями, (3) с большим числом соседей. Это \"центры философских школ\" — узлы, вокруг которых концентрируются взаимосвязанные фундаментальные идеи. Низкое = либо изолированная концепция, либо мост между группами.";
        },
        usage: () => "Используйте для поиска ядер философских школ — концепций, которые не просто связаны со многими идеями, но образуют с ними плотные, сильно связанные группы. Отличается от простой кластеризации тем, что учитывает масштаб влияния.",
        formula: () => "Cohesion = clustering × log(1 + strength) × log(1 + neighbors)"
    },
    
    'rich-club': {
        name: "Rich-Club (Клуб влиятельных)",
        description: "Степень связности узла с другими высокостепенными узлами",
        interpretation: () => {
            return "Высокое значение = концепция связана с другими центральными идеями. Это \"философская элита\" — идеи, которые не просто важны сами по себе, но образуют взаимосвязанное ядро традиции. Низкое = концепция на периферии, связана в основном с менее центральными идеями.";
        },
        usage: () => "Используйте для выявления концепций, образующих \"элитный клуб\" философской системы — взаимосвязанное ядро центральных идей. Если у Платона, Аристотеля, Канта высокий rich-club, их центральные концепции образуют плотно связанную сеть, несмотря на временную дистанцию.",
        formula: () => "RC(v) = (high_degree_neighbors / total_neighbors) × log(avg_neighbor_degree)"
    },
    
    // Философские метрики
    'problem-generation': {
        name: "Индекс проблемности (Problem Generation Index)",
        description: "Насколько концепция порождает проблемы и критику",
        interpretation: () => "Высокое значение = концепция вызывает много критики, оппозиции и выявляет внутренние противоречия. Это \"проблемные\" идеи, которые стимулируют дискуссии и развитие философской мысли. Низкое значение = концепция относительно бесспорна или малоизвестна.",
        usage: () => "Используйте для выявления концепций, которые стали катализаторами философских дебатов. Высокий индекс не означает «плохую» концепцию, а наоборот — интеллектуально продуктивную.",
        formula: () => "PGI = Σ(critique×2 + oppose×3 + contradiction×4) × weight"
    },
    
    'critical-power': {
        name: "Индекс критической силы (Critical Power Index)",
        description: "Насколько концепция сама критикует другие концепции",
        interpretation: () => "Высокое значение = концепция активно критикует и оппонирует другим идеям, особенно влиятельным. Это \"критические\" концепции, которые подвергают сомнению устоявшиеся взгляды. Учитывается влиятельность критикуемых концепций.",
        usage: () => "Используйте для поиска «разрушительных» концепций — тех, что ставят под вопрос фундаментальные идеи. Критика влиятельных концепций ценится выше.",
        formula: () => "CPI = Σ(critique×2 + oppose×3) × weight × target_influence"
    },
    
    'revolutionary': {
        name: "Индекс революционности (Revolutionary Index)",
        description: "Насколько концепция порывает с традицией и создаёт новое",
        interpretation: () => "Высокое значение = концепция противопоставляет себя предшественникам, критикует устоявшиеся идеи, синтезирует противоположности и порождает новые направления, при этом слабо укоренена в предшествующей традиции. Это революционные идеи, меняющие ход философии.",
        usage: () => "Используйте для выявления переломных моментов в истории философии — концепций, которые радикально меняют направление мысли.",
        formula: () => "RI = oppositions_to_earlier×2 + critiques_of_influential×1.5 + syntheses×2 + developments - rootedness×3"
    },
    
    'paradigm-shift': {
        name: "Индекс парадигмального сдвига (Paradigm Shift Index)",
        description: "Насколько концепция меняет способ мышления (метод, а не только содержание)",
        interpretation: () => "Высокое значение = концепция меняет не просто взгляды, но сам способ мышления. Это методологические концепции, влияющие на разные области, которые принимаются многими более поздними философами. Это смена парадигмы в философии.",
        usage: () => "Используйте для поиска концепций, изменивших метод философствования. Такие идеи создают новые способы постановки вопросов и поиска ответов.",
        formula: () => "PSI = is_methodological×5 + rubrics_breadth×2 + later_adopters"
    },
    
    'influence': {
        name: "Индекс влияния (Influence Index)",
        description: "Улучшенная метрика влияния с учётом типов связей и временной динамики",
        interpretation: () => "Высокое значение = концепция оказала сильное прямое влияние на более поздние идеи и вступила в продуктивный диалог с современниками. Учитывается тип влияния (развитие, применение, диалог) и его сила.",
        usage: () => "Более тонкая метрика влияния, чем простой подсчёт связей. Различает прямое историческое влияние и синхронный диалог. Используйте для понимания реального исторического воздействия концепций.",
        formula: () => "II = forward_influence + contemporary_influence×0.5, где учитываются типы и веса связей"
    },
    
    'foundational': {
        name: "Индекс основополагания (Foundational Index)",
        description: "Насколько концепция является основанием для других (служит предпосылкой)",
        interpretation: () => "Высокое значение = концепция служит предпосылкой, условием или основой для других идей. Это фундаментальные концепции, без которых не могут существовать другие. Из них «вырастают» новые концепции.",
        usage: () => "Используйте для поиска фундамента философских систем — базовых концепций, на которых строится здание мысли.",
        formula: () => "FI = presuppositions×3 + conditions×2 + emergences×2.5 + applications + developments"
    },
    
    'synthetic': {
        name: "Индекс синтетичности (Synthetic Index)",
        description: "Насколько концепция объединяет разные традиции",
        interpretation: () => "Высокое значение = концепция синтезирует идеи разных философов, рубрик и традиций. Это мосты между направлениями мысли, объединяющие разнородное. Примиряет противоречия и создаёт единство из многообразия.",
        usage: () => "Используйте для поиска синтетических концепций — тех, что преодолевают дихотомии и объединяют противоположности. Это концепции-посредники между традициями.",
        formula: () => "SI = syntheses×3 + reconciliations×2 + diverse_influences×2 + thematic_breadth"
    },
    
    'dialogical': {
        name: "Индекс диалогичности (Dialogical Index)",
        description: "Насколько концепция находится в диалоге с другими",
        interpretation: () => "Высокое значение = концепция вступает в активный диалог с другими идеями, имеет двусторонние связи и дополняет другие концепции. Это не монолог, а беседа философских идей.",
        usage: () => "Используйте для выявления концепций, вокруг которых разворачивается философский диалог. Они не навязывают односторонне, а участвуют в обмене идеями.",
        formula: () => "DI = dialogues×2 + bidirectional×3 + complements"
    },
    
    'coherence': {
        name: "Индекс внутренней когерентности (Internal Coherence Index)",
        description: "Насколько концепции философа согласованы между собой",
        interpretation: () => "Высокое значение = концепция хорошо согласована с другими идеями того же философа. Много положительных связей (предпосылки, следствия, развития) и мало противоречий. Низкое = концепция противоречит другим идеям того же автора.",
        usage: () => "Используйте для оценки систематичности мышления философа. Высокая когерентность = последовательная система, низкая = эклектика или эволюция взглядов.",
        formula: () => "ICI = positive_links - negative_links×2"
    },
    
    'tension': {
        name: "Индекс напряжения (Tension Index)",
        description: "Степень внутреннего напряжения и конфликтности концепции",
        interpretation: () => "Высокое значение = концепция содержит внутренние напряжения, противоречия, оппозиции. Это диалектически насыщенные идеи, полные внутренних конфликтов. Низкое = концепция относительно гармонична.",
        usage: () => "Используйте для поиска диалектически богатых концепций. Высокое напряжение не всегда недостаток — это может быть продуктивное противоречие, стимулирующее развитие мысли.",
        formula: () => "TI = tensions×2 + oppositions + contradictions×3"
    },
    
    // Продвинутые метрики
    'transformation': {
        name: "Индекс трансформации (Transformation Index)",
        description: "Насколько концепция трансформирует заимствованные идеи",
        interpretation: () => "Высокое значение = концепция не просто принимает влияния, но активно их трансформирует, развивает, применяет, синтезирует. Это творческая переработка, а не пассивное восприятие. Соотношение выходных трансформаций к входным влияниям.",
        usage: () => "Используйте для поиска концепций, которые являются не только получателями, но и трансформаторами идей. Показывает творческую активность концепции.",
        formula: () => "TI = (developments + applications + syntheses) / influences × 10 + sum"
    },
    
    'fertility': {
        name: "Индекс концептуальной плодовитости (Conceptual Fertility Index)",
        description: "Насколько концепция порождает новые концепции",
        interpretation: () => "Высокое значение = из концепции вырастает много новых идей, она активно развивается другими философами. Это интеллектуально плодородные концепции, дающие богатый урожай новых мыслей.",
        usage: () => "Используйте для поиска «материнских» концепций — тех, что порождают целые семейства новых идей. Показывает генеративный потенциал концепции.",
        formula: () => "CFI = emergences×3 + developments×2 + later_adopters"
    },
    
    'complexity': {
        name: "Индекс концептуальной сложности (Conceptual Complexity Index)",
        description: "Насколько концепция сложна и многоаспектна",
        interpretation: () => "Высокое значение = концепция имеет много типов связей, охватывает разные рубрики, содержит противоречия и предпосылки, связана с концепциями многих философов. Это многомерные, сложные идеи, не сводимые к простым формулам.",
        usage: () => "Используйте для оценки интеллектуальной сложности концепций. Высокая сложность = богатство содержания, но и трудность понимания.",
        formula: () => "CCI = (link_type_diversity)×2 + rubrics×3 + contradictions×5 + presuppositions×2 + related_philosophers"
    },
    
    'continuity': {
        name: "Индекс преемственности (Conceptual Continuity Index)",
        description: "Насколько концепция сохраняет преемственность через время",
        interpretation: () => "Высокое значение = концепция постоянно упоминается и развивается на протяжении многих поколений без больших разрывов. Это идеи с непрерывной традицией, сохраняющие актуальность через века. Низкое = концепция была забыта или имеет прерывистую историю.",
        usage: () => "Используйте для оценки исторической устойчивости концепций. Показывает, какие идеи сохраняют живую традицию, а какие переживают периоды забвения.",
        formula: () => "CCI = (generations - gaps) × later_references"
    },
    
    'temporal-influence': {
        name: "Паттерн временного влияния (Temporal Influence Pattern)",
        description: "Как влияние концепции изменяется во времени",
        interpretation: () => "Классифицирует концепции по паттерну влияния во времени: lasting (устойчивое, от момента появления до далёкого будущего), fading (угасающее, сильное сразу, потом исчезает), delayed (отложенное, слабое сразу, сильное позже), normal (нормальное, стандартное распространение).",
        usage: () => "Используйте для понимания динамики влияния концепций. Разные паттерны говорят о разных механизмах распространения идей. Отложенное влияние может указывать на «опережающие время» концепции.",
        formula: () => "Анализ распределения ссылок по временным периодам: 0-50, 50-150, 150-300, 300+ лет"
    },
    
    // Метрики философов
    'philosopher-profile': {
        name: "Профиль философа (Philosopher Profile)",
        description: "Комплексная характеристика творчества философа",
        interpretation: () => "Показывает средние значения различных метрик для всех концепций философа: влияние, революционность, когерентность. Позволяет охарактеризовать стиль мышления философа в целом.",
        usage: () => "Используйте для сравнения философов между собой и понимания их уникальных характеристик. Высокая революционность при низкой когерентности = радикальный, но эклектичный мыслитель.",
        formula: () => "Усреднение метрик всех концепций философа"
    },
    
    'philosopher-systematic': {
        name: "Индекс систематичности философа (Philosopher Systematic Index)",
        description: "Насколько концепции философа связаны между собой",
        interpretation: () => "Высокое значение = концепции философа образуют плотную сеть взаимных связей. Это систематический мыслитель, строящий целостную архитектуру идей. Низкое = концепции слабо связаны, философ разрабатывает отдельные темы без единой системы.",
        usage: () => "Используйте для различения систематических и несистематических мыслителей. Кант, Гегель, Спиноза должны иметь высокие значения.",
        formula: () => "Плотность внутренних связей: internal_links / max_possible_links × 100%"
    },
    
    'philosopher-reach': {
        name: "Индекс исторического охвата (Historical Reach Index)",
        description: "Временной размах влияния философа",
        interpretation: () => "Высокое значение = философ повлиял на много более поздних мыслителей на протяжении многих поколений. Это мыслители с длительным и широким влиянием. Низкое = влияние ограничено современниками или ближайшими потомками.",
        usage: () => "Используйте для оценки исторического масштаба влияния философа. Показывает, какие мыслители остаются актуальными через века.",
        formula: () => "HRI = influenced_philosophers_count × generations"
    },
    
    'philosopher-interdisciplinary': {
        name: "Индекс междисциплинарности (Interdisciplinary Index)",
        description: "Насколько философ охватывает разные тематические области",
        interpretation: () => "Высокое значение = философ работает в разных рубриках (этика, метафизика, эпистемология и т.д.) с относительно равномерным распределением. Это универсальные мыслители. Низкое = философ специализируется в узкой области.",
        usage: () => "Используйте для различения универсалов и специалистов. Учитывается как количество рубрик, так и энтропия распределения (равномерность).",
        formula: () => "II = rubric_count × (1 + entropy)"
    }
};

// Функция для получения описания метрики
function getMetricDescription(metricKey) {
    const desc = metricDescriptions[metricKey];
    if (!desc) return null;
    
    return {
        name: desc.name,
        description: desc.description,
        interpretation: typeof desc.interpretation === 'function' ? desc.interpretation() : desc.interpretation,
        usage: typeof desc.usage === 'function' ? desc.usage() : desc.usage,
        formula: typeof desc.formula === 'function' ? desc.formula() : desc.formula
    };
}
```

---

## 6. ФУНКЦИИ УПРАВЛЕНИЯ МОДАЛЬНЫМ ОКНОМ {#функции-управления}

```javascript
// ============================================
// УПРАВЛЕНИЕ МОДАЛЬНЫМ ОКНОМ СТАТИСТИКИ
// ============================================

let currentStatsView = null;
let isStatsModalOpen = false;

// Открыть модальное окно
function openStatsModal() {
    if (!philosophyMetrics) {
        initializePhilosophyMetrics();
    }
    
    // Синхронизируем состояния переключателей с глобальными переменными
    document.getElementById('statsUseWeightsToggle').checked = useWeightedPaths;
    document.getElementById('statsRespectDirectionToggle').checked = respectDirection;
    
    const modal = document.getElementById('statsModal');
    modal.classList.add('active');
    isStatsModalOpen = true;
    
    // Показываем обзор по умолчанию если ещё не было выбора
    if (!currentStatsView) {
        setTimeout(() => {
            const firstItem = document.querySelector('.stats-nav-item');
            if (firstItem) {
                firstItem.click();
            }
        }, 100);
    } else {
        // Восстанавливаем последний просмотр
        loadStatsContent(currentStatsView);
        updateActiveNavItem(currentStatsView);
    }
    
    console.log('📊 Модальное окно статистики открыто');
}

// Закрыть модальное окно
function closeStatsModal() {
    const modal = document.getElementById('statsModal');
    modal.classList.remove('active');
    isStatsModalOpen = false;
    console.log('📊 Модальное окно статистики закрыто');
}

// Обработка изменения параметров (веса, направленность)
function handleStatsParameterChange() {
    const newWeights = document.getElementById('statsUseWeightsToggle').checked;
    const newDirection = document.getElementById('statsRespectDirectionToggle').checked;
    
    // Обновляем глобальные переменные
    useWeightedPaths = newWeights;
    respectDirection = newDirection;
    
    // Обновляем основные переключатели в легенде (если есть)
    const mainWeightsToggle = document.getElementById('useWeightsToggle');
    const mainDirectionToggle = document.getElementById('respectDirectionToggle');
    if (mainWeightsToggle) mainWeightsToggle.checked = newWeights;
    if (mainDirectionToggle) mainDirectionToggle.checked = newDirection;
    
    // Сбрасываем кэш графа
    invalidateGraphCache();
    
    // Если визуализация активна, сбрасываем её
    if (window.isVisualizingBySize) {
        resetNodeSizes();
    }
    
    console.log('⚙️ Параметры изменены: веса =', newWeights, ', направленность =', newDirection);
    
    // Перезагружаем текущий контент с новыми параметрами
    if (currentStatsView) {
        loadStatsContent(currentStatsView);
    }
}

// Переключение между видами статистики
function switchStatsView(viewName, event) {
    if (event && event.target) {
        // Обновляем активный пункт навигации
        document.querySelectorAll('.stats-nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        let targetItem = event.target;
        while (targetItem && !targetItem.classList.contains('stats-nav-item')) {
            targetItem = targetItem.parentElement;
        }
        if (targetItem) {
            targetItem.classList.add('active');
        }
    }
    
    currentStatsView = viewName;
    loadStatsContent(viewName);
    
    console.log('📊 Переключение на метрику:', viewName);
}

// Обновить активный пункт навигации
function updateActiveNavItem(viewName) {
    document.querySelectorAll('.stats-nav-item').forEach(item => {
        item.classList.remove('active');
        const onclick = item.getAttribute('onclick');
        if (onclick && onclick.includes(`'${viewName}'`)) {
            item.classList.add('active');
        }
    });
}

// Загрузка контента для выбранной метрики
function loadStatsContent(viewName) {
    const contentArea = document.getElementById('statsContentArea');
    let html = '';
    
    // Определяем функцию генератора для каждой метрики
    const generators = {
        'overview': generateOverviewContent,
        'degree': generateDegreeContent,
        'pagerank': generatePageRankContent,
        'betweenness': generateBetweennessContent,
        'closeness': generateClosenessContent,
        'eigenvector': generateEigenvectorContent,
        'weighted-clustering': generateWeightedClusteringContent,
        'local-cohesion': generateLocalCohesionContent,
        'rich-club': generateRichClubContent,
        'problem-generation': generateProblemGenerationContent,
        'critical-power': generateCriticalPowerContent,
        'revolutionary': generateRevolutionaryContent,
        'paradigm-shift': generateParadigmShiftContent,
        'influence': generateInfluenceContent,
        'foundational': generateFoundationalContent,
        'synthetic': generateSyntheticContent,
        'dialogical': generateDialogicalContent,
        'coherence': generateCoherenceContent,
        'tension': generateTensionContent,
        'transformation': generateTransformationContent,
        'fertility': generateFertilityContent,
        'complexity': generateComplexityContent,
        'continuity': generateContinuityContent,
        'temporal-influence': generateTemporalInfluenceContent,
        'philosopher-profile': generatePhilosopherProfileContent,
        'philosopher-systematic': generatePhilosopherSystematicContent,
        'philosopher-reach': generatePhilosopherReachContent,
        'philosopher-interdisciplinary': generatePhilosopherInterdisciplinaryContent,
        'concept-rankings': generateConceptRankingsContent,
        'philosopher-rankings': generatePhilosopherRankingsContent
    };
    
    const generator = generators[viewName];
    if (generator) {
        html = generator();
    } else {
        html = `
            <div class="empty-state">
                <div class="empty-state-icon">🚧</div>
                <div class="empty-state-text">Метрика в разработке</div>
                <div class="empty-state-hint">Эта метрика будет добавлена в следующей версии</div>
            </div>
        `;
    }
    
    contentArea.innerHTML = html;
    contentArea.scrollTop = 0; // Скроллим наверх при смене контента
}

// Закрытие модального окна при клике вне его
document.addEventListener('click', function(event) {
    if (!isStatsModalOpen) return;
    const modal = document.getElementById('statsModal');
    if (event.target === modal) {
        closeStatsModal();
    }
});

// Закрытие модального окна по Escape
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape' && isStatsModalOpen) {
        closeStatsModal();
    }
});

// Расчёт метрики из модального окна
async function calculateMetricFromModal(metricKey) {
    try {
        closeStatsModal();
        
        // Используем существующие функции расчёта
        await runSingleMetric(metricKey);
        
        // Открываем модальное окно снова и показываем результат
        setTimeout(() => {
            openStatsModal();
            const navItems = document.querySelectorAll('.stats-nav-item');
            navItems.forEach(item => {
                const onclick = item.getAttribute('onclick');
                if (onclick && onclick.includes(`'${metricKey}'`)) {
                    item.click();
                }
            });
        }, 1000);
    } catch (error) {
        console.error('❌ Ошибка при расчёте метрики:', error);
        alert('Произошла ошибка при расчёте метрики');
        openStatsModal(); // Возвращаемся в модальное окно
    }
}
```

---

*Продолжение следует в третьей части (генераторы контента и визуализация)...*
