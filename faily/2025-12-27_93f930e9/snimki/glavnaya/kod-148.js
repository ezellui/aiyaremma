/**
 * Утилиты для парсинга ответов от Claude
 */

class ResponseParser {
  /**
   * Извлекает JSON из ответа Claude
   */
  static extractJSON(text) {
    try {
      // Ищем JSON между ```json и ```
      const jsonMatch = text.match(/```json\s*([\s\S]*?)\s*```/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[1]);
      }

      // Ищем JSON между { и }
      const jsonObjectMatch = text.match(/\{[\s\S]*\}/);
      if (jsonObjectMatch) {
        return JSON.parse(jsonObjectMatch[0]);
      }

      // Если не нашли, пробуем распарсить весь текст
      return JSON.parse(text);
    } catch (error) {
      return null;
    }
  }

  /**
   * Разделяет ответ на секции
   */
  static splitIntoSections(text) {
    const sections = {};
    const sectionRegex = /##\s*([^\n]+)\n([\s\S]*?)(?=##\s|$)/g;
    
    let match;
    while ((match = sectionRegex.exec(text)) !== null) {
      const title = match[1].trim();
      const content = match[2].trim();
      sections[title] = content;
    }

    return sections;
  }

  /**
   * Извлекает список из текста
   */
  static extractList(text) {
    const items = [];
    const lines = text.split('\n');

    for (const line of lines) {
      const trimmed = line.trim();
      
      // Маркированный список
      if (trimmed.startsWith('-') || trimmed.startsWith('*')) {
        items.push(trimmed.substring(1).trim());
      }
      
      // Нумерованный список
      const numberedMatch = trimmed.match(/^\d+\.\s*(.+)$/);
      if (numberedMatch) {
        items.push(numberedMatch[1].trim());
      }
    }

    return items;
  }

  /**
   * Очищает текст от markdown форматирования
   */
  static stripMarkdown(text) {
    return text
      .replace(/```[\s\S]*?```/g, '') // Удаляем code blocks
      .replace(/`([^`]+)`/g, '$1')    // Удаляем inline code
      .replace(/\*\*([^*]+)\*\*/g, '$1') // Удаляем bold
      .replace(/\*([^*]+)\*/g, '$1')     // Удаляем italic
      .replace(/##\s*/g, '')             // Удаляем заголовки
      .replace(/\n{3,}/g, '\n\n')        // Нормализуем переводы строк
      .trim();
  }
}

module.exports = ResponseParser;