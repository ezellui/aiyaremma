// В основном JavaScript файле

function renderDomainColoring(mode = 'domain') {
    // Показываем индикатор загрузки
    document.getElementById('loading').style.display = 'flex';
    
    // Используем Web Worker для рендеринга доменной карты в фоновом режиме
    if (window.Worker) {
        const worker = new Worker(URL.createObjectURL(new Blob([/* весь код Web Worker */], { type: 'application/javascript' })));
        
        worker.onmessage = function(e) {
            domainCtx.putImageData(e.data.imageData, 0, 0);
            
            // Рисуем критические точки
            if (settings.showCriticalPoints) {
                drawCriticalPointsOnDomain();
            }
            
            // Скрываем индикатор загрузки
            document.getElementById('loading').style.display = 'none';
            
            // Завершаем worker
            worker.terminate();
        };
        
        worker.postMessage({
            width: domainCanvas.width,
            height: domainCanvas.height,
            functionStr: functionStr,
            viewScale: viewScale,
            viewOffsetX: viewOffsetX,
            viewOffsetY: viewOffsetY,
            centerX: centerX,
            centerY: centerY,
            mode: mode, // Используем переданный режим
            options: {
                quality: qualityLevel,
                colorScheme: 'default' // Можно заменить на 'rainbow', 'hsv', 'magnetic' и т.д.
            }
        });
    } else {
        // Запасной вариант если Worker не поддерживается...
    }
}