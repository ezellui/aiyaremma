/**
 * Модель пользователя
 */

const { v4: uuidv4 } = require('uuid');

class User {
  constructor(data = {}) {
    this.userId = data.user_id || uuidv4();
    this.username = data.username;
    this.email = data.email;
    this.passwordHash = data.password_hash;
    this.role = data.role || 'user';
    this.createdAt = data.created_at || new Date();
    this.lastLogin = data.last_login;
    this.userSettings = data.user_settings || {};
    this.claudeApiKeyEncrypted = data.claude_api_key_encrypted;
    this.useOwnApiKey = data.use_own_api_key || false;
    this.apiKeyAddedAt = data.api_key_added_at;
    this.apiKeyLastUsed = data.api_key_last_used;
    this.isActive = data.is_active !== undefined ? data.is_active : true;
    this.emailVerified = data.email_verified || false;
  }

  toJSON() {
    return {
      userId: this.userId,
      username: this.username,
      email: this.email,
      role: this.role,
      createdAt: this.createdAt,
      lastLogin: this.lastLogin,
      userSettings: this.userSettings,
      hasApiKey: !!this.claudeApiKeyEncrypted,
      useOwnApiKey: this.useOwnApiKey,
      apiKeyAddedAt: this.apiKeyAddedAt,
      apiKeyLastUsed: this.apiKeyLastUsed,
      isActive: this.isActive,
      emailVerified: this.emailVerified
    };
  }

  toSafeJSON() {
    const json = this.toJSON();
    delete json.passwordHash;
    return json;
  }

  toDB() {
    return {
      user_id: this.userId,
      username: this.username,
      email: this.email,
      password_hash: this.passwordHash,
      role: this.role,
      created_at: this.createdAt,
      last_login: this.lastLogin,
      user_settings: this.userSettings,
      claude_api_key_encrypted: this.claudeApiKeyEncrypted,
      use_own_api_key: this.useOwnApiKey,
      api_key_added_at: this.apiKeyAddedAt,
      api_key_last_used: this.apiKeyLastUsed,
      is_active: this.isActive,
      email_verified: this.emailVerified
    };
  }

  static fromDB(data) {
    return new User(data);
  }
}

module.exports = User;