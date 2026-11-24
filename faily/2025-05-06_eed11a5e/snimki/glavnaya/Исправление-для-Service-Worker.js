// Исправление проблемы с регистрацией Service Worker
if ('serviceWorker' in navigator) {
    // Проверяем, что мы используем https:// или http://localhost
    const isSecureContext = window.location.protocol === 'https:' || 
                           window.location.hostname === 'localhost' ||
                           window.location.hostname === '127.0.0.1';
    
    if (isSecureContext) {
        // Используем относительный путь вместо абсолютного
        navigator.serviceWorker.register('./service-worker.js')
            .then(registration => {
                console.log('Service Worker зарегистрирован:', registration);
            })
            .catch(error => {
                console.error('Ошибка регистрации Service Worker:', error);
            });
    } else {
        console.warn('Service Worker не может быть зарегистрирован: требуется HTTPS или localhost');
    }
}