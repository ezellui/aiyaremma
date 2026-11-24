// ПОЛНЫЙ СПИСОК ВСЕХ 124 УЛУЧШЕННЫХ ОПИСАНИЙ СВЯЗЕЙ
// Каждое описание переработано для раскрытия философского плана связи

const allImprovedRelations = [
    
    // ПИФАГОР
    { source: "number_essence", target: "harmony_spheres", type: "presuppose", weight: 3, 
      description: "Числовая структура космоса делает возможной гармонию сфер: интервалы планетных орбит подчиняются тем же пропорциям, что и музыкальные консонансы" },
    
    { source: "metempsychosis", target: "harmony_spheres", type: "influence", weight: 1, 
      description: "Переселение душ подчинено космической гармонии: душа странствует по сферам, очищаясь через музыкально-числовой порядок до возвращения к единому" },
    
    // АРИСТОТЕЛЬ
    { source: "act_potency", target: "entelechy", type: "presuppose", weight: 3, 
      description: "Энтелехия как чистый акт без потенции: завершенность, где форма полностью реализована и ничто не остается в возможности" },
    
    { source: "logos", target: "categories", type: "consequence", weight: 2, 
      description: "Логос структурирует категории: способы, которыми разум предицирует бытие - субстанция, качество, количество как грамматика сущего" },
    
    { source: "logos", target: "unmoved_mover", type: "consequence", weight: 2, 
      description: "Логос космоса тождествен перводвигателю: чистое мышление, мыслящее само себя, движет через любовь, будучи объектом желания" },
    
    { source: "matter_ar", target: "four_causes", type: "consequence", weight: 3, 
      description: "Материя дает материальную причину, но сама по себе неопределенна: из чего вещь, но не что она есть - потенциальность, требующая формы" },
    
    // ПЛОТИН
    { source: "nous", target: "world_soul", type: "consequence", weight: 2, 
      description: "Душа эманирует из Ума как его образ, обращенный к материи: опосредует между умопостигаемым и чувственным, оживляя космос" },
    
    { source: "contemplation", target: "nous", type: "consequence", weight: 2, 
      description: "Созерцание реализует Ум как мышление идей: не дискурсивное познание, а интуитивное схватывание всех эйдосов в едином акте" },
    
    { source: "the_one", target: "nous", type: "emerge_from", weight: 3, 
      description: "Единое переполняется собственной полнотой и рождает Ум: первое самоотличие, первый взгляд абсолюта на себя как на другое" },
    
    // БЭКОН
    { source: "idols", target: "idols_marketplace", type: "exemplify", weight: 2, 
      description: "Идолы площади - тирания языка: слова, рожденные в толпе, подменяют вещи фантомами и заставляют разум спорить о несуществующем" },
    
    // ДЕКАРТ
    { source: "cogito", target: "dualism", type: "emerge_from", weight: 3, 
      description: "Cogito обнаруживает метафизическую пропасть: мышление дано с аподиктической достоверностью, тело остается под сомнением - две субстанции без общей меры" },
    
    { source: "cogito", target: "clear_distinct", type: "exemplify", weight: 2, 
      description: "Cogito - первая ясная и отчетливая идея: само сомнение в мышлении с очевидностью доказывает существование мыслящего, это парадигма достоверности" },
    
    { source: "cogito", target: "infinite_idea", type: "consequence", weight: 2, 
      description: "Конечность cogito требует врожденной идеи бесконечного: конечное существо не может создать из себя идею, превосходящую его - след Бога в уме" },
    
    // КАНТ
    { source: "transcendental", target: "apriori", type: "condition", weight: 3, 
      description: "Трансцендентальное исследование вопрошает об условиях возможности: не что мы познаем априори, но как вообще возможно доопытное познание" },
    
    { source: "categorical", target: "phenomenon", type: "influence", weight: 2, 
      description: "Категорический императив действует в феноменальном мире через ноуменальную свободу: причинность из свободы не нарушает естественной каузальности, а сосуществует с ней" },
    
    { source: "aesthetic_judgment", target: "phenomenon", type: "consequence", weight: 2, 
      description: "Эстетическое суждение схватывает феномены не как объекты познания, а как символы сверхчувственного: целесообразность без цели указывает за пределы опыта" },
    
    // ФИХТЕ
    { source: "practical_primacy", target: "tathandlung", type: "consequence", weight: 3, 
      description: "Примат практики укоренен в дело-действии: бытие не предшествует деятельности, но само есть акт самополагания Я" },
    
    { source: "imagination", target: "non_ego", type: "mediate", weight: 3, 
      description: "Продуктивное воображение полагает не-Я как границу: творит препятствие, необходимое для бесконечного стремления Я к самореализации" },
    
    { source: "wissenschaftslehre", target: "absolute_ego", type: "presuppose", weight: 3, 
      description: "Наукоучение начинается с абсолютного Я как первого основоположения: не эмпирическое Я, но трансцендентальное условие всякого сознания и бытия" },
    
    { source: "striving", target: "absolute_ego", type: "consequence", weight: 3, 
      description: "Стремление конституирует природу Я: не состояние, но бесконечная деятельность самоопределения против ограничения" },
    
    { source: "imagination", target: "striving", type: "consequence", weight: 2, 
      description: "Воображение направляет бесконечное стремление Я: создает образы целей, делая абстрактную деятельность конкретным проектом" },
    
    // ШЕЛЛИНГ
    { source: "absolute_identity", target: "transcendental_idealism_system", type: "presuppose", weight: 3, 
      description: "Абсолютное тождество субъекта и объекта требует систематического развертывания: единство природы и духа раскрывается через потенции" },
    
    // ГЕГЕЛЬ
    { source: "dialectic", target: "absolute_idea", type: "instrument", weight: 3, 
      description: "Диалектика - метод самодвижения идеи: через отрицание и снятие противоречия идея познает себя, достигая абсолютного самопознания" },
    
    { source: "abstract", target: "aufhebung", type: "limit", weight: 2, 
      description: "Абстрактное преодолевается снятием: односторонность первого определения требует перехода в противоположность и синтеза в конкретном" },
    
    { source: "concrete", target: "absolute_idea", type: "culminate", weight: 3, 
      description: "Конкретное - полнота идеи: тотальность всех опосредованных определений, где различия сохранены в единстве" },
    
    { source: "concrete", target: "dialectic", type: "consequence", weight: 3, 
      description: "Конкретное как результат диалектического процесса: единство многообразного через опосредование, богатство определений в целостности" },
    
    { source: "absolute_idea", target: "dialectic", type: "culminate", weight: 3, 
      description: "Абсолютная идея - завершение диалектики: самопознание духа достигнуто, круг замкнут, метод и содержание совпадают" },
    
    // ШОПЕНГАУЭР
    { source: "denial_will", target: "suffering", type: "complement", weight: 2, 
      description: "Отрицание воли - единственный выход из страдания: аскетическое умерщвление желаний ведет к состоянию безволия, где прекращается круговорот страсти" },
    
    { source: "individuation", target: "representation", type: "condition", weight: 2, 
      description: "Principium individuationis создает мир представления: пространство и время разделяют единую волю на множество феноменов, порождая иллюзию отдельных вещей" },
    
    // КОНТ
    { source: "positive_knowledge", target: "sociology", type: "apply", weight: 2, 
      description: "Позитивное знание создает социологию как науку: наблюдение социальных фактов и законов без метафизических спекуляций о сущностях" },
    
    { source: "hierarchy_sciences", target: "positive_knowledge", type: "consequence", weight: 2, 
      description: "Иерархия наук реализует позитивистский идеал: от простого к сложному, от математики к социологии, где каждая наука основана на предыдущей" },
    
    { source: "hierarchy_sciences", target: "sociology", type: "culminate", weight: 2, 
      description: "Социология венчает иерархию как наиболее сложная позитивная наука: изучает системы максимальной интеграции, использует все низшие науки" },
    
    // КЬЕРКЕГОР
    { source: "stages_existence", target: "leap_faith", type: "culminate", weight: 2, 
      description: "Три стадии (эстетическая, этическая, религиозная) ведут к прыжку веры: каждая превосходит предыдущую через качественный скачок, не логический переход" },
    
    { source: "repetition", target: "stages_existence", type: "mediate", weight: 2, 
      description: "Повторение связывает стадии экзистенции: не возврат к тому же, но возвращение к себе на новом уровне через веру" },
    
    { source: "absurd", target: "leap_faith", type: "consequence", weight: 2, 
      description: "Абсурд христианства требует прыжка веры: credo quia absurdum - верю потому что абсурдно, разум не может обосновать веру" },
    
    { source: "stages_existence", target: "anxiety", type: "presuppose", weight: 2, 
      description: "Экзистенциальные стадии пронизаны тревогой: головокружение свободы перед бездной возможностей, основание для выбора" },
    
    { source: "moment", target: "stages_existence", type: "consequence", weight: 2, 
      description: "Мгновение как атом вечности определяет переход между стадиями: время и вечность соприкасаются в экзистенциальном решении" },
    
    { source: "stages_existence", target: "despair", type: "presuppose", weight: 2, 
      description: "Стадии структурированы отчаянием как болезнью к смерти: отчаяние не хотеть быть собой или отчаяние хотеть быть собой" },
    
    // МАРКС
    { source: "base_superstructure", target: "class_struggle", type: "condition", weight: 3, 
      description: "Экономический базис детерминирует классовую борьбу: отношения производства определяют противоречие между трудом и капиталом" },
    
    { source: "ideology", target: "base_superstructure", type: "consequence", weight: 3, 
      description: "Идеология как элемент надстройки одновременно отражает и мистифицирует базис: ложное сознание маскирует реальность эксплуатации" },
    
    // ДИЛЬТЕЙ
    { source: "leben_dilthey", target: "erlebnis", type: "presuppose", weight: 3, 
      description: "Жизнь как первичная реальность дана в непосредственном переживании: не конструируется рассудком, но изначально самодостоверна во внутреннем опыте" },
    
    { source: "hermeneutics_life", target: "leben_dilthey", type: "presuppose", weight: 3, 
      description: "Герменевтика жизни исходит из жизни как текста: историческая жизнь объективируется в культурных формах, требующих интерпретации" },
    
    { source: "historical_reason", target: "geisteswissenschaften", type: "condition", weight: 2, 
      description: "Критика исторического разума обосновывает науки о духе: как возможно познание исторической реальности без редукции к природе" },
    
    { source: "objective_spirit_dilthey", target: "leben_dilthey", type: "consequence", weight: 2, 
      description: "Объективный дух - кристаллизация исторической жизни в устойчивых формах: язык, искусство, институты как отчужденные смыслы" },
    
    { source: "erlebnis", target: "historical_reason", type: "condition", weight: 2, 
      description: "Переживание обосновывает исторический разум: внутренний опыт времени и становления делает возможным понимание истории" },
    
    // БРЕНТАНО
    { source: "immanent_objectivity", target: "intentionality_brentano", type: "exemplify", weight: 2, 
      description: "Имманентная объективность раскрывает парадокс интенциональности: объект существует в акте сознания, не как реальная вещь, но как интенциональное содержание" },
    
    // НИЦШЕ
    { source: "will_power", target: "ubermensch", type: "culminate", weight: 3, 
      description: "Воля к власти достигает высшей формы в сверхчеловеке: не господство над другими, но самопреодоление, творение новых ценностей" },
    
    { source: "god_dead", target: "ubermensch", type: "consequence", weight: 3, 
      description: "Смерть Бога освобождает место для сверхчеловека: крушение трансцендентных ценностей требует переоценки всех ценностей, человек становится творцом смысла" },
    
    { source: "perspectivism", target: "god_dead", type: "emerge_from", weight: 3, 
      description: "Перспективизм вырастает из смерти Бога: без абсолютной точки зрения истина становится множественной - нет фактов, только интерпретации" },
    
    { source: "master_morality", target: "will_power", type: "exemplify", weight: 3, 
      description: "Мораль господ воплощает активную волю к власти: творение ценностей из избытка силы, утверждение жизни, а не реакция на угнетение" },
    
    { source: "master_morality", target: "ubermensch", type: "consequence", weight: 3, 
      description: "Мораль господ рождает сверхчеловека как творца ценностей: законодательствующий тип, полагающий благо из собственной мощи" },
    
    { source: "dionysian", target: "will_power", type: "presuppose", weight: 3, 
      description: "Дионисийское начало - витальная мощь воли к власти: опьянение как растворение индивидуации, экстатическое слияние с первосилой жизни" },
    
    { source: "apollonian", target: "will_power", type: "presuppose", weight: 2, 
      description: "Аполлоническое начало - воля к форме и мере: индивидуация через прекрасную иллюзию, светлый сон против хаоса становления" },
    
    { source: "ressentiment", target: "will_power", type: "oppose", weight: 3, 
      description: "Ресентимент как антитеза воли к власти: бессильная месть, творящая через отрицание, яд памяти о нанесенной обиде" },
    
    // МЕЙНОНГ
    { source: "sosein", target: "object_theory", type: "presuppose", weight: 3, 
      description: "Принцип независимости так-бытия от бытия: объект имеет свойства независимо от существования, золотая гора золота даже если её нет" },
    
    // ФРЕЙД
    { source: "dream_work", target: "unconscious", type: "exemplify", weight: 3, 
      description: "Сновидение - царская дорога к бессознательному: работа сна через сгущение и смещение открывает доступ к вытесненному желанию" },
    
    { source: "id_ego_superego", target: "unconscious", type: "presuppose", weight: 3, 
      description: "Структурная топика психики требует бессознательного: Оно как резервуар влечений, недоступных сознанию, основа психического аппарата" },
    
    { source: "id_ego_superego", target: "reality_principle", type: "consequence", weight: 2, 
      description: "Я опосредует Оно и реальность: между слепым влечением и внешним миром, откладывает удовлетворение ради адаптации" },
    
    { source: "repression", target: "oedipus_complex", type: "condition", weight: 2, 
      description: "Вытеснение Эдипова комплекса - структурообразующая репрессия: запрет инцеста формирует бессознательное и символический порядок культуры" },
    
    // ФРЕГЕ
    { source: "context_principle", target: "sense_reference", type: "condition", weight: 3, 
      description: "Контекстный принцип обосновывает различие смысла и значения: только в контексте предложения слово обретает смысл и референцию к объекту" },
    
    // ДЬЮИ
    { source: "learning_doing", target: "inquiry", type: "instrument", weight: 2, 
      description: "Обучение через делание как метод исследования: не пассивное усвоение, но активное экспериментирование, где знание рождается в практике" },
    
    // БЕРГСОН
    { source: "creative_evolution", target: "elan_vital", type: "presuppose", weight: 3, 
      description: "Творческая эволюция движима élan vital как витальным импульсом: не механическое развертывание, но непредсказуемое творчество новых форм" },
    
    { source: "matter_memory", target: "duree", type: "presuppose", weight: 2, 
      description: "Материя и память укоренены в длительности: прошлое не исчезает, но сохраняется в памяти, сосуществуя с настоящим в потоке времени" },
    
    { source: "pure_perception", target: "matter_memory", type: "presuppose", weight: 2, 
      description: "Чистое восприятие материи требует памяти: актуальное схватывание материи невозможно без виртуального прошлого, формирующего образ" },
    
    { source: "image_bergson", target: "pure_perception", type: "consequence", weight: 2, 
      description: "Образ как продукт чистого восприятия занимает промежуточное положение: между объективной вещью и субъективным представлением" },
    
    { source: "open_closed_morality", target: "creative_evolution", type: "consequence", weight: 2, 
      description: "Мораль - этап творческой эволюции: от закрытой морали социального инстинкта к открытой морали мистической интуиции" },
    
    { source: "laughter", target: "intellect_spatialization", type: "influence", weight: 1, 
      description: "Смех наказывает механическое в живом: интеллект застывает длительность в пространственных формах, комическое восстает против этого окостенения" },
    
    { source: "laughter", target: "elan_vital", type: "consequence", weight: 1, 
      description: "Смех - защитная реакция élan vital: жизненный порыв через комическое отвергает автоматизм и механизацию, восстанавливая гибкость творчества" },
    
    { source: "intuition_bergson", target: "image_bergson", type: "instrument", weight: 2, 
      description: "Интуиция постигает длительность через образы: не концептуальное мышление, но симпатическое вчувствование в промежуточную реальность становления" },
    
    // ГУССЕРЛЬ
    { source: "noesis_noema", target: "eidetic", type: "consequence", weight: 2, 
      description: "Структура ноэсис-ноэма раскрывается через эйдетический анализ: интенциональный акт и его предметное содержание в их сущностной корреляции" },
    
    { source: "intersubjectivity", target: "lifeworld", type: "condition", weight: 2, 
      description: "Интерсубъективность конституирует жизненный мир как общее поле: дорефлективный опыт возможен только в горизонте интерсубъективной очевидности" },
    
    // РАССЕЛ
    { source: "russell_paradox", target: "logical_atomism", type: "consequence", weight: 2, 
      description: "Парадокс множества всех множеств ведет к логическому атомизму: необходима теория типов, ограничивающая допустимые образования" },
    
    // ХАЙДЕГГЕР
    { source: "dasein", target: "sein", type: "condition", weight: 3, 
      description: "Dasein - место вопроса о бытии: единственное сущее, способное спрашивать о смысле бытия, экстатически открытое бытию" },
    
    { source: "geworfenheit", target: "sorge", type: "presuppose", weight: 2, 
      description: "Заброшенность - экзистенциал заботы: Dasein всегда уже находится в мире, не выбирая своей фактичности, это априорная ситуативность" },
    
    { source: "dasein", target: "geworfenheit", type: "presuppose", weight: 2, 
      description: "Dasein конституировано заброшенностью: не выбирает своё 'вот' (Da), но всегда уже брошено в определенную ситуацию и язык" },
    
    { source: "aletheia", target: "sein", type: "presuppose", weight: 2, 
      description: "Истина как несокрытость (алетейя) принадлежит бытию: не соответствие, но раскрытие-сокрытие, событие обнажения сущего" },
    
    { source: "dwelling", target: "dasein", type: "consequence", weight: 2, 
      description: "Пребывание - аутентичный способ бытия Dasein: не просто нахождение в месте, но собирающее обитание в близости к вещам и миру" },
    
    { source: "das_man", target: "dasein", type: "limit", weight: 2, 
      description: "Das Man блокирует собственное Dasein: усредненность публичности растворяет экзистенцию в анонимном 'они', бегство от себя" },
    
    { source: "das_man", target: "geworfenheit", type: "influence", weight: 2, 
      description: "Das Man определяет модус заброшенности: публичность интерпретирует фактичность, навязывая готовые смыслы, бегство от ужаса" },
    
    { source: "das_man", target: "sein_zum_tode", type: "limit", weight: 2, 
      description: "Das Man уклоняется от бытия-к-смерти: 'умирают, но не я' - публичность нейтрализует смерть как безличное событие" },
    
    { source: "ereignis", target: "sein", type: "presuppose", weight: 2, 
      description: "Событие (Ereignis) требует бытия как со-бытия: человек и бытие взаимно присваивают друг друга в событии истины" },
    
    { source: "ereignis", target: "aletheia", type: "consequence", weight: 3, 
      description: "Событие свершает истину как несокрытость: раскрытие-сокрытие бытия в просвете, временение истины как события" },
    
    { source: "geviert", target: "dwelling", type: "condition", weight: 2, 
      description: "Четверица (небо, земля, божества, смертные) необходима для пребывания: подлинное жилище собирает четверицу в единство мира" },
    
    { source: "geviert", target: "dasein", type: "consequence", weight: 2, 
      description: "Четверица определяет топологию Dasein: человек как смертный собирает в себе игру четырех, место встречи бытия" },
    
    { source: "kehre", target: "sein", type: "internal_contradiction", weight: 2, 
      description: "Поворот (Kehre) - внутреннее противоречие в мышлении бытия: от аналитики Dasein к истории бытия, от сущего к бытию самому" },
    
    { source: "vorhanden", target: "zuhanden", type: "oppose", weight: 3, bidirectional: true, 
      description: "Наличное (Vorhanden) как теоретический объект противостоит подручному (Zuhanden) как практическому орудию: разрыв в способах данности сущего" },
    
    { source: "dasein", target: "zuhanden", type: "consequence", weight: 3, 
      description: "Dasein первично имеет дело с подручным: вещи открываются в практическом обращении, а не в незаинтересованном созерцании" },
    
    { source: "sorge", target: "zuhanden", type: "consequence", weight: 2, 
      description: "Забота реализуется в обращении с подручным: озабоченность вещами мира как модус заботы о бытии" },
    
    { source: "das_man", target: "sorge", type: "oppose", weight: 2, 
      description: "Das Man блокирует подлинную заботу: публичность растворяет экзистенциальную ответственность в усредненности, бегство от тревоги" },
    
    { source: "ereignis", target: "dasein", type: "consequence", weight: 3, 
      description: "Событие определяет Dasein: человек не субъект, но тот, кто присвоен бытию, принадлежит событию раскрытия" },
    
    { source: "geviert", target: "ereignis", type: "consequence", weight: 2, 
      description: "Четверица вырастает из события бытия: структура мира как игра зеркал, где каждое отражает остальные в просвете" },
    
    { source: "being_in_world", target: "geworfenheit", type: "presuppose", weight: 2, 
      description: "Бытие-в-мире всегда уже заброшено: не выбираем своего вхождения в мир, априорная фактичность как условие экзистенции" },
    
    { source: "being_in_world", target: "sein", type: "condition", weight: 3, 
      description: "Бытие-в-мире открывает доступ к бытию: экстатическая открытость Dasein есть просвет, где бытие является" },
    
    // ВИТГЕНШТЕЙН
    { source: "showing_saying", target: "limits_language", type: "condition", weight: 3, 
      description: "Различие показывания и говорения определяет границы языка: логическая форма показывается в структуре предложения, но не может быть высказана" },
    
    { source: "private_language", target: "language_game", type: "consequence", weight: 3, 
      description: "Невозможность приватного языка следует из социальной природы языковых игр: значение требует публичного критерия правильности" },
    
    { source: "form_of_life", target: "rule_following", type: "consequence", weight: 3, 
      description: "Форма жизни обосновывает следование правилу: не интерпретация правила, но укорененная в практике уверенность, 'скала' действования" },
    
    // ГАДАМЕР
    { source: "effective_history", target: "tradition_gadamer", type: "presuppose", weight: 3, 
      description: "История воздействий разворачивается в традиции: мы всегда уже находимся в истории, которая действует на нас и формирует понимание" },
    
    { source: "prejudice_gadamer", target: "tradition_gadamer", type: "consequence", weight: 2, 
      description: "Пред-рассудки вырастают из традиции как продуктивные условия: не препятствия, но предварительные суждения, открывающие горизонт понимания" },
    
    { source: "prejudice_gadamer", target: "horizon_understanding", type: "condition", weight: 2, 
      description: "Пред-рассудки конституируют горизонт понимания: исторически обусловленное предпонимание необходимо для всякой интерпретации" },
    
    // ЛАКАН
    { source: "big_other", target: "three_registers", type: "presuppose", weight: 3, 
      description: "Большой Другой укоренен в Символическом регистре: порядок языка и закона, структурирующий субъективность до субъекта" },
    
    { source: "desire_other", target: "objet_petit_a", type: "presuppose", weight: 3, 
      description: "Желание Другого кристаллизуется в объекте а: желание быть желанным находит причину в недостижимом объекте, остатке Реального" },
    
    { source: "lack", target: "desire_other", type: "condition", weight: 3, 
      description: "Нехватка порождает желание Другого: субъект конституирован утратой, ищет восполнения в признании Другого" },
    
    { source: "signifier", target: "big_other", type: "presuppose", weight: 2, 
      description: "Означающее принадлежит Большому Другому: язык предшествует субъекту, определяя место в символическом порядке" },
    
    { source: "mirror_stage", target: "lack", type: "emerge_from", weight: 2, 
      description: "Стадия зеркала порождает нехватку: расщепление между воображаемым образом целостности и реальной фрагментацией тела" },
    
    { source: "three_registers", target: "lack", type: "consequence", weight: 3, 
      description: "Три регистра структурируют нехватку: Реальное как травматическая невозможность, дыра в Символическом, вокруг которой организуется желание" },
    
    { source: "objet_petit_a", target: "lack", type: "consequence", weight: 3, 
      description: "Объект а как причина желания кристаллизует нехватку: частичный объект, остаток от операции означивания, поддерживает фантазм" },
    
    { source: "signifier", target: "desire_other", type: "consequence", weight: 3, 
      description: "Означающее производит желание: субъект представлен означающим для другого означающего, расщепление рождает нехватку и желание" },
    
    // САРТР
    { source: "for_itself", target: "nothingness", type: "presuppose", weight: 3, 
      description: "Для-себя необходимо требует ничто: сознание есть негация в-себе, дистанция от полноты бытия, просвет небытия в бытии" },
    
    { source: "for_itself", target: "freedom_sartre", type: "consequence", weight: 2, 
      description: "Для-себя обречено на свободу: сознание не совпадает с собой, всегда впереди себя, эта несамотождественность и есть свобода" },
    
    { source: "in_itself", target: "existence", type: "consequence", weight: 2, 
      description: "В-себе есть полнота существования: массивная непрозрачная позитивность, совпадение с собой без трещины сознания" },
    
    { source: "project", target: "existence", type: "presuppose", weight: 3, 
      description: "Проект требует экзистенции: существование предшествует сущности, человек сначала есть, затем делает себя проектом" },
    
    { source: "project", target: "freedom_sartre", type: "presuppose", weight: 3, 
      description: "Проект невозможен без свободы: выбор себя в будущем, набросок возможностей, трансценденция наличной данности" },
    
    { source: "project", target: "for_itself", type: "consequence", weight: 3, 
      description: "Проект - способ бытия для-себя: сознание существует как трансценденция к возможностям, забегание вперед себя" },
    
    // ЛЕВИНАС
    { source: "ethics_first_philosophy", target: "other_levinas", type: "presuppose", weight: 3, 
      description: "Этика первичнее онтологии потому что Другой предшествует бытию: этическое отношение конституирует субъективность до всякого познания" },
    
    { source: "responsibility", target: "face", type: "consequence", weight: 3, 
      description: "Ответственность рождается из встречи с лицом: я становлюсь заложником Другого, чья уязвимость взывает до всякого выбора" },
    
    { source: "trace", target: "other_levinas", type: "exemplify", weight: 2, 
      description: "След - парадоксальный знак инаковости Другого: присутствие отсутствующего, метка трансцендентности, которая уже удалилась" },
    
    { source: "infinity_levinas", target: "other_levinas", type: "presuppose", weight: 3, 
      description: "Бесконечность присутствует в Другом: идея бесконечного переполняет конечное сознание, Другой как то, что превосходит всякое схватывание" },
    
    { source: "responsibility", target: "ethics_first_philosophy", type: "presuppose", weight: 3, 
      description: "Ответственность - основание этики как первой философии: я всегда уже ответственен до свободы, пассивность более пассивная чем пассивность" },
    
    // ФУКО
    { source: "discipline", target: "biopower", type: "emerge_from", weight: 2, 
      description: "Дисциплина эволюционирует в биовласть: от анатомо-политики индивидуальных тел к био-политике управления популяциями" },
    
    { source: "biopower", target: "episteme", type: "influence", weight: 2, 
      description: "Биовласть конституирует эпистему модерна: статистика, демография, медицина создают знание о популяции как объекте оптимизации жизни" },
    
    { source: "heterotopia", target: "episteme", type: "influence", weight: 2, 
      description: "Гетеротопии проблематизируют эпистему: аномальные пространства (больница, тюрьма, кладбище) обнажают условия возможности дискурса о норме" },
    
    { source: "problematization", target: "archaeology", type: "instrument", weight: 2, 
      description: "Проблематизация - метод археологии дискурса: не решение проблем, но исследование того, как нечто становится проблемой для мысли" },
    
    { source: "dispositif", target: "power_knowledge", type: "consequence", weight: 3, 
      description: "Диспозитив реализует комплекс власть-знание: гетерогенный ансамбль дискурсов, институций, практик, материализующих отношения силы" },
    
    { source: "dispositif", target: "discipline", type: "consequence", weight: 3, 
      description: "Диспозитив осуществляет дисциплинарную власть: сеть отношений, где знание и власть взаимно производят друг друга" },
    
    { source: "dispositif", target: "panopticon", type: "exemplify", weight: 2, 
      description: "Паноптикум как образцовый диспозитив: архитектура, дискурс реформы, практики надзора в едином ансамбле власти-знания" },
    
    // ДЕЛЁЗ
    { source: "deterritorialization", target: "rhizome", type: "instrument", weight: 3, 
      description: "Детерриториализация действует через ризому: линии ускользания от территориальных кодов, бегство от стратификации" },
    
    { source: "event", target: "difference", type: "exemplify", weight: 2, 
      description: "Событие - чистое различие на поверхности: не субстанция, но становление, смысл как эффект без причины" },
    
    { source: "multiplicity", target: "rhizome", type: "consequence", weight: 3, 
      description: "Множественность ризоматична: n-мерности без центрального стержня, плато интенсивностей без начала и конца" },
    
    { source: "difference", target: "rhizome", type: "consequence", weight: 3, 
      description: "Различие само по себе ризоматично: против арборесцентной логики тождества, множественные линии ускользания" },
    
    // ЛЕЙБНИЦ - КАНТ
    { source: "sufficient_reason", target: "antinomies", type: "influence", weight: 1, 
      description: "Лейбницев принцип достаточного основания порождает кантовские антиномии: требование полного объяснения загоняет разум в космологические противоречия о начале мира и свободе" }
];

// Экспорт
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { allImprovedRelations };
}
