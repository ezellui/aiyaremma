// Находим код, который вызывает worker
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
        // ДОБАВИТЬ ЭТИ ПАРАМЕТРЫ:
        argumentPhase: state.argumentPhase,
        functionPhase: state.functionPhase
    }
});