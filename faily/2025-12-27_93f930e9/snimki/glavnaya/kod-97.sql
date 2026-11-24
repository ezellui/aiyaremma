-- Таблица шаблонов категорий
CREATE TABLE IF NOT EXISTS category_templates (
    template_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    default_definition TEXT,
    category_type VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(user_id) ON DELETE SET NULL,
    is_system BOOLEAN DEFAULT FALSE,
    usage_count INTEGER DEFAULT 0,
    
    CONSTRAINT unique_category_name UNIQUE (name)
);

-- Индексы
CREATE INDEX idx_category_templates_name ON category_templates(name);
CREATE INDEX idx_category_templates_type ON category_templates(category_type);
CREATE INDEX idx_category_templates_system ON category_templates(is_system);
CREATE INDEX idx_category_templates_usage ON category_templates(usage_count DESC);

-- Комментарии
COMMENT ON TABLE category_templates IS 'Шаблоны категорий для переиспользования';
COMMENT ON COLUMN category_templates.is_system IS 'Системный шаблон (встроенный)';

-- Таблица шаблонов типов связей
CREATE TABLE IF NOT EXISTS relationship_type_templates (
    template_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type_name VARCHAR(255) NOT NULL,
    description TEXT,
    default_direction VARCHAR(50) DEFAULT 'unidirectional',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(user_id) ON DELETE SET NULL,
    is_system BOOLEAN DEFAULT FALSE,
    usage_count INTEGER DEFAULT 0,
    
    CONSTRAINT unique_type_name UNIQUE (type_name),
    CONSTRAINT valid_direction CHECK (default_direction IN ('unidirectional', 'bidirectional', 'reflexive'))
);

-- Индексы
CREATE INDEX idx_rel_templates_name ON relationship_type_templates(type_name);
CREATE INDEX idx_rel_templates_system ON relationship_type_templates(is_system);
CREATE INDEX idx_rel_templates_usage ON relationship_type_templates(usage_count DESC);

-- Комментарии
COMMENT ON TABLE relationship_type_templates IS 'Шаблоны типов связей для переиспользования';