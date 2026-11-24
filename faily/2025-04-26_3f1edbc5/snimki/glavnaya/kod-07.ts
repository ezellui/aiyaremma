const result = await client.query(
  `INSERT INTO categories(
    concept_id, name, definition, extended_description, source,
    tradition_concept, philosopher
  ) 
  VALUES($1, $2, $3, $4, $5, $6, $7) 
  RETURNING *`,
  [
    category.concept_id,
    category.name,
    category.definition,
    category.extended_description || null,
    category.source || null,
    category.tradition_concept || null,
    category.philosopher || null
  ]
);