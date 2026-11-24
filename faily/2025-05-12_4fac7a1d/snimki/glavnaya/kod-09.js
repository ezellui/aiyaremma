// Функция для инициализации интерфейса преобразованной решётки
function setupTransformedGrid() {
    // Получаем ссылки на элементы управления
    const useTransformedGridCheckbox = document.getElementById('use-transformed-grid');
    const gridDensityRange = document.getElementById('grid-density-range');
    const gridThicknessRange = document.getElementById('grid-thickness-range');
    
    // Обработчик изменения типа решётки
    useTransformedGridCheckbox.addEventListener('change', function() {
        state.useTransformedGrid = this.checked;
        renderVisualization();
    });
    
    // Обработчики изменения параметров решётки
    gridDensityRange.addEventListener('input', function() {
        state.gridDensity = parseFloat(this.value);
        if (state.useTransformedGrid) {
            renderVisualization();
        }
    });
    
    gridThicknessRange.addEventListener('input', function() {
        state.gridThickness = parseFloat(this.value);
        if (state.useTransformedGrid) {
            renderVisualization();
        }
    });
}