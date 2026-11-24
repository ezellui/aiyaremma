const relations = [
    // РАССЕЛ
    { 
        source: "russell_paradox", 
        target: "logical_atomism", 
        type: "consequence", 
        weight: 2,
        description: "Парадокс Рассела влечёт логический атомизм: обнаружение противоречия в наивной теории множеств требует новой логической основы. Russell's paradox мотивирует разложение сложных утверждений на атомарные факты - программу logical atomism."
    },
    { 
        source: "sense_data", 
        target: "external_world", 
        type: "consequence", 
        weight: 2,
        description: "Чувственные данные влекут проблему внешнего мира: если непосредственно даны только sense-data, существование external world требует вывода. Sense data - эпистемологическая база, из которой нужно реконструировать знание о внешнем мире."
    },
    { 
        source: "acquaintance_description", 
        target: "sense_data", 
        type: "presuppose", 
        weight: 3,
        description: "Знание-знакомство и знание-по-описанию предполагают чувственные данные: знакомство - непосредственное знание sense-data. Acquaintance with sense-data - фундамент, описания строятся на основе знакомства с чувственными данными."
    },
    { 
        source: "theory_descriptions", 
        target: "acquaintance_description", 
        type: "presuppose", 
        weight: 2,
        description: "Теория дескрипций предполагает различение знакомства и описания: определённые дескрипции отсылают к тому, с чем мы не знакомы. Theory of descriptions анализирует, как язык отсылает к объектам через acquaintance и description."
    },
    { 
        source: "logical_atomism", 
        target: "theory_descriptions", 
        type: "instrument", 
        weight: 3,
        description: "Логический атомизм использует теорию дескрипций как инструмент: анализ сложных предложений через определённые дескрипции. Theory of descriptions - техника разложения кажущихся простыми утверждений на логические атомы."
    },

    // КАССИРЕР
    { 
        source: "animal_symbolicum", 
        target: "symbolic_forms", 
        type: "consequence", 
        weight: 3,
        description: "Animal symbolicum следует из символических форм: человек определяется не как animal rationale, но как символическое животное. Symbolic forms (миф, язык, наука) конституируют человека - animal symbolicum живёт в символической вселенной."
    },
    { 
        source: "symbolic_pregnance", 
        target: "symbolic_forms", 
        type: "presuppose", 
        weight: 3,
        description: "Символическая преформация предполагает символические формы: восприятие изначально насыщено смыслом. Symbolic pregnance - феномен, где чувственное непосредственно несёт значение, делая возможными symbolic forms как способы смыслового структурирования."
    },
    { 
        source: "symbolic_forms", 
        target: "cultural_philosophy", 
        type: "presuppose", 
        weight: 3,
        description: "Символические формы предполагают философию культуры: культура - система символических форм. Cultural philosophy Кассирера основана на анализе symbolic forms (миф, религия, язык, искусство, наука) как объективаций духа."
    },
    { 
        source: "myth_cassirer", 
        target: "symbolic_forms", 
        type: "exemplify", 
        weight: 3,
        description: "Миф иллюстрирует символические формы: мифическое мышление - автономная символическая форма со своей логикой. Myth Кассирера - не примитивная наука, но полноценная symbolic form с особым способом символизации (конкретное тождество)."
    },
    { 
        source: "functional_concept", 
        target: "symbolic_forms", 
        type: "instrument", 
        weight: 2,
        description: "Функциональное понятие - инструмент анализа символических форм: форма важнее субстанции, отношение важнее вещи. Functional concept позволяет понять symbolic forms как системы отношений, а не собрания объектов."
    },
    { 
        source: "cultural_philosophy", 
        target: "animal_symbolicum", 
        type: "culminate", 
        weight: 2,
        description: "Философия культуры кульминирует в animal symbolicum: анализ символических форм приводит к новому определению человека. Cultural philosophy завершается антропологией - человек как символическое животное, создающее культуру."
    },

    // ВИТГЕНШТЕЙН
    { 
        source: "private_language", 
        target: "language_game", 
        type: "consequence", 
        weight: 3,
        description: "Аргумент против приватного языка следует из языковых игр: язык существенно публичен, правила требуют сообщества. Private language argument показывает, что language games невозможны в изоляции - значение требует коллективной практики."
    },
    { 
        source: "logical_space", 
        target: "showing_saying", 
        type: "consequence", 
        weight: 2,
        description: "Логическое пространство влечёт различение показывания и говорения: структура logical space может только показываться, не говориться. Границы выразимости определяются логическим пространством - форма отображения показывается в предложениях."
    },
    { 
        source: "rule_following", 
        target: "family_resemblance", 
        type: "consequence", 
        weight: 3,
        description: "Следование правилу влечёт семейное сходство: правила не фиксируют сущность, но указывают на семейство применений. Rule-following показывает, что понятия связаны family resemblance, а не общей чертой - нет единого правила для всех употреблений."
    },
    { 
        source: "picture_theory", 
        target: "showing_saying", 
        type: "consequence", 
        weight: 3,
        description: "Теория изображения влечёт показывание-говорение: предложение изображает факт, но логическая форма изображения только показывается. Picture theory ведёт к различению - предложение говорит, что есть случай, но показывает, как оно изображает."
    },
    { 
        source: "form_of_life", 
        target: "rule_following", 
        type: "consequence", 
        weight: 3,
        description: "Форма жизни влечёт следование правилу: правила укоренены в Lebensform, коллективной практике. Form of life делает возможным rule-following - правила действуют на фоне разделяемых форм жизни, не обосновываемых далее."
    },
    { 
        source: "limits_language", 
        target: "form_of_life", 
        type: "develop", 
        weight: 2,
        description: "Границы языка развиваются в форму жизни: ранний Витгенштейн - логические границы, поздний - антропологические. Limits переосмыслены - не универсальная логическая структура, но множественность form of life как последних оснований."
    },
    { 
        source: "language_game", 
        target: "picture_theory", 
        type: "critique", 
        weight: 2,
        description: "Языковые игры критикуют теорию изображения: язык не только изображает факты, но выполняет множество функций. Language games показывают несостоятельность picture theory - значение не сводится к референции, употребление разнообразно."
    },
    { 
        source: "language_game", 
        target: "logical_space", 
        type: "critique", 
        weight: 2,
        description: "Языковые игры критикуют логическое пространство: нет единой логической структуры языка, есть множество игр. Language games подрывают идею универсального logical space - каждая игра со своей 'грамматикой', нет общего основания."
    },
    { 
        source: "picture_theory", 
        target: "language_game", 
        type: "internal_contradiction", 
        weight: 2,
        description: "Теория изображения и языковые игры во внутреннем противоречии Витгенштейна: ранняя и поздняя философии несовместимы. Picture theory предполагает единую логическую форму, language games - множественность без общей сущности."
    },
    { 
        source: "logical_space", 
        target: "picture_theory", 
        type: "presuppose", 
        weight: 3,
        description: "Логическое пространство предполагает теорию изображения: предложения - точки в пространстве возможностей. Picture theory требует logical space как тотальность возможных положений дел, которые предложения изображают."
    },
    { 
        source: "family_resemblance", 
        target: "language_game", 
        type: "presuppose", 
        weight: 2,
        description: "Семейное сходство предполагает языковые игры: понятия связаны как члены семьи, а не общей сущностью. Family resemblance объясняет единство language games без общего знаменателя - игры пересекаются, но нет единой черты."
    },
    { 
        source: "rule_following", 
        target: "language_game", 
        type: "presuppose", 
        weight: 3, 
        bidirectional: true,
        description: "Следование правилу и языковые игры взаимно предполагаются: language games конституируются правилами, правила существуют только в играх. Rule-following делает возможными игры, игры дают контекст для правил - взаимная импликация."
    },
    { 
        source: "language_game", 
        target: "form_of_life", 
        type: "presuppose", 
        weight: 2,
        description: "Языковые игры предполагают форму жизни: игры укоренены в Lebensform как последнем основании. Language games невозможны вне form of life - разделяемая практика делает возможным согласие в суждениях."
    },
    { 
        source: "logical_space", 
        target: "limits_language", 
        type: "condition", 
        weight: 3,
        description: "Логическое пространство - условие границ языка: пределы мыслимого определяются logical space. Limits of language совпадают с границами логического пространства - что невыразимо в пространстве возможностей, о том нельзя говорить."
    },
    { 
        source: "showing_saying", 
        target: "limits_language", 
        type: "condition", 
        weight: 3,
        description: "Показывание-говорение - условие границ языка: то, что не может быть сказано, может показываться. Showing-saying определяет limits - этика, эстетика, мистическое показываются, но не говорятся, лежа на границе языка."
    },
    { 
        source: "picture_theory", 
        target: "limits_language", 
        type: "condition", 
        weight: 2,
        description: "Теория изображения - условие границ языка: можно говорить только о том, что изобразимо. Picture theory устанавливает limits - предложение изображает возможное положение дел, невозможное неизобразимо и невыразимо."
    },
    { 
        source: "private_language", 
        target: "rule_following", 
        type: "mediate", 
        weight: 3,
        description: "Приватный язык опосредует следование правилу: аргумент против private language показывает, что rule-following требует критерия правильности. Приватные правила невозможны - следование правилу требует публичной проверки."
    },
    { 
        source: "private_language", 
        target: "form_of_life", 
        type: "limit", 
        weight: 3,
        description: "Приватный язык ограничивает форму жизни: аргумент показывает, что Lebensform существенно коллективна. Private language argument устанавливает предел - form of life невозможна в изоляции, язык требует сообщества."
    },

    // ХАЙДЕГГЕР
    { 
        source: "dwelling", 
        target: "das_man", 
        type: "oppose", 
        weight: 2,
        description: "Обитание противоположно das Man: подлинное жительство (Wohnen) против растворения в безличном 'Люди'. Dwelling - укоренённость в бытии, das Man - бегство от себя в усреднённость публичности."
    },
    { 
        source: "das_man", 
        target: "sorge", 
        type: "oppose", 
        weight: 2,
        description: "Das Man противостоит заботе: безличное 'Люди' избегает подлинной Sorge. Das Man - модус неподлинной заботы, где Dasein заботится о том, что 'делается', забывая собственное бытие."
    },
    { 
        source: "vorhanden", 
        target: "zuhanden", 
        type: "oppose", 
        weight: 3, 
        bidirectional: true,
        description: "Наличное и подручное радикально противоположны: Vorhandenheit (presence-at-hand) - теоретическое созерцание вещей, Zuhandenheit (readiness-to-hand) - практическое обращение с орудиями. Vorhanden возникает из поломки Zuhanden - теория вторична относительно практики."
    },
    { 
        source: "dwelling", 
        target: "dasein", 
        type: "consequence", 
        weight: 2,
        description: "Обитание следует из Dasein (поздний Хайдеггер): Dasein - не субъект, но место бытия, Wohnen - способ быть этим местом. Dwelling - экзистенциал позднего Хайдеггера, человек обитает, поскольку есть Dasein."
    },
    { 
        source: "geviert", 
        target: "dasein", 
        type: "consequence", 
        weight: 2,
        description: "Четверица (Geviert) следует из Dasein: земля-небо-боги-смертные структурируют бытие Dasein. Geviert - онтологическая структура позднего Хайдеггера, где Dasein обитает в четверичном."
    },
    { 
        source: "geviert", 
        target: "ereignis", 
        type: "consequence", 
        weight: 2,
        description: "Четверица следует из События: Geviert - способ совершения Ereignis. Со-бытие (appropriating event) собирает четверицу - земля, небо, боги, смертные сбываются в Ereignis."
    },
    { 
        source: "dasein", 
        target: "zuhanden", 
        type: "consequence", 
        weight: 3,
        description: "Dasein влечёт подручность: первичный способ встречи вещей для Dasein - Zuhandenheit. Dasein изначально погружено в практическое обращение с orудиями, теоретическое отношение (Vorhanden) производно."
    },
    { 
        source: "dasein", 
        target: "sorge", 
        type: "consequence", 
        weight: 3,
        description: "Dasein влечёт заботу: бытие Dasein есть Sorge (забота, попечение). Структура бытия-в-мире конституируется заботой - Dasein всегда уже озабочено своим бытием и миром."
    },
    { 
        source: "ereignis", 
        target: "aletheia", 
        type: "consequence", 
        weight: 3,
        description: "Событие влечёт истину-несокрытость: Ereignis - событие алетейи, раскрытие бытия. Aletheia совершается в Ereignis как просвет, где сущее выходит из сокрытости в несокрытость."
    },
    { 
        source: "ereignis", 
        target: "dasein", 
        type: "consequence", 
        weight: 3,
        description: "Событие влечёт Dasein (поздний Хайдеггер): Dasein - место события бытия. Ereignis требует Dasein как Da (Вот) бытия - человек нужен бытию как просвет, где оно сбывается."
    },
    { 
        source: "sein_zum_tode", 
        target: "sorge", 
        type: "consequence", 
        weight: 3,
        description: "Бытие-к-смерти следует из заботы: Sein-zum-Tode - предельная структура Sorge. Забота конституируется конечностью - Dasein заботится о бытии, ибо смертно, смерть делает возможной подлинную заботу."
    },
    { 
        source: "sorge", 
        target: "zuhanden", 
        type: "consequence", 
        weight: 2,
        description: "Забота влечёт подручность: Sorge практически озабочена миром. Zuhanden - модус заботы об орудиях, повседневная забота обращается с вещами как подручными."
    },
    { 
        source: "das_man", 
        target: "geworfenheit", 
        type: "influence", 
        weight: 2,
        description: "Das Man влияет на заброшенность: безличное 'Люди' - способ интерпретации Geworfenheit. Das Man скрывает радикальность заброшенности, предлагая готовые смыслы, маскирующие фактичность."
    },
    { 
        source: "kehre", 
        target: "sein", 
        type: "internal_contradiction", 
        weight: 2,
        description: "Поворот (Kehre) - внутреннее противоречие Хайдеггера: от аналитики Dasein к мышлению Sein. Kehre маркирует разрыв - ранний Хайдеггер идёт от Dasein к бытию, поздний - от бытия к Dasein, но направления несовместимы."
    },
    { 
        source: "being_in_world", 
        target: "dasein", 
        type: "presuppose", 
        weight: 3, 
        bidirectional: true,
        description: "Бытие-в-мире и Dasein взаимно предполагаются: In-der-Welt-sein - конституция Dasein, Dasein - способ быть-в-мире. Не два элемента, но единая структура - Dasein существенно экстатично, уже вне себя в мире."
    },
    { 
        source: "being_in_world", 
        target: "geworfenheit", 
        type: "presuppose", 
        weight: 2,
        description: "Бытие-в-мире предполагает заброшенность: In-der-Welt-sein всегда уже брошено. Being-in-world не выбирается - Dasein обнаруживает себя уже в мире, Geworfenheit фундирует фактичность бытия-в-мире."
    },
    { 
        source: "aletheia", 
        target: "sein", 
        type: "presuppose", 
        weight: 2,
        description: "Алетейя предполагает бытие: истина как несокрытость - способ свершения Sein. Aletheia не свойство суждений, но событие бытия - Sein раскрывает себя как несокрытость."
    },
    { 
        source: "dasein", 
        target: "geworfenheit", 
        type: "presuppose", 
        weight: 2,
        description: "Dasein предполагает заброшенность: существование Dasein фактично, всегда уже брошено. Geworfenheit - экзистенциал Dasein, которое обнаруживает себя в мире, не зная откуда и зачем."
    },
    { 
        source: "ereignis", 
        target: "sein", 
        type: "presuppose", 
        weight: 3,
        description: "Событие предполагает бытие: Ereignis - способ, которым Sein сбывается (поздний Хайдеггер). Бытие не субстанция, но событие - Sein есть Ereignis, присвоение человека бытию и бытия человеку."
    },
    { 
        source: "geworfenheit", 
        target: "sorge", 
        type: "presuppose", 
        weight: 2,
        description: "Заброшенность предполагает заботу: Geworfenheit - один из моментов структуры Sorge. Забота включает заброшенность (фактичность), проект (экзистенциальность), падение - Geworfenheit конституирует заботу."
    },
    { 
        source: "being_in_world", 
        target: "sein", 
        type: "condition", 
        weight: 3,
        description: "Бытие-в-мире - условие понимания бытия: только через In-der-Welt-sein Dasein может вопрошать о Sein. Being-in-world делает возможной онтологию - Dasein понимает бытие, ибо уже в мире, где встречает сущее."
    },
    { 
        source: "geviert", 
        target: "dwelling", 
        type: "condition", 
        weight: 2,
        description: "Четверица - условие обитания: Wohnen возможно только в Geviert. Dwelling требует четверицы как онтологического пространства - человек обитает, щадя четверичное единство земли, неба, богов, смертных."
    },
    { 
        source: "dasein", 
        target: "sein", 
        type: "condition", 
        weight: 3,
        description: "Dasein - условие бытия: бытие требует Dasein как места своего просвета. Sein нуждается в Dasein - без Вот (Da) бытия нет раскрытия бытия, Dasein - онтическое сущее с онтологическим пониманием."
    },
    { 
        source: "sein_zum_tode", 
        target: "dasein", 
        type: "condition", 
        weight: 2,
        description: "Бытие-к-смерти - условие подлинного Dasein: только перед лицом смерти Dasein обретает себя. Sein-zum-Tode делает возможной подлинность - смерть индивидуализирует, вырывая Dasein из das Man к собственному бытию."
    },
    { 
        source: "dwelling", 
        target: "geviert", 
        type: "exemplify", 
        weight: 3,
        description: "Обитание иллюстрирует четверицу: Wohnen - конкретный способ щадящего собирания Geviert. Dwelling показывает четверицу в действии - крестьянская хижина, мост собирают землю-небо-богов-смертных."
    },
    { 
        source: "kehre", 
        target: "ereignis", 
        type: "mediate", 
        weight: 2,
        description: "Поворот опосредует Событие: Kehre - не смена тем, but сам Ereignis как поворот бытия к человеку. Поворот медиирует между ранним и поздним Хайдеггером через мысль о взаимоприсвоении бытия и Dasein."
    },
    { 
        source: "das_man", 
        target: "dasein", 
        type: "limit", 
        weight: 2,
        description: "Das Man ограничивает Dasein: безличное 'Люди' скрывает собственное бытие. Das Man устанавливает предел подлинности - усреднённость публичности препятствует Dasein быть самим собой."
    },
    { 
        source: "das_man", 
        target: "sein_zum_tode", 
        type: "limit", 
        weight: 2,
        description: "Das Man ограничивает бытие-к-смерти: 'Люди' говорят 'люди умирают', скрывая мою смерть. Das Man уклоняется от Sein-zum-Tode, нейтрализуя смерть в безличное событие, лишая её индивидуализирующей силы."
    },

    // КАРНАП
    { 
        source: "linguistic_framework", 
        target: "internal_external", 
        type: "presuppose", 
        weight: 3,
        description: "Лингвистический каркас предполагает различение внутренних и внешних вопросов: внутренние решаются в рамках каркаса, внешние - о принятии каркаса. Linguistic framework делает возможным internal/external distinction - вопросы о существовании внутренние, о каркасе - прагматические."
    },
    { 
        source: "logical_syntax", 
        target: "linguistic_framework", 
        type: "presuppose", 
        weight: 2,
        description: "Логический синтаксис предполагает лингвистический каркас: синтаксис определяет правила каркаса. Logical syntax конституирует linguistic framework - каркас задаётся синтаксическими правилами, а не метафизическими обязательствами."
    },
    { 
        source: "construction_world", 
        target: "protocol_sentences", 
        type: "presuppose", 
        weight: 2,
        description: "Логическое построение мира предполагает протокольные предложения: мир реконструируется из protocol sentences. Construction of the world из чувственного опыта требует базиса - протокольных предложений как эмпирического фундамента."
    },
    { 
        source: "protocol_sentences", 
        target: "verification_principle", 
        type: "presuppose", 
        weight: 3,
        description: "Протокольные предложения предполагают принцип верификации: осмысленность проверяется сводимостью к protocol sentences. Verification principle требует базиса - протокольных предложений как последних верификаторов, к которым редуцируется значение."
    },
    { 
        source: "logical_syntax", 
        target: "verification_principle", 
        type: "instrument", 
        weight: 3,
        description: "Логический синтаксис - инструмент принципа верификации: синтаксические правила определяют верифицируемость. Logical syntax формализует verification principle - осмысленность как синтаксическая правильность плюс эмпирическая проверяемость."
    },
    { 
        source: "internal_external", 
        target: "verification_principle", 
        type: "mediate", 
        weight: 2,
        description: "Внутренние-внешние вопросы опосредуют верификацию: различение спасает verification principle от самоприменения. Internal/external distinction медиирует - метафизические (внешние) вопросы не верифицируемы, но и не бессмысленны, а прагматичны."
    },

    // БАТАЙ
    { 
        source: "sovereignty_bataille", 
        target: "transgression", 
        type: "consequence", 
        weight: 3,
        description: "Суверенность следует из трансгрессии: souveraineté достигается через нарушение запретов. Transgression - путь к суверенности, выход из мира полезности (труда, проекта) в бесполезную трату, мгновение абсолютной свободы."
    },
    { 
        source: "general_economy", 
        target: "expenditure", 
        type: "presuppose", 
        weight: 3,
        description: "Общая экономика предполагает расточение: экономика не ограничивается производством, но включает dépense. General economy основана на избытке энергии, требующем траты - expenditure, а не накопление, первично."
    },
    { 
        source: "heterology", 
        target: "general_economy", 
        type: "presuppose", 
        weight: 2,
        description: "Гетерология предполагает общую экономику: наука о гетерогенном (отброшенном, низком) требует иной экономики. Heterology изучает то, что исключено из полезности - general economy включает расточение гетерогенного."
    },
    { 
        source: "transgression", 
        target: "sacred_profane", 
        type: "presuppose", 
        weight: 3,
        description: "Трансгрессия предполагает священное-профанное: нарушение требует границы между сакральным и мирским. Transgression не уничтожает sacred/profane, но пересекает границу - священное познаётся через запрет и его нарушение."
    },
    { 
        source: "sacred_profane", 
        target: "expenditure", 
        type: "exemplify", 
        weight: 2,
        description: "Священное-профанное иллюстрирует расточение: жертвоприношение (sacred) - чистая трата, труд (profane) - накопление. Sacred/profane показывают два режима - dépense в сакральном против полезности профанного."
    },
    { 
        source: "inner_experience", 
        target: "sovereignty_bataille", 
        type: "instrument", 
        weight: 3,
        description: "Внутренний опыт - инструмент суверенности: expérience intérieure - некоммуникабельный экстаз. Inner experience ведёт к souveraineté через выход за пределы дискурсивного знания, мистика без Бога как абсолютная имманентность."
    },
    { 
        source: "expenditure", 
        target: "transgression", 
        type: "instrument", 
        weight: 2,
        description: "Расточение - инструмент трансгрессии: dépense нарушает экономику полезности. Expenditure (жертва, праздник, эротизм) - способы transgression, разрывающие цепь средств-целей через бесполезную трату."
    },

    // ГАДАМЕР
    { 
        source: "prejudice_gadamer", 
        target: "tradition_gadamer", 
        type: "consequence", 
        weight: 2,
        description: "Предрассудок следует из традиции: Vorurteil не ошибка, но предпонимание, данное Tradition. Prejudice у Гадамера - позитивное условие понимания, мы понимаем из традиции, которая даёт предрассудки как горизонт."
    },
    { 
        source: "fusion_horizons", 
        target: "horizon_understanding", 
        type: "synthesize", 
        weight: 3,
        description: "Слияние горизонтов синтезирует горизонты понимания: Horizontverschmelzung - не поглощение, but создание нового горизонта. Fusion of horizons синтезирует прошлое и настоящее в расширенный horizon - понимание как продуктивное событие."
    },
    { 
        source: "hermeneutic_circle", 
        target: "horizon_understanding", 
        type: "presuppose", 
        weight: 3,
        description: "Герменевтический круг предполагает горизонт понимания: целое понимается из частей, части из целого, оба в горизонте. Hermeneutic circle движется в horizon - предпонимание конституирует горизонт, в котором совершается круговое движение."
    },
    { 
        source: "effective_history", 
        target: "tradition_gadamer", 
        type: "presuppose", 
        weight: 3,
        description: "Действенная история предполагает традицию: Wirkungsgeschichte - не прошлое, но живое действие Tradition в настоящем. Effective history - способ присутствия традиции, мы понимаем в горизонте, сформированном историческим действием."
    },
    { 
        source: "prejudice_gadamer", 
        target: "horizon_understanding", 
        type: "condition", 
        weight: 2,
        description: "Предрассудок - условие горизонта понимания: Vorurteil конституирует horizon. Без предрассудков нет понимания - prejudice задаёт горизонт, в котором нечто может быть понято, чистое сознание невозможно."
    },
    { 
        source: "tradition_gadamer", 
        target: "horizon_understanding", 
        type: "condition", 
        weight: 3,
        description: "Традиция - условие горизонта понимания: Tradition даёт horizon, в котором мы понимаем. Понимание не выход из традиции, но её продолжение - традиция конституирует горизонт как живое предание."
    },
    { 
        source: "application", 
        target: "hermeneutic_circle", 
        type: "culminate", 
        weight: 3,
        description: "Применение кульминирует в герменевтическом круге: Anwendung - не внешнее приложение, но момент понимания. Application завершает hermeneutic circle - понять значит применить к себе, понимание всегда ситуативно."
    },

    // ЛАКАН
    { 
        source: "signifier", 
        target: "desire_other", 
        type: "consequence", 
        weight: 3,
        description: "Означающее влечёт желание Другого: signifiant конституирует субъект, чьё желание - желание Другого. Signifier структурирует бессознательное - субъект представлен означающим для другого означающего, desire циркулирует в цепи signifiers."
    },
    { 
        source: "three_registers", 
        target: "lack", 
        type: "consequence", 
        weight: 3,
        description: "Три регистра влекут нехватку: Реальное-Воображаемое-Символическое структурированы вокруг manque. Three registers - способы отношения к lack: Воображаемое отрицает, Символическое символизирует, Реальное - сама нехватка."
    },
    { 
        source: "objet_petit_a", 
        target: "lack", 
        type: "consequence", 
        weight: 3,
        description: "Objet petit a следует из нехватки: объект а - причина желания, заполнитель manque. Objet a - не объект желания, but причина - то, что делает объект желанным, оставаясь недостижимым, воплощение нехватки."
    },
    { 
        source: "big_other", 
        target: "three_registers", 
        type: "presuppose", 
        weight: 3,
        description: "Большой Другой предполагает три регистра: Autre (A) - место Символического порядка. Big Other структурирует three registers - гарант Символического, зеркало Воображаемого, пустота Реального."
    },
    { 
        source: "desire_other", 
        target: "objet_petit_a", 
        type: "presuppose", 
        weight: 3,
        description: "Желание Другого предполагает objet petit a: désir de l'Autre направлено на недостижимый объект а. Desire of the Other структурировано objet a как причиной - субъект желает того, чего желает Другой, но объект а ускользает."
    },
    { 
        source: "signifier", 
        target: "big_other", 
        type: "presuppose", 
        weight: 2,
        description: "Означающее предполагает Большого Другого: signifiant существует в поле Autre. Signifier требует Другого как места означающего - цепь означающих разворачивается в Символическом порядке Большого Другого."
    },
    { 
        source: "three_registers", 
        target: "mirror_stage", 
        type: "presuppose", 
        weight: 3,
        description: "Три регистра предполагают стадию зеркала: stade du miroir - генезис Воображаемого регистра. Mirror stage вводит Воображаемое как идентификацию с образом, основание для трёх регистров структурирования субъекта."
    },
    { 
        source: "lack", 
        target: "desire_other", 
        type: "condition", 
        weight: 3,
        description: "Нехватка - условие желания Другого: manque порождает désir. Lack делает возможным desire - субъект желает, потому что конституирован нехваткой, желание - попытка заполнить непоправимую утрату."
    },
    { 
        source: "mirror_stage", 
        target: "lack", 
        type: "emerge_from", 
        weight: 2,
        description: "Стадия зеркала порождает нехватку: идентификация с образом создаёт раскол субъекта. Mirror stage вводит manque - между Я и образом разрыв, субъект отчуждён от себя, нехватка бытия конституируется."
    },

    // САРТР
    { 
        source: "engagement", 
        target: "bad_faith", 
        type: "oppose", 
        weight: 2,
        description: "Ангажированность противоположна дурной вере: engagement - принятие свободы и ответственности, mauvaise foi - бегство от них. Engagement требует честности перед свободой, bad faith - самообман, отрицающий выбор."
    },
    { 
        source: "project", 
        target: "bad_faith", 
        type: "oppose", 
        weight: 3,
        description: "Проект противостоит дурной вере: projet - свободное самоопределение, bad faith - отказ от проектирования. Project - аутентичное упражнение свободы, mauvaise foi притворяется, что выбора нет, отрицая проект."
    },
    { 
        source: "engagement", 
        target: "project", 
        type: "consequence", 
        weight: 3,
        description: "Ангажированность следует из проекта: engagement - политическое и этическое выражение projet. Проект требует ангажированности - выбирая себя, я выбираю для всех, свобода обязывает к commitment."
    },
    { 
        source: "in_itself", 
        target: "existence", 
        type: "consequence", 
        weight: 2,
        description: "В-себе-бытие следует из существования: en-soi - модус existence без сознания. In-itself - плотное, самотождественное бытие вещей, existence без самоотношения, бытие = бытию."
    },
    { 
        source: "look", 
        target: "for_itself", 
        type: "consequence", 
        weight: 2,
        description: "Взгляд следует из для-себя-бытия: le regard Другого объективирует pour-soi. Look обнаруживает for-itself как объект для Другого - я существую для себя, но взгляд делает меня в-себе для Другого."
    },
    { 
        source: "for_itself", 
        target: "freedom_sartre", 
        type: "consequence", 
        weight: 2,
        description: "Для-себя-бытие влечёт свободу: pour-soi есть liberté. For-itself - не субстанция, but постоянное самопревосхождение, свобода конституирует pour-soi как бытие, которое есть то, что оно не есть."
    },
    { 
        source: "project", 
        target: "for_itself", 
        type: "consequence", 
        weight: 3,
        description: "Проект следует из для-себя: pour-soi существует как projet. For-itself - проектирующее бытие, оно есть свои возможности, project - способ бытия для-себя как самопревосхождения."
    },
    { 
        source: "look", 
        target: "bad_faith", 
        type: "influence", 
        weight: 2,
        description: "Взгляд влияет на дурную веру: le regard Другого соблазняет к mauvaise foi. Look показывает мне моё бытие-для-другого, искушая принять эту объектность как сущность - бегство в то, чем меня видят."
    },
    { 
        source: "for_itself", 
        target: "in_itself", 
        type: "internal_contradiction", 
        weight: 2, 
        bidirectional: true,
        description: "Для-себя и в-себе во внутреннем противоречии: pour-soi стремится стать en-soi-pour-soi (Бог), но это невозможно. For-itself желает плотности in-itself, сохраняя сознание - противоречивый проект быть основанием себя."
    },
    { 
        source: "freedom_sartre", 
        target: "bad_faith", 
        type: "internal_contradiction", 
        weight: 2, 
        bidirectional: true,
        description: "Свобода и дурная вера во внутреннем противоречии: liberté делает возможной mauvaise foi, но bad faith отрицает свободу. Парадокс - свобода свободна отрицать себя, но это самообман, использующий свободу против свободы."
    },
    { 
        source: "for_itself", 
        target: "nothingness", 
        type: "presuppose", 
        weight: 3,
        description: "Для-себя предполагает ничто: pour-soi конституировано néant. For-itself - дыра в бытии, ничтожение (néantisation) в-себе, nothingness делает возможным сознание как отрицание данности."
    },
    { 
        source: "project", 
        target: "existence", 
        type: "presuppose", 
        weight: 3,
        description: "Проект предполагает существование: projet возможен, ибо existence предшествует essence. Проектирование требует, чтобы человек сначала существовал без готовой сущности - existence делает возможным самоопределение."
    },
    { 
        source: "project", 
        target: "freedom_sartre", 
        type: "presuppose", 
        weight: 3,
        description: "Проект предполагает свободу: projet - упражнение liberté. Проектирование требует свободы - я выбираю себя, создаю свою сущность через project, что возможно только если я свободен."
    },
    { 
        source: "existence", 
        target: "nothingness", 
        type: "presuppose", 
        weight: 3,
        description: "Существование предполагает ничто: existence (человеческое) требует néant как разрыва с en-soi. Existence отлично от бытия - человек существует, вводя ничто в бытие, отрицая данность."
    },
    { 
        source: "nothingness", 
        target: "freedom_sartre", 
        type: "condition", 
        weight: 3,
        description: "Ничто - условие свободы: néant делает возможной liberté. Nothingness - онтологическое основание свободы, способность ничтожить данность (отрицать, трансцендировать) конституирует свободу как отсутствие детерминации."
    },
    { 
        source: "engagement", 
        target: "freedom_sartre", 
        type: "culminate", 
        weight: 2,
        description: "Ангажированность кульминирует в свободе: liberté завершается в engagement. Свобода не абстрактна - она реализуется в commitment, выборе ситуации и действия, ангажированность - свобода в действии."
    },

    // ЛЕВИНАС
    { 
        source: "responsibility", 
        target: "face", 
        type: "consequence", 
        weight: 3,
        description: "Ответственность следует из лица: visage Другого призывает к responsabilité до всякой свободы. Face - не феномен, but эпифания, взывающая 'не убий', ответственность возникает в встрече с лицом Другого."
    },
    { 
        source: "saying_said", 
        target: "face", 
        type: "consequence", 
        weight: 2,
        description: "Говорение-сказанное следуют из лица: le Dire (saying) - событие встречи с visage, le Dit (said) - тематизация. Face требует различения - saying открывается Другому, said фиксирует в понятиях, лицо взывает до сказанного."
    },
    { 
        source: "infinity_levinas", 
        target: "other_levinas", 
        type: "presuppose", 
        weight: 3,
        description: "Бесконечность предполагает Другого: infini - не математическое, but этическое превосхождение тотальности. Infinity Левинаса - Другой как абсолютно внешний, непоглощаемый в тотальность, бесконечное в конечном."
    },
    { 
        source: "responsibility", 
        target: "ethics_first_philosophy", 
        type: "presuppose", 
        weight: 3,
        description: "Ответственность предполагает этику как первую философию: responsabilité первичнее онтологии. Ethics as first philosophy основана на ответственности - отношение к Другому предшествует вопрошанию о бытии."
    },
    { 
        source: "ethics_first_philosophy", 
        target: "other_levinas", 
        type: "presuppose", 
        weight: 3,
        description: "Этика как первая философия предполагает Другого: Autrui - не тема онтологии, but основание этики. Ethics первична, ибо Другой первичнее бытия - встреча с Autrui предшествует пониманию бытия."
    },
    { 
        source: "face", 
        target: "other_levinas", 
        type: "exemplify", 
        weight: 3,
        description: "Лицо иллюстрирует Другого: visage - способ явления Autrui. Face - не феноменологический объект, but эпифания Другого, который не сводится к явлению, бесконечный в своей наготе и уязвимости."
    },
    { 
        source: "trace", 
        target: "other_levinas", 
        type: "exemplify", 
        weight: 2,
        description: "След иллюстрирует Другого: trace - знак абсолютной внешности Autrui. Trace не феномен, but указание на непредставимое - Другой оставляет след, не являясь, бесконечность обозначается в отсутствии."
    },
];
