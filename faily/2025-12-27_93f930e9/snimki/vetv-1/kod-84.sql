-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    user_settings JSONB DEFAULT '{}',
    claude_api_key_encrypted TEXT,
    use_own_api_key BOOLEAN DEFAULT FALSE,
    api_key_added_at TIMESTAMP WITH TIME ZONE,
    api_key_last_used TIMESTAMP WITH TIME ZONE
);

-- Индексы для пользователей
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Таблица совместного использования API ключей
CREATE TABLE IF NOT EXISTS shared_api_keys (
    share_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    shared_with_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    shared_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    permissions JSONB DEFAULT '{}',
    UNIQUE(owner_id, shared_with_id)
);

-- Индексы для shared_api_keys
CREATE INDEX idx_shared_api_keys_owner ON shared_api_keys(owner_id);
CREATE INDEX idx_shared_api_keys_shared_with ON shared_api_keys(shared_with_id);
CREATE INDEX idx_shared_api_keys_active ON shared_api_keys(is_active) WHERE is_active = TRUE;

-- Таблица использования API
CREATE TABLE IF NOT EXISTS api_key_usage (
    usage_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    usage_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    operation_type VARCHAR(100) NOT NULL,
    tokens_used INTEGER DEFAULT 0,
    estimated_cost DECIMAL(10, 4) DEFAULT 0,
    concept_id UUID
);

-- Индексы для api_key_usage
CREATE INDEX idx_api_key_usage_user ON api_key_usage(user_id);
CREATE INDEX idx_api_key_usage_date ON api_key_usage(usage_date);
CREATE INDEX idx_api_key_usage_concept ON api_key_usage(concept_id);

-- Таблица активности пользователей
CREATE TABLE IF NOT EXISTS user_activity (
    activity_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    activity_type VARCHAR(100) NOT NULL,
    target_id UUID,
    activity_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    details JSONB DEFAULT '{}'
);

-- Индексы для user_activity
CREATE INDEX idx_user_activity_user ON user_activity(user_id);
CREATE INDEX idx_user_activity_date ON user_activity(activity_date);
CREATE INDEX idx_user_activity_type ON user_activity(activity_type);