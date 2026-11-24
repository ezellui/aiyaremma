-- migrations/00008_create_claude_interactions_table.sql

-- Создание типа для запросов к Claude на основе типов из философских констант
CREATE TYPE claude_query_type AS ENUM (
    -- Основные взаимодействия
    'graph_validation', 'graph_enrichment', 'thesis_generation',
    
    -- Анализ и синтез
    'synthesis_analysis', 'compatibility_analysis', 'parent_concept_detection',
    'name_analysis', 'historical_context', 'concept_evolution',
    
    -- Практическое применение и интерпретация
    'practical_application', 'dialogue_generation', 'argument_analysis',
    
    -- Аналитические операции
    'critical_analysis', 'historical_analysis', 'comparative_analysis',
    'conceptual_analysis', 'logical_analysis', 'hermeneutical_analysis',
    'phenomenological_analysis', 'linguistic_analysis', 'pragmatic_analysis',
    'structural_analysis', 'genealogical_analysis', 'deconstructive_analysis',
    'psychoanalytical_analysis', 'feminist_analysis', 'postcolonial_analysis',
    
    -- Общее
    'general_query'
);

CREATE TABLE claude_interactions (
    interaction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    concept_id UUID,
    query_type claude_query_type NOT NULL,
    query_content TEXT NOT NULL,
    response_content TEXT,
    interaction_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processing_time FLOAT,
    token_count INTEGER,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    error_message TEXT,
    model_version VARCHAR(50),
    metadata JSONB DEFAULT '{}',
    
    -- Поля для отслеживания использованных констант
    used_category_types TEXT[],
    used_relationship_types TEXT[],
    used_thesis_types TEXT[],
    used_synthesis_types TEXT[],
    
    -- Внешние ключи
    CONSTRAINT fk_claude_interactions_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,
    
    CONSTRAINT fk_claude_interactions_concept
        FOREIGN KEY (concept_id)
        REFERENCES concepts(concept_id)
        ON DELETE SET NULL
);

-- Индексы
CREATE INDEX idx_claude_interactions_user_id ON claude_interactions(user_id);
CREATE INDEX idx_claude_interactions_concept_id ON claude_interactions(concept_id);
CREATE INDEX idx_claude_interactions_query_type ON claude_interactions(query_type);
CREATE INDEX idx_claude_interactions_interaction_date ON claude_interactions(interaction_date);
CREATE INDEX idx_claude_interactions_status ON claude_interactions(status);
CREATE INDEX idx_claude_interactions_processing_time ON claude_interactions(processing_time);
CREATE INDEX idx_claude_interactions_token_count ON claude_interactions(token_count);
CREATE INDEX idx_claude_interactions_used_category_types ON claude_interactions USING GIN(used_category_types);
CREATE INDEX idx_claude_interactions_used_relationship_types ON claude_interactions USING GIN(used_relationship_types);
CREATE INDEX idx_claude_interactions_used_thesis_types ON claude_interactions USING GIN(used_thesis_types);
CREATE INDEX idx_claude_interactions_used_synthesis_types ON claude_interactions USING GIN(used_synthesis_types);

-- Комментарии
COMMENT ON TABLE claude_interactions IS 'История взаимодействий с Claude API';
COMMENT ON COLUMN claude_interactions.query_type IS 'Тип запроса к Claude (на основе типов из констант)';
COMMENT ON COLUMN claude_interactions.processing_time IS 'Время обработки запроса в секундах';
COMMENT ON COLUMN claude_interactions.token_count IS 'Количество использованных токенов';
COMMENT ON COLUMN claude_interactions.used_category_types IS 'Типы категорий, использованные в запросе или ответе';
COMMENT ON COLUMN claude_interactions.used_relationship_types IS 'Типы отношений, использованные в запросе или ответе';
COMMENT ON COLUMN claude_interactions.used_thesis_types IS 'Типы тезисов, использованные в запросе или ответе';
COMMENT ON COLUMN claude_interactions.used_synthesis_types IS 'Типы синтеза, использованные в запросе или ответе';
