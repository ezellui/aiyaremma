// ... другие функции ...

// ВСТАВИТЬ ФУНКЦИЮ parseExpressionValue ЗДЕСЬ
// Функция для парсинга математических выражений
function parseExpressionValue(expression) {
    try {
        // Заменяем pi и e на их значения
        const processedExpression = expression
            .replace(/pi/gi, 'Math.PI')
            .replace(/e/gi, 'Math.E');
        
        // Используем Function вместо eval для большей безопасности
        // eslint-disable-next-line no-new-func
        const result = new Function('return ' + processedExpression)();
        
        if (typeof result !== 'number' || isNaN(result)) {
            throw new Error('Результат не является числом');
        }
        
        return result;
    } catch (error) {
        console.error('Ошибка при парсинге выражения:', error);
        throw error;
    }
}

// ... продолжение других функций или начало инициализации ...