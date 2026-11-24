-- Таблица взаимодействий с Claude
CREATE TABLE IF NOT EXISTS claude_interactions (
    interaction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    concept_id UUID REFERENCES concepts(concept_id) ON DELETE SET NULL,
    
    -- Данные запроса
    query_type VARCHAR(100) NOT NULL,
    query_content TEXT NOT NULL,
    query_parameters JSONB DEFAULT '{}',
    
    -- Данные ответа
    response_content TEXT,
    response_metadata JSONB DEFAULT '{}',
    
    -- Метрики
    interaction_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processing_time DECIMAL(10, 3), -- в секундах
    tokens_used INTEGER,
    
    -- Статус
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    error_message TEXT,
    
    -- API ключ
    used_user_key BOOLEAN DEFAULT FALSE
);

-- Индексы
CREATE INDEX idx_claude_user ON claude_interactions(user_id);
CREATE INDEX idx_claude_concept ON claude_interactions(concept_id) WHERE concept_id IS NOT NULL;
CREATE INDEX idx_claude_date ON claude_interactions(interaction_date DESC);
CREATE INDEX idx_claude_type ON claude_interactions(query_type);
CREATE INDEX idx_claude_status ON claude_interactions(status);

-- Комментарии
COMMENT ON TABLE claude_interactions IS 'История взаимодействий с Claude API';
COMMENT ON COLUMN claude_interactions.used_user_key IS 'Был ли использован пользовательский API ключ';

-- Таблица названий концепций
CREATE TABLE IF NOT EXISTS concept_names (
    name_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    concept_id UUID NOT NULL REFERENCES concepts(concept_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    analysis TEXT,
    alternative_names JSONB DEFAULT '[]',
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    interaction_id UUID REFERENCES claude_interactions(interaction_id) ON DELETE SET NULL,
    is_current BOOLEAN DEFAULT TRUE,
    
    CONSTRAINT unique_current_name UNIQUE (concept_id, is_current) WHERE is_current = TRUE
);

-- Индексы
CREATE INDEX idx_concept_names_concept ON concept_names(concept_id);
CREATE INDEX idx_concept_names_current ON concept_names(is_current) WHERE is_current = TRUE;

-- Комментарии
COMMENT ON TABLE concept_names IS 'История анализа и альтернативы названий концепций';

-- Таблица происхождения концепций
CREATE TABLE IF NOT EXISTS concept_origins (
    origin_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    concept_id UUID NOT NULL REFERENCES concepts(concept_id) ON DELETE CASCADE,
    parent_concepts JSONB DEFAULT '[]',
    influence_weights JSONB DEFAULT '{}',
    analysis TEXT,
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    interaction_id UUID REFERENCES claude_interactions(interaction_id) ON DELETE SET NULL
);

-- Индексы
CREATE INDEX idx_origins_concept ON concept_origins(concept_id);
CREATE INDEX idx_origins_parents ON concept_origins USING GIN (parent_concepts);

-- Комментарии
COMMENT ON TABLE concept_origins IS 'Анализ происхождения концепций';

-- Таблица трансформаций
CREATE TABLE IF NOT EXISTS transformations (
    transformation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID NOT NULL,
    source_type VARCHAR(50) NOT NULL CHECK (source_type IN ('graph', 'theses', 'concept')),
    target_id UUID NOT NULL,
    target_type VARCHAR(50) NOT NULL CHECK (target_type IN ('graph', 'theses', 'concept')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    interaction_id UUID REFERENCES claude_interactions(interaction_id) ON DELETE SET NULL,
    transformation_details JSONB DEFAULT '{}'
);

-- Индексы
CREATE INDEX idx_transform_source ON transformations(source_id, source_type);
CREATE INDEX idx_transform_target ON transformations(target_id, target_type);
CREATE INDEX idx_transform_date ON transformations(created_at DESC);

-- Комментарии
COMMENT ON TABLE transformations IS 'История трансформаций между графами и тезисами';

-- Таблица участников диалогов
CREATE TABLE IF NOT EXISTS dialogue_participants (
    participant_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dialogue_id UUID NOT NULL, -- Ссылка на MongoDB
    concept_id UUID NOT NULL REFERENCES concepts(concept_id) ON DELETE CASCADE,
    role VARCHAR(100),
    key_theses JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Индексы
CREATE INDEX idx_dialogue_part_dialogue ON dialogue_participants(dialogue_id);
CREATE INDEX idx_dialogue_part_concept ON dialogue_participants(concept_id);

-- Комментарии
COMMENT ON TABLE dialogue_participants IS 'Участники философских диалогов';