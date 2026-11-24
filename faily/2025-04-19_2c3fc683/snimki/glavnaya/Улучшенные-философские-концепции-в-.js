// Предустановленные философские концепции
const philosophicalConcepts = [
    // 1. Феноменология Гуссерля
    {
        name: "Феноменология Гуссерля",
        description: "Философия Эдмунда Гуссерля, исследующая структуры сознания и их отношение к феноменам. Ключевые понятия: интенциональность сознания – направленность на предметы, эпохе (феноменологическая редукция), трансцендентальное эго, жизненный мир (Lebenswelt).",
        nodes: [
            { id: 1, text: "Сознание", x: 400, y: 100, color: "#3498db" },
            { id: 2, text: "Интенциональность", x: 600, y: 100, color: "#9b59b6" },
            { id: 3, text: "Феномен", x: 600, y: 200, color: "#2ecc71" },
            { id: 4, text: "Трансцендентальное Эго", x: 200, y: 100, color: "#e74c3c" },
            { id: 5, text: "Жизненный мир", x: 400, y: 300, color: "#f39c12" },
            { id: 6, text: "Ноэзис", x: 300, y: 200, color: "#1abc9c" },
            { id: 7, text: "Ноэма", x: 500, y: 200, color: "#34495e" },
            { id: 8, text: "Сущность", x: 700, y: 300, color: "#8e44ad" },
            { id: 9, text: "Время", x: 200, y: 300, color: "#16a085" },
            { id: 10, text: "Бытие", x: 300, y: 400, color: "#d35400" },
            { id: 11, text: "Истина", x: 600, y: 400, color: "#7f8c8d" },
            { id: 12, text: "Трансцендентное", x: 700, y: 150, color: "#27ae60" },
            { id: 13, text: "Имманентное", x: 250, y: 200, color: "#f1c40f" }
        ],
        edges: [
            { id: 1, source: 1, target: 2, type: "Тождество (А тождественно Б)", bidirectional: true },
            { id: 2, source: 1, target: 3, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 3, source: 4, target: 1, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 4, source: 4, target: 13, type: "Тождество (А тождественно Б)", bidirectional: true },
            { id: 5, source: 1, target: 5, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 6, source: 1, target: 6, type: "Тождество (А тождественно Б)", bidirectional: false },
            { id: 7, source: 3, target: 7, type: "Тождество (А тождественно Б)", bidirectional: false },
            { id: 8, source: 6, target: 7, type: "Диалектическое противоречие (А переходит в своё иное - Б)", bidirectional: true },
            { id: 9, source: 7, target: 3, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 10, source: 3, target: 8, type: "Феноменологическая (А является феноменом Б)", bidirectional: false },
            { id: 11, source: 9, target: 1, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 12, source: 5, target: 10, type: "Феноменологическая (А является феноменом Б)", bidirectional: false },
            { id: 13, source: 1, target: 12, type: "Эпистемическая (А познаёт Б)", bidirectional: false },
            { id: 14, source: 8, target: 11, type: "Тождество (А тождественно Б)", bidirectional: true },
            { id: 15, source: 10, target: 11, type: "Феноменологическая (А является феноменом Б)", bidirectional: false },
            { id: 16, source: 5, target: 12, type: "Герменевтическая (А истолковывает Б)", bidirectional: false },
            { id: 17, source: 2, target: 12, type: "Телеологическая (А целеустремлено к Б)", bidirectional: false }
        ]
    },
    // 2. Диалектический материализм Маркса
    {
        name: "Диалектический материализм Маркса",
        description: "Философское учение Карла Маркса и Фридриха Энгельса, согласно которому материя первична по отношению к сознанию, а развитие происходит через диалектические противоречия. Ключевые понятия: общественное бытие, общественное сознание, базис, надстройка, отчуждение, прибавочная стоимость.",
        nodes: [
            { id: 1, text: "Материя", x: 400, y: 100, color: "#3498db" },
            { id: 2, text: "Сознание", x: 600, y: 100, color: "#2ecc71" },
            { id: 3, text: "Бытие", x: 200, y: 150, color: "#e74c3c" },
            { id: 4, text: "Практика", x: 300, y: 200, color: "#9b59b6" },
            { id: 5, text: "Диалектика", x: 500, y: 200, color: "#f39c12" },
            { id: 6, text: "Общественные отношения", x: 400, y: 300, color: "#1abc9c" },
            { id: 7, text: "Производительные силы", x: 250, y: 350, color: "#34495e" },
            { id: 8, text: "Надстройка", x: 550, y: 350, color: "#8e44ad" },
            { id: 9, text: "Необходимость", x: 300, y: 450, color: "#16a085" },
            { id: 10, text: "Свобода", x: 500, y: 450, color: "#d35400" },
            { id: 11, text: "Отчуждение", x: 700, y: 250, color: "#7f8c8d" },
            { id: 12, text: "Субстанция", x: 200, y: 250, color: "#27ae60" },
            { id: 13, text: "Историческая закономерность", x: 400, y: 400, color: "#f1c40f" }
        ],
        edges: [
            { id: 1, source: 1, target: 2, type: "Причинность (А вызывает Б)", bidirectional: false },
            { id: 2, source: 1, target: 3, type: "Тождество (А тождественно Б)", bidirectional: true },
            { id: 3, source: 3, target: 2, type: "Причинность (А вызывает Б)", bidirectional: false },
            { id: 4, source: 3, target: 6, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 5, source: 4, target: 3, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: true },
            { id: 6, source: 4, target: 1, type: "Эпистемическая (А познаёт Б)", bidirectional: false },
            { id: 7, source: 5, target: 1, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 8, source: 5, target: 13, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 9, source: 7, target: 6, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 10, source: 6, target: 2, type: "Причинность (А вызывает Б)", bidirectional: false },
            { id: 11, source: 6, target: 8, type: "Причинность (А вызывает Б)", bidirectional: false },
            { id: 12, source: 7, target: 8, type: "Диалектическое противоречие (А переходит в своё иное - Б)", bidirectional: true },
            { id: 13, source: 9, target: 10, type: "Диалектическое противоречие (А переходит в своё иное - Б)", bidirectional: true },
            { id: 14, source: 1, target: 12, type: "Тождество (А тождественно Б)", bidirectional: true },
            { id: 15, source: 6, target: 11, type: "Причинность (А вызывает Б)", bidirectional: false },
            { id: 16, source: 13, target: 10, type: "Телеологическая (А целеустремлено к Б)", bidirectional: false },
            { id: 17, source: 1, target: 9, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 18, source: 2, target: 13, type: "Эпистемическая (А познаёт Б)", bidirectional: false }
        ]
    },
    // 3. Онтология Хайдеггера
    {
        name: "Онтология Хайдеггера",
        description: "Философия Мартина Хайдеггера, исследующая вопрос о смысле бытия. Центральные понятия: Dasein (присутствие), бытие-в-мире, временность, историчность, подручность, забота, язык как дом бытия.",
        nodes: [
            { id: 1, text: "Бытие", x: 400, y: 100, color: "#3498db" },
            { id: 2, text: "Сущее", x: 600, y: 100, color: "#2ecc71" },
            { id: 3, text: "Dasein (Присутствие)", x: 300, y: 200, color: "#e74c3c" },
            { id: 4, text: "Время", x: 200, y: 300, color: "#9b59b6" },
            { id: 5, text: "Мир", x: 600, y: 250, color: "#f39c12" },
            { id: 6, text: "Язык", x: 700, y: 300, color: "#1abc9c" },
            { id: 7, text: "Забота", x: 300, y: 300, color: "#34495e" },
            { id: 8, text: "Бытие-к-смерти", x: 450, y: 400, color: "#8e44ad" },
            { id: 9, text: "Подручность", x: 550, y: 350, color: "#16a085" },
            { id: 10, text: "Историчность", x: 350, y: 450, color: "#d35400" },
            { id: 11, text: "Разомкнутость", x: 200, y: 400, color: "#7f8c8d" },
            { id: 12, text: "Экзистенция", x: 500, y: 150, color: "#27ae60" },
            { id: 13, text: "Ничто", x: 700, y: 150, color: "#f1c40f" }
        ],
        edges: [
            { id: 1, source: 1, target: 2, type: "Диалектическое противоречие (А переходит в своё иное - Б)", bidirectional: true },
            { id: 2, source: 3, target: 1, type: "Герменевтическая (А истолковывает Б)", bidirectional: false },
            { id: 3, source: 3, target: 5, type: "Феноменологическая (А является феноменом Б)", bidirectional: false },
            { id: 4, source: 4, target: 1, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: true },
            { id: 5, source: 6, target: 1, type: "Репрезентационная (А представляет/отражает Б)", bidirectional: false },
            { id: 6, source: 3, target: 7, type: "Тождество (А тождественно Б)", bidirectional: true },
            { id: 7, source: 3, target: 8, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 8, source: 3, target: 12, type: "Тождество (А тождественно Б)", bidirectional: true },
            { id: 9, source: 2, target: 9, type: "Феноменологическая (А является феноменом Б)", bidirectional: false },
            { id: 10, source: 4, target: 10, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 11, source: 10, target: 3, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 12, source: 3, target: 11, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 13, source: 6, target: 3, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 14, source: 3, target: 4, type: "Феноменологическая (А является феноменом Б)", bidirectional: false },
            { id: 15, source: 1, target: 13, type: "Диалектическое противоречие (А переходит в своё иное - Б)", bidirectional: true },
            { id: 16, source: 7, target: 8, type: "Телеологическая (А целеустремлено к Б)", bidirectional: false },
            { id: 17, source: 5, target: 9, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false }
        ]
    },
    // 4. Платоновский идеализм
    {
        name: "Платоновский идеализм",
        description: "Философская система Платона, утверждающая первичность идей (форм) по отношению к материальному миру. Ключевые понятия: мир идей, мир вещей, анамнезис (припоминание), благо, эйдос, пещера, душа.",
        nodes: [
            { id: 1, text: "Идея (Эйдос)", x: 400, y: 100, color: "#3498db" },
            { id: 2, text: "Единое", x: 300, y: 50, color: "#2ecc71" },
            { id: 3, text: "Благо", x: 500, y: 50, color: "#e74c3c" },
            { id: 4, text: "Душа", x: 300, y: 200, color: "#9b59b6" },
            { id: 5, text: "Материальный мир", x: 500, y: 300, color: "#f39c12" },
            { id: 6, text: "Знание", x: 200, y: 250, color: "#1abc9c" },
            { id: 7, text: "Мнение", x: 600, y: 250, color: "#34495e" },
            { id: 8, text: "Истина", x: 300, y: 350, color: "#8e44ad" },
            { id: 9, text: "Бытие", x: 400, y: 200, color: "#16a085" },
            { id: 10, text: "Становление", x: 500, y: 200, color: "#d35400" },
            { id: 11, text: "Разум", x: 200, y: 150, color: "#7f8c8d" },
            { id: 12, text: "Красота", x: 600, y: 50, color: "#27ae60" },
            { id: 13, text: "Справедливость", x: 700, y: 100, color: "#f1c40f" }
        ],
        edges: [
            { id: 1, source: 2, target: 1, type: "Иерархическая (А подчиняет Б)", bidirectional: false },
            { id: 2, source: 3, target: 1, type: "Иерархическая (А подчиняет Б)", bidirectional: false },
            { id: 3, source: 1, target: 9, type: "Тождество (А тождественно Б)", bidirectional: true },
            { id: 4, source: 5, target: 10, type: "Тождество (А тождественно Б)", bidirectional: true },
            { id: 5, source: 1, target: 5, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 6, source: 4, target: 1, type: "Эпистемическая (А познаёт Б)", bidirectional: false },
            { id: 7, source: 4, target: 5, type: "Эпистемическая (А познаёт Б)", bidirectional: false },
            { id: 8, source: 6, target: 1, type: "Репрезентационная (А представляет/отражает Б)", bidirectional: false },
            { id: 9, source: 7, target: 5, type: "Репрезентационная (А представляет/отражает Б)", bidirectional: false },
            { id: 10, source: 9, target: 8, type: "Тождество (А тождественно Б)", bidirectional: true },
            { id: 11, source: 1, target: 8, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 12, source: 4, target: 6, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 13, source: 11, target: 6, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 14, source: 3, target: 2, type: "Тождество (А тождественно Б)", bidirectional: true },
            { id: 15, source: 3, target: 12, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 16, source: 3, target: 13, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 17, source: 9, target: 10, type: "Диалектическое противоречие (А переходит в своё иное - Б)", bidirectional: true },
            { id: 18, source: 6, target: 7, type: "Диалектическое противоречие (А переходит в своё иное - Б)", bidirectional: true }
        ]
    },
    // 5. Экзистенциализм Сартра
    {
        name: "Экзистенциализм Сартра",
        description: "Философия Жан-Поля Сартра, фокусирующаяся на проблемах свободы, ответственности и аутентичности человеческого существования. Ключевые понятия: существование предшествует сущности, бытие-для-себя, бытие-в-себе, ничто, свобода, ответственность, тревога.",
        nodes: [
            { id: 1, text: "Существование", x: 300, y: 100, color: "#3498db" },
            { id: 2, text: "Сущность", x: 500, y: 100, color: "#2ecc71" },
            { id: 3, text: "Свобода", x: 400, y: 200, color: "#e74c3c" },
            { id: 4, text: "Ответственность", x: 600, y: 200, color: "#9b59b6" },
            { id: 5, text: "Бытие-для-себя", x: 200, y: 200, color: "#f39c12" },
            { id: 6, text: "Бытие-в-себе", x: 600, y: 300, color: "#1abc9c" },
            { id: 7, text: "Ничто", x: 300, y: 300, color: "#34495e" },
            { id: 8, text: "Сознание", x: 200, y: 400, color: "#8e44ad" },
            { id: 9, text: "Тревога", x: 500, y: 350, color: "#16a085" },
            { id: 10, text: "Другой", x: 700, y: 350, color: "#d35400" },
            { id: 11, text: "Проект", x: 400, y: 400, color: "#7f8c8d" },
            { id: 12, text: "Аутентичность", x: 600, y: 400, color: "#27ae60" },
            { id: 13, text: "Ситуация", x: 350, y: 500, color: "#f1c40f" }
        ],
        edges: [
            { id: 1, source: 1, target: 2, type: "Причинность (А вызывает Б)", bidirectional: false },
            { id: 2, source: 5, target: 1, type: "Тождество (А тождественно Б)", bidirectional: true },
            { id: 3, source: 6, target: 2, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 4, source: 1, target: 3, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 5, source: 3, target: 4, type: "Причинность (А вызывает Б)", bidirectional: false },
            { id: 6, source: 5, target: 7, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 7, source: 7, target: 3, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 8, source: 5, target: 8, type: "Тождество (А тождественно Б)", bidirectional: true },
            { id: 9, source: 3, target: 9, type: "Причинность (А вызывает Б)", bidirectional: false },
            { id: 10, source: 5, target: 10, type: "Диалектическое противоречие (А переходит в своё иное - Б)", bidirectional: true },
            { id: 11, source: 8, target: 11, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 12, source: 11, target: 12, type: "Телеологическая (А целеустремлено к Б)", bidirectional: false },
            { id: 13, source: 13, target: 3, type: "Диалектическое противоречие (А переходит в своё иное - Б)", bidirectional: true },
            { id: 14, source: 8, target: 6, type: "Эпистемическая (А познаёт Б)", bidirectional: false },
            { id: 15, source: 1, target: 13, type: "Феноменологическая (А является феноменом Б)", bidirectional: false },
            { id: 16, source: 5, target: 6, type: "Диалектическое противоречие (А переходит в своё иное - Б)", bidirectional: true },
            { id: 17, source: 10, target: 4, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false }
        ]
    },
    // 6. Логический атомизм (ранний Витгенштейн)
    {
        name: "Логический атомизм (ранний Витгенштейн)",
        description: "Философская концепция раннего Людвига Витгенштейна, изложенная в 'Логико-философском трактате'. Ключевые понятия: атомарный факт, логическое пространство, картина (образ), границы языка, показывание и высказывание, невысказываемое.",
        nodes: [
            { id: 1, text: "Мир", x: 400, y: 100, color: "#3498db" },
            { id: 2, text: "Факт", x: 300, y: 200, color: "#2ecc71" },
            { id: 3, text: "Язык", x: 500, y: 200, color: "#e74c3c" },
            { id: 4, text: "Логическая форма", x: 400, y: 300, color: "#9b59b6" },
            { id: 5, text: "Предложение", x: 600, y: 300, color: "#f39c12" },
            { id: 6, text: "Имя", x: 250, y: 300, color: "#1abc9c" },
            { id: 7, text: "Объект (Предмет)", x: 150, y: 200, color: "#34495e" },
            { id: 8, text: "Истина", x: 700, y: 200, color: "#8e44ad" },
            { id: 9, text: "Знак", x: 500, y: 400, color: "#16a085" },
            { id: 10, text: "Мысль", x: 300, y: 400, color: "#d35400" },
            { id: 11, text: "Невысказываемое", x: 600, y: 100, color: "#7f8c8d" },
            { id: 12, text: "Бытие", x: 200, y: 100, color: "#27ae60" },
            { id: 13, text: "Картина", x: 400, y: 500, color: "#f1c40f" }
        ],
        edges: [
            { id: 1, source: 1, target: 2, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 2, source: 7, target: 2, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 3, source: 3, target: 5, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 4, source: 6, target: 7, type: "Репрезентационная (А представляет/отражает Б)", bidirectional: false },
            { id: 5, source: 4, target: 3, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 6, source: 4, target: 1, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 7, source: 5, target: 2, type: "Репрезентационная (А представляет/отражает Б)", bidirectional: false },
            { id: 8, source: 5, target: 8, type: "Феноменологическая (А является феноменом Б)", bidirectional: false },
            { id: 9, source: 9, target: 5, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 10, source: 10, target: 13, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 11, source: 13, target: 1, type: "Репрезентационная (А представляет/отражает Б)", bidirectional: false },
            { id: 12, source: 13, target: 4, type: "Феноменологическая (А является феноменом Б)", bidirectional: false },
            { id: 13, source: 3, target: 11, type: "Герменевтическая (А истолковывает Б)", bidirectional: false },
            { id: 14, source: 11, target: 12, type: "Тождество (А тождественно Б)", bidirectional: true },
            { id: 15, source: 3, target: 10, type: "Репрезентационная (А представляет/отражает Б)", bidirectional: false },
            { id: 16, source: 5, target: 10, type: "Тождество (А тождественно Б)", bidirectional: true },
            { id: 17, source: 4, target: 8, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false }
        ]
    },
    // 7. Языковые игры (поздний Витгенштейн)
    {
        name: "Языковые игры (поздний Витгенштейн)",
        description: "Философская концепция позднего Людвига Витгенштейна, изложенная в 'Философских исследованиях'. Ключевые понятия: языковая игра, форма жизни, семейное сходство, следование правилу, приватный язык, терапевтическая функция философии.",
        nodes: [
            { id: 1, text: "Язык", x: 400, y: 100, color: "#3498db" },
            { id: 2, text: "Языковая игра", x: 600, y: 150, color: "#2ecc71" },
            { id: 3, text: "Форма жизни", x: 200, y: 150, color: "#e74c3c" },
            { id: 4, text: "Значение", x: 400, y: 250, color: "#9b59b6" },
            { id: 5, text: "Правило", x: 500, y: 350, color: "#f39c12" },
            { id: 6, text: "Практика", x: 300, y: 350, color: "#1abc9c" },
            { id: 7, text: "Общность", x: 200, y: 450, color: "#34495e" },
            { id: 8, text: "Знак", x: 600, y: 250, color: "#8e44ad" },
            { id: 9, text: "Семейное сходство", x: 400, y: 450, color: "#16a085" },
            { id: 10, text: "Понимание", x: 600, y: 450, color: "#d35400" },
            { id: 11, text: "Сознание", x: 700, y: 350, color: "#7f8c8d" },
            { id: 12, text: "Мир", x: 150, y: 250, color: "#27ae60" },
            { id: 13, text: "Философия", x: 750, y: 250, color: "#f1c40f" }
        ],
        edges: [
            { id: 1, source: 3, target: 1, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 2, source: 1, target: 2, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 3, source: 3, target: 2, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 4, source: 4, target: 6, type: "Тождество (А тождественно Б)", bidirectional: true },
            { id: 5, source: 6, target: 5, type: "Феноменологическая (А является феноменом Б)", bidirectional: false },
            { id: 6, source: 2, target: 5, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 7, source: 7, target: 5, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 8, source: 8, target: 4, type: "Диалектическое противоречие (А переходит в своё иное - Б)", bidirectional: true },
            { id: 9, source: 2, target: 9, type: "Феноменологическая (А является феноменом Б)", bidirectional: false },
            { id: 10, source: 10, target: 5, type: "Эпистемическая (А познаёт Б)", bidirectional: false },
            { id: 11, source: 10, target: 2, type: "Герменевтическая (А истолковывает Б)", bidirectional: false },
            { id: 12, source: 11, target: 1, type: "Эпистемическая (А познаёт Б)", bidirectional: false },
            { id: 13, source: 1, target: 12, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: true },
            { id: 14, source: 13, target: 1, type: "Герменевтическая (А истолковывает Б)", bidirectional: false },
            { id: 15, source: 7, target: 9, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 16, source: 2, target: 12, type: "Репрезентационная (А представляет/отражает Б)", bidirectional: false },
            { id: 17, source: 13, target: 11, type: "Эпистемическая (А познаёт Б)", bidirectional: false }
        ]
    },
    // 7. Языковые игры (поздний Витгенштейн)
    {
        name: "Языковые игры (поздний Витгенштейн)",
        description: "Философская концепция позднего Людвига Витгенштейна, изложенная в 'Философских исследованиях'. Ключевые понятия: языковая игра, форма жизни, семейное сходство, следование правилу, приватный язык, терапевтическая функция философии.",
        nodes: [
            { id: 1, text: "Язык", x: 400, y: 100, color: "#3498db" },
            { id: 2, text: "Языковая игра", x: 600, y: 150, color: "#2ecc71" },
            { id: 3, text: "Форма жизни", x: 200, y: 150, color: "#e74c3c" },
            { id: 4, text: "Значение", x: 400, y: 250, color: "#9b59b6" },
            { id: 5, text: "Правило", x: 500, y: 350, color: "#f39c12" },
            { id: 6, text: "Практика", x: 300, y: 350, color: "#1abc9c" },
            { id: 7, text: "Общность", x: 200, y: 450, color: "#34495e" },
            { id: 8, text: "Знак", x: 600, y: 250, color: "#8e44ad" },
            { id: 9, text: "Семейное сходство", x: 400, y: 450, color: "#16a085" },
            { id: 10, text: "Понимание", x: 600, y: 450, color: "#d35400" },
            { id: 11, text: "Сознание", x: 700, y: 350, color: "#7f8c8d" },
            { id: 12, text: "Мир", x: 150, y: 250, color: "#27ae60" },
            { id: 13, text: "Философия", x: 750, y: 250, color: "#f1c40f" }
        ],
        edges: [
            { id: 1, source: 3, target: 1, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 2, source: 1, target: 2, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 3, source: 3, target: 2, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 4, source: 4, target: 6, type: "Тождество (А тождественно Б)", bidirectional: true },
            { id: 5, source: 6, target: 5, type: "Феноменологическая (А является феноменом Б)", bidirectional: false },
            { id: 6, source: 2, target: 5, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 7, source: 7, target: 5, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 8, source: 8, target: 4, type: "Диалектическое противоречие (А переходит в своё иное - Б)", bidirectional: true },
            { id: 9, source: 2, target: 9, type: "Феноменологическая (А является феноменом Б)", bidirectional: false },
            { id: 10, source: 10, target: 5, type: "Эпистемическая (А познаёт Б)", bidirectional: false },
            { id: 11, source: 10, target: 2, type: "Герменевтическая (А истолковывает Б)", bidirectional: false },
            { id: 12, source: 11, target: 1, type: "Эпистемическая (А познаёт Б)", bidirectional: false },
            { id: 13, source: 1, target: 12, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: true },
            { id: 14, source: 13, target: 1, type: "Герменевтическая (А истолковывает Б)", bidirectional: false },
            { id: 15, source: 7, target: 9, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 16, source: 2, target: 12, type: "Репрезентационная (А представляет/отражает Б)", bidirectional: false },
            { id: 17, source: 13, target: 11, type: "Эпистемическая (А познаёт Б)", bidirectional: false }
        ]
    },
    // 8. Трансцендентальный идеализм Канта
    {
        name: "Трансцендентальный идеализм Канта",
        description: "Философская система Иммануила Канта, исследующая границы и возможности человеческого познания. Ключевые понятия: вещь-в-себе (ноумен), явление (феномен), трансцендентальные формы чувственности (пространство и время), категории рассудка, трансцендентальное единство апперцепции, регулятивные идеи разума.",
        nodes: [
            { id: 1, text: "Сознание", x: 400, y: 100, color: "#3498db" },
            { id: 2, text: "Вещь-в-себе", x: 200, y: 150, color: "#2ecc71" },
            { id: 3, text: "Явление", x: 350, y: 200, color: "#e74c3c" },
            { id: 4, text: "Пространство", x: 250, y: 300, color: "#9b59b6" },
            { id: 5, text: "Время", x: 350, y: 300, color: "#f39c12" },
            { id: 6, text: "Рассудок", x: 500, y: 200, color: "#1abc9c" },
            { id: 7, text: "Разум", x: 600, y: 100, color: "#34495e" },
            { id: 8, text: "Категории", x: 500, y: 300, color: "#8e44ad" },
            { id: 9, text: "Опыт", x: 400, y: 400, color: "#16a085" },
            { id: 10, text: "Априорное", x: 600, y: 200, color: "#d35400" },
            { id: 11, text: "Апостериорное", x: 600, y: 350, color: "#7f8c8d" },
            { id: 12, text: "Идеи разума", x: 700, y: 200, color: "#27ae60" },
            { id: 13, text: "Трансцендентальное единство апперцепции", x: 300, y: 50, color: "#f1c40f" },
            { id: 14, text: "Свобода", x: 700, y: 300, color: "#3498db" },
            { id: 15, text: "Императив", x: 550, y: 450, color: "#2ecc71" }
        ],
        edges: [
            { id: 1, source: 1, target: 2, type: "Эпистемическая (А познаёт Б)", bidirectional: false },
            { id: 2, source: 2, target: 3, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 3, source: 4, target: 3, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 4, source: 5, target: 3, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 5, source: 1, target: 4, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 6, source: 1, target: 5, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 7, source: 6, target: 3, type: "Эпистемическая (А познаёт Б)", bidirectional: false },
            { id: 8, source: 6, target: 8, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 9, source: 8, target: 9, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 10, source: 13, target: 1, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 11, source: 7, target: 12, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 12, source: 10, target: 8, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 13, source: 11, target: 9, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 14, source: 7, target: 14, type: "Эпистемическая (А познаёт Б)", bidirectional: false },
            { id: 15, source: 14, target: 15, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 16, source: 6, target: 7, type: "Иерархическая (А подчиняет Б)", bidirectional: false },
            { id: 17, source: 12, target: 9, type: "Телеологическая (А целеустремлено к Б)", bidirectional: false },
            { id: 18, source: 7, target: 6, type: "Иерархическая (А подчиняет Б)", bidirectional: false },
            { id: 19, source: 13, target: 8, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false }
        ]
    },
    // 9. Абсолютный идеализм Гегеля
    {
        name: "Абсолютный идеализм Гегеля",
        description: "Философская система Георга Вильгельма Фридриха Гегеля, рассматривающая действительность как саморазвитие Абсолютной Идеи. Ключевые понятия: диалектика, отрицание отрицания, снятие, абсолютный дух, в-себе-бытие, для-себя-бытие, в-себе-и-для-себя-бытие, субъективный, объективный и абсолютный дух.",
        nodes: [
            { id: 1, text: "Абсолютная Идея", x: 400, y: 100, color: "#3498db" },
            { id: 2, text: "Бытие", x: 300, y: 200, color: "#2ecc71" },
            { id: 3, text: "Ничто", x: 500, y: 200, color: "#e74c3c" },
            { id: 4, text: "Становление", x: 400, y: 250, color: "#9b59b6" },
            { id: 5, text: "В-себе-бытие", x: 250, y: 300, color: "#f39c12" },
            { id: 6, text: "Для-себя-бытие", x: 400, y: 350, color: "#1abc9c" },
            { id: 7, text: "В-себе-и-для-себя-бытие", x: 550, y: 300, color: "#34495e" },
            { id: 8, text: "Субъективный дух", x: 250, y: 450, color: "#8e44ad" },
            { id: 9, text: "Объективный дух", x: 400, y: 500, color: "#16a085" },
            { id: 10, text: "Абсолютный дух", x: 550, y: 450, color: "#d35400" },
            { id: 11, text: "Диалектика", x: 200, y: 150, color: "#7f8c8d" },
            { id: 12, text: "Снятие", x: 600, y: 150, color: "#27ae60" },
            { id: 13, text: "Сознание", x: 300, y: 400, color: "#f1c40f" },
            { id: 14, text: "Свобода", x: 500, y: 400, color: "#3498db" },
            { id: 15, text: "История", x: 650, y: 350, color: "#2ecc71" }
        ],
        edges: [
            { id: 1, source: 1, target: 2, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 2, source: 2, target: 3, type: "Диалектическое противоречие (А переходит в своё иное - Б)", bidirectional: true },
            { id: 3, source: 2, target: 4, type: "Диалектическое противоречие (А переходит в своё иное - Б)", bidirectional: false },
            { id: 4, source: 3, target: 4, type: "Диалектическое противоречие (А переходит в своё иное - Б)", bidirectional: false },
            { id: 5, source: 4, target: 5, type: "Эволюционная (А развивается в Б)", bidirectional: false },
            { id: 6, source: 5, target: 6, type: "Эволюционная (А развивается в Б)", bidirectional: false },
            { id: 7, source: 6, target: 7, type: "Эволюционная (А развивается в Б)", bidirectional: false },
            { id: 8, source: 7, target: 1, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: true },
            { id: 9, source: 11, target: 1, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 10, source: 11, target: 12, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 11, source: 12, target: 7, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 12, source: 1, target: 8, type: "Эволюционная (А развивается в Б)", bidirectional: false },
            { id: 13, source: 8, target: 9, type: "Эволюционная (А развивается в Б)", bidirectional: false },
            { id: 14, source: 9, target: 10, type: "Эволюционная (А развивается в Б)", bidirectional: false },
            { id: 15, source: 10, target: 1, type: "Тождество (А тождественно Б)", bidirectional: true },
            { id: 16, source: 13, target: 8, type: "Тождество (А тождественно Б)", bidirectional: true },
            { id: 17, source: 14, target: 9, type: "Феноменологическая (А является феноменом Б)", bidirectional: false },
            { id: 18, source: 15, target: 9, type: "Феноменологическая (А является феноменом Б)", bidirectional: false },
            { id: 19, source: 15, target: 1, type: "Телеологическая (А целеустремлено к Б)", bidirectional: false }
        ]
    },
    // 9. Абсолютный идеализм Гегеля
    {
        name: "Абсолютный идеализм Гегеля",
        description: "Философская система Георга Вильгельма Фридриха Гегеля, рассматривающая действительность как саморазвитие Абсолютной Идеи. Ключевые понятия: диалектика, отрицание отрицания, снятие, абсолютный дух, в-себе-бытие, для-себя-бытие, в-себе-и-для-себя-бытие, субъективный, объективный и абсолютный дух.",
        nodes: [
            { id: 1, text: "Абсолютная Идея", x: 400, y: 100, color: "#3498db" },
            { id: 2, text: "Бытие", x: 300, y: 200, color: "#2ecc71" },
            { id: 3, text: "Ничто", x: 500, y: 200, color: "#e74c3c" },
            { id: 4, text: "Становление", x: 400, y: 250, color: "#9b59b6" },
            { id: 5, text: "В-себе-бытие", x: 250, y: 300, color: "#f39c12" },
            { id: 6, text: "Для-себя-бытие", x: 400, y: 350, color: "#1abc9c" },
            { id: 7, text: "В-себе-и-для-себя-бытие", x: 550, y: 300, color: "#34495e" },
            { id: 8, text: "Субъективный дух", x: 250, y: 450, color: "#8e44ad" },
            { id: 9, text: "Объективный дух", x: 400, y: 500, color: "#16a085" },
            { id: 10, text: "Абсолютный дух", x: 550, y: 450, color: "#d35400" },
            { id: 11, text: "Диалектика", x: 200, y: 150, color: "#7f8c8d" },
            { id: 12, text: "Снятие", x: 600, y: 150, color: "#27ae60" },
            { id: 13, text: "Сознание", x: 300, y: 400, color: "#f1c40f" },
            { id: 14, text: "Свобода", x: 500, y: 400, color: "#3498db" },
            { id: 15, text: "История", x: 650, y: 350, color: "#2ecc71" }
        ],
        edges: [
            { id: 1, source: 1, target: 2, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 2, source: 2, target: 3, type: "Диалектическое противоречие (А переходит в своё иное - Б)", bidirectional: true },
            { id: 3, source: 2, target: 4, type: "Диалектическое противоречие (А переходит в своё иное - Б)", bidirectional: false },
            { id: 4, source: 3, target: 4, type: "Диалектическое противоречие (А переходит в своё иное - Б)", bidirectional: false },
            { id: 5, source: 4, target: 5, type: "Эволюционная (А развивается в Б)", bidirectional: false },
            { id: 6, source: 5, target: 6, type: "Эволюционная (А развивается в Б)", bidirectional: false },
            { id: 7, source: 6, target: 7, type: "Эволюционная (А развивается в Б)", bidirectional: false },
            { id: 8, source: 7, target: 1, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: true },
            { id: 9, source: 11, target: 1, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 10, source: 11, target: 12, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 11, source: 12, target: 7, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 12, source: 1, target: 8, type: "Эволюционная (А развивается в Б)", bidirectional: false },
            { id: 13, source: 8, target: 9, type: "Эволюционная (А развивается в Б)", bidirectional: false },
            { id: 14, source: 9, target: 10, type: "Эволюционная (А развивается в Б)", bidirectional: false },
            { id: 15, source: 10, target: 1, type: "Тождество (А тождественно Б)", bidirectional: true },
            { id: 16, source: 13, target: 8, type: "Тождество (А тождественно Б)", bidirectional: true },
            { id: 17, source: 14, target: 9, type: "Феноменологическая (А является феноменом Б)", bidirectional: false },
            { id: 18, source: 15, target: 9, type: "Феноменологическая (А является феноменом Б)", bidirectional: false },
            { id: 19, source: 15, target: 1, type: "Телеологическая (А целеустремлено к Б)", bidirectional: false }
        ]
    },
    // 10. Дуализм Декарта
    {
        name: "Дуализм Декарта",
        description: "Философская система Рене Декарта, основанная на радикальном разделении между мыслящей и протяженной субстанциями. Ключевые понятия: методическое сомнение, cogito ergo sum, врожденные идеи, мыслящая субстанция (res cogitans), протяженная субстанция (res extensa), Бог как гарант истинности познания, психофизическая проблема.",
        nodes: [
            { id: 1, text: "Cogito", x: 400, y: 100, color: "#3498db" },
            { id: 2, text: "Мыслящая субстанция", x: 250, y: 200, color: "#2ecc71" },
            { id: 3, text: "Протяженная субстанция", x: 550, y: 200, color: "#e74c3c" },
            { id: 4, text: "Бог", x: 400, y: 50, color: "#9b59b6" },
            { id: 5, text: "Сомнение", x: 300, y: 150, color: "#f39c12" },
            { id: 6, text: "Истина", x: 500, y: 150, color: "#1abc9c" },
            { id: 7, text: "Врожденные идеи", x: 200, y: 300, color: "#34495e" },
            { id: 8, text: "Ясность и отчетливость", x: 400, y: 250, color: "#8e44ad" },
            { id: 9, text: "Тело", x: 600, y: 300, color: "#16a085" },
            { id: 10, text: "Душа", x: 200, y: 400, color: "#d35400" },
            { id: 11, text: "Шишковидная железа", x: 400, y: 350, color: "#7f8c8d" },
            { id: 12, text: "Механицизм", x: 600, y: 400, color: "#27ae60" },
            { id: 13, text: "Свобода воли", x: 300, y: 450, color: "#f1c40f" }
        ],
        edges: [
            { id: 1, source: 5, target: 1, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 2, source: 1, target: 2, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 3, source: 1, target: 6, type: "Эпистемическая (А познаёт Б)", bidirectional: false },
            { id: 4, source: 4, target: 6, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 5, source: 4, target: 2, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 6, source: 4, target: 3, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 7, source: 2, target: 3, type: "Диалектическое противоречие (А переходит в своё иное - Б)", bidirectional: true },
            { id: 8, source: 4, target: 7, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 9, source: 8, target: 6, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 10, source: 2, target: 10, type: "Тождество (А тождественно Б)", bidirectional: true },
            { id: 11, source: 3, target: 9, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 12, source: 11, target: 2, type: "Причинность (А вызывает Б)", bidirectional: true },
            { id: 13, source: 11, target: 3, type: "Причинность (А вызывает Б)", bidirectional: true },
            { id: 14, source: 12, target: 3, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 15, source: 2, target: 7, type: "Эпистемическая (А познаёт Б)", bidirectional: false },
            { id: 16, source: 10, target: 13, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 17, source: 7, target: 8, type: "Феноменологическая (А является феноменом Б)", bidirectional: false }
        ]
    },
    // 11. Монадология Лейбница
    {
        name: "Монадология Лейбница",
        description: "Философская система Готфрида Вильгельма Лейбница, основанная на концепции монад как простых субстанций. Ключевые понятия: монада, предустановленная гармония, принцип достаточного основания, принцип тождества неразличимых, перцепция и апперцепция, возможные миры, теодицея.",
        nodes: [
            { id: 1, text: "Монада", x: 400, y: 100, color: "#3498db" },
            { id: 2, text: "Бог", x: 400, y: 50, color: "#2ecc71" },
            { id: 3, text: "Предустановленная гармония", x: 600, y: 150, color: "#e74c3c" },
            { id: 4, text: "Перцепция", x: 250, y: 200, color: "#9b59b6" },
            { id: 5, text: "Апперцепция", x: 400, y: 200, color: "#f39c12" },
            { id: 6, text: "Принцип достаточного основания", x: 200, y: 100, color: "#1abc9c" },
            { id: 7, text: "Возможные миры", x: 600, y: 100, color: "#34495e" },
            { id: 8, text: "Субстанция", x: 300, y: 300, color: "#8e44ad" },
            { id: 9, text: "Душа", x: 500, y: 300, color: "#16a085" },
            { id: 10, text: "Лучший из возможных миров", x: 500, y: 50, color: "#d35400" },
            { id: 11, text: "Закон непрерывности", x: 200, y: 250, color: "#7f8c8d" },
            { id: 12, text: "Принцип тождества неразличимых", x: 300, y: 50, color: "#27ae60" },
            { id: 13, text: "Истина", x: 600, y: 250, color: "#f1c40f" }
        ],
        edges: [
            { id: 1, source: 1, target: 8, type: "Тождество (А тождественно Б)", bidirectional: true },
            { id: 2, source: 2, target: 1, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 3, source: 2, target: 3, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 4, source: 1, target: 4, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 5, source: 4, target: 5, type: "Эволюционная (А развивается в Б)", bidirectional: false },
            { id: 6, source: 6, target: 1, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 7, source: 2, target: 7, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 8, source: 7, target: 10, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 9, source: 3, target: 1, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 10, source: 1, target: 9, type: "Феноменологическая (А является феноменом Б)", bidirectional: false },
            { id: 11, source: 11, target: 1, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 12, source: 12, target: 1, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 13, source: 6, target: 13, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 14, source: 3, target: 13, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 15, source: 5, target: 9, type: "Тождество (А тождественно Б)", bidirectional: true },
            { id: 16, source: 2, target: 6, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false },
            { id: 17, source: 2, target: 12, type: "Конституирующая (А формирует/конституирует Б)", bidirectional: false }
        ]
    }
];

