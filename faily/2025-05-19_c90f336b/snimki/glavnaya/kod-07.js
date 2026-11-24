// Найдите в Web Worker обработчик сообщений и замените его полностью

// Обработчик сообщений от основного потока
self.onmessage = function(e) {
    const { width, height, functionStr, viewScale, viewOffsetX, viewOffsetY, centerX, centerY, mode, options } = e.data;
    
    // Выбираем режим визуализации
    switch (mode) {
        case 'domain':
            renderDomainColoring(width, height, functionStr, viewScale, viewOffsetX, viewOffsetY, centerX, centerY, options);
            break;
        case 'mandelbrot':
            renderMandelbrotSet(width, height, viewScale, viewOffsetX, viewOffsetY, centerX, centerY, options);
            break;
        case 'julia':
            renderJuliaSet(width, height, viewScale, viewOffsetX, viewOffsetY, centerX, centerY, options);
            break;
        case 'newton':
            renderNewtonFractal(width, height, viewScale, viewOffsetX, viewOffsetY, centerX, centerY, options);
            break;
        case 'adaptive':
            renderAdaptiveDomain(width, height, functionStr, viewScale, viewOffsetX, viewOffsetY, centerX, centerY, options);
            break;
        default:
            renderDomainColoring(width, height, functionStr, viewScale, viewOffsetX, viewOffsetY, centerX, centerY, options);
    }
};