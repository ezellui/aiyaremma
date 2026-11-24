private async preparePrompt(templateName: string, data: Record<string, any>): Promise<string> {
  try {
    const template = await this.promptService.getTemplate(templateName);
    if (!template) {
      throw new Error(`Template not found: ${templateName}`);
    }
    
    let prompt = template.template;
    
    // Замена параметров в шаблоне
    for (const param of template.parameters) {
      const value = data[param];
      
      if (value === undefined) {
        logger.warn(`Parameter ${param} is missing in data for template ${templateName}`);
        prompt = prompt.replace(new RegExp(`\\{\\{${param}\\}\\}`, 'g'), '');
        continue;
      }
      
      // Обработка массивов
      if (Array.isArray(value)) {
        // Заменяем блоки {{#each param}} ... {{/each}}
        const eachRegex = new RegExp(`\\{\\{#each ${param}\\}\\}([\\s\\S]*?)\\{\\{/each\\}\\}`, 'g');
        prompt = prompt.replace(eachRegex, (match, content) => {
          return value.map((item, index) => {
            return content
              .replace(/\{\{this\}\}/g, item)
              .replace(/\{\{@last\}\}/g, String(index === value.length - 1))
              .replace(/\{\{#unless @last\}\}([^]*?)\{\{\/unless\}\}/g, (m, c) => 
                index !== value.length - 1 ? c : ''
              );
          }).join('');
        });
        
        // Заменяем простые {{param}} на строку с разделителями
        prompt = prompt.replace(new RegExp(`\\{\\{${param}\\}\\}`, 'g'), value.join(', '));
      } else {
        // Обработка обычных значений
        let stringValue = value;
        if (typeof value === 'object') {
          stringValue = JSON.stringify(value, null, 2);
        }
        prompt = prompt.replace(new RegExp(`\\{\\{${param}\\}\\}`, 'g'), stringValue);
      }
      
      // Обработка условных блоков {{#if param}} ... {{/if}}
      const ifRegex = new RegExp(`\\{\\{#if ${param}\\}\\}([\\s\\S]*?)\\{\\{/if\\}\\}`, 'g');
      prompt = prompt.replace(ifRegex, (match, content) => {
        if (Array.isArray(value) ? value.length > 0 : Boolean(value)) {
          return content;
        }
        return '';
      });
    }
    
    return prompt;
  } catch (error) {
    logger.error(`Error preparing prompt: ${error}`);
    throw new Error(`Failed to prepare prompt: ${error}`);
  }
}