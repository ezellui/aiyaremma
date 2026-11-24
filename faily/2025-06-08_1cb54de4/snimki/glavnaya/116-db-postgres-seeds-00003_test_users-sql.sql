-- Seed data: Test Users
-- Тестовые пользователи для разработки и тестирования

-- Очистка существующих тестовых пользователей (опционально)
-- DELETE FROM users WHERE email LIKE '%@test.philosophy.com';

-- Функция для генерации хеша пароля (для примера используем простой SHA256)
-- В продакшене должен использоваться bcrypt или аналогичный алгоритм
-- Пароль по умолчанию для всех тестовых пользователей: "Test123!"

-- Вставка тестовых пользователей
INSERT INTO users (
    user_id, 
    username, 
    email, 
    password_hash, 
    created_at, 
    last_login, 
    user_settings,
    claude_api_key_encrypted,
    use_own_api_key,
    api_key_added_at
) VALUES
-- Администратор
(
    '770e8400-e29b-41d4-a716-446655440001',
    'admin',
    'admin@test.philosophy.com',
    -- В реальности здесь должен быть bcrypt хеш
    '$2a$10$YourHashHere1234567890123456789012345678901234567890123',
    '2024-01-01 00:00:00',
    '2024-12-15 10:30:00',
    '{
        "theme": "dark",
        "language": "ru",
        "notifications": {
            "email": true,
            "inApp": true,
            "synthesisComplete": true,
            "analysisComplete": true
        },
        "defaultView": "graph",
        "autoSave": true,
        "tutorialCompleted": true
    }'::jsonb,
    NULL,
    false,
    NULL
),

-- Исследователь философии
(
    '770e8400-e29b-41d4-a716-446655440002',
    'researcher',
    'researcher@test.philosophy.com',
    '$2a$10$YourHashHere1234567890123456789012345678901234567890123',
    '2024-01-15 08:00:00',
    '2024-12-14 16:45:00',
    '{
        "theme": "light",
        "language": "ru",
        "notifications": {
            "email": true,
            "inApp": false,
            "synthesisComplete": true,
            "analysisComplete": false
        },
        "defaultView": "theses",
        "autoSave": true,
        "tutorialCompleted": true,
        "preferredTraditions": ["german_idealism", "phenomenology"],
        "researchInterests": ["epistemology", "metaphysics"]
    }'::jsonb,
    -- Зашифрованный API ключ (в реальности должен быть настоящий зашифрованный ключ)
    'encrypted_api_key_researcher_1234567890',
    true,
    '2024-02-01 10:00:00'
),

-- Студент философии
(
    '770e8400-e29b-41d4-a716-446655440003',
    'student',
    'student@test.philosophy.com',
    '$2a$10$YourHashHere1234567890123456789012345678901234567890123',
    '2024-02-01 12:00:00',
    '2024-12-13 14:20:00',
    '{
        "theme": "auto",
        "language": "ru",
        "notifications": {
            "email": false,
            "inApp": true,
            "synthesisComplete": false,
            "analysisComplete": false
        },
        "defaultView": "concepts",
        "autoSave": false,
        "tutorialCompleted": false,
        "studyLevel": "bachelor",
        "university": "МГУ"
    }'::jsonb,
    NULL,
    false,
    NULL
),

-- Преподаватель философии
(
    '770e8400-e29b-41d4-a716-446655440004',
    'professor',
    'professor@test.philosophy.com',
    '$2a$10$YourHashHere1234567890123456789012345678901234567890123',
    '2024-01-20 09:00:00',
    '2024-12-12 11:15:00',
    '{
        "theme": "light",
        "language": "ru",
        "notifications": {
            "email": true,
            "inApp": true,
            "synthesisComplete": true,
            "analysisComplete": true
        },
        "defaultView": "graph",
        "autoSave": true,
        "tutorialCompleted": true,
        "teachingSubjects": ["history_of_philosophy", "ethics", "logic"],
        "academicTitle": "professor",
        "institution": "Философский факультет МГУ"
    }'::jsonb,
    'encrypted_api_key_professor_0987654321',
    true,
    '2024-01-25 14:30:00'
),

