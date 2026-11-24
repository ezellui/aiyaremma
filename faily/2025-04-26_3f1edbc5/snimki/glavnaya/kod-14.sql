CREATE TABLE connections (
    connection_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    concept_id UUID NOT NULL REFERENCES concepts(concept_id) ON DELETE CASCADE,
    source_category_id UUID NOT NULL REFERENCES categories(category_id) ON DELETE CASCADE,
    target_category_id UUID NOT NULL REFERENCES categories(category_id) ON DELETE CASCADE,
    connection_type VARCHAR(50) NOT NULL,
    direction VARCHAR(20) NOT NULL,
    description TEXT,
    tradition_concepts JSONB DEFAULT '[]'::jsonb,  -- Массив традиций/концепций
    philosophers JSONB DEFAULT '[]'::jsonb,        -- Массив философов
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_connection_type CHECK (
        connection_type IN (
            'hierarchical', 'causal', 'dialectical', 
            'functional', 'derivative', 'associative'
        )
    ),
    CONSTRAINT check_direction CHECK (
        direction IN ('directed', 'bidirectional', 'undirected')
    )
);

-- Добавляем индексы для поиска по JSONB массивам
CREATE INDEX idx_categories_tradition_concepts ON categories USING GIN (tradition_concepts);
CREATE INDEX idx_categories_philosophers ON categories USING GIN (philosophers);
CREATE INDEX idx_connections_tradition_concepts ON connections USING GIN (tradition_concepts);
CREATE INDEX idx_connections_philosophers ON connections USING GIN (philosophers);