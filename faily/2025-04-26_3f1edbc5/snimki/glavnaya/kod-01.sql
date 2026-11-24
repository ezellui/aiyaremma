CREATE TABLE categories (
    category_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    concept_id UUID NOT NULL REFERENCES concepts(concept_id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    definition TEXT NOT NULL,
    extended_description TEXT,
    source TEXT,
    tradition_concept VARCHAR(100),  -- Добавлено
    philosopher VARCHAR(100),        -- Добавлено
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);