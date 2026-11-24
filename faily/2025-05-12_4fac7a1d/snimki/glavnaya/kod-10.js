// Находим функцию renderVisualization и добавляем в нее передачу параметра useTransformedGrid
function renderVisualization() {
    if (state.isCalculating) return;
    
    // ... существующий код ...
    
    // При отправке сообщения в worker добавляем новые параметры:
    worker.postMessage({
        type: 'calculate',
        params: {
            expression: state.functionExpression,
            width: canvasWidth,
            height: canvasHeight,
            xMin: state.xMin,
            xMax: state.xMax,
            yMin: state.yMin,
            yMax: state.yMax,
            colorScheme: state.colorScheme,
            showGrid: state.showGrid,
            gridDensity: state.gridDensity,
            showAxes: state.showAxes,
            applyDerivative: state.applyDerivative,
            applyInverse: state.applyInverse,
            // Добавляем новые параметры:
            useTransformedGrid: state.useTransformedGrid,
            gridThickness: state.gridThickness,
            argumentPhase: state.argumentPhase || 0,
            functionPhase: state.functionPhase || 0
        }
    });
}