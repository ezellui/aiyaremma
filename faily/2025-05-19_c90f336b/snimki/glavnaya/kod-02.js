// Найдите в коде Web Worker место после определения объекта Complex и cosh/sinh функций
// Примерно после строк:
// function cosh(x) { return (Math.exp(x) + Math.exp(-x)) / 2; }
// function sinh(x) { return (Math.exp(x) - Math.exp(-x)) / 2; }

// Добавьте здесь систему кэширования
const FunctionCache = {
    // Максимальный размер кэша
    maxCacheSize: 10000,
    
    // Структуры кэша для разных типов функций
    caches: {
        exp: new Map(),
        log: new Map(),
        sin: new Map(),
        cos: new Map(),
        pow: new Map(),
        // Добавьте кэш для других функций по необходимости
    },
    
    // Получение значения из кэша
    get: function(funcName, z, precision = 5) {
        // ... остальной код из Части 3 ...
    },
    
    // ... остальные методы системы кэширования ...
};

// Оптимизированные версии функций
const ComplexOptimized = {
    // Оптимизированная экспонента с кэшированием
    expCached: function(a, precision = 5) {
        // ... код из Части 3 ...
    },
    
    // ... остальные оптимизированные методы ...
};

// Добавляем оптимизированные методы в объект Complex
Object.assign(Complex, ComplexOptimized);