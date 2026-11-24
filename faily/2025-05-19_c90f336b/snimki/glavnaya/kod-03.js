// Найдите в коде Web Worker объект Complex
const Complex = {
    add: function(a, b) { ... },
    multiply: function(a, b) { ... },
    
    // ... другие существующие методы ...
    
    // Добавьте сюда методы для обработки ошибок и граничных случаев
    safeCompute: function(func, fallback = { re: NaN, im: NaN }) {
        // ... код из Части 3 ...
    },
    
    handlePole: function(z, polePosition, poleOrder = 1, visualization = 'clip') {
        // ... код из Части 3 ...
    },
    
    handleBranchCut: function(z, line, visualization = 'jump') {
        // ... код из Части 3 ...
    },
    
    // ... остальные методы обработки ошибок и граничных случаев ...
};