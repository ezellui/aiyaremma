// Define application state
const state = {
    functionExpression: 'z^2 - 1',
    scale: 5,
    xMin: -5,
    xMax: 5,
    yMin: -5,
    yMax: 5,
    resolution: 500,
    gridDensity: 1,
    colorScheme: 'standard',
    highlightZeros: false,
    highlightPoles: false,
    showGrid: true,
    showAxes: true,
    applyDerivative: false,
    applyInverse: false,
    useTransformedGrid: false,  // Добавьте эту строку
    gridThickness: 0.05,        // Добавьте эту строку
    imageData: null,
    markers: [],
    isCalculating: false
};