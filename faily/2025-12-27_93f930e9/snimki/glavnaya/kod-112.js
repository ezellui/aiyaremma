/**
 * Модель использования API ключа
 */

const { v4: uuidv4 } = require('uuid');

class ApiKeyUsage {
  constructor(data = {}) {
    this.usageId = data.usage_id || uuidv4();
    this.userId = data.user_id;
    this.usageDate = data.usage_date || new Date();
    this.operationType = data.operation_type;
    this.tokensUsed = data.tokens_used || 0;
    this.estimatedCost = data.estimated_cost || 0;
    this.conceptId = data.concept_id;
    this.requestMetadata = data.request_metadata || {};
  }

  toJSON() {
    return {
      usageId: this.usageId,
      userId: this.userId,
      usageDate: this.usageDate,
      operationType: this.operationType,
      tokensUsed: this.tokensUsed,
      estimatedCost: this.estimatedCost,
      conceptId: this.conceptId,
      requestMetadata: this.requestMetadata
    };
  }

  toDB() {
    return {
      usage_id: this.usageId,
      user_id: this.userId,
      usage_date: this.usageDate,
      operation_type: this.operationType,
      tokens_used: this.tokensUsed,
      estimated_cost: this.estimatedCost,
      concept_id: this.conceptId,
      request_metadata: this.requestMetadata
    };
  }

  static fromDB(data) {
    return new ApiKeyUsage(data);
  }
}

module.exports = ApiKeyUsage;