POST /graphs/{concept-id}
Content-Type: application/json
X-User-Id: <user-id>

{
  "categories": [
    {
      "name": "Тезис",
      "definition": "Исходное утверждение",
      "type": "онтологическая",
      "certainty": 1.0
    },
    {
      "name": "Антитезис",
      "definition": "Противоположное утверждение",
      "type": "онтологическая",
      "certainty": 1.0
    }
  ],
  "relationships": [
    {
      "sourceCategoryId": "...",
      "targetCategoryId": "...",
      "type": "диалектическая",
      "strength": 1.0
    }
  ]
}