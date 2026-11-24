-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user' CHECK (role IN ('user', 'admin', 'moderator')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    user_settings JSONB DEFAULT '{}',
    
    -- Поля для API ключей Claude
    claude_api_key_encrypted TEXT,
    use_own_api_key BOOLEAN DEFAULT FALSE,
    api_key_added_at TIMESTAMP WITH TIME ZONE,
    api_key_last_used TIMESTAMP WITH TIME ZONE,
    
    -- Метаданные
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    
    -- Индексы
    CONSTRAINT username_length CHECK (char_length(username) >= 3),
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Индексы для таблицы users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_created_at ON users(created_at DESC);
CREATE INDEX idx_users_is_active ON users(is_active) WHERE is_active = TRUE;

-- Комментарии
COMMENT ON TABLE users IS 'Пользователи платформы';
COMMENT ON COLUMN users.user_id IS 'Уникальный идентификатор пользователя';
COMMENT ON COLUMN users.claude_api_key_encrypted IS 'Зашифрованный API ключ Claude пользователя';
COMMENT ON COLUMN users.use_own_api_key IS 'Флаг использования собственного ключа API';

-- Таблица совместного использования API ключей
CREATE TABLE IF NOT EXISTS shared_api_keys (
    share_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    shared_with_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    shared_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    permissions JSONB DEFAULT '{}',
    
    -- Ограничения
    CONSTRAINT different_users CHECK (owner_id != shared_with_id),
    CONSTRAINT unique_share UNIQUE (owner_id, shared_with_id)
);

-- Индексы
CREATE INDEX idx_shared_keys_owner ON shared_api_keys(owner_id);
CREATE INDEX idx_shared_keys_shared_with ON shared_api_keys(shared_with_id);
CREATE INDEX idx_shared_keys_active ON shared_api_keys(is_active) WHERE is_active = TRUE;

-- Комментарии
COMMENT ON TABLE shared_api_keys IS 'Совместное использование API ключей между пользователями';

-- Таблица использования API ключей
CREATE TABLE IF NOT EXISTS api_key_usage (
    usage_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    usage_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    operation_type VARCHAR(100) NOT NULL,
    tokens_used INTEGER DEFAULT 0,
    estimated_cost DECIMAL(10, 6) DEFAULT 0.0,
    concept_id UUID,
    request_metadata JSONB DEFAULT '{}',
    
    -- Индексы
    CONSTRAINT positive_tokens CHECK (tokens_used >= 0),
    CONSTRAINT positive_cost CHECK (estimated_cost >= 0)
);

-- Индексы
CREATE INDEX idx_api_usage_user ON api_key_usage(user_id);
CREATE INDEX idx_api_usage_date ON api_key_usage(usage_date DESC);
CREATE INDEX idx_api_usage_operation ON api_key_usage(operation_type);
CREATE INDEX idx_api_usage_concept ON api_key_usage(concept_id) WHERE concept_id IS NOT NULL;

-- Комментарии
COMMENT ON TABLE api_key_usage IS 'Отслеживание использования API ключей Claude';

-- Таблица активности пользователей
CREATE TABLE IF NOT EXISTS user_activity (
    activity_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    activity_type VARCHAR(100) NOT NULL,
    target_id UUID,
    target_type VARCHAR(50),
    activity_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    details JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT
);

-- Индексы
CREATE INDEX idx_activity_user ON user_activity(user_id);
CREATE INDEX idx_activity_date ON user_activity(activity_date DESC);
CREATE INDEX idx_activity_type ON user_activity(activity_type);
CREATE INDEX idx_activity_target ON user_activity(target_id, target_type) WHERE target_id IS NOT NULL;

-- Комментарии
COMMENT ON TABLE user_activity IS 'Журнал активности пользователей';