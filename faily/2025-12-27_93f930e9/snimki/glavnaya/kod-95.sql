-- Таблица концепций
CREATE TABLE IF NOT EXISTS concepts (
    concept_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    creator_id UUID NOT NULL REFERENCES users(user_id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    creation_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Флаги и метаданные
    is_synthesis BOOLEAN DEFAULT FALSE,
    is_public BOOLEAN DEFAULT FALSE,
    is_archived BOOLEAN DEFAULT FALSE,
    
    -- Данные синтеза
    parent_concepts JSONB DEFAULT '[]',
    synthesis_method VARCHAR(100),
    focus VARCHAR(500),
    innovation_degree INTEGER CHECK (innovation_degree BETWEEN 1 AND 5),
    
    -- Контекст
    historical_context TEXT,
    tags JSONB DEFAULT '[]',
    
    -- Статистика
    views_count INTEGER DEFAULT 0,
    likes_count INTEGER DEFAULT 0,
    
    -- Ограничения
    CONSTRAINT name_length CHECK (char_length(name) >= 1 AND char_length(name) <= 255)
);

-- Индексы
CREATE INDEX idx_concepts_creator ON concepts(creator_id);
CREATE INDEX idx_concepts_name ON concepts(name);
CREATE INDEX idx_concepts_created ON concepts(creation_date DESC);
CREATE INDEX idx_concepts_modified ON concepts(last_modified DESC);
CREATE INDEX idx_concepts_public ON concepts(is_public) WHERE is_public = TRUE;
CREATE INDEX idx_concepts_synthesis ON concepts(is_synthesis) WHERE is_synthesis = TRUE;
CREATE INDEX idx_concepts_innovation ON concepts(innovation_degree) WHERE innovation_degree IS NOT NULL;
CREATE INDEX idx_concepts_tags ON concepts USING GIN (tags);

-- Полнотекстовый поиск
ALTER TABLE concepts ADD COLUMN search_vector tsvector;

CREATE INDEX idx_concepts_search ON concepts USING GIN (search_vector);

CREATE OR REPLACE FUNCTION concepts_search_trigger() RETURNS trigger AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('russian', coalesce(NEW.name, '')), 'A') ||
        setweight(to_tsvector('russian', coalesce(NEW.description, '')), 'B');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER concepts_search_update BEFORE INSERT OR UPDATE
    ON concepts FOR EACH ROW EXECUTE FUNCTION concepts_search_trigger();

-- Триггер для обновления last_modified
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_modified = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_concepts_modified
    BEFORE UPDATE ON concepts
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

-- Комментарии
COMMENT ON TABLE concepts IS 'Философские концепции';
COMMENT ON COLUMN concepts.is_synthesis IS 'Флаг синтезированной концепции';
COMMENT ON COLUMN concepts.parent_concepts IS 'Массив UUID родительских концепций для синтеза';
COMMENT ON COLUMN concepts.innovation_degree IS 'Степень инновационности (1-5)';