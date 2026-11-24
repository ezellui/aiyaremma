-- Таблица исторических контекстов (метаданные)
CREATE TABLE IF NOT EXISTS historical_contexts_meta (
    context_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    concept_id UUID NOT NULL REFERENCES concepts(concept_id) ON DELETE CASCADE,
    time_period VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    interaction_id UUID REFERENCES claude_interactions(interaction_id)
);

-- Индексы для historical_contexts_meta
CREATE INDEX idx_historical_contexts_concept ON historical_contexts_meta(concept_id);

-- Таблица эволюций концепций (метаданные)
CREATE TABLE IF NOT EXISTS concept_evolutions_meta (
    evolution_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    concept_id UUID NOT NULL REFERENCES concepts(concept_id) ON DELETE CASCADE,
    target_concept_id UUID REFERENCES concepts(concept_id) ON DELETE SET NULL,
    evolution_context TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    interaction_id UUID REFERENCES claude_interactions(interaction_id)
);

-- Индексы для concept_evolutions_meta
CREATE INDEX idx_concept_evolutions_concept ON concept_evolutions_meta(concept_id);
CREATE INDEX idx_concept_evolutions_target ON concept_evolutions_meta(target_concept_id);

-- Таблица диалогов (метаданные)
CREATE TABLE IF NOT EXISTS dialogue_interpretations_meta (
    dialogue_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    philosophical_question TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    interaction_id UUID REFERENCES claude_interactions(interaction_id)
);

-- Таблица участников диалогов
CREATE TABLE IF NOT EXISTS dialogue_participants (
    participant_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dialogue_id UUID NOT NULL REFERENCES dialogue_interpretations_meta(dialogue_id) ON DELETE CASCADE,
    concept_id UUID NOT NULL REFERENCES concepts(concept_id) ON DELETE CASCADE,
    role VARCHAR(100),
    key_theses JSONB DEFAULT '[]'
);

-- Индексы для dialogue_participants
CREATE INDEX idx_dialogue_participants_dialogue ON dialogue_participants(dialogue_id);
CREATE INDEX idx_dialogue_participants_concept ON dialogue_participants(concept_id);