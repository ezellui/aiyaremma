const connection: Omit<Connection, 'connection_id' | 'created_at' | 'last_modified' | 'source_category' | 'target_category'> = {
  concept_id: conceptId,
  source_category_id: data.source_category_id,
  target_category_id: data.target_category_id,
  connection_type: data.connection_type,
  direction: data.direction,
  description: data.description,
  tradition_concepts: data.tradition_concepts || [],  // По умолчанию пустой массив
  philosophers: data.philosophers || []                // По умолчанию пустой массив
};