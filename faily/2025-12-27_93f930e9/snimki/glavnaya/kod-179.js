{
  conceptId: UUID,
  creatorId: UUID,
  name: String,
  description: String,
  isSynthesis: Boolean,
  parentConcepts: [UUID],
  synthesisMethod: String,
  innovationDegree: String,
  tags: [String],
  isPublic: Boolean,
  createdAt: DateTime,
  lastModified: DateTime
}