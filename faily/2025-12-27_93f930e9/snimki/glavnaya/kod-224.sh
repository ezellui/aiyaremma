GET /graphs/{concept-id}/export?format=d3

Response:
{
  "nodes": [
    {"id": "...", "name": "Тезис", "centrality": 0.8}
  ],
  "links": [
    {"source": "...", "target": "...", "strength": 1.0}
  ]
}