// Дополненный перечень философских категорий
const categories = [
    // Исходные категории
    "Бытие", "Сущность", "Сознание", "Материя", "Субстанция", 
    "Субъект", "Мир", "Истина", "Знание", "Язык", 
    "Знак", "Время", "Пространство", "Свобода", "Необходимость", 
    "Ценность", "Трансцендентное", "Имманентное", "Единое", "Множественное", 
    "Целое", "Разрыв",
    
    // Добавленные категории для Феноменологии Гуссерля
    "Интенциональность", "Феномен", "Трансцендентальное Эго", "Жизненный мир", 
    "Ноэзис", "Ноэма",
    
    // Добавленные категории для Диалектического материализма Маркса
    "Практика", "Диалектика", "Общественные отношения", "Производительные силы", 
    "Надстройка", "Историческая закономерность", "Отчуждение",
    
    // Добавленные категории для Онтологии Хайдеггера
    "Сущее", "Dasein (Присутствие)", "Забота", "Бытие-к-смерти", "Подручность", 
    "Историчность", "Разомкнутость", "Экзистенция", "Ничто",
    
    // Добавленные категории для Платоновского идеализма
    "Идея (Эйдос)", "Благо", "Душа", "Материальный мир", "Мнение", 
    "Становление", "Разум", "Красота", "Справедливость",
    
    // Добавленные категории для Экзистенциализма Сартра
    "Существование", "Бытие-для-себя", "Бытие-в-себе", "Ответственность", 
    "Тревога", "Другой", "Проект", "Аутентичность", "Ситуация",
    
    // Добавленные категории для Логического атомизма (ранний Витгенштейн)
    "Факт", "Логическая форма", "Предложение", "Имя", "Объект (Предмет)",
    "Мысль", "Невысказываемое", "Картина",
    
    // Добавленные категории для Языковых игр (поздний Витгенштейн)
    "Языковая игра", "Форма жизни", "Значение", "Правило", "Общность",
    "Семейное сходство", "Понимание", "Философия",
    
    // Добавленные категории для Трансцендентального идеализма Канта
    "Вещь-в-себе", "Явление", "Рассудок", "Категории", "Опыт",
    "Априорное", "Апостериорное", "Идеи разума", "Трансцендентальное единство апперцепции", "Императив",
    
    // Добавленные категории для Абсолютного идеализма Гегеля
    "Абсолютная Идея", "В-себе-бытие", "Для-себя-бытие", "В-себе-и-для-себя-бытие",
    "Субъективный дух", "Объективный дух", "Абсолютный дух", "Диалектика", "Снятие", "История",
    
    // Добавленные категории для Дуализма Декарта
    "Cogito", "Мыслящая субстанция", "Протяженная субстанция", "Бог", "Сомнение",
    "Врожденные идеи", "Ясность и отчетливость", "Тело", "Душа", "Шишковидная железа", "Механицизм", "Свобода воли",
    
    // Добавленные категории для Монадологии Лейбница
    "Монада", "Предустановленная гармония", "Перцепция", "Апперцепция", 
    "Принцип достаточного основания", "Возможные миры", "Лучший из возможных миров",
    "Закон непрерывности", "Принцип тождества неразличимых"
];

// Типы фундаментальных философских связей
const relationTypes = [
    "Причинность (А вызывает Б)",
    "Тождество (А тождественно Б)",
    "Дополнение (А дополняет Б)",
    "Диалектическое противоречие (А переходит в своё иное - Б)",
    "Иерархическая (А подчиняет Б)",
    "Герменевтическая (А истолковывает Б)",
    "Репрезентационная (А представляет/отражает Б)",
    "Конституирующая (А формирует/конституирует Б)",
    "Эпистемическая (А познаёт Б)",
    "Феноменологическая (А является феноменом Б)",
    "Эволюционная (А развивается в Б)",
    "Аксиологическая (А ценностно определяет Б)",
    "Телеологическая (А целеустремлено к Б)"
];