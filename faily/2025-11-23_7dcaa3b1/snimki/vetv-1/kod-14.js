'critical-power': {
    name: "Индекс критической силы (Critical Power Index)",
    
    description: "Измеряет способность концепции эффективно критиковать, деконструировать и опровергать другие философские идеи. В отличие от революционности (создание нового) и проблемности (порождение вопросов), критическая сила оценивает аналитическую и разрушительную мощь концепции.",
    
    interpretation: () => `Высокое значение указывает на концепции с сильным критическим потенциалом:<br><br>

<strong>• Эффективность (главное):</strong> критика порождает последствия - развития, синтезы, пересмотр критикуемых идей<br><br>

<strong>• Качество целей:</strong> различаются критики центральных концепций (major: >15 связей), средних (5-15) и периферийных (<5)<br><br>

<strong>• Конструктивность:</strong> соотношение critique/oppose к synthesize показывает тип критики:<br>
&nbsp;&nbsp;- Высокий ratio (>0.5): конструктивная критика (Кант - критикует, чтобы построить)<br>
&nbsp;&nbsp;- Низкий ratio (<0.3): деструктивная критика (Ницше, скептики - разрушают без альтернативы)<br><br>

<strong>• Широта атаки:</strong> количество философов/эпох, подвергнутых критике<br><br>

<strong>• Временная перспектива:</strong> ретроспективная критика (традиции) vs синхронная (современников)<br><br>

Индекс взвешивает активность (количество критик) через эффективность (реальное воздействие).`,
    
    usage: () => `<strong>Используйте для поиска:</strong><br><br>

<strong>1. Деструкторов парадигм</strong> (effectiveness > 30, low constructiveness):<br>
&nbsp;&nbsp;• Юм: разрушение причинности, индукции, субстанции<br>
&nbsp;&nbsp;• Секст Эмпирик: тотальная критика догматизма<br>
&nbsp;&nbsp;• Ницше: деконструкция морали, истины, метафизики<br><br>

<strong>2. Конструктивных критиков</strong> (effectiveness > 40, high constructiveness):<br>
&nbsp;&nbsp;• Кант: критика через построение (трансцендентальная философия)<br>
&nbsp;&nbsp;• Гегель: имманентная критика как развитие<br>
&nbsp;&nbsp;• Деррида: деконструкция с новой герменевтикой<br><br>

<strong>3. Системных критиков</strong> (targetedPhilosophers > 5):<br>
&nbsp;&nbsp;• Аристотель vs досократики<br>
&nbsp;&nbsp;• Фуко vs вся западная эпистема<br>
&nbsp;&nbsp;• Витгенштейн vs традиционная философия языка<br><br>

<strong>4. Точечных, но мощных критиков</strong> (high effectiveness, few targets):<br>
&nbsp;&nbsp;• Рассел → Фреге (парадокс перевернул логику)<br>
&nbsp;&nbsp;• Гёдель → Гильберт (теоремы разрушили программу формализации)<br><br>

<strong>Сравнение с другими метриками:</strong><br>
&nbsp;&nbsp;• revolutionaryIndex: о создании нового (Декарт: Cogito)<br>
&nbsp;&nbsp;• problemGenerationIndex: о порождении вопросов (Кант: вещь-в-себе)<br>
&nbsp;&nbsp;• criticalPowerIndex: о разрушении старого (Юм: причинность)<br><br>

<strong>Фильтрация:</strong><br>
&nbsp;&nbsp;• total > 80: мощные критические концепции<br>
&nbsp;&nbsp;• effectiveness > 40: реально эффективная критика<br>
&nbsp;&nbsp;• majorTargets > 2: атака на центральные идеи<br>
&nbsp;&nbsp;• constructivenessRatio > 0.5: конструктивная критика<br>
&nbsp;&nbsp;• constructivenessRatio < 0.3: чистая деструкция`,
    
    formula: () => `<strong>Интегральная формула:</strong><br><br>

CPI = WeightedActivity×1.0 + MajorTargetBonus×1.5 + Effectiveness×2.0 +<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;TargetedPhilosophers×0.8 + EraSpan/100 + ConstructivenessBonus(3)<br><br>

<strong>Компоненты:</strong><br><br>

<strong>1. WeightedActivity</strong> = Σ(critique×2 + oppose×3) × weight<br>
&nbsp;&nbsp;Базовая критическая активность с учётом веса связей<br><br>

<strong>2. MajorTargetBonus</strong> = #targets_with_>15_incoming_links × 2<br>
&nbsp;&nbsp;Бонус за критику центральных, влиятельных концепций<br><br>

<strong>3. Effectiveness</strong> (главное!) = CriticalConsequences + OwnDevelopments×2<br>
&nbsp;&nbsp;• CriticalConsequences: сумма develop/synthesize/complement у критикуемых целей<br>
&nbsp;&nbsp;• OwnDevelopments: develop/synthesize, порождённые самой критикой<br>
&nbsp;&nbsp;Измеряет реальное воздействие, а не просто количество<br><br>

<strong>4. TargetedPhilosophers</strong> = количество уникальных философов, подвергнутых критике<br>
&nbsp;&nbsp;Широта атаки<br><br>

<strong>5. EraSpan</strong> = max(target_birth) - min(target_birth)<br>
&nbsp;&nbsp;Временной диапазон критикуемых философов (в годах)<br><br>

<strong>6. ConstructivenessBonus</strong> = 3 если (syntheses / critiques) > 0.3, иначе 0<br>
&nbsp;&nbsp;Бонус за конструктивную критику<br><br>

<strong>Категоризация целей:</strong><br>
&nbsp;&nbsp;• Major target: >15 входящих связей (центральные концепции)<br>
&nbsp;&nbsp;• Medium target: 5-15 входящих связей<br>
&nbsp;&nbsp;• Minor target: <5 входящих связей<br><br>

<strong>Типы критики (по временной перспективе):</strong><br>
&nbsp;&nbsp;• Ретроспективная: критика философов из прошлого (birth < current_philosopher)<br>
&nbsp;&nbsp;• Синхронная: критика современников (|birth_diff| < 30 лет)`
}