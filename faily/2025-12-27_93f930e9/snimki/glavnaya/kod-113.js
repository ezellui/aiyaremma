/**
 * Сервис шифрования для API ключей
 */

const crypto = require('crypto');
const config = require('../config/config');

class EncryptionService {
  constructor() {
    this.algorithm = 'aes-256-cbc';
    this.key = Buffer.from(config.encryption.key.padEnd(32, '0').substring(0, 32));
  }

  /**
   * Шифрует строку
   */
  encrypt(text) {
    if (!text) return null;

    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv(this.algorithm, this.key, iv);
    
    let encrypted = cipher.update(text, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    
    return iv.toString('hex') + ':' + encrypted;
  }

  /**
   * Расшифровывает строку
   */
  decrypt(encryptedText) {
    if (!encryptedText) return null;

    const parts = encryptedText.split(':');
    const iv = Buffer.from(parts[0], 'hex');
    const encrypted = parts[1];
    
    const decipher = crypto.createDecipheriv(this.algorithm, this.key, iv);
    
    let decrypted = decipher.update(encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    
    return decrypted;
  }
}

module.exports = new EncryptionService();