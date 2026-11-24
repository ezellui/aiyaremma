'critical-power': {
    name: "Индекс критической силы (Critical Power Index)",
    
    description: "Измеряет способность концепции эффективно критиковать, деконструировать и опровергать другие философские идеи. В отличие от революционности (создание нового) и проблемности (порождение вопросов), критическая сила оценивает аналитическую и разрушительную мощь концепции.",
    
    interpretation: () => `Высокое значение указывает на концепции с сильным критическим потенциалом:<br><br>
<strong>Эффективность</strong> (главное): критика порождает последствия - развития, синтезы, пересмотр идей<br>
<strong>Качество целей</strong>: различаются критики центральных (>15 связей), средних (5-15) и периферийных (<5) концепций<br>
<strong>Конструктивность</strong>: ratio critique/synthesize показывает тип - конструктивная (>0.5, как Кант) или деструктивная (<0.3, как Ницше)<br>
<strong>Широта атаки</strong>: количество философов/эпох, подвергнутых критике<br>
<strong>Временная перспектива</strong>: ретроспективная (традиции) vs синхронная (современники)<br><br>
Индекс взвешивает активность через эффективность (реальное воздействие).`,
    
    usage: () => `<strong>Используйте для поиска:</strong><br><br>
<strong>Деструкторы парадигм</strong> (effectiveness > 30, низкая конструктивность): Юм, Секст Эмпирик, Ницше<br>
<strong>Конструктивные критики</strong> (effectiveness > 40, высокая конструктивность): Кант, Гегель, Деррида<br>
<strong>Системные критики</strong> (targetedPhilosophers > 5): Аристотель, Фуко, Витгенштейн<br>
<strong>Точечные критики</strong> (высокая effectiveness, мало целей): Рассел, Гёдель<br><br>
<strong>Сравнение:</strong> revolutionaryIndex (создание) → problemGenerationIndex (вопросы) → criticalPowerIndex (разрушение)<br><br>
<strong>Пороги фильтрации:</strong> total > 80 (мощные), effectiveness > 40 (эффективные), majorTargets > 2 (атакуют центр), constructivenessRatio > 0.5 (конструктивные) или < 0.3 (деструктивные)`,
    
    formula: () => `<strong>Формула:</strong><br>
CPI = WeightedActivity×1.0 + MajorTargetBonus×1.5 + <strong>Effectiveness×2.0</strong> + TargetedPhilosophers×0.8 + EraSpan/100 + ConstructivenessBonus(3)<br><br>
<strong>Ключевые компоненты:</strong><br>
<strong>WeightedActivity:</strong> Σ(critique×2 + oppose×3) × weight<br>
<strong>MajorTargetBonus:</strong> количество критик центральных концепций (>15 связей) × 2<br>
<strong>Effectiveness:</strong> последствия критики (develop/synthesize у целей) + собственные развития × 2<br>
<strong>TargetedPhilosophers:</strong> уникальные философы под критикой<br>
<strong>EraSpan:</strong> временной диапазон критикуемых (в годах)<br>
<strong>ConstructivenessBonus:</strong> +3 если syntheses/critiques > 0.3<br><br>
<strong>Категории целей:</strong> Major (>15 связей), Medium (5-15), Minor (<5)<br>
<strong>Типы:</strong> ретроспективная (birth < текущего) vs синхронная (|birth_diff| < 30)`
}