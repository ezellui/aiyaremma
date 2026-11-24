-- Функция для безопасного инкремента счетчика
CREATE OR REPLACE FUNCTION safe_increment(table_name TEXT, column_name TEXT, row_id UUID)
RETURNS VOID AS $$
BEGIN
    EXECUTE format('UPDATE %I SET %I = %I + 1 WHERE %I = $1', 
                   table_name, column_name, column_name, 
                   table_name || '_id')
    USING row_id;
END;
$$ LANGUAGE plpgsql;

-- Функция для получения статистики использования API
CREATE OR REPLACE FUNCTION get_api_usage_stats(
    p_user_id UUID,
    p_start_date TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    p_end_date TIMESTAMP WITH TIME ZONE DEFAULT NULL
)
RETURNS TABLE (
    total_requests BIGINT,
    total_tokens BIGINT,
    total_cost DECIMAL,
    by_operation JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::BIGINT as total_requests,
        COALESCE(SUM(tokens_used), 0)::BIGINT as total_tokens,
        COALESCE(SUM(estimated_cost), 0) as total_cost,
        jsonb_object_agg(
            operation_type,
            jsonb_build_object(
                'count', count,
                'tokens', tokens,
                'cost', cost
            )
        ) as by_operation
    FROM (
        SELECT
            operation_type,
            COUNT(*)::BIGINT as count,
            COALESCE(SUM(tokens_used), 0)::BIGINT as tokens,
            COALESCE(SUM(estimated_cost), 0) as cost
        FROM api_key_usage
        WHERE user_id = p_user_id
            AND (p_start_date IS NULL OR usage_date >= p_start_date)
            AND (p_end_date IS NULL OR usage_date <= p_end_date)
        GROUP BY operation_type
    ) stats;
END;
$$ LANGUAGE plpgsql;

-- Функция для очистки старых записей активности
CREATE OR REPLACE FUNCTION cleanup_old_activity(days_to_keep INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM user_activity
    WHERE activity_date < CURRENT_TIMESTAMP - (days_to_keep || ' days')::INTERVAL;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Комментарии
COMMENT ON FUNCTION get_api_usage_stats IS 'Получение статистики использования API для пользователя';
COMMENT ON FUNCTION cleanup_old_activity IS 'Очистка старых записей активности пользователей';