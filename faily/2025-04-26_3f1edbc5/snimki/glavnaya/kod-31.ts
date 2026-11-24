const generateThesesPrompt = `
На основе следующего графа философской концепции сформулируй ${params.count} ключевых тезисов в области ${params.type}.

Название концепции: ${concept.name}
Описание: ${concept.description}

Категории:
${categories.map(cat => {
  let catText = `- ${cat.name}: ${cat.definition}`;
  
  if (cat.tradition_concepts.length > 0) {
    catText += `\n  Традиции: ${cat.tradition_concepts.join(', ')}`;
  }
  
  if (cat.philosophers.length > 0) {
    catText += `\n  Философы: ${cat.philosophers.join(', ')}`;
  }
  
  if (params.useWeights && cat.attributes.length > 0) {
    catText += `\n  Характеристики: ${cat.attributes.map(attr => 
      `${attr.attribute_type}: ${attr.value}`
    ).join(', ')}`;
  }
  
  return catText;
}).join('\n')}

Связи:
${connections.map(conn => {
  let connText = `- ${conn.source_category.name} ${conn.direction === 'directed' ? '->' : '<->'} ${conn.target_category.name} (${conn.connection_type}): ${conn.description}`;
  
  if (conn.tradition_concepts.length > 0) {
    connText += `\n  Традиции: ${conn.tradition_concepts.join(', ')}`;
  }
  
  if (conn.philosophers.length > 0) {
    connText += `\n  Философы: ${conn.philosophers.join(', ')}`;
  }
  
  if (params.useWeights && conn.attributes.length > 0) {
    connText += `\n  Характеристики: ${conn.attributes.map(attr => 
      `${attr.attribute_type}: ${attr.value}`
    ).join(', ')}`;
  }
  
  return connText;
}).join('\n')}

...
`;