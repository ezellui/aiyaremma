-- Таблица взаимодействий с Claude
CREATE TABLE IF NOT EXISTS claude_interactions (
    interaction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    concept_id UUID REFERENCES concepts(concept_id) ON DELETE SET NULL,
    query_type VARCHAR(100) NOT NULL,
    query_content TEXT NOT NULL,
    response_content TEXT,
    interaction_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processing_time DECIMAL(10, 3),
    tokens_used INTEGER,
    error_message TEXT,
    status VARCHAR(50) DEFAULT 'pending'
);

-- Индексы для claude_interactions
CREATE INDEX idx_claude_interactions_user ON claude_interactions(user_id);
CREATE INDEX idx_claude_interactions_concept ON claude_interactions(concept_id);
CREATE INDEX idx_claude_interactions_date ON claude_interactions(interaction_date);
CREATE INDEX idx_claude_interactions_type ON claude_interactions(query_type);
CREATE INDEX idx_claude_interactions_status ON claude_interactions(status);