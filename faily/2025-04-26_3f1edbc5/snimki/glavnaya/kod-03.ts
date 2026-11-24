export interface Category {
  category_id: string;
  concept_id: string;
  name: string;
  definition: string;
  extended_description?: string;
  source?: string;
  tradition_concept?: string;  // Добавлено
  philosopher?: string;        // Добавлено
  created_at: Date;
  last_modified: Date;
  attributes?: CategoryAttribute[];
}