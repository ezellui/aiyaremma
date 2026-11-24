CREATE TABLE connections (
    connection_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    concept_id UUID NOT NULL REFERENCES concepts(concept_id) ON DELETE CASCADE,
    source_category_id UUID NOT NULL REFERENCES categories(category_id) ON DELETE CASCADE,
    target_category_id UUID NOT NULL REFERENCES categories(category_id) ON DELETE CASCADE,
    connection_type VARCHAR(50) NOT NULL,
    direction VARCHAR(20) NOT NULL,
    description TEXT,
    tradition_concept VARCHAR(100),  -- Добавлено
    philosopher VARCHAR(100),        -- Добавлено
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