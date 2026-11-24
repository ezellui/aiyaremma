export interface Connection {
  connection_id: string;
  concept_id: string;
  source_category_id: string;
  target_category_id: string;
  connection_type: 'hierarchical' | 'causal' | 'dialectical' | 'functional' | 'derivative' | 'associative';
  direction: 'directed' | 'bidirectional' | 'undirected';
  description?: string;
  tradition_concept?: string;  // Добавлено
  philosopher?: string;        // Добавлено
  created_at: Date;
  last_modified: Date;
  attributes?: ConnectionAttribute[];
  // Для удобства в UI - заполняются при запросе
  source_category?: Category;
  target_category?: Category;
}