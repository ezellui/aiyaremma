{
  relationshipId: UUID,
  conceptId: UUID,
  sourceCategoryId: UUID,
  targetCategoryId: UUID,
  type: String,
  direction: String,
  strength: Number (0-1),
  innovationDegree: String,
  description: String,
  metadata: Object,
  createdAt: DateTime
}