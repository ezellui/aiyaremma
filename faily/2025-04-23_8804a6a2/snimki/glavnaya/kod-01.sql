-- Синтезированная концепция
INSERT INTO concepts (concept_id, user_id, name, description, creation_date, last_modified, historical_context, is_synthesis, parent_concepts, synthesis_method, focus_area) VALUES
('4b5c6d7e-8f9a-0b1c-2d3e-4f5a6b7c8d9e', 'f47ac10b-58cc-4372-a567-0e02b2c3d479', 'Интегративная теория эвдемонической добродетели', 'Синтез аристотелевской этики добродетели с элементами кантианского деонтологического подхода...', '2025-04-20 11:45:32.789+00', '2025-04-23 16:30:18.567+00', 'Современный синтез древнегреческой и просвещенческой этических традиций', TRUE, '["3a7c27d1-35e4-47c3-a0d7-e189eb7c3fb6", "9d8c7b6a-5e4f-3g2h-1i0j-k9l8m7n6o5p4"]', 'integrative', 'ethical');

-- Метаданные синтеза
INSERT INTO synthesis_meta (synthesis_id, result_concept_id, source_concept_ids, synthesis_method, innovation_level, abstraction_level, historical_context, target_application, created_at, compatibility_analysis) VALUES
('c1d2e3f4-g5h6-i7j8-k9l0-m1n2o3p4q5r6', '4b5c6d7e-8f9a-0b1c-2d3e-4f5a6b7c8d9e', 
'["3a7c27d1-35e4-47c3-a0d7-e189eb7c3fb6", "9d8c7b6a-5e4f-3g2h-1i0j-k9l8m7n6o5p4"]',
'integrative', 'moderate', 'intermediate', 'contemporary', 
'Применение в современном этическом образовании и развитии корпоративной этики', 
'2025-04-20 11:45:32.789+00',
'{
  "fully_compatible": [...],
  "potentially_compatible": [...],
  "incompatible": [...],
  "synthesis_strategies": [...]
}'
);