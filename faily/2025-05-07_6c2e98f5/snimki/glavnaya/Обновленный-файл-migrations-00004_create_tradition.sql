-- migrations/00004_create_traditions_table.sql

-- Создание типа для философских традиций
CREATE TYPE philosophical_tradition_type AS ENUM (
    -- Античная философия
    'ancient_greek', 'presocratic', 'socratic', 'platonic', 'aristotelian',
    'stoic', 'epicurean', 'skeptic', 'neoplatonic',
    
    -- Средневековая философия
    'patristic', 'scholastic', 'thomistic', 'nominalism', 'realism',
    
    -- Восточные традиции
    'confucian', 'daoist', 'buddhist', 'hindu', 'vedanta', 'zen',
    
    -- Новое время
    'rationalism', 'empiricism', 'enlightenment', 'idealism', 
    'german_idealism', 'romanticism', 'utilitarianism',
    
    -- Современная философия
    'phenomenology', 'existentialism', 'hermeneutics', 'marxism',
    'critical_theory', 'pragmatism', 'analytic', 'postmodern',
    'poststructuralism', 'feminist', 'continental', 'process',
    
    -- Метафилософские подходы
    'naturalism', 'non_naturalism', 'constructivism', 'essentialism',
    'pluralism', 'monism', 'dualism'
);

-- Создание типа для исторических периодов
CREATE TYPE historical_period_type AS ENUM (
    'ancient', 'medieval', 'renaissance', 'early_modern', 'modern', 'contemporary'
);

CREATE TABLE traditions (
    tradition_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    tradition_type philosophical_tradition_type NOT NULL,
    time_period historical_period_type,
    description TEXT,
    key_principles TEXT[],
    geographical_origin VARCHAR(100),
    key_figures UUID[],
    parent_tradition UUID,
    child_traditions UUID[],
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Внешние ключи
    CONSTRAINT fk_traditions_parent
        FOREIGN KEY (parent_tradition)
        REFERENCES traditions(tradition_id)
        ON DELETE SET NULL
);

-- Индексы
CREATE INDEX idx_traditions_name ON traditions(name);
CREATE INDEX idx_traditions_tradition_type ON traditions(tradition_type);
CREATE INDEX idx_traditions_time_period ON traditions(time_period);
CREATE INDEX idx_traditions_parent_tradition ON traditions(parent_tradition);
CREATE INDEX idx_traditions_key_figures ON traditions USING GIN(key_figures);
CREATE INDEX idx_traditions_geographical_origin ON traditions(geographical_origin);

-- Триггер для обновления updated_at
CREATE TRIGGER update_traditions_updated_at
    BEFORE UPDATE ON traditions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Комментарии
COMMENT ON TABLE traditions IS 'Философские традиции и школы';
COMMENT ON COLUMN traditions.tradition_id IS 'Уникальный идентификатор традиции';
COMMENT ON COLUMN traditions.tradition_type IS 'Тип философской традиции (из PHILOSOPHICAL_TRADITIONS)';
COMMENT ON COLUMN traditions.time_period IS 'Исторический период традиции (из HISTORICAL_PERIODS)';
COMMENT ON COLUMN traditions.key_principles IS 'Основные принципы традиции';
COMMENT ON COLUMN traditions.geographical_origin IS 'Географическое происхождение традиции';
COMMENT ON COLUMN traditions.key_figures IS 'Ключевые философы традиции';
