export interface Category {
  category_id: string;
  concept_id: string;
  name: string;
  definition: string;
  extended_description?: string;
  source?: string;
  tradition_concepts: string[];  // Изменено на массив
  philosophers: string[];        // Изменено на массив
  created_at: Date;
  last_modified: Date;
  attributes?: CategoryAttribute[];
}