-- Энтузиаст философии
(
    '770e8400-e29b-41d4-a716-446655440005',
    'enthusiast',
    'enthusiast@test.philosophy.com',
    '$2a$10$YourHashHere1234567890123456789012345678901234567890123',
    '2024-03-01 15:00:00',
    '2024-12-10 19:45:00',
    '{
        "theme": "dark",
        "language": "ru",
        "notifications": {
            "email": true,
            "inApp": false,
            "synthesisComplete": false,
            "analysisComplete": true
        },
        "defaultView": "dialogue",
        "autoSave": true,
        "tutorialCompleted": true,
        "interests": ["stoicism", "existentialism", "eastern_philosophy"]
    }'::jsonb,
    NULL,
    false,
    NULL
),

-- Тестовый пользователь для API
(
    '770e8400-e29b-41d4-a716-446655440006',
    'api_tester',
    'api@test.philosophy.com',
    '$2a$10$YourHashHere1234567890123456789012345678901234567890123',
    '2024-04-01 10:00:00',
    '2024-12-15 12:00:00',
    '{
        "theme": "light",
        "language": "en",
        "notifications": {
            "email": false,
            "inApp": false,
            "synthesisComplete": false,
            "analysisComplete": false
        },
        "defaultView": "api",
        "autoSave": false,
        "tutorialCompleted": true,
        "apiTesting": true,
        "rateLimit": "unlimited"
    }'::jsonb,
    'encrypted_api_key_api_tester_555666777',
    true,
    '2024-04-01 10:30:00'
),

-- Пользователь с общим доступом к API ключу
(
    '770e8400-e29b-41d4-a716-446655440007',
    'shared_user',
    'shared@test.philosophy.com',
    '$2a$10$YourHashHere1234567890123456789012345678901234567890123',
    '2024-05-01 14:00:00',
    '2024-12-11 16:30:00',
    '{
        "theme": "auto",
        "language": "ru",
        "notifications": {
            "email": true,
            "inApp": true,
            "synthesisComplete": true,
            "analysisComplete": false
        },
        "defaultView": "theses",
        "autoSave": true,
        "tutorialCompleted": true
    }'::jsonb,
    NULL,
    false,
    NULL
),

-- Пользователь без API ключа
(
    '770e8400-e29b-41d4-a716-446655440008',
    'basic_user',
    'basic@test.philosophy.com',
    '$2a$10$YourHashHere1234567890123456789012345678901234567890123',
    '2024-06-01 11:00:00',
    '2024-12-09 13:20:00',
    '{
        "theme": "light",
        "language": "ru",
        "notifications": {
            "email": false,
            "inApp": true,
            "synthesisComplete": false,
            "analysisComplete": false
        },
        "defaultView": "concepts",
        "autoSave": false,
        "tutorialCompleted": false
    }'::jsonb,
    NULL,
    false,
    NULL
),

-- Модератор контента
(
    '770e8400-e29b-41d4-a716-446655440009',
    'moderator',
    'moderator@test.philosophy.com',
    '$2a$10$YourHashHere1234567890123456789012345678901234567890123',
    '2024-01-10 08:30:00',
    '2024-12-15 11:45:00',
    '{
        "theme": "light",
        "language": "ru",
        "notifications": {
            "email": true,
            "inApp": true,
            "synthesisComplete": true,
            "analysisComplete": true,
            "newElementsForApproval": true,
            "contentReported": true
        },
        "defaultView": "moderation",
        "autoSave": true,
        "tutorialCompleted": true,
        "moderationQueue": true,
        "canApproveElements": true
    }'::jsonb,
    'encrypted_api_key_moderator_111222333',
    true,
    '2024-01-15 09:00:00'
),

