-- Таблица шаблонов категорий
CREATE TABLE IF NOT EXISTS category_templates (
    template_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    default_definition TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(user_id),
    is_system BOOLEAN DEFAULT FALSE
);

-- Индексы для category_templates
CREATE INDEX idx_category_templates_name ON category_templates(name);
CREATE INDEX idx_category_templates_system ON category_templates(is_system);

-- Таблица шаблонов типов связей
CREATE TABLE IF NOT EXISTS relationship_type_templates (
    template_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    default_direction VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(user_id),
    is_system BOOLEAN DEFAULT FALSE
);

-- Индексы для relationship_type_templates
CREATE INDEX idx_relationship_type_templates_name ON relationship_type_templates(type_name);
CREATE INDEX idx_relationship_type_templates_system ON relationship_type_templates(is_system);