-- Функция для автоматического обновления last_modified
CREATE OR REPLACE FUNCTION update_last_modified()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_TABLE_NAME IN ('concepts') THEN
        NEW.last_modified = CURRENT_TIMESTAMP;
    ELSIF TG_TABLE_NAME IN ('historical_contexts', 'practical_applications') THEN
        NEW.updated_at = CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Триггер для таблицы concepts (уже был)
DROP TRIGGER IF EXISTS update_concepts_last_modified ON concepts;
CREATE TRIGGER update_concepts_last_modified
    BEFORE UPDATE ON concepts
    FOR EACH ROW
    EXECUTE FUNCTION update_last_modified();

-- Функция для подсчета использования API ключа
CREATE OR REPLACE FUNCTION get_user_api_usage(
    p_user_id UUID,
    p_start_date TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    p_end_date TIMESTAMP WITH TIME ZONE DEFAULT NULL
)
RETURNS TABLE (
    total_requests BIGINT,
    total_tokens BIGINT,
    total_cost DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::BIGINT as total_requests,
        COALESCE(SUM(tokens_used), 0)::BIGINT as total_tokens,
        COALESCE(SUM(estimated_cost), 0) as total_cost
    FROM api_key_usage
    WHERE user_id = p_user_id
        AND (p_start_date IS NULL OR usage_date >= p_start_date)
        AND (p_end_date IS NULL OR usage_date <= p_end_date);
END;
$$ LANGUAGE plpgsql;

-- Функция для поиска концепций
CREATE OR REPLACE FUNCTION search_concepts(
    p_search_term VARCHAR,
    p_limit INTEGER DEFAULT 10,
    p_offset INTEGER DEFAULT 0
)
RETURNS TABLE (
    concept_id UUID,
    name VARCHAR,
    description TEXT,
    creator_id UUID,
    creation_date TIMESTAMP WITH TIME ZONE,
    relevance REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.concept_id,
        c.name,
        c.description,
        c.creator_id,
        c.creation_date,
        ts_rank(
            to_tsvector('russian', c.name || ' ' || COALESCE(c.description, '')),
            plainto_tsquery('russian', p_search_term)
        ) as relevance
    FROM concepts c
    WHERE to_tsvector('russian', c.name || ' ' || COALESCE(c.description, '')) 
        @@ plainto_tsquery('russian', p_search_term)
    ORDER BY relevance DESC
    LIMIT p_limit
    OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;

-- Функция для получения статистики концепций пользователя
CREATE OR REPLACE FUNCTION get_user_concept_stats(p_user_id UUID)
RETURNS TABLE (
    total_concepts BIGINT,
    total_synthesis BIGINT,
    total_categories BIGINT,
    avg_innovation_degree DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(DISTINCT c.concept_id)::BIGINT as total_concepts,
        COUNT(DISTINCT c.concept_id) FILTER (WHERE c.is_synthesis = TRUE)::BIGINT as total_synthesis,
        0::BIGINT as total_categories, -- Будет подсчитываться из Neo4j
        AVG(c.innovation_degree) as avg_innovation_degree
    FROM concepts c
    WHERE c.creator_id = p_user_id;
END;
$$ LANGUAGE plpgsql;