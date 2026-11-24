function initWorker() {
    const workerCode = `
        // Импорт math.js
        importScripts('https://cdnjs.cloudflare.com/ajax/libs/mathjs/11.5.0/math.min.js');
        
        // Complex math functions...
        
        // ...Существующий код...
    `;
    
    // Создание worker'а
    const blob = new Blob([workerCode], { type: 'application/javascript' });
    worker = new Worker(URL.createObjectURL(blob));
    
    // Обработчики...
}