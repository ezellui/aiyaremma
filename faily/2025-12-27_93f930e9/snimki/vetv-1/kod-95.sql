-- Таблица исторических контекстов
CREATE TABLE IF NOT EXISTS historical_contexts (
    context_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    concept_id UUID NOT NULL REFERENCES concepts(concept_id) ON DELETE CASCADE,
    time_period VARCHAR(100),
    historical_analysis TEXT,
    influences JSONB DEFAULT '[]',
    contemporaries JSONB DEFAULT '[]',
    subsequent_influence JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    interaction_id UUID REFERENCES claude_interactions(interaction_id)
);

-- Индексы для historical_contexts
CREATE INDEX idx_historical_contexts_concept ON historical_contexts(concept_id);
CREATE INDEX idx_historical_contexts_created ON historical_contexts(created_at);

-- Таблица практических применений
CREATE TABLE IF NOT EXISTS practical_applications (
    application_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    concept_id UUID NOT NULL REFERENCES concepts(concept_id) ON DELETE CASCADE,
    domains JSONB DEFAULT '[]',
    application_analysis TEXT,
    implementation_methods JSONB DEFAULT '[]',
    relevance_mappings JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    interaction_id UUID REFERENCES claude_interactions(interaction_id)
);

-- Индексы для practical_applications
CREATE INDEX idx_practical_applications_concept ON practical_applications(concept_id);
CREATE INDEX idx_practical_applications_created ON practical_applications(created_at);

-- Таблица эволюций концепций
CREATE TABLE IF NOT EXISTS concept_evolutions (
    evolution_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    concept_id UUID NOT NULL REFERENCES concepts(concept_id) ON DELETE CASCADE,
    target_concept_id UUID REFERENCES concepts(concept_id) ON DELETE SET NULL,
    evolution_context TEXT,
    suggested_changes JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    interaction_id UUID REFERENCES claude_interactions(interaction_id)
);

-- Индексы для concept_evolutions
CREATE INDEX idx_concept_evolutions_concept ON concept_evolutions(concept_id);
CREATE INDEX idx_concept_evolutions_target ON concept_evolutions(target_concept_id);
CREATE INDEX idx_concept_evolutions_created ON concept_evolutions(created_at);

-- Таблица диалогов
CREATE TABLE IF NOT EXISTS dialogue_interpretations (
    dialogue_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    philosophical_question TEXT NOT NULL,
    dialogue_content TEXT,
    discussion_points JSONB DEFAULT '[]',
    arguments JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    interaction_id UUID REFERENCES claude_interactions(interaction_id)
);

-- Индексы для dialogue_interpretations
CREATE INDEX idx_dialogue_interpretations_created ON dialogue_interpretations(created_at);

-- Таблица участников диалогов
CREATE TABLE IF NOT EXISTS dialogue_participants (
    participant_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dialogue_id UUID NOT NULL REFERENCES dialogue_interpretations(dialogue_id) ON DELETE CASCADE,
    concept_id UUID NOT NULL REFERENCES concepts(concept_id) ON DELETE CASCADE,
    role VARCHAR(100),
    key_theses JSONB DEFAULT '[]'
);

-- Индексы для dialogue_participants
CREATE INDEX idx_dialogue_participants_dialogue ON dialogue_participants(dialogue_id);
CREATE INDEX idx_dialogue_participants_concept ON dialogue_participants(concept_id);

-- Триггеры для автоматического обновления updated_at
DROP TRIGGER IF EXISTS update_historical_contexts_updated ON historical_contexts;
CREATE TRIGGER update_historical_contexts_updated
    BEFORE UPDATE ON historical_contexts
    FOR EACH ROW
    EXECUTE FUNCTION update_last_modified();

DROP TRIGGER IF EXISTS update_practical_applications_updated ON practical_applications;
CREATE TRIGGER update_practical_applications_updated
    BEFORE UPDATE ON practical_applications
    FOR EACH ROW
    EXECUTE FUNCTION update_last_modified();