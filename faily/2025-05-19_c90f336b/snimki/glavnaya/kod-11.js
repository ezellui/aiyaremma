// В основном JavaScript файле, после функции renderDomainColoring()

// Функция для рендеринга множества Мандельброта
function renderMandelbrotSet(options = {}) {
    renderDomainColoring('mandelbrot'); // Используем существующую функцию с новым режимом
}

// Функция для рендеринга множества Жюлиа
function renderJuliaSet(options = {}) {
    // Получаем параметры из слайдеров, если они существуют
    if (document.getElementById('juliaRe') && document.getElementById('juliaIm')) {
        const cRe = parseFloat(document.getElementById('juliaRe').value);
        const cIm = parseFloat(document.getElementById('juliaIm').value);
        options.c = { re: cRe, im: cIm };
    }
    
    // Модифицируем вызов renderDomainColoring для включения параметров Жюлиа
    const worker = new Worker(URL.createObjectURL(new Blob([/* весь код Web Worker */], { type: 'application/javascript' })));
    
    worker.onmessage = function(e) {
        domainCtx.putImageData(e.data.imageData, 0, 0);
        document.getElementById('loading').style.display = 'none';
        worker.terminate();
    };
    
    worker.postMessage({
        width: domainCanvas.width,
        height: domainCanvas.height,
        viewScale: viewScale,
        viewOffsetX: viewOffsetX,
        viewOffsetY: viewOffsetY,
        centerX: centerX,
        centerY: centerY,
        mode: 'julia',
        options: {
            c: options.c || { re: -0.7, im: 0.27 },
            maxIterations: options.maxIterations || 100,
            coloringMethod: options.coloringMethod || 'fire',
            escapeRadius: options.escapeRadius || 2,
            quality: qualityLevel
        }
    });
}

// Функция для рендеринга фрактала Ньютона
function renderNewtonFractal(options = {}) {
    renderDomainColoring('newton'); // Используем существующую функцию с новым режимом
}

// Обработчик для обновления множества Жюлиа
function updateJuliaSet() {
    const cRe = parseFloat(document.getElementById('juliaRe').value);
    const cIm = parseFloat(document.getElementById('juliaIm').value);
    
    document.getElementById('juliaReValue').textContent = cRe;
    document.getElementById('juliaImValue').textContent = cIm;
    
    renderJuliaSet({
        c: { re: cRe, im: cIm }
    });
}