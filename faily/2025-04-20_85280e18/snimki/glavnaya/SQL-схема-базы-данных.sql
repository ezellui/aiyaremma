-- Создание базы данных
CREATE DATABASE philosophy_db;

-- Использование созданной базы данных
USE philosophy_db;

-- Таблица концепций
CREATE TABLE concepts (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    source VARCHAR(50) NOT NULL CHECK (source IN ('original', 'generated')),
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица авторов
CREATE TABLE authors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    UNIQUE KEY (name)
);

-- Таблица для связи концепций и авторов (многие ко многим)
CREATE TABLE concept_authors (
    concept_id VARCHAR(36) NOT NULL,
    author_id INT NOT NULL,
    PRIMARY KEY (concept_id, author_id),
    FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE
);

-- Таблица тезисов
CREATE TABLE theses (
    id VARCHAR(36) PRIMARY KEY,
    content TEXT NOT NULL,
    concept_id VARCHAR(36) NOT NULL,
    FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
);

-- Таблица ключевых слов
CREATE TABLE keywords (
    id INT AUTO_INCREMENT PRIMARY KEY,
    word VARCHAR(100) NOT NULL,
    UNIQUE KEY (word)
);

-- Таблица для связи тезисов и ключевых слов (многие ко многим)
CREATE TABLE thesis_keywords (
    thesis_id VARCHAR(36) NOT NULL,
    keyword_id INT NOT NULL,
    PRIMARY KEY (thesis_id, keyword_id),
    FOREIGN KEY (thesis_id) REFERENCES theses(id) ON DELETE CASCADE,
    FOREIGN KEY (keyword_id) REFERENCES keywords(id) ON DELETE CASCADE
);

-- Таблица тем
CREATE TABLE topics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    UNIQUE KEY (name)
);

-- Таблица для связи тезисов и тем (многие ко многим)
CREATE TABLE thesis_topics (
    thesis_id VARCHAR(36) NOT NULL,
    topic_id INT NOT NULL,
    PRIMARY KEY (thesis_id, topic_id),
    FOREIGN KEY (thesis_id) REFERENCES theses(id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
);

-- Таблица для связей между концепциями (для отслеживания родительских концепций)
CREATE TABLE concept_relations (
    parent_id VARCHAR(36) NOT NULL,
    child_id VARCHAR(36) NOT NULL,
    PRIMARY KEY (parent_id, child_id),
    FOREIGN KEY (parent_id) REFERENCES concepts(id) ON DELETE CASCADE,
    FOREIGN KEY (child_id) REFERENCES concepts(id) ON DELETE CASCADE
);

-- Таблица запросов на генерацию
CREATE TABLE generation_requests (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL CHECK (status IN ('processing', 'completed', 'error')),
    error TEXT,
    result_concept_id VARCHAR(36),
    generation_params JSON,
    FOREIGN KEY (result_concept_id) REFERENCES concepts(id) ON DELETE SET NULL
);

-- Таблица для связи запросов и выбранных концепций
CREATE TABLE request_selected_concepts (
    request_id VARCHAR(36) NOT NULL,
    concept_id VARCHAR(36) NOT NULL,
    PRIMARY KEY (request_id, concept_id),
    FOREIGN KEY (request_id) REFERENCES generation_requests(id) ON DELETE CASCADE,
    FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
);

-- Индексы для оптимизации запросов
CREATE INDEX idx_theses_concept_id ON theses(concept_id);
CREATE INDEX idx_concept_authors_author_id ON concept_authors(author_id);
CREATE INDEX idx_thesis_keywords_keyword_id ON thesis_keywords(keyword_id);
CREATE INDEX idx_thesis_topics_topic_id ON thesis_topics(topic_id);
CREATE INDEX idx_concept_relations_child_id ON concept_relations(child_id);
CREATE INDEX idx_generation_requests_status ON generation_requests(status);
CREATE INDEX idx_generation_requests_user_id ON generation_requests(user_id);
CREATE INDEX idx_request_selected_concepts_concept_id ON request_selected_concepts(concept_id);

-- Пример вставки начальных данных (философские концепции)
INSERT INTO authors (name) VALUES ('Платон'), ('Аристотель'), ('Кант'), ('Ницше'), ('Хайдеггер');

-- Пример вставки начальных тем
INSERT INTO topics (name) VALUES 
('Онтология'), ('Гносеология'), ('Этика'), ('Эстетика'), 
('Логика'), ('Антропология'), ('Социальная философия'), ('Историософия');

-- Пример вставки начальных ключевых слов
INSERT INTO keywords (word) VALUES 
('бытие'), ('сознание'), ('познание'), ('истина'), ('субъект'),
('объект'), ('материя'), ('идея'), ('опыт'), ('разум'), 
('мышление'), ('воля'), ('свобода'), ('необходимость'), ('причинность'), 
('этика'), ('мораль'), ('добро'), ('зло'), ('красота');
