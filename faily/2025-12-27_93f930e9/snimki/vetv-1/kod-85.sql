-- Таблица концепций
CREATE TABLE IF NOT EXISTS concepts (
    concept_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    creator_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    creation_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_synthesis BOOLEAN DEFAULT FALSE,
    parent_concepts JSONB DEFAULT '[]',
    synthesis_method VARCHAR(100),
    focus VARCHAR(500),
    innovation_degree INTEGER CHECK (innovation_degree BETWEEN 1 AND 5),
    historical_context VARCHAR(500)
);

-- Индексы для concepts
CREATE INDEX idx_concepts_creator ON concepts(creator_id);
CREATE INDEX idx_concepts_name ON concepts(name);
CREATE INDEX idx_concepts_created ON concepts(creation_date);
CREATE INDEX idx_concepts_synthesis ON concepts(is_synthesis) WHERE is_synthesis = TRUE;

-- Таблица названий концепций
CREATE TABLE IF NOT EXISTS concept_names (
    name_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    concept_id UUID NOT NULL REFERENCES concepts(concept_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    analysis TEXT,
    alternative_names JSONB DEFAULT '[]',
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    interaction_id UUID
);

-- Индексы для concept_names
CREATE INDEX idx_concept_names_concept ON concept_names(concept_id);

-- Таблица происхождения концепций
CREATE TABLE IF NOT EXISTS concept_origins (
    origin_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    concept_id UUID NOT NULL REFERENCES concepts(concept_id) ON DELETE CASCADE,
    parent_concepts JSONB DEFAULT '[]',
    influence_weights JSONB DEFAULT '[]',
    analysis TEXT,
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    interaction_id UUID
);

-- Индексы для concept_origins
CREATE INDEX idx_concept_origins_concept ON concept_origins(concept_id);

-- Таблица трансформаций
CREATE TABLE IF NOT EXISTS transformations (
    transformation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    target_id UUID NOT NULL,
    target_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    interaction_id UUID,
    transformation_details JSONB DEFAULT '{}'
);

-- Индексы для transformations
CREATE INDEX idx_transformations_source ON transformations(source_id, source_type);
CREATE INDEX idx_transformations_target ON transformations(target_id, target_type);
CREATE INDEX idx_transformations_created ON transformations(created_at);