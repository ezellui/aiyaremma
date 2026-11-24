-- Таблица философов
CREATE TABLE IF NOT EXISTS philosophers (
    philosopher_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    birth_year INTEGER,
    death_year INTEGER,
    description TEXT,
    traditions JSONB DEFAULT '[]'
);

-- Индексы для philosophers
CREATE INDEX idx_philosophers_name ON philosophers(name);

-- Таблица философских традиций
CREATE TABLE IF NOT EXISTS traditions (
    tradition_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    time_period VARCHAR(100),
    description TEXT,
    key_figures JSONB DEFAULT '[]'
);

-- Индексы для traditions
CREATE INDEX idx_traditions_name ON traditions(name);

-- Связь между концепциями и философами
CREATE TABLE IF NOT EXISTS concept_philosophers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    concept_id UUID NOT NULL REFERENCES concepts(concept_id) ON DELETE CASCADE,
    philosopher_id UUID NOT NULL REFERENCES philosophers(philosopher_id) ON DELETE CASCADE,
    relationship_type VARCHAR(100),
    UNIQUE(concept_id, philosopher_id)
);

-- Индексы для concept_philosophers
CREATE INDEX idx_concept_philosophers_concept ON concept_philosophers(concept_id);
CREATE INDEX idx_concept_philosophers_philosopher ON concept_philosophers(philosopher_id);

-- Связь между концепциями и традициями
CREATE TABLE IF NOT EXISTS concept_traditions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    concept_id UUID NOT NULL REFERENCES concepts(concept_id) ON DELETE CASCADE,
    tradition_id UUID NOT NULL REFERENCES traditions(tradition_id) ON DELETE CASCADE,
    relationship_strength DECIMAL(3, 2) CHECK (relationship_strength BETWEEN 0 AND 1),
    UNIQUE(concept_id, tradition_id)
);

-- Индексы для concept_traditions
CREATE INDEX idx_concept_traditions_concept ON concept_traditions(concept_id);
CREATE INDEX idx_concept_traditions_tradition ON concept_traditions(tradition_id);