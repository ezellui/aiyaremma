const result = await client.query(
  `INSERT INTO categories(
    concept_id, name, definition, extended_description, source,
    tradition_concepts, philosophers
  ) 
  VALUES($1, $2, $3, $4, $5, $6, $7) 
  RETURNING *`,
  [
    category.concept_id,
    category.name,
    category.definition,
    category.extended_description || null,
    category.source || null,
    JSON.stringify(category.tradition_concepts),
    JSON.stringify(category.philosophers)
  ]
);