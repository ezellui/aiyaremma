GET /graphs/{concept-id}/analyze

Response:
{
  "stats": {
    "categoryCount": 10,
    "relationshipCount": 15,
    "avgCentrality": 0.5
  },
  "centralCategories": [...],
  "isolatedCategories": [...],
  "strongRelationships": [...],
  "isConnected": true,
  "cyclesCount": 2
}