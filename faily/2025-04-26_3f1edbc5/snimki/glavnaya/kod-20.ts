const result = await client.query(
  `INSERT INTO connections(
    concept_id, source_category_id, target_category_id, 
    connection_type, direction, description,
    tradition_concepts, philosophers
  ) 
  VALUES($1, $2, $3, $4, $5, $6, $7, $8) 
  RETURNING *`,
  [
    connection.concept_id,
    connection.source_category_id,
    connection.target_category_id,
    connection.connection_type,
    connection.direction,
    connection.description || null,
    JSON.stringify(connection.tradition_concepts),
    JSON.stringify(connection.philosophers)
  ]
);