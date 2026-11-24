// Внутри функции evaluateFunction или во время вычисления значения функции
function evaluateFunction(z, funcStr) {
    try {
        // Используем безопасное вычисление
        return Complex.safeCompute(() => {
            // ... существующий код вычисления ...
            
            // Используем кэшированные версии где возможно
            if (token.value === 'exp') {
                return Complex.expCached(arg);
            } else if (token.value === 'log') {
                return Complex.logCached(arg);
            }
            // ... и т.д. для других функций ...
            
            // ... остальная логика ...
        });
    } catch (e) {
        console.error('Ошибка в функции:', e);
        return { re: NaN, im: NaN };
    }
}