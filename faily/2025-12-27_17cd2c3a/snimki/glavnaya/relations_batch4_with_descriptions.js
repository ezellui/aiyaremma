const relations = [
    // БРЕНТАНО
    { 
        source: "evidence_brentano", 
        target: "inner_perception", 
        type: "consequence", 
        weight: 2,
        description: "Очевидность (Evidenz) у Брентано следует из внутреннего восприятия: психические акты даны себе с непосредственной достоверностью. Inner perception, в отличие от внешнего наблюдения, обладает аподиктической очевидностью - самосознание психического акта неопровержимо."
    },
    { 
        source: "intentionality_brentano", 
        target: "psychical_physical", 
        type: "presuppose", 
        weight: 3,
        description: "Интенциональность предполагает различение психического и физического: интенциональная направленность на объект - критерий психического. Только психические феномены обладают intentionality (отнесённостью к содержанию), физические - нет."
    },
    { 
        source: "descriptive_psychology", 
        target: "intentionality_brentano", 
        type: "exemplify", 
        weight: 3,
        description: "Дескриптивная психология иллюстрирует интенциональность: описание психических актов (представление, суждение, любовь-ненависть) раскрывает их интенциональную структуру. Descriptive psychology - метод анализа intentionality через классификацию актов сознания."
    },
    { 
        source: "immanent_objectivity", 
        target: "intentionality_brentano", 
        type: "exemplify", 
        weight: 2,
        description: "Имманентная предметность exemplifies интенциональность: объект 'существует' в акте сознания (inexistere). Intentional object не требует реального существования - можно мыслить несуществующее, имманентная объективность указывает на направленность сознания."
    },
    { 
        source: "judgment_presentation", 
        target: "intentionality_brentano", 
        type: "exemplify", 
        weight: 2,
        description: "Суждение и представление иллюстрируют интенциональность: представление полагает объект, суждение принимает или отвергает его. Различие актов показывает разные модусы intentionality - различные способы направленности на объект."
    },
    { 
        source: "inner_perception", 
        target: "psychical_physical", 
        type: "instrument", 
        weight: 2,
        description: "Внутреннее восприятие - инструмент различения психического и физического: только психическое дано во внутреннем восприятии с очевидностью. Inner perception даёт привилегированный доступ к психическому, физическое познаётся лишь косвенно."
    },
    { 
        source: "descriptive_psychology", 
        target: "inner_perception", 
        type: "instrument", 
        weight: 2,
        description: "Дескриптивная психология использует внутреннее восприятие как метод: описание психических феноменов основано на непосредственной данности актов сознания. Inner perception - эмпирическая база дескриптивной психологии."
    },

    // ПИРС
    { 
        source: "secondness", 
        target: "thirdness", 
        type: "presuppose", 
        weight: 3,
        description: "Вторичность (secondness - реакция, сопротивление) предполагает третичность (thirdness - опосредование, закон): отношение требует медиации. Без thirdness нет связи между firstness и secondness, третичность синтезирует качество и факт в знак."
    },
    { 
        source: "firstness", 
        target: "secondness", 
        type: "presuppose", 
        weight: 2,
        description: "Первичность (firstness - качество, возможность) предполагает вторичность: чистое качество должно актуализироваться в факте. Secondness - реализация firstness, столкновение с сопротивлением, превращающее возможность в действительность."
    },
    { 
        source: "synechism", 
        target: "thirdness", 
        type: "presuppose", 
        weight: 2,
        description: "Синехизм (принцип непрерывности) предполагает третичность: континуум требует опосредующих звеньев. Synechism - метафизика thirdness, утверждающая, что реальность непрерывна через законы и привычки (habits)."
    },
    { 
        source: "thirdness", 
        target: "semiosis", 
        type: "presuppose", 
        weight: 3,
        description: "Третичность предполагает семиозис: знаковый процесс - триадическое отношение (знак-объект-интерпретанта). Semiosis невозможен без thirdness - опосредование делает возможной репрезентацию и интерпретацию."
    },
    { 
        source: "fallibilism", 
        target: "pragmatic_maxim", 
        type: "presuppose", 
        weight: 2,
        description: "Фаллибилизм предполагает прагматическую максиму: признание погрешимости знания требует проверки через практические следствия. Pragmatic maxim - способ уточнения понятий через их эффекты, учитывающий фаллибилистическую природу познания."
    },
    { 
        source: "pragmatic_maxim", 
        target: "semiosis", 
        type: "apply", 
        weight: 3,
        description: "Прагматическая максима применяется к семиозису: смысл понятия - в его практических последствиях, познаваемых через знаки. Semiosis реализует pragmatic maxim - значение знака раскрывается в интерпретантах как возможных действиях."
    },
    { 
        source: "abduction", 
        target: "pragmatic_maxim", 
        type: "instrument", 
        weight: 2,
        description: "Абдукция (гипотетический вывод) - инструмент прагматической максимы: выдвижение гипотез о практических следствиях. Abduction порождает новые идеи, которые затем проверяются через их pragmatic consequences."
    },

    // НИЦШЕ
    { 
        source: "master_morality", 
        target: "slave_morality", 
        type: "oppose", 
        weight: 3, 
        bidirectional: true,
        description: "Мораль господ и мораль рабов радикально противоположны: первая утверждает жизнь, силу, благородство (gut/schlecht - хороший/плохой), вторая отрицает их через ressentiment (gut/böse - добрый/злой). Это не эволюция, но два несовместимых ценностных порядка."
    },
    { 
        source: "ressentiment", 
        target: "master_morality", 
        type: "oppose", 
        weight: 3,
        description: "Ressentiment противоположен морали господ: реактивная злоба слабых против сильных. Master morality творит ценности из избытка силы, ressentiment - из бессилия и мести, превращая силу в зло."
    },
    { 
        source: "ressentiment", 
        target: "will_power", 
        type: "oppose", 
        weight: 3,
        description: "Ressentiment противостоит воле к власти: реактивная эмоция отрицает жизнеутверждающую силу. Will to power - активное творчество ценностей, ressentiment - реактивное отравление жизни через моральное осуждение."
    },
    { 
        source: "master_morality", 
        target: "ubermensch", 
        type: "consequence", 
        weight: 3,
        description: "Мораль господ ведёт к сверхчеловеку: Übermensch - завершение аристократической этики, творец ценностей. Сверхчеловек - не биологическая эволюция, но этический идеал господской морали, доведённый до совершенства."
    },
    { 
        source: "perspectivism", 
        target: "will_power", 
        type: "consequence", 
        weight: 3,
        description: "Перспективизм следует из воли к власти: нет фактов, только интерпретации, каждая - выражение определённой воли. Perspectivism - эпистемология will to power, где познание - орудие власти, а истина - полезная перспектива."
    },
    { 
        source: "god_dead", 
        target: "ubermensch", 
        type: "consequence", 
        weight: 3,
        description: "'Бог умер' влечёт сверхчеловека: смерть Бога освобождает место для Übermensch. Христианская мораль обесценена, нужен новый творец ценностей - сверхчеловек заполняет вакуум, оставленный смертью Бога."
    },
    { 
        source: "slave_morality", 
        target: "god_dead", 
        type: "influence", 
        weight: 2,
        description: "Мораль рабов влияет на смерть Бога: христианская мораль, доведённая до логического конца (воля к истине), саморазрушается. Slave morality подрывает свои собственные основания, её воля к истине убивает христианского Бога."
    },
    { 
        source: "dionysian", 
        target: "apollonian", 
        type: "internal_contradiction", 
        weight: 3, 
        bidirectional: true,
        description: "Дионисийское и аполлоническое во внутреннем противоречии: опьянение/сновидение, хаос/форма, единство/индивидуация. Трагедия возникает из их напряжения - Dionysian экстаз разрушает Apollonian границы, но требует их для выражения. Противоречие продуктивно, но неснимаемо."
    },
    { 
        source: "apollonian", 
        target: "will_power", 
        type: "presuppose", 
        weight: 2,
        description: "Аполлоническое предполагает волю к власти: форма, мера, individuation - проявления воли, стремящейся к оформлению. Apollonian - воля к власти как принцип формы, упорядочивающая хаос через сновидческую иллюзию."
    },
    { 
        source: "eternal_return", 
        target: "will_power", 
        type: "presuppose", 
        weight: 3,
        description: "Вечное возвращение предполагает волю к власти: amor fati требует воли утверждать жизнь бесконечно. Eternal return - высшая формула will to power, абсолютное утверждение бытия во всей его случайности и страдании."
    },
    { 
        source: "dionysian", 
        target: "will_power", 
        type: "presuppose", 
        weight: 3,
        description: "Дионисийское предполагает волю к власти: экстаз, разрушение границ, творческое опьянение - модус воли. Dionysian - воля к власти как избыток, переполнение, разрушение и созидание в экстатическом единстве."
    },
    { 
        source: "master_morality", 
        target: "will_power", 
        type: "exemplify", 
        weight: 3,
        description: "Мораль господ иллюстрирует волю к власти: благородные ценности - творческое выражение силы. Master morality - не подчинение внешним нормам, but spontaneous expression воли, утверждающей себя и жизнь."
    },
    { 
        source: "eternal_return", 
        target: "dionysian", 
        type: "culminate", 
        weight: 3,
        description: "Вечное возвращение кульминирует в дионисийском: amor fati - высшая форма дионисийского утверждения. Eternal return требует дионисийской мудрости - радостного приятия всего, включая страдание, в его вечном повторении."
    },
    { 
        source: "will_power", 
        target: "ubermensch", 
        type: "culminate", 
        weight: 3,
        description: "Воля к власти кульминирует в сверхчеловеке: Übermensch - совершенное воплощение творческой воли. Сверхчеловек - не цель эволюции, но высшая актуализация will to power, создающей ценности из себя."
    },
    { 
        source: "ubermensch", 
        target: "eternal_return", 
        type: "mediate", 
        weight: 3,
        description: "Сверхчеловек опосредует вечное возвращение: только Übermensch способен выдержать мысль о вечном возвращении. Он медиирует между человеком и amor fati, преобразуя ужас повторения в радость утверждения."
    },
    { 
        source: "perspectivism", 
        target: "god_dead", 
        type: "emerge_from", 
        weight: 3,
        description: "Перспективизм возникает из смерти Бога: без абсолютной точки зрения остаются только перспективы. God is dead означает конец метафизической истины, рождая perspectivism - признание множественности интерпретаций без привилегированной."
    },
    { 
        source: "ressentiment", 
        target: "slave_morality", 
        type: "emerge_from", 
        weight: 3,
        description: "Мораль рабов возникает из ressentiment: бессильная злоба слабых против сильных творит реактивную мораль. Slave morality - продукт ressentiment, превращающего неспособность отомстить в моральное превосходство страдающих."
    },

    // ФРЕГЕ
    { 
        source: "function_argument", 
        target: "begriffsschrift", 
        type: "consequence", 
        weight: 2,
        description: "Функция-аргумент следует из Begriffsschrift (понятийного письма): логическая нотация Фреге строится на различении функции и аргумента. Begriffsschrift формализует это различие, заменяя субъект-предикатную логику функциональной."
    },
    { 
        source: "thought", 
        target: "sense_reference", 
        type: "presuppose", 
        weight: 2,
        description: "Мысль (Gedanke) предполагает различение смысла и значения: мысль - это Sinn (смысл) предложения, независимый от субъективных представлений. Thought требует различения Sinn/Bedeutung для объективности логики."
    },
    { 
        source: "sense_reference", 
        target: "function_argument", 
        type: "presuppose", 
        weight: 3,
        description: "Смысл-значение предполагает функцию-аргумент: Sinn/Bedeutung применяется не только к именам, но и к функциям. Функции имеют смысл (способ данности) и значение (курс значений), расширяя семантическую теорию на всю логику."
    },
    { 
        source: "context_principle", 
        target: "sense_reference", 
        type: "condition", 
        weight: 3,
        description: "Принцип контекста - условие смысла-значения: значение слова определяется только в контексте предложения. Context principle делает возможным различение Sinn/Bedeutung - изолированное имя не имеет определённого смысла."
    },
    { 
        source: "logicism", 
        target: "begriffsschrift", 
        type: "instrument", 
        weight: 3,
        description: "Логицизм использует Begriffsschrift как инструмент: сведение арифметики к логике требует формальной системы. Begriffsschrift - техническое средство реализации logicism, формальный язык для определения числа через логические понятия."
    },

    // МЕЙНОНГ
    { 
        source: "incomplete_objects", 
        target: "non_existent_objects", 
        type: "consequence", 
        weight: 2,
        description: "Неполные объекты следуют из несуществующих: если можно мыслить несуществующее, можно мыслить недоопределённое. Incomplete objects (золотая гора без определённой высоты) - подкласс non-existent objects, показывающий независимость Sosein от полноты определений."
    },
    { 
        source: "sosein", 
        target: "object_theory", 
        type: "presuppose", 
        weight: 3,
        description: "Sosein (так-бытие) предполагает теорию объектов: объект имеет свойства независимо от существования. Object theory основана на принципе независимости Sosein от Sein - круглый квадрат круглый и квадратный, хотя не существует."
    },
    { 
        source: "object_theory", 
        target: "non_existent_objects", 
        type: "presuppose", 
        weight: 3,
        description: "Теория объектов предполагает несуществующие объекты: Gegenstandstheorie включает всё, о чём можно мыслить. Non-existent objects необходимы, ибо мышление направлено на объекты, которые могут не существовать - интенциональность шире онтологии."
    },
    { 
        source: "sosein", 
        target: "non_existent_objects", 
        type: "exemplify", 
        weight: 3,
        description: "Sosein иллюстрируется несуществующими объектами: золотая гора золотая (Sosein), хотя не существует (нет Sein). Non-existent objects демонстрируют автономию так-бытия - объект обладает свойствами до и независимо от существования."
    },
    { 
        source: "assumptions", 
        target: "non_existent_objects", 
        type: "instrument", 
        weight: 2,
        description: "Допущения (Annahmen) - инструмент работы с несуществующими объектами: мы делаем допущения о том, чего нет. Assumptions - психологический акт, позволяющий интенционально относиться к non-existent objects без полагания их существования."
    },

    // ФРЕЙД
    { 
        source: "death_drive", 
        target: "pleasure_principle", 
        type: "oppose", 
        weight: 3,
        description: "Влечение к смерти (Todestrieb) противоположно принципу удовольствия: Танатос стремится к неорганическому, Эрос - к жизни. Death drive - not reduction напряжения (pleasure principle), но влечение к нулевой точке, абсолютному покою смерти."
    },
    { 
        source: "pleasure_principle", 
        target: "reality_principle", 
        type: "oppose", 
        weight: 3, 
        bidirectional: true,
        description: "Принцип удовольствия и принцип реальности противоположны, но взаимосвязаны: первый требует немедленного удовлетворения, второй - отсрочки ради адаптации. Reality principle не отменяет, но модифицирует pleasure principle, вводя обходные пути к удовольствию."
    },
    { 
        source: "unconscious", 
        target: "dream_work", 
        type: "consequence", 
        weight: 3,
        description: "Бессознательное влечёт работу сновидения: Traumarbeit - процесс искажения бессознательных желаний. Dream-work (сгущение, смещение, символизация) - механизм, которым unconscious обходит цензуру, проявляясь в замаскированной форме."
    },
    { 
        source: "id_ego_superego", 
        target: "reality_principle", 
        type: "consequence", 
        weight: 2,
        description: "Структура Оно-Я-Сверх-Я влечёт принцип реальности: Ego развивается как посредник между Ид и реальностью. Reality principle - функция Я, медиирующего между требованиями Оно (удовольствие) и внешнего мира (реальность)."
    },
    { 
        source: "oedipus_complex", 
        target: "unconscious", 
        type: "consequence", 
        weight: 3,
        description: "Эдипов комплекс следует из бессознательного: инцестуозные желания вытесняются, образуя ядро unconscious. Oedipus complex - универсальная структура бессознательного, конфликт желания и запрета, конституирующий субъект."
    },
    { 
        source: "id_ego_superego", 
        target: "unconscious", 
        type: "presuppose", 
        weight: 3,
        description: "Структура Оно-Я-Сверх-Я предполагает бессознательное: Ид полностью, Сверх-Я частично бессознательны. Unconscious не совпадает с Ид - большая часть психического аппарата вне сознания, топика структурирует бессознательное."
    },
    { 
        source: "unconscious", 
        target: "repression", 
        type: "condition", 
        weight: 3,
        description: "Бессознательное - условие вытеснения: Verdrängung создаёт unconscious, помещая неприемлемое вне сознания. Без бессознательного как системы некуда вытеснять - repression предполагает топику сознательное/предсознательное/бессознательное."
    },
    { 
        source: "repression", 
        target: "oedipus_complex", 
        type: "condition", 
        weight: 2,
        description: "Вытеснение - условие Эдипова комплекса: инцестуозные желания должны быть вытеснены для разрешения комплекса. Repression трансформирует Эдипов конфликт в бессознательную структуру, формирующую Сверх-Я и идентификацию."
    },
    { 
        source: "transference", 
        target: "unconscious", 
        type: "exemplify", 
        weight: 2,
        description: "Перенос иллюстрирует бессознательное: Übertragung - проекция бессознательных желаний на аналитика. Transference показывает, как unconscious повторяет прошлые отношения, не зная об этом - автоматизм бессознательного."
    },
    { 
        source: "dream_work", 
        target: "unconscious", 
        type: "exemplify", 
        weight: 3,
        description: "Работа сновидения exemplifies бессознательное: Traumarbeit демонстрирует законы unconscious (отсутствие противоречия, вневременность, замещение реальности). Dream-work - королевская дорога к бессознательному, его процессы видимы в сновидении."
    },

    // ГУССЕРЛЬ
    { 
        source: "lifeworld", 
        target: "epoché", 
        type: "oppose", 
        weight: 2,
        description: "Жизненный мир и эпохе в напряжённом отношении: Lebenswelt - дорефлексивная очевидность, epoché - её приостановка. Феноменология заключает Lebenswelt в скобки, чтобы тематизировать, но поздний Гуссерль видит в жизненном мире фундамент, предшествующий эпохе."
    },
    { 
        source: "noesis_noema", 
        target: "eidetic", 
        type: "consequence", 
        weight: 3,
        description: "Ноэза-ноэма следуют из эйдетического: акт сознания (noesis) и его интенциональный коррелят (noema) - эйдетические структуры. Eidetic reduction раскрывает сущностную корреляцию между актом и его смыслом."
    },
    { 
        source: "noesis_noema", 
        target: "evidence", 
        type: "consequence", 
        weight: 2,
        description: "Ноэза-ноэма влекут очевидность: адекватность ноэмы ноэзе даёт Evidenz. Evidence возникает в совпадении интенции (noesis) и её наполнения (noema) - самоданность вещи сознанию."
    },
    { 
        source: "phenomenology", 
        target: "constitution", 
        type: "consequence", 
        weight: 2,
        description: "Феноменология ведёт к конституированию: задача phenomenology - прояснить, как объекты конституируются в сознании. Constitution - не творение, но раскрытие смыслового генезиса предметности в интенциональных актах."
    },
    { 
        source: "phenomenology", 
        target: "evidence", 
        type: "consequence", 
        weight: 2,
        description: "Феноменология влечёт очевидность: цель phenomenology - достижение аподиктической Evidenz. Феноменологический метод ведёт к самоданности вещей - к созерцанию сущностей в их изначальной очевидности."
    },
    { 
        source: "eidetic", 
        target: "intentionality", 
        type: "consequence", 
        weight: 2,
        description: "Эйдетическое следует из интенциональности: сущностное усмотрение раскрывает структуру intentionality. Eidetic reduction - метод обнаружения априорных законов интенциональной направленности сознания."
    },
    { 
        source: "intersubjectivity", 
        target: "transcendental_ego", 
        type: "critique", 
        weight: 2,
        description: "Интерсубъективность критикует трансцендентальное Я: проблема солипсизма требует обоснования другого Я. Intersubjectivity - критическая точка феноменологии, где transcendental ego должно конституировать других субъектов, оставаясь единственным конституирующим."
    },
    { 
        source: "constitution", 
        target: "transcendental_ego", 
        type: "presuppose", 
        weight: 3,
        description: "Конституирование предполагает трансцендентальное Я: constitution - деятельность transcendental ego. Всякая предметность конституируется в актах Я - трансцендентальный субъект - полюс, в котором собирается смысл."
    },
    { 
        source: "constitution", 
        target: "intentionality", 
        type: "presuppose", 
        weight: 3,
        description: "Конституирование основано на интенциональности: объекты конституируются через интенциональные акты. Constitution - развёртывание intentionality, процесс наделения смыслом через направленность сознания."
    },
    { 
        source: "noesis_noema", 
        target: "intentionality", 
        type: "presuppose", 
        weight: 3,
        description: "Ноэза-ноэма предполагают интенциональность: корреляция акта и смысла - структура intentionality. Noesis/noema - две стороны интенционального отношения, сознание как акт и его интенциональный объект."
    },
    { 
        source: "evidence", 
        target: "constitution", 
        type: "presuppose", 
        weight: 2,
        description: "Очевидность предполагает конституирование: Evidenz - самоданность конституированного. Без constitution нет данности - вещь должна быть конституирована как смысл, чтобы быть очевидной."
    },
    { 
        source: "phenomenology", 
        target: "epoché", 
        type: "presuppose", 
        weight: 3,
        description: "Феноменология предполагает эпохе: phenomenology начинается с заключения в скобки естественной установки. Epoché - методический принцип феноменологии, без приостановки веры в мир нет феноменологической редукции."
    },
    { 
        source: "phenomenology", 
        target: "intentionality", 
        type: "presuppose", 
        weight: 3,
        description: "Феноменология основана на интенциональности: сознание всегда сознание о чём-то. Intentionality - фундаментальное открытие phenomenology, делающее возможным исследование корреляции сознания и мира."
    },
    { 
        source: "epoché", 
        target: "intentionality", 
        type: "presuppose", 
        weight: 3,
        description: "Эпохе предполагает интенциональность: заключение в скобки раскрывает интенциональную направленность. Epoché не уничтожает мир, но обнажает его как интенциональный коррелят - intentionality становится видимой после редукции."
    },
    { 
        source: "intentionality", 
        target: "lifeworld", 
        type: "condition", 
        weight: 2,
        description: "Интенциональность - условие жизненного мира: Lebenswelt конституируется интенциональными актами. Жизненный мир - не данность, но интенциональное достижение, горизонт всех интенций."
    },
    { 
        source: "intersubjectivity", 
        target: "lifeworld", 
        type: "condition", 
        weight: 3,
        description: "Интерсубъективность - условие жизненного мира: Lebenswelt - не моя приватная сфера, но общий мир. Intersubjectivity делает возможным жизненный мир как интерсубъективно разделяемый горизонт опыта."
    },
    { 
        source: "evidence", 
        target: "intentionality", 
        type: "condition", 
        weight: 3,
        description: "Очевидность - условие интенциональности: Evidenz - критерий наполнения интенции. Без возможности очевидности intentionality была бы пустой направленностью - evidence делает интенциональность познающей."
    },
    { 
        source: "transcendental_ego", 
        target: "evidence", 
        type: "condition", 
        weight: 2,
        description: "Трансцендентальное Я - условие очевидности: Evidenz дана только transcendental ego. Очевидность требует субъекта, для которого нечто очевидно - чистое Я как полюс всякой самоданности."
    },
    { 
        source: "transcendental_ego", 
        target: "phenomenology", 
        type: "condition", 
        weight: 3,
        description: "Трансцендентальное Я - условие феноменологии: phenomenology - наука о трансцендентальной субъективности. Без редукции к transcendental ego феноменология остаётся психологией - чистое Я делает возможной трансцендентальную философию."
    },
    { 
        source: "noesis_noema", 
        target: "phenomenology", 
        type: "exemplify", 
        weight: 2,
        description: "Ноэза-ноэма иллюстрируют феноменологию: анализ корреляции акта и смысла - paradigm case феноменологического исследования. Noesis/noema показывают, как phenomenology описывает интенциональные структуры."
    },
    { 
        source: "evidence", 
        target: "eidetic", 
        type: "instrument", 
        weight: 3,
        description: "Очевидность - инструмент эйдетического: Evidenz даёт доступ к сущностям. Eidetic intuition - очевидное усмотрение сущностей, evidence делает возможным созерцание априорных структур."
    },
    { 
        source: "transcendental_ego", 
        target: "eidetic", 
        type: "instrument", 
        weight: 2,
        description: "Трансцендентальное Я - инструмент эйдетического: чистое Я совершает эйдетическую редукцию. Transcendental ego - субъект eidetic variation, способный усматривать сущности через вариацию в фантазии."
    },
    { 
        source: "phenomenology", 
        target: "eidetic", 
        type: "instrument", 
        weight: 3,
        description: "Феноменология использует эйдетическое: eidetic reduction - метод phenomenology. Феноменология не эмпирическая наука о фактах, но эйдетическая наука о сущностях сознания."
    },
    { 
        source: "epoché", 
        target: "transcendental_ego", 
        type: "instrument", 
        weight: 3,
        description: "Эпохе - инструмент обнаружения трансцендентального Я: заключение в скобки открывает чистое сознание. Epoché редуцирует эмпирическое Я к transcendental ego - остаток после выключения мира."
    },
    { 
        source: "epoché", 
        target: "evidence", 
        type: "instrument", 
        weight: 2,
        description: "Эпохе - инструмент очевидности: приостановка тезиса раскрывает самоданность. Epoché устраняет предрассудки, делая возможной аподиктическую Evidenz чистого сознания."
    },

    // БЕРГСОН
    { 
        source: "intuition_bergson", 
        target: "intellect_spatialization", 
        type: "oppose", 
        weight: 3, 
        bidirectional: true,
        description: "Интуиция и интеллект радикально противоположны: intuition схватывает длительность изнутри, intellect пространственно разделяет непрерывное. Интеллект создан для действия с материей (spatialization), интуиция - для постижения жизни как durée."
    },
    { 
        source: "pure_perception", 
        target: "intellect_spatialization", 
        type: "oppose", 
        weight: 2,
        description: "Чистое восприятие противостоит пространственности интеллекта: perception в чистом виде схватывает вещи в их становлении. Intellect spatializes восприятие, фиксируя его в геометрических схемах, искажая текучую реальность."
    },
    { 
        source: "image_bergson", 
        target: "pure_perception", 
        type: "consequence", 
        weight: 2,
        description: "Образ следует из чистого восприятия: images - это вещи между материей и представлением. Pure perception раскрывает мир как совокупность images, данных до разделения на субъект и объект."
    },
    { 
        source: "open_closed_morality", 
        target: "creative_evolution", 
        type: "consequence", 
        weight: 2,
        description: "Открытая и закрытая мораль вытекают из творческой эволюции: закрытая (привычка, общество) против открытой (мистика, человечество). Creative evolution объясняет эти два типа - закрытая морабиологически, открытая - духовный порыв élan vital."
    },
    { 
        source: "laughter", 
        target: "elan_vital", 
        type: "consequence", 
        weight: 1,
        description: "Смех следует из жизненного порыва: le rire - социальная реакция на механизацию жизни. Laughter корректирует застывание живого, указывая на несоответствие механического автоматизма творческому élan vital."
    },
    { 
        source: "creative_evolution", 
        target: "duree", 
        type: "consequence", 
        weight: 3,
        description: "Творческая эволюция следует из длительности: évolution créatrice - durée в живом. Эволюция - не механическое развёртывание, но творческая длительность, непредсказуемое порождение нового."
    },
    { 
        source: "laughter", 
        target: "intellect_spatialization", 
        type: "influence", 
        weight: 1,
        description: "Смех влияет на понимание интеллекта: le rire раскрывает механистичность мышления. Laughter возникает, когда живое становится автоматом - это указывает на spatializing tendency интеллекта, омертвляющего жизнь."
    },
    { 
        source: "duree", 
        target: "elan_vital", 
        type: "presuppose", 
        weight: 3,
        description: "Длительность предполагает жизненный порыв: durée - не пустое время, но творческое становление. Élan vital - это durée в её творческом аспекте, длительность как непрерывное созидание нового."
    },
    { 
        source: "matter_memory", 
        target: "duree", 
        type: "presuppose", 
        weight: 2,
        description: "Материя и память предполагают длительность: Matière et Mémoire исследует durée через память. Memory - сохранение прошлого в настоящем, конкретное проявление длительности как накопления времени."
    },
    { 
        source: "creative_evolution", 
        target: "elan_vital", 
        type: "presuppose", 
        weight: 3,
        description: "Творческая эволюция основана на жизненном порыве: évolution créatrice движима élan vital. Без жизненного порыва эволюция была бы механической - élan vital объясняет непредсказуемость и новизну в развитии жизни."
    },
    { 
        source: "pure_perception", 
        target: "matter_memory", 
        type: "presuppose", 
        weight: 2,
        description: "Чистое восприятие предполагает материю и память: perception актуально (материя), но пронизано прошлым (память). Pure perception - теоретический предел, реальное восприятие всегда синтез matter и memory."
    },
    { 
        source: "intuition_bergson", 
        target: "duree", 
        type: "instrument", 
        weight: 3,
        description: "Интуиция - инструмент постижения длительности: только intuition схватывает durée изнутри. Интеллект пространственно разделяет длительность, интуиция совпадает с ней - метод философии для Бергсона."
    },
    { 
        source: "intuition_bergson", 
        target: "image_bergson", 
        type: "instrument", 
        weight: 2,
        description: "Интуиция - инструмент постижения образов: intuition проникает в images без интеллектуального опосредования. Образы даны интуиции непосредственно, до разделения на восприятие и воспоминание."
    },
    { 
        source: "open_closed_morality", 
        target: "elan_vital", 
        type: "emerge_from", 
        weight: 2,
        description: "Открытая и закрытая мораль возникают из жизненного порыва: открытая мораль - прорыв élan vital через социальные рамки. Закрытая мораль биологически обусловлена, открытая - мистическое продолжение творческого порыва."
    },

    // ДЬЮИ
    { 
        source: "democracy_education", 
        target: "experience_dewey", 
        type: "consequence", 
        weight: 2,
        description: "Демократия и образование следуют из опыта: education - реорганизация experience, демократия - социальная форма, максимизирующая опыт. Democracy and education взаимосвязаны через расширение и обогащение experience."
    },
    { 
        source: "instrumentalism", 
        target: "inquiry", 
        type: "presuppose", 
        weight: 3,
        description: "Инструментализм предполагает исследование: идеи - инструменты для inquiry. Instrumentalism - эпистемология, где мышление - орудие решения проблем, а истина - успешное завершение inquiry."
    },
    { 
        source: "warranted_assertibility", 
        target: "instrumentalism", 
        type: "presuppose", 
        weight: 3,
        description: "Обоснованная утверждаемость предполагает инструментализм: warranted assertibility заменяет 'истину' как результат inquiry. Утверждение обосновано, если оно инструментально успешно - истина как работающее убеждение."
    },
    { 
        source: "experience_dewey", 
        target: "inquiry", 
        type: "condition", 
        weight: 3,
        description: "Опыт - условие исследования: inquiry возникает из проблемной ситуации в experience. Без опытного столкновения с неопределённостью нет мотива для inquiry - исследование реструктурирует нарушенный опыт."
    },
    { 
        source: "learning_doing", 
        target: "inquiry", 
        type: "instrument", 
        weight: 2,
        description: "Обучение через делание - инструмент исследования: learning by doing реализует inquiry в образовании. Активное экспериментирование - способ inquiry, знание приобретается через практическое решение проблем."
    },

    // УАЙТХЕД
    { 
        source: "concrescence", 
        target: "actual_occasion", 
        type: "consequence", 
        weight: 3,
        description: "Срастание (concrescence) следует из актуального события: процесс становления actual occasion. Concrescence - синтез многих в одно, процесс, которым актуальное событие конституирует себя через prehension."
    },
    { 
        source: "fallacy_misplaced_concreteness", 
        target: "process_reality", 
        type: "critique", 
        weight: 2,
        description: "Ошибка неуместной конкретности критикует субстанциальную метафизику: принятие абстракций за конкретную реальность. Fallacy of misplaced concreteness - критический инструмент process philosophy, разоблачающий иллюзию постоянных субстанций."
    },
    { 
        source: "actual_occasion", 
        target: "process_reality", 
        type: "presuppose", 
        weight: 3,
        description: "Актуальное событие предполагает процессуальную реальность: actual occasion - единица process reality. Реальность состоит не из субстанций, но из событий - атомов становления, каждое из которых процесс."
    },
    { 
        source: "prehension", 
        target: "actual_occasion", 
        type: "presuppose", 
        weight: 3,
        description: "Схватывание предполагает актуальное событие: prehension - способ, которым actual occasion включает другие события. Без prehension нет concrescence - событие конституируется через схватывание всех других событий."
    },
    { 
        source: "creativity_whitehead", 
        target: "process_reality", 
        type: "presuppose", 
        weight: 3,
        description: "Креативность предполагает процессуальную реальность: creativity - ultimate category процессуальной онтологии. Становление нового из многих (concrescence) требует креативности как универсального принципа process reality."
    },
    { 
        source: "eternal_objects", 
        target: "actual_occasion", 
        type: "condition", 
        weight: 2,
        description: "Вечные объекты - условие актуального события: eternal objects (чистые потенциальности) ингрессируют в actual occasion. Без вечных объектов события были бы неопределимыми - они дают форму процессу становления."
    },
];
