-- Таблица философов
CREATE TABLE IF NOT EXISTS philosophers (
    philosopher_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    birth_year INTEGER,
    death_year INTEGER,
    description TEXT,
    traditions JSONB DEFAULT '[]',
    key_works JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Ограничения
    CONSTRAINT valid_years CHECK (
        (birth_year IS NULL OR (birth_year >= -3000 AND birth_year <= 2100)) AND
        (death_year IS NULL OR (death_year >= -3000 AND death_year <= 2100)) AND
        (birth_year IS NULL OR death_year IS NULL OR death_year >= birth_year)
    )
);

-- Индексы
CREATE INDEX idx_philosophers_name ON philosophers(name);
CREATE INDEX idx_philosophers_birth ON philosophers(birth_year) WHERE birth_year IS NOT NULL;
CREATE INDEX idx_philosophers_traditions ON philosophers USING GIN (traditions);

-- Комментарии
COMMENT ON TABLE philosophers IS 'Философы';
COMMENT ON COLUMN philosophers.traditions IS 'Массив философских традиций';

-- Таблица философских традиций
CREATE TABLE IF NOT EXISTS traditions (
    tradition_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    time_period VARCHAR(255),
    description TEXT,
    key_figures JSONB DEFAULT '[]',
    related_traditions JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Индексы
CREATE INDEX idx_traditions_name ON traditions(name);
CREATE INDEX idx_traditions_period ON traditions(time_period);
CREATE INDEX idx_traditions_figures ON traditions USING GIN (key_figures);

-- Комментарии
COMMENT ON TABLE traditions IS 'Философские традиции';

-- Таблица связи концепций с философами
CREATE TABLE IF NOT EXISTS concept_philosophers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    concept_id UUID NOT NULL REFERENCES concepts(concept_id) ON DELETE CASCADE,
    philosopher_id UUID NOT NULL REFERENCES philosophers(philosopher_id) ON DELETE CASCADE,
    relationship_type VARCHAR(100) DEFAULT 'influenced_by',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_concept_philosopher UNIQUE (concept_id, philosopher_id)
);

-- Индексы
CREATE INDEX idx_concept_phil_concept ON concept_philosophers(concept_id);
CREATE INDEX idx_concept_phil_philosopher ON concept_philosophers(philosopher_id);
CREATE INDEX idx_concept_phil_type ON concept_philosophers(relationship_type);

-- Комментарии
COMMENT ON TABLE concept_philosophers IS 'Связь концепций с философами';

-- Таблица связи концепций с традициями
CREATE TABLE IF NOT EXISTS concept_traditions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    concept_id UUID NOT NULL REFERENCES concepts(concept_id) ON DELETE CASCADE,
    tradition_id UUID NOT NULL REFERENCES traditions(tradition_id) ON DELETE CASCADE,
    relationship_strength DECIMAL(3, 2) CHECK (relationship_strength BETWEEN 0 AND 1),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_concept_tradition UNIQUE (concept_id, tradition_id)
);

-- Индексы
CREATE INDEX idx_concept_trad_concept ON concept_traditions(concept_id);
CREATE INDEX idx_concept_trad_tradition ON concept_traditions(tradition_id);
CREATE INDEX idx_concept_trad_strength ON concept_traditions(relationship_strength);

-- Комментарии
COMMENT ON TABLE concept_traditions IS 'Связь концепций с философскими традициями';