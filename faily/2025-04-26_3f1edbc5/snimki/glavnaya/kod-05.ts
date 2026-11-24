export interface CategoryCreateDTO {
  name: string;
  definition: string;
  extended_description?: string;
  source?: string;
  tradition_concept?: string;  // Добавлено
  philosopher?: string;        // Добавлено
}

export interface CategoryUpdateDTO {
  name?: string;
  definition?: string;
  extended_description?: string;
  source?: string;
  tradition_concept?: string;  // Добавлено
  philosopher?: string;        // Добавлено
}

export interface ConnectionCreateDTO {
  source_category_id: string;
  target_category_id: string;
  connection_type: 'hierarchical' | 'causal' | 'dialectical' | 'functional' | 'derivative' | 'associative';
  direction: 'directed' | 'bidirectional' | 'undirected';
  description?: string;
  tradition_concept?: string;  // Добавлено
  philosopher?: string;        // Добавлено
}

export interface ConnectionUpdateDTO {
  connection_type?: 'hierarchical' | 'causal' | 'dialectical' | 'functional' | 'derivative' | 'associative';
  direction?: 'directed' | 'bidirectional' | 'undirected';
  description?: string;
  tradition_concept?: string;  // Добавлено
  philosopher?: string;        // Добавлено
}