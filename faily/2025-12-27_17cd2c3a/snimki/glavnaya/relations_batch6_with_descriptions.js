const relations = [
    // МЕРЛО-ПОНТИ
    { 
        source: "wild_being", 
        target: "flesh", 
        type: "consequence", 
        weight: 2,
        description: "Дикое бытие следует из плоти: être sauvage - необработанное, дорефлексивное измерение chair. Wild being - плоть мира до культурных наслоений, первичная ткань бытия, из которой возникают субъект и объект."
    },
    { 
        source: "lived_body", 
        target: "flesh", 
        type: "consequence", 
        weight: 3,
        description: "Проживаемое тело следует из плоти: corps vécu - не объект, но chair как способ бытия-в-мире. Lived body - это плоть, которая чувствует и чувствуется, плоть конкретизируется в проживаемой телесности."
    },
    { 
        source: "reversibility", 
        target: "chiasm", 
        type: "presuppose", 
        weight: 3,
        description: "Обратимость предполагает хиазм: réversibilité - структура chiasme. Reversibility (касающееся-касаемое, видящее-видимое) требует хиазматического переплетения - обратимость возможна только в хиазме плоти."
    },
    { 
        source: "flesh", 
        target: "chiasm", 
        type: "presuppose", 
        weight: 3,
        description: "Плоть предполагает хиазм: chair структурирована как chiasme, переплетение. Flesh - не субстанция, but хиазматическое сплетение видимого и невидимого, касающегося и касаемого."
    },
    { 
        source: "perception_phenomenology", 
        target: "lived_body", 
        type: "presuppose", 
        weight: 3,
        description: "Феноменология восприятия предполагает проживаемое тело: восприятие - не ментальный акт, but телесное. Phenomenology of perception основана на corps vécu - тело не инструмент восприятия, но его субъект."
    },
    { 
        source: "chiasm", 
        target: "visible_invisible", 
        type: "presuppose", 
        weight: 2,
        description: "Хиазм предполагает видимое-невидимое: chiasme - переплетение visible et invisible. Видимое требует невидимого как своей изнанки - хиазм структурирует их взаимопроникновение."
    },
    { 
        source: "visible_invisible", 
        target: "reversibility", 
        type: "exemplify", 
        weight: 3,
        description: "Видимое-невидимое иллюстрирует обратимость: видимое оборачивается невидимым, невидимое - видимым. Visible/invisible - paradigm case réversibilité, каждое содержит другое как свою глубину."
    },

    // КУАЙН
    { 
        source: "indeterminacy_translation", 
        target: "inscrutability_reference", 
        type: "consequence", 
        weight: 3,
        description: "Неопределённость перевода влечёт непрозрачность референции: если перевод радикально неопределён, референция неоднозначна. Indeterminacy of translation показывает, что нет факта о том, к чему отсылают термины - inscrutability of reference неизбежна."
    },
    { 
        source: "web_belief", 
        target: "two_dogmas", 
        type: "consequence", 
        weight: 3,
        description: "Сеть убеждений следует из критики двух догм: отказ от аналитико-синтетического различия ведёт к холизму. Web of belief - следствие two dogmas critique: убеждения пересматриваются целостно, нет изолированных истин."
    },
    { 
        source: "inscrutability_reference", 
        target: "web_belief", 
        type: "influence", 
        weight: 2,
        description: "Непрозрачность референции влияет на сеть убеждений: если референция неопределённа, пересмотр убеждений более гибок. Inscrutability усиливает холизм web of belief - можно менять онтологию, сохраняя теорию."
    },
    { 
        source: "two_dogmas", 
        target: "naturalized_epistemology", 
        type: "presuppose", 
        weight: 3,
        description: "Критика двух догм предполагает натурализованную эпистемологию: отказ от априорного требует эмпирического изучения познания. Two dogmas critique открывает путь к naturalized epistemology - эпистемология становится частью естественной науки."
    },
    { 
        source: "naturalized_epistemology", 
        target: "web_belief", 
        type: "presuppose", 
        weight: 3,
        description: "Натурализованная эпистемология предполагает сеть убеждений: познание изучается как каузальный процесс формирования web. Naturalized epistemology исследует, как стимулы порождают сеть убеждений - холизм естественно объясняется психологически."
    },
    { 
        source: "ontological_commitment", 
        target: "inscrutability_reference", 
        type: "presuppose", 
        weight: 2,
        description: "Онтологические обязательства предполагают непрозрачность референции: 'to be is to be the value of a variable', но переменные референциально непрозрачны. Ontological commitment требует quantification, но inscrutability показывает, что нет факта о референции кванторов."
    },

    // ДЕЛЁЗ
    { 
        source: "virtual_actual", 
        target: "multiplicity", 
        type: "consequence", 
        weight: 2,
        description: "Виртуальное-актуальное влечёт множественность: virtuel - не возможное, but реальное непроявленное, актуализирующееся в multiplicités. Virtual/actual порождает множественности как способы актуализации виртуального - не единство, но многообразие."
    },
    { 
        source: "virtual_actual", 
        target: "event", 
        type: "consequence", 
        weight: 3,
        description: "Виртуальное-актуальное следует в событии: événement - актуализация виртуального. Event - не факт в актуальном, but виртуальное, воплощающееся - битва существует виртуально в актуальных ранениях."
    },
    { 
        source: "multiplicity", 
        target: "difference", 
        type: "consequence", 
        weight: 3,
        description: "Множественность влечёт различие: multiplicité - не собрание единиц, but внутренняя différence. Multiplicity порождает difference - множественное различается само с собой, различие имманентно множественности."
    },
    { 
        source: "multiplicity", 
        target: "rhizome", 
        type: "consequence", 
        weight: 3,
        description: "Множественность ведёт к ризоме: rhizome - модель множественности без центра и иерархии. Multiplicité реализуется в rhizome - горизонтальное распространение, множественные входы, отсутствие единого корня."
    },
    { 
        source: "difference", 
        target: "rhizome", 
        type: "consequence", 
        weight: 3,
        description: "Различие влечёт ризому: différence производит ризоматическое распространение. Difference генерирует rhizome - различие не между терминами, but производящий принцип, порождающий множественные связи."
    },
    { 
        source: "virtual_actual", 
        target: "difference", 
        type: "presuppose", 
        weight: 3,
        description: "Виртуальное-актуальное предполагает различие: различение virtuel/actuel требует différence как онтологического принципа. Virtual/actual - не оппозиция, but различие как продуктивность, виртуальное дифференцируется, актуализируясь."
    },
    { 
        source: "difference", 
        target: "body_without_organs", 
        type: "presuppose", 
        weight: 2,
        description: "Различие предполагает тело без органов: différence требует CsO как плана консистенции. Body without organs - не хаос, but план, где различие разворачивается без организации в органы - интенсивность до экстенсивности."
    },
    { 
        source: "fold", 
        target: "rhizome", 
        type: "presuppose", 
        weight: 2,
        description: "Складка предполагает ризому: pli - операция создания внутреннего без внешнего, rhizome - результат. Fold предполагает ризоматическую структуру - складки создают множественные внутренние без трансцендентного центра."
    },
    { 
        source: "fold", 
        target: "body_without_organs", 
        type: "apply", 
        weight: 2,
        description: "Складка применяется к телу без органов: pli организует CsO без органической организации. Fold - способ структурирования body without organs, складывание интенсивностей без создания органов."
    },
    { 
        source: "rhizome", 
        target: "assemblage", 
        type: "exemplify", 
        weight: 2,
        description: "Ризома иллюстрируется сборкой: agencement - конкретная форма rhizome. Assemblage показывает ризому в действии - гетерогенные элементы в горизонтальных связях без иерархии."
    },
    { 
        source: "fold", 
        target: "difference", 
        type: "exemplify", 
        weight: 2,
        description: "Складка иллюстрирует различие: pli - способ производства différence. Fold exemplifies difference - складывание создаёт различие, внутреннее отличается от себя через складку."
    },
    { 
        source: "event", 
        target: "difference", 
        type: "exemplify", 
        weight: 2,
        description: "Событие иллюстрирует различие: événement - différence как становление. Event показывает различие в действии - не различие между терминами, but само становление-иным."
    },
    { 
        source: "deterritorialization", 
        target: "rhizome", 
        type: "instrument", 
        weight: 3,
        description: "Детерриториализация - инструмент ризомы: déterritorialisation - движение, создающее rhizome. Deterritorialization производит ризому - бегство от организации, создание новых линий связи, освобождение потоков."
    },
    { 
        source: "desiring_machines", 
        target: "body_without_organs", 
        type: "culminate", 
        weight: 2,
        description: "Машины желания кульминируют в теле без органов: machines désirantes стремятся к CsO как пределу. Desiring machines производят интенсивности, достигая предела в body without organs - но CsO также опасен (полное тело смерти)."
    },

    // ФУКО
    { 
        source: "heterotopia", 
        target: "panopticon", 
        type: "oppose", 
        weight: 2, 
        bidirectional: true,
        description: "Гетеротопия и паноптикон противоположны: hétérotopies - контр-пространства, panopticon - тотальный контроль. Heterotopia (кладбище, театр, корабль) - пространства иного, panopticon - пространство абсолютной видимости, взаимоисключающие логики."
    },
    { 
        source: "care_self", 
        target: "discipline", 
        type: "oppose", 
        weight: 2,
        description: "Забота о себе противостоит дисциплине: souci de soi (античная) - свобода самопреобразования, discipline (современная) - принуждение к норме. Care of the self - этика свободы против дисциплинарной нормализации."
    },
    { 
        source: "dispositif", 
        target: "power_knowledge", 
        type: "consequence", 
        weight: 3,
        description: "Диспозитив следует из власти-знания: dispositif - конкретная конфигурация pouvoir-savoir. Apparatus воплощает power-knowledge - сеть гетерогенных элементов (институции, дискурсы, архитектура), производящая субъектов через знание-власть."
    },
    { 
        source: "dispositif", 
        target: "discipline", 
        type: "consequence", 
        weight: 3,
        description: "Диспозитив влечёт дисциплину: dispositif производит дисциплинарные эффекты. Apparatus (школа, казарма, больница) реализует discipline - нормализацию через наблюдение, экзамен, упражнение."
    },
    { 
        source: "panopticon", 
        target: "biopower", 
        type: "consequence", 
        weight: 3,
        description: "Паноптикон ведёт к биовласти: архитектура тотального наблюдения распространяется на население. Panopticon - диаграмма дисциплинарной власти, которая в XVIII-XIX вв. трансформируется в bio-pouvoir - управление жизнью популяций."
    },
    { 
        source: "problematization", 
        target: "care_self", 
        type: "consequence", 
        weight: 2,
        description: "Проблематизация следует из заботы о себе: problématisation - саморабота через вопрошание. Care of the self осуществляется через проблематизацию себя и истины - не следование норме, but критическое отношение."
    },
    { 
        source: "biopower", 
        target: "episteme", 
        type: "influence", 
        weight: 2,
        description: "Биовласть влияет на эпистему: bio-pouvoir порождает науки о населении (демография, статистика, евгеника). Biopower формирует episteme модерна - жизнь становится объектом знания и управления."
    },
    { 
        source: "heterotopia", 
        target: "episteme", 
        type: "influence", 
        weight: 2,
        description: "Гетеротопия влияет на эпистему: hétérotopies нарушают episteme, показывая её относительность. Heterotopia - пространства, где эпистема функционирует иначе, обнажая произвольность познавательных порядков."
    },
    { 
        source: "power_knowledge", 
        target: "episteme", 
        type: "presuppose", 
        weight: 3,
        description: "Власть-знание предполагает эпистему: pouvoir-savoir действует в рамках episteme. Power-knowledge требует эпистемы как исторического априори - порядка дискурса, делающего возможными определённые истины."
    },
    { 
        source: "dispositif", 
        target: "panopticon", 
        type: "exemplify", 
        weight: 2,
        description: "Диспозитив иллюстрируется паноптиконом: panopticon - парадигмальный apparatus. Panopticon exemplifies dispositif - архитектурное решение, производящее дисциплинарных субъектов через видимость."
    },
    { 
        source: "panopticon", 
        target: "discipline", 
        type: "exemplify", 
        weight: 3,
        description: "Паноптикон иллюстрирует дисциплину: Bentham's panopticon - модель discipline. Panopticon показывает дисциплину в чистом виде - интериоризация наблюдения, самоконтроль, нормализация через видимость."
    },
    { 
        source: "panopticon", 
        target: "power_knowledge", 
        type: "exemplify", 
        weight: 3,
        description: "Паноптикон иллюстрирует власть-знание: видение = знание = власть в архитектуре panopticon. Panopticon - конкретизация pouvoir-savoir, где знание о заключённых производит власть над ними."
    },
    { 
        source: "archaeology", 
        target: "episteme", 
        type: "instrument", 
        weight: 3,
        description: "Археология - инструмент анализа эпистемы: archéologie раскапывает исторические слои episteme. Archaeology - метод выявления эпистемологических разрывов, обнаружения правил формирования дискурса."
    },
    { 
        source: "power_knowledge", 
        target: "discipline", 
        type: "instrument", 
        weight: 3,
        description: "Власть-знание - инструмент дисциплины: pouvoir-savoir производит дисциплинарные эффекты. Power-knowledge осуществляет discipline - экзамен создаёт знание о индивиде и власть его нормализовать."
    },
    { 
        source: "problematization", 
        target: "archaeology", 
        type: "instrument", 
        weight: 2,
        description: "Проблематизация - инструмент археологии: problématisation - метод выявления того, как нечто становится проблемой. Problematization направляет archaeology - вопрос не 'что истинно', but 'как это стало истиной'."
    },
    { 
        source: "discipline", 
        target: "biopower", 
        type: "emerge_from", 
        weight: 2,
        description: "Биовласть возникает из дисциплины: bio-pouvoir - расширение discipline на популяцию. Biopower эмергирует, когда дисциплинарные техники (индивидуальное тело) дополняются регуляцией популяций (социальное тело)."
    },
    { 
        source: "heterotopia", 
        target: "power_knowledge", 
        type: "limit", 
        weight: 2,
        description: "Гетеротопия ограничивает власть-знание: hétérotopies - пространства, где pouvoir-savoir функционирует иначе. Heterotopia устанавливает предел power-knowledge - контр-места, ускользающие от тотализации знания-власти."
    },

    // ДЕРРИДА
    { 
        source: "logocentrism", 
        target: "deconstruction", 
        type: "oppose", 
        weight: 3, 
        bidirectional: true,
        description: "Логоцентризм и деконструкция радикально противоположны: logocentrisme - метафизика присутствия, déconstruction - её разборка. Logocentrism привилегирует речь/присутствие/логос, deconstruction показывает его зависимость от того, что он исключает (письмо/отсутствие)."
    },
    { 
        source: "trace_derrida", 
        target: "logocentrism", 
        type: "critique", 
        weight: 3,
        description: "След критикует логоцентризм: trace подрывает logocentrisme, показывая первичность отсутствия. Trace Деррида - не отпечаток присутствия, but структура отсылки без истока, критика метафизики присутствия."
    },
    { 
        source: "iterability", 
        target: "differance", 
        type: "presuppose", 
        weight: 2,
        description: "Итерабельность предполагает различание: itérabilité - повторимость с различием, требует différance. Iterability - структура знака как повторяемого, но различающегося, что возможно только через différance как отсрочку/различие."
    },
    { 
        source: "arche_writing", 
        target: "trace_derrida", 
        type: "presuppose", 
        weight: 3,
        description: "Архе-письмо предполагает след: archi-écriture - генерализованное письмо как структура trace. Arche-writing - не эмпирическое письмо, but условие возможности речи и письма, структурированное как след без оригинала."
    },
    { 
        source: "differance", 
        target: "trace_derrida", 
        type: "presuppose", 
        weight: 3,
        description: "Различание предполагает след: différance производит trace. Differance - движение, которое структурирует след, отсрочка/различие создаёт след как отсылку без присутствия."
    },
    { 
        source: "deconstruction", 
        target: "differance", 
        type: "apply", 
        weight: 3,
        description: "Деконструкция применяет различание: déconstruction использует différance для разборки бинарных оппозиций. Deconstruction - практика чтения, обнаруживающая differance в текстах, показывающая неразрешимость оппозиций."
    },
    { 
        source: "pharmakon", 
        target: "supplement", 
        type: "exemplify", 
        weight: 2,
        description: "Фармакон иллюстрирует дополнение: pharmakon (яд/лекарство) - случай supplément. Pharmakon показывает логику supplement - письмо у Платона одновременно яд и лекарство, дополнение подрывает то, что дополняет."
    },
    { 
        source: "supplement", 
        target: "differance", 
        type: "exemplify", 
        weight: 3,
        description: "Дополнение иллюстрирует различание: supplément - конкретизация différance. Supplement exemplifies differance - дополняющее замещает, восполняя нехватку, которую само создаёт, структура отсрочки и различия."
    },

    // РОРТИ
    { 
        source: "anti_representationalism", 
        target: "edifying_philosophy", 
        type: "presuppose", 
        weight: 3,
        description: "Антирепрезентационализм предполагает назидательную философию: отказ от теории познания-как-зеркала требует иной философии. Anti-representationalism открывает путь к edifying philosophy - философия не обосновывает, but расширяет беседу."
    },
    { 
        source: "ironism", 
        target: "contingency_rorty", 
        type: "presuppose", 
        weight: 3,
        description: "Иронизм предполагает контингентность: ironist признаёт случайность своего конечного словаря. Ironism основан на contingency - ирония возможна, только если нет необходимой истины, все описания контингентны."
    },
    { 
        source: "vocabularies", 
        target: "anti_representationalism", 
        type: "presuppose", 
        weight: 2,
        description: "Словари предполагают антирепрезентационализм: vocabularies - не репрезентации реальности, but инструменты. Final vocabularies основаны на anti-representationalism - слова не отображают, but используются для целей."
    },
    { 
        source: "contingency_rorty", 
        target: "vocabularies", 
        type: "presuppose", 
        weight: 3,
        description: "Контингентность предполагает словари: случайность языка, самости, сообщества требует vocabularies как исторических конструктов. Contingency делает возможными final vocabularies - нет природного языка, только исторически случайные словари."
    },
    { 
        source: "solidarity", 
        target: "contingency_rorty", 
        type: "presuppose", 
        weight: 2,
        description: "Солидарность предполагает контингентность: solidarity строится на признании общей случайности. Solidarity у Рорти - не открытие универсальной человечности, but создание 'мы' через признание contingency наших словарей."
    },
    { 
        source: "conversation_mankind", 
        target: "edifying_philosophy", 
        type: "exemplify", 
        weight: 3,
        description: "Беседа человечества иллюстрирует назидательную философию: философия как продолжение conversation, не поиск оснований. Conversation of mankind exemplifies edifying philosophy - философия поддерживает беседу, не завершает её в системе."
    },
];