-- Демо пользователь
(
    '770e8400-e29b-41d4-a716-446655440010',
    'demo',
    'demo@test.philosophy.com',
    '$2a$10$YourHashHere1234567890123456789012345678901234567890123',
    '2024-07-01 12:00:00',
    CURRENT_TIMESTAMP,
    '{
        "theme": "light",
        "language": "ru",
        "notifications": {
            "email": false,
            "inApp": false,
            "synthesisComplete": false,
            "analysisComplete": false
        },
        "defaultView": "tour",
        "autoSave": false,
        "tutorialCompleted": false,
        "isDemoAccount": true,
        "demoExpiresAt": "2025-01-01T00:00:00Z"
    }'::jsonb,
    NULL,
    false,
    NULL
)
ON CONFLICT (user_id) DO UPDATE SET
    username = EXCLUDED.username,
    email = EXCLUDED.email,
    password_hash = EXCLUDED.password_hash,
    last_login = EXCLUDED.last_login,
    user_settings = EXCLUDED.user_settings,
    claude_api_key_encrypted = EXCLUDED.claude_api_key_encrypted,
    use_own_api_key = EXCLUDED.use_own_api_key,
    api_key_added_at = EXCLUDED.api_key_added_at;

-- Создание тестовых общих API ключей
INSERT INTO shared_api_keys (
    share_id,
    owner_id,
    shared_with_id,
    shared_at,
    expires_at,
    is_active,
    permissions
) VALUES
-- Профессор делится ключом со студентом
(
    '880e8400-e29b-41d4-a716-446655440001',
    '770e8400-e29b-41d4-a716-446655440004', -- professor
    '770e8400-e29b-41d4-a716-446655440003', -- student
    '2024-10-01 10:00:00',
    '2025-06-01 00:00:00', -- До конца учебного года
    true,
    '{
        "canUse": true,
        "canShare": false,
        "maxTokensPerDay": 50000,
        "allowedOperations": ["thesis_generation", "graph_analysis", "dialogue"],
        "restrictedOperations": ["synthesis", "evolution"]
    }'::jsonb
),

-- Исследователь делится ключом с shared_user
(
    '880e8400-e29b-41d4-a716-446655440002',
    '770e8400-e29b-41d4-a716-446655440002', -- researcher
    '770e8400-e29b-41d4-a716-446655440007', -- shared_user
    '2024-11-01 14:00:00',
    '2025-02-01 00:00:00',
    true,
    '{
        "canUse": true,
        "canShare": true,
        "maxTokensPerDay": 100000,
        "allowedOperations": ["all"],
        "restrictedOperations": []
    }'::jsonb
)
ON CONFLICT (share_id) DO UPDATE SET
    expires_at = EXCLUDED.expires_at,
    is_active = EXCLUDED.is_active,
    permissions = EXCLUDED.permissions;

-- Добавление записей об активности для тестовых пользователей
INSERT INTO user_activity (
    activity_id,
    user_id,
    activity_type,
    target_id,
    activity_date,
    details
) 
SELECT 
    gen_random_uuid(),
    user_id,
    activity_type,
    target_id,
    activity_date,
    details
FROM (
    VALUES
    -- Активность администратора
    ('770e8400-e29b-41d4-a716-446655440001', 'login', NULL, '2024-12-15 10:30:00'::timestamp, '{"ip": "127.0.0.1", "userAgent": "Mozilla/5.0"}'::jsonb),
    ('770e8400-e29b-41d4-a716-446655440001', 'create_concept', '990e8400-e29b-41d4-a716-446655440001', '2024-12-15 10:35:00'::timestamp, '{"conceptName": "Тестовая концепция"}'::jsonb),
    
    -- Активность исследователя
    ('770e8400-e29b-41d4-a716-446655440002', 'login', NULL, '2024-12-14 16:45:00'::timestamp, '{"ip": "192.168.1.100", "userAgent": "Chrome/120.0"}'::jsonb),
    ('770e8400-e29b-41d4-a716-446655440002', 'generate_thesis', '990e8400-e29b-41d4-a716-446655440002', '2024-12-14 17:00:00'::timestamp, '{"thesisType": "ontological", "tokensUsed": 1500}'::jsonb),
    
    -- Активность студента
    ('770e8400-e29b-41d4-a716-446655440003', 'login', NULL, '2024-12-13 14:20:00'::timestamp, '{"ip": "10.0.0.50", "userAgent": "Firefox/121.0"}'::jsonb),
    ('770e8400-e29b-41d4-a716-446655440003', 'view_concept', '990e8400-e29b-41d4-a716-446655440001', '2024-12-13 14:25:00'::timestamp, '{"viewDuration": 300}'::jsonb)
) AS t(user_id, activity_type, target_id, activity_date, details);
