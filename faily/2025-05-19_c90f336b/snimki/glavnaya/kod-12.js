// В основном JavaScript файле

function switchMode(mode) {
    currentMode = mode;
    
    // Обновление классов кнопок
    document.getElementById('biomorphicMode').classList.remove('active');
    document.getElementById('domainMode').classList.remove('active');
    document.getElementById('riemannMode').classList.remove('active');
    document.getElementById('fieldMode').classList.remove('active');
    
    // Новые режимы
    if (document.getElementById('adaptiveMode')) {
        document.getElementById('adaptiveMode').classList.remove('active');
    }
    if (document.getElementById('mandelbrotMode')) {
        document.getElementById('mandelbrotMode').classList.remove('active');
    }
    if (document.getElementById('juliaMode')) {
        document.getElementById('juliaMode').classList.remove('active');
    }
    if (document.getElementById('newtonMode')) {
        document.getElementById('newtonMode').classList.remove('active');
    }
    
    document.getElementById(`${mode}Mode`).classList.add('active');
    
    // Обновляем информационный текст и переключаем отображение
    const modeInfo = document.getElementById('modeInfo');
    
    // Скрыть/показать настройки для Жюлиа
    if (document.getElementById('julia-settings')) {
        document.getElementById('julia-settings').style.display = (mode === 'julia') ? 'block' : 'none';
    }
    
    switch(mode) {
        // ... существующие режимы ...
        
        case 'adaptive':
            modeInfo.textContent = 'Адаптивный режим Доменной Карты: интеллектуальный алгоритм автоматически увеличивает детализацию в областях с быстрым изменением функции, обеспечивая оптимальный баланс между качеством и производительностью.';
            mainCanvas.style.display = 'none';
            particleCanvas.style.display = 'none';
            staticCanvas.style.display = 'none';
            domainCanvas.style.display = 'block';
            renderDomainColoring('adaptive');
            break;
        case 'mandelbrot':
            modeInfo.textContent = 'Множество Мандельброта: фрактал, определяемый точками c, для которых итерации функции z² + c остаются ограниченными. Визуализация показывает скорость ухода на бесконечность для точек вне множества.';
            mainCanvas.style.display = 'none';
            particleCanvas.style.display = 'none';
            staticCanvas.style.display = 'none';
            domainCanvas.style.display = 'block';
            renderMandelbrotSet();
            break;
        case 'julia':
            modeInfo.textContent = 'Множество Жюлиа: фрактал, определяемый точками z, для которых итерации функции z² + c остаются ограниченными для фиксированного c. Визуализация показывает границу между устойчивыми и неустойчивыми областями.';
            mainCanvas.style.display = 'none';
            particleCanvas.style.display = 'none';
            staticCanvas.style.display = 'none';
            domainCanvas.style.display = 'block';
            renderJuliaSet();
            break;
        case 'newton':
            modeInfo.textContent = 'Фрактал Ньютона: визуализация метода Ньютона для поиска корней функции z³ - 1. Разные цвета соответствуют областям притяжения трех различных корней, а оттенки показывают скорость сходимости.';
            mainCanvas.style.display = 'none';
            particleCanvas.style.display = 'none';
            staticCanvas.style.display = 'none';
            domainCanvas.style.display = 'block';
            renderNewtonFractal();
            break;
    }
}