export interface CategoryCreateDTO {
  name: string;
  definition: string;
  extended_description?: string;
  source?: string;
  tradition_concepts?: string[];  // Массив
  philosophers?: string[];        // Массив
}

export interface CategoryUpdateDTO {
  name?: string;
  definition?: string;
  extended_description?: string;
  source?: string;
  tradition_concepts?: string[];  // Массив
  philosophers?: string[];        // Массив
}

export interface ConnectionCreateDTO {
  source_category_id: string;
  target_category_id: string;
  connection_type: 'hierarchical' | 'causal' | 'dialectical' | 'functional' | 'derivative' | 'associative';
  direction: 'directed' | 'bidirectional' | 'undirected';
  description?: string;
  tradition_concepts?: string[];  // Массив
  philosophers?: string[];        // Массив
}

export interface ConnectionUpdateDTO {
  connection_type?: 'hierarchical' | 'causal' | 'dialectical' | 'functional' | 'derivative' | 'associative';
  direction?: 'directed' | 'bidirectional' | 'undirected';
  description?: string;
  tradition_concepts?: string[];  // Массив
  philosophers?: string[];        // Массив